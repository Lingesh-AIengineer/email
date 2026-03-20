import logging
import os
import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Set up the logger
log_filename = os.path.join(LOGS_DIR, f"app_{datetime.datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("VoiceEmailAssistant")

def log_activity(activity: str):
    logger.info(activity)

def log_error(error_msg: str):
    logger.error(error_msg)

def get_recent_logs(num_lines: int = 50) -> list:
    try:
        with open(log_filename, "r", encoding='utf-8') as f:
            lines = f.readlines()
            return lines[-num_lines:]
    except FileNotFoundError:
        return ["No logs found for today yet."]
