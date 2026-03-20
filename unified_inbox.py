from logger import log_activity

def get_simulated_messages() -> list:
    """Return a list of simulated messages from WhatsApp and Telegram."""
    log_activity("Fetching simulated messages for Unified Inbox...")
    return [
        {
            "id": "wa_1",
            "sender": "John Doe (WhatsApp)",
            "subject": "Lunch Today?",
            "snippet": "Hey, are we still on for lunch at 1 PM?",
            "body": "Hey, are we still on for lunch at 1 PM? Let me know if you need to reschedule.",
            "type": "whatsapp"
        },
        {
            "id": "tg_1",
            "sender": "Project Team Group (Telegram)",
            "subject": "Deployment Status",
            "snippet": "Server deployment is complete. Please monitor the logs.",
            "body": "Server deployment is complete. Please monitor the logs for any issues and report back by EOD.",
            "type": "telegram"
        }
    ]

def collect_unified_inbox(gmail_emails: list) -> list:
    """Combine real emails and simulated messages."""
    log_activity("Aggregating Unified Inbox...")
    simulated_msgs = get_simulated_messages()
    
    # Combined list
    unified_inbox = []
    unified_inbox.extend(gmail_emails)
    unified_inbox.extend(simulated_msgs)
    
    return unified_inbox
