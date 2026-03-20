import pyttsx3
import whisper
import speech_recognition as sr
from logger import log_activity, log_error

# Initialize TTS
engine = pyttsx3.init()
engine.setProperty('rate', 160)

# Initialize Whisper model
try:
    log_activity("Loading Whisper base model...")
    whisper_model = whisper.load_model("base")
    log_activity("Whisper model loaded successfully.")
except Exception as e:
    log_error(f"Failed to load Whisper model: {str(e)}")
    whisper_model = None

def speak(text: str):
    """Convert text to speech."""
    try:
        log_activity(f"Assistant speaking: {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        log_error(f"TTS Error: {str(e)}")

def listen() -> str:
    """Listen to microphone and return transcribed text using Whisper."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        log_activity("Listening to user input...")
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            log_activity("Audio captured, processing with Whisper...")
            
            # Save audio to temp file for Whisper
            with open("temp_audio.wav", "wb") as f:
                f.write(audio.get_wav_data())
            
            if whisper_model:
                result = whisper_model.transcribe("temp_audio.wav", fp16=False)
                text = result['text'].strip()
                log_activity(f"User said: {text}")
                return text
            else:
                log_error("Whisper model not initialized. Using fallback recognition.")
                # Fallback to Google if Whisper failed to load
                text = recognizer.recognize_google(audio)
                log_activity(f"User said (fallback): {text}")
                return text
                
        except sr.WaitTimeoutError:
            log_activity("Listening timed out.")
            return ""
        except Exception as e:
            log_error(f"Error during listening/transcription: {str(e)}")
            return ""
