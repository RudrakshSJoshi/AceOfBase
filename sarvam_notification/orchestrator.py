import aiohttp
from fastapi import FastAPI
import logging
from datetime import datetime
import os
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

orchestrator_app = FastAPI(title="Notification Orchestrator", version="1.0.0")

# Allow all origins for CORS
orchestrator_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs - Fixed the port numbers based on your other services
SPEECH_SERVICE_URL = "http://localhost:9002"  # Speech service
CALL_SERVICE_URL = "http://localhost:9001"    # Call service

# Configuration
HIGH_PRIORITY_LEVELS = {"high", "critical"}
DEFAULT_PHONE_NUMBER = "+918439214644"  # Your phone number

@orchestrator_app.post("/process")
async def process_notification(request: dict):
    """Orchestrate notification processing"""
    try:
        notification_id = request.get("id")
        message = request.get("message", "")
        priority = request.get("priority", "medium")
        phone_number = request.get("phone_number") or DEFAULT_PHONE_NUMBER
        
        logger.info(f"Processing notification {notification_id} with priority {priority}")
        
        results = {"speech": None, "call": None}
        
        # Always send speech notification
        speech_result = await send_speech_notification(message, priority)
        results["speech"] = speech_result
        
        # Send call notification for high priority
        if priority.lower() in HIGH_PRIORITY_LEVELS:
            call_result = await make_call_request(phone_number, message, priority)
            results["call"] = call_result
        
        # Determine overall status
        overall_status = determine_status(results, priority)
        
        return {
            "notification_id": notification_id,
            "status": overall_status,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        return {"status": "failed", "error": str(e)}

@orchestrator_app.get("/health")
async def orchestrator_health_check():
    return {"status": "healthy", "service": "orchestrator", "timestamp": datetime.now().isoformat()}

async def send_speech_notification(message: str, priority: str) -> dict:
    """Send speech notification to speech service"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{SPEECH_SERVICE_URL}/speak",
                json={"message": message, "priority": priority},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                return await response.json()
                
    except Exception as e:
        logger.error(f"Speech service call failed: {e}")
        return {"status": "failed", "error": str(e)}

async def make_call_request(phone_number: str, message: str, priority: str) -> dict:
    """Make call via call service"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CALL_SERVICE_URL}/call",
                json={
                    "phone_number": phone_number,
                    "message": message,
                    "priority": priority
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                return await response.json()
                
    except Exception as e:
        logger.error(f"Call service call failed: {e}")
        return {"status": "failed", "error": str(e)}

def determine_status(results: dict, priority: str) -> str:
    """Determine overall notification status"""
    speech_success = results.get("speech", {}).get("status") == "success"
    call_result = results.get("call")
    
    if priority.lower() in HIGH_PRIORITY_LEVELS:
        # High priority needs both speech and call
        call_success = call_result and call_result.get("status") == "success"
        
        if speech_success and call_success:
            return "success"
        elif speech_success or call_success:
            return "partial"
        else:
            return "failed"
    else:
        # Low/medium priority only needs speech
        return "success" if speech_success else "failed"

# Add this to run the service
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(orchestrator_app, host="0.0.0.0", port=9000)