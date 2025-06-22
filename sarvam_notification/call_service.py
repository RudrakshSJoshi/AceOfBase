from fastapi import FastAPI
import logging
import os
from datetime import datetime 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
  
call_app = FastAPI(title="Call Service", version="1.0.0")

# Initialize Twilio
twilio_client = None
from_number = None

try:
    from twilio.rest import Client as TwilioClient
    
    # Set via environment variables or defaults
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "ACbcad108e1ccd3b9f753635c617dbfa18")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "c71af5b34cc04ccfb0f640615dac60b7")
    from_number = os.getenv("TWILIO_FROM_NUMBER", "(903) 459-7027")
    
    twilio_client = TwilioClient(account_sid, auth_token)
    logger.info("Twilio client initialized")
    
except Exception as e:
    logger.error(f"Twilio initialization failed: {e}")

@call_app.post("/call")
async def make_call(request: dict):
    """Make a voice call"""
    try:
        if not twilio_client:
            return {"status": "failed", "error": "Twilio not available"}
        
        phone_number = request.get("phone_number")
        message = request.get("message", "")
        priority = request.get("priority", "high")
        
        if not phone_number:
            return {"status": "failed", "error": "Phone number required"}
        
        # Create TwiML for the call
        twiml = create_twiml(message, priority)
        
        # Make the call
        call = twilio_client.calls.create(
            from_=from_number,
            to=phone_number,
            twiml=twiml
        )
        
        logger.info(f"Call created: {call.sid} to {phone_number}")
        
        return {
            "status": "success",
            "call_sid": call.sid,
            "to": phone_number,
            "message": "Call initiated successfully"
        }
        
    except Exception as e:
        logger.error(f"Call failed: {e}")
        return {"status": "failed", "error": str(e)}

@call_app.get("/call/{call_sid}/status")
async def get_call_status(call_sid: str):
    """Get call status"""
    try:
        if not twilio_client:
            return {"error": "Twilio not available"}
        
        call = twilio_client.calls(call_sid).fetch()
        
        return {
            "call_sid": call.sid,
            "status": call.status,
            "duration": call.duration,
            "start_time": str(call.start_time),
            "end_time": str(call.end_time)
        }
        
    except Exception as e:
        logger.error(f"Failed to get call status: {e}")
        return {"error": str(e)}

@call_app.get("/health")
async def call_health_check():
    return {
        "status": "healthy",
        "service": "call",
        "twilio_available": twilio_client is not None,
        "timestamp": datetime.now().isoformat()
    }

def create_twiml(message: str, priority: str) -> str:
    """Create TwiML for the call"""
    clean_message = message.replace('"', '').replace("'", "")
    
    if priority.lower() in ["critical", "high"]:
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>
        Urgent alert notification. {clean_message}.
        This is a {priority} priority alert.
        The message will repeat once more.
    </Say>
    <Pause length="1"/>
    <Say>
        {clean_message}
    </Say>
    <Pause length="1"/>
    <Say>
        End of urgent alert. Please acknowledge receipt.
    </Say>
</Response>'''
    else:
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>
        Alert notification. {clean_message}.
    </Say>
    <Pause length="1"/>
    <Say>
        End of alert. Thank you.
    </Say>
</Response>'''
    
    return twiml.strip()

# Add this to run the service
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(call_app, host="0.0.0.0", port=9001)