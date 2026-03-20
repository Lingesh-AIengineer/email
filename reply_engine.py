from transformers import pipeline
from logger import log_activity, log_error

try:
    log_activity("Loading smart reply model...")
    # Using flan-t5-small for instructional text-to-text generation
    reply_generator = pipeline("text2text-generation", model="google/flan-t5-small")
    log_activity("Smart reply model loaded successfully.")
except Exception as e:
    log_error(f"Failed to load smart reply model: {str(e)}")
    reply_generator = None

def suggest_reply(email_content: str) -> str:
    """Generate a short suggested reply based on the email content."""
    if not reply_generator:
        log_error("Reply generator model is not available.")
        return "Received, thank you."
    
    prompt = f"Write a short, professional email reply to the following message:\n{email_content}"
    
    try:
        log_activity("Generating suggested reply...")
        response = reply_generator(prompt, max_length=50, do_sample=True, top_p=0.95)
        return response[0]['generated_text']
    except Exception as e:
        log_error(f"Error during reply generation: {str(e)}")
        return "Received, thank you."
