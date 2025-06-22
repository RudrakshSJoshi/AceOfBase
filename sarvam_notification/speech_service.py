import os
import subprocess
import platform
import base64
from fastapi import FastAPI
import logging
from datetime import datetime
speech_app = FastAPI(title="Speech Notification Service", version="1.0.0")

# Initialize Sarvam AI if available
sarvam_client = None
try:
    from sarvamai import AsyncSarvamAI
    api_key = os.getenv("SARVAM_API_KEY", "sk_nflhd9sq_i1LriyyGRbgwVwlyDySc6wru")
    sarvam_client = AsyncSarvamAI(api_subscription_key=api_key)
    logging.info("Sarvam AI initialized")
except Exception as e:
    logging.warning(f"Sarvam AI not available: {e}")

@speech_app.post("/speak")
async def create_speech_notification(request: dict):
    """Process speech notification"""
    try:
        message = request.get("message", "")
        priority = request.get("priority", "medium")
        
        # Add priority context to message
        speech_text = f"{priority} priority alert. {message}"
        
        # Try speech generation
        success = await play_speech(speech_text)
        
        return {
            "status": "success" if success else "failed",
            "message": "Speech notification processed",
            "method": "sarvam" if sarvam_client else "windows_sapi"
        }
        
    except Exception as e:
        logging.error(f"Speech notification failed: {e}")
        return {"status": "failed", "error": str(e)}

@speech_app.get("/health")
async def speech_health_check():
    return {
        "status": "healthy", 
        "service": "speech",
        "sarvam_available": sarvam_client is not None,
        "timestamp": datetime.now().isoformat()
    }

async def play_speech(text: str) -> bool:
    """Play speech with fallback options"""
    # Try Sarvam AI
    if sarvam_client:
        try:
            response = await sarvam_client.text_to_speech.convert(
                text=text,
                target_language_code="en-IN",
                speaker="anushka"
            )
            
            # Play audio
            combined_audio = "".join(response.audios)
            audio_bytes = base64.b64decode(combined_audio)
            
            if play_audio_pygame(audio_bytes):
                logging.info("Sarvam speech played successfully")
                return True
                
        except Exception as e:
            logging.error(f"Sarvam speech failed: {e}")
    
    # Fallback to Windows SAPI
    if platform.system() == "Windows":
        return await play_windows_sapi(text)
    
    # Final fallback
    logging.info(f"[SPEECH FALLBACK] {text}")
    return True

def play_audio_pygame(audio_bytes: bytes) -> bool:
    """Play audio using pygame"""
    try:
        import pygame
        import io
        
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        audio_buffer = io.BytesIO(audio_bytes)
        pygame.mixer.music.load(audio_buffer)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        pygame.mixer.quit()
        return True
        
    except Exception as e:
        logging.error(f"Pygame playback failed: {e}")
        return False

async def play_windows_sapi(text: str) -> bool:
    """Play speech using Windows SAPI"""
    try:
        clean_text = text.replace('"', '').replace("'", "")
        
        powershell_cmd = f'''
        Add-Type -AssemblyName System.Speech
        $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $synth.Speak("{clean_text}")
        $synth.Dispose()
        '''
        
        result = subprocess.run(
            ["powershell", "-Command", powershell_cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.returncode == 0
        
    except Exception as e:
        logging.error(f"Windows SAPI failed: {e}")
        return False
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(speech_app, host="0.0.0.0", port=9002)