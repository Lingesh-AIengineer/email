from logger import log_activity, log_error

USER_PIN = "1234"

def verify_pin(input_pin: str) -> bool:
    """Verify if the entered PIN is correct."""
    is_valid = input_pin.strip() == USER_PIN
    if is_valid:
        log_activity("PIN verification successful.")
    else:
        log_activity(f"Failed PIN attempt: {input_pin}")
    return is_valid

def confirm_action(voice_input: str) -> bool:
    """Check if the user confirmed an action via voice."""
    affirmative = ["yes", "yeah", "sure", "confirm", "send", "do it"]
    if any(word in voice_input.lower() for word in affirmative):
        log_activity("User confirmed action via voice.")
        return True
    
    log_activity("User denied action via voice.")
    return False
