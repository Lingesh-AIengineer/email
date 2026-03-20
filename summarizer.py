from transformers import pipeline
from logger import log_activity, log_error

try:
    log_activity("Loading summarization model...")
    # Using a smaller model for faster local execution
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    log_activity("Summarization model loaded successfully.")
except Exception as e:
    log_error(f"Failed to load summarization model: {str(e)}")
    summarizer = None

def summarize_text(text: str, max_length: int = 50, min_length: int = 10) -> str:
    """Summarize long email text."""
    if not summarizer:
        log_error("Summarizer model is not available.")
        return text[:200] + "..." # Fallback: return first 200 chars
    
    # If text is very short, no need to summarize
    if len(text.split()) < 30:
        return text
    
    try:
        log_activity("Summarizing text...")
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        log_error(f"Error during summarization: {str(e)}")
        return text[:200] + "..."
