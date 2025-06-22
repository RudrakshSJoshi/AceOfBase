import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class NotificationRequest(BaseModel):
    message: str
    priority: str  # low, medium, high, critical
    phone_number: Optional[str] = None
    source: Optional[str] = "api"
    metadata: Optional[Dict] = None

class NotificationResponse(BaseModel):
    id: str
    status: str
    message: str
    timestamp: str

# API Gateway Service
app = FastAPI(title="Notification Gateway", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs - Fixed to match your actual service ports
SPEECH_SERVICE_URL = "http://localhost:9002"  # Speech service
CALL_SERVICE_URL = "http://localhost:9001"    # Call service
ORCHESTRATOR_URL = "http://localhost:9000"    # Orchestrator service

# In-memory storage (replace with database in production)
notifications_db = {}

# WebSocket connections
active_connections: List[WebSocket] = []

@app.post("/api/v1/notifications", response_model=NotificationResponse)
async def create_notification(request: NotificationRequest):
    """Create a new notification"""
    try:
        notification_id = str(uuid.uuid4())
        
        # Store in memory
        notification_data = {
            "id": notification_id,
            "message": request.message,
            "priority": request.priority,
            "phone_number": request.phone_number,
            "source": request.source,
            "metadata": request.metadata or {},
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        notifications_db[notification_id] = notification_data
        
        # Send to orchestrator
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{ORCHESTRATOR_URL}/process",
                    json=notification_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Orchestrator returned status {response.status}")
                    else:
                        result = await response.json()
                        # Update notification status based on orchestrator response
                        notification_data["status"] = result.get("status", "processed")
                        notification_data["results"] = result.get("results", {})
                        notifications_db[notification_id] = notification_data
            except Exception as e:
                logger.error(f"Failed to contact orchestrator: {e}")
                notification_data["status"] = "failed"
                notification_data["error"] = str(e)
                notifications_db[notification_id] = notification_data
        
        # Broadcast to WebSocket clients
        await broadcast_notification(notification_data)
        
        return NotificationResponse(
            id=notification_id,
            status=notification_data["status"],
            message="Notification processed",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/notifications/{notification_id}")
async def get_notification_status(notification_id: str):
    """Get notification status"""
    try:
        if notification_id not in notifications_db:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return notifications_db[notification_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/notifications")
async def list_notifications():
    """List all notifications"""
    return {"notifications": list(notifications_db.values())}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info("WebSocket client connected")
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway", "timestamp": datetime.now().isoformat()}

@app.get("/services/health")
async def check_all_services():
    """Check health of all dependent services"""
    services = {
        "orchestrator": ORCHESTRATOR_URL,
        "speech": SPEECH_SERVICE_URL,
        "call": CALL_SERVICE_URL
    }
    
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for service_name, url in services.items():
            try:
                async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        results[service_name] = {"status": "healthy", "data": data}
                    else:
                        results[service_name] = {"status": "unhealthy", "error": f"HTTP {response.status}"}
            except Exception as e:
                results[service_name] = {"status": "unreachable", "error": str(e)}
    
    return {
        "gateway": {"status": "healthy"},
        "services": results,
        "timestamp": datetime.now().isoformat()
    }

async def broadcast_notification(notification_data: Dict):
    """Broadcast notification to all WebSocket clients"""
    if active_connections:
        message = json.dumps(notification_data)
        for connection in active_connections.copy():
            try:
                await connection.send_text(message)
            except:
                active_connections.remove(connection)

# Add this to run the service
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9080)