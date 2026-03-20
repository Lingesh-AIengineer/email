import os.path
import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from logger import log_activity, log_error

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = 'credentials.json'

def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                log_error("credentials.json not found! Cannot authenticate Gmail API.")
                return None
            
            from google_auth_oauthlib.flow import Flow
            from http.server import BaseHTTPRequestHandler, HTTPServer
            from urllib.parse import urlparse, parse_qs
            
            # Use Flow instead of InstalledAppFlow to allow explicit redirect_uri
            flow = Flow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES, redirect_uri='http://localhost:8501/oauth2callback')
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            with open('auth_link.txt', 'w') as f:
                f.write(auth_url)
            print(f"AUTHORIZATION_URL_IS:{auth_url}\n")
            
            # Start a custom local server to catch the redirect robustly
            class AuthHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"<h1>Authentication successful!</h1><p>You can close this window and return to the application.</p>")
                    query = parse_qs(urlparse(self.path).query)
                    if 'code' in query:
                        self.server.auth_code = query['code'][0]
            
            httpd = HTTPServer(('localhost', 8501), AuthHandler)
            httpd.auth_code = None
            while httpd.auth_code is None:
                httpd.handle_request()
                
            flow.fetch_token(code=httpd.auth_code)
            creds = flow.credentials
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        log_activity("Gmail authenticated successfully.")
        return service
    except HttpError as error:
        log_error(f"Gmail Error: {error}")
        return None

def fetch_recent_emails(service, max_results=5) -> list:
    """Fetch the latest max_results emails from the inbox."""
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        email_list = []
        if not messages:
            log_activity("No new emails found.")
            return []
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                
                # Extract headers
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                
                # Extract body
                body = ""
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            if part.get('body') and part['body'].get('data'):
                                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                    body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
                
                email_list.append({
                    "id": msg['id'],
                    "sender": sender,
                    "subject": subject,
                    "snippet": msg['snippet'],
                    "body": body,
                    "type": "email"
                })
            return email_list
            
    except HttpError as error:
        log_error(f"Error fetching emails: {error}")
        return []

def send_email(service, to_email: str, subject: str, content: str) -> bool:
    """Send an email."""
    try:
        message = EmailMessage()
        message.set_content(content)
        message['To'] = to_email
        message['From'] = 'me'
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        log_activity(f"Email sent to {to_email}. Msg Id: {send_message['id']}")
        return True
    except HttpError as error:
        log_error(f"Error sending email: {error}")
        return False
