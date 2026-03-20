import streamlit as st
import pandas as pd
import time
import threading

# Import project modules
from logger import get_recent_logs, log_activity, log_error
from gmail_service import authenticate_gmail, fetch_recent_emails, send_email
from unified_inbox import collect_unified_inbox
from summarizer import summarize_text
from reply_engine import suggest_reply
from security import verify_pin, confirm_action
from voice_engine import listen, speak

st.set_page_config(page_title="Voice-Driven Email Assistant", page_icon="🎤", layout="wide")

def run_voice_assistant(service):
    """The main loop for voice interaction."""
    speak("Assistant triggered. How can I help you today?")
    while True:
        command = listen().lower()
        if not command:
            continue
        
        if "exit" in command or "stop" in command or "quit" in command:
            speak("Goodbye!")
            log_activity("User exited voice assistant.")
            break
            
        elif "check inbox" in command or "read email" in command:
            speak("Checking your unified inbox.")
            emails = fetch_recent_emails(service, max_results=3)
            inbox = collect_unified_inbox(emails)
            
            if not inbox:
                speak("You have no new messages.")
                continue
                
            speak(f"You have {len(inbox)} recent messages. Reading the latest one.")
            latest = inbox[0]
            speak(f"Message from {latest['sender']}. Subject: {latest['subject']}.")
            
            # Ask if user wants summary
            speak("Would you like me to summarize the message?")
            ans = listen().lower()
            if confirm_action(ans):
                summary = summarize_text(latest['body'])
                speak(f"Summary: {summary}")
            
            # Ask for smart reply
            speak("Would you like a suggested reply?")
            ans = listen().lower()
            if confirm_action(ans):
                suggestion = suggest_reply(latest['body'])
                speak(f"Suggested reply is: {suggestion}")
                
        elif "send email" in command:
            speak("Who is the recipient?")
            # For proof of concept, we just echo back or hardcode
            recipient = listen().lower().replace(" at ", "@").replace(" ", "")
            if not recipient:
                speak("I didn't catch the email address. Cancelling.")
                continue
                
            speak("What is the subject?")
            subject = listen()
            
            speak("What is the message?")
            body = listen()
            
            speak(f"To: {recipient}. Subject: {subject}. Message: {body}. Do you confirm?")
            ans = listen().lower()
            if confirm_action(ans):
                speak("Please speak your 4-digit PIN to authorize sending.")
                pin_input = listen()
                
                # Try to extract numbers
                numbers = ''.join(filter(str.isdigit, pin_input))
                if not numbers:
                    # sometimes whisper outputs numbers as words
                    speak("PIN not recognized. Cancelling.")
                    continue
                    
                if verify_pin(numbers):
                    speak("PIN verified. Sending email.")
                    if send_email(service, recipient, subject, body):
                        speak("Email sent successfully.")
                    else:
                        speak("Failed to send email.")
                else:
                    speak("Incorrect PIN. Access denied.")
            else:
                speak("Cancelled sending email.")
        else:
            speak("Command not recognized. Please say check inbox, send email, or exit.")


def main():
    st.title("🎤 Voice-Driven Email Assistant Dashboard")
    st.markdown("A multi-module intelligent assistant empowering users through speech interaction.")
    
    # Initialize Gmail Service
    if 'gmail_service' not in st.session_state:
        st.session_state.gmail_service = authenticate_gmail()
        
    if st.session_state.gmail_service is None:
        st.error("Failed to authenticate with Gmail API. Please check credentials.json.")
        st.stop()
        
    # Sidebar
    st.sidebar.header("Navigation")
    menu = st.sidebar.radio("Go to:", ["Admin Dashboard", "Unified Inbox", "Assistant Control"])
    
    if menu == "Assistant Control":
        st.header("Voice Control Center")
        st.write("Click the button below to start voice interaction. The assistant will guide you.")
        if st.button("🎙️ Start Voice Assistant"):
            st.info("Assistant is running. Please check your terminal and speak into the microphone.")
            log_activity("Voice Assistant triggered from UI.")
            run_voice_assistant(st.session_state.gmail_service)
            st.success("Assistant session ended.")
            
    elif menu == "Unified Inbox":
        st.header("Unified Inbox (Emails & Messages)")
        with st.spinner("Fetching emails and simulated messages..."):
            raw_emails = fetch_recent_emails(st.session_state.gmail_service, max_results=10)
            inbox_items = collect_unified_inbox(raw_emails)
            
        if not inbox_items:
            st.write("No messages found.")
        else:
            for item in inbox_items:
                with st.expander(f"[{item['type'].upper()}] From: {item['sender']} - {item['subject']}"):
                    st.write(f"**Snippet:** {item['snippet']}")
                    st.write(f"**Body:**\n{item['body']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Summarize {item['id']}"):
                            with st.spinner("Summarizing..."):
                                sum_res = summarize_text(item['body'])
                                st.info(sum_res)
                    with col2:
                        if st.button(f"Suggest Reply {item['id']}"):
                            with st.spinner("Generating Reply..."):
                                rep_res = suggest_reply(item['body'])
                                st.success(rep_res)
                                
    elif menu == "Admin Dashboard":
        st.header("Activity Logs & System Metrics")
        
        # Display Logs
        st.subheader("Recent System Logs")
        logs = get_recent_logs(20)
        logs_text = "".join(logs)
        st.text_area("System Logs", value=logs_text, height=300, disabled=True)
        
        # Mock Metrics
        st.subheader("Performance Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Emails Processed", "124", "12")
        col2.metric("Voice Interactions", "89", "5")
        col3.metric("Summaries Generated", "45", "3")
        
        st.caption("Auto-refreshing is not enabled. Switch tabs to refresh logs.")

if __name__ == "__main__":
    main()
