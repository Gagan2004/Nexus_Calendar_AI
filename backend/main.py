
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from simple_agent import ConversationalCalendarAgent
import traceback
from loguru import logger
import logging
import os
from datetime import datetime
from typing import Optional

logging.basicConfig(filename="debug.log", level=logging.DEBUG)
logger.add("debug.log", level="DEBUG", rotation="1 MB")

app = FastAPI(
    title="AI Calendar Assistant API",
    description="Conversational AI agent for booking appointments on Google Calendar",
    version="1.0.0"
)

# Initialize conversational agent
try:
    agent = ConversationalCalendarAgent()
    logger.info("✅ ConversationalCalendarAgent loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load agent: {e}")
    agent = None

class Message(BaseModel):
    input: str
    session_id: Optional[str] = None

class ResetRequest(BaseModel):
    session_id: Optional[str] = None

class BookingInfo(BaseModel):
    name: str
    date: str
    time: str
    duration: int = 30

@app.get("/")
def root():
    return {
        "status": "✅ AI Calendar Assistant API is running",
        "message": "Welcome to the AI Calendar Assistant! Use /chat to interact with the bot.",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Natural language conversation",
            "Google Calendar integration",
            "Intelligent time slot suggestions",
            "Booking confirmation and management"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_loaded": agent is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat")
def chat_with_bot(msg: Message):
    """Main chat endpoint for conversational booking"""
    logger.info("🔥 /chat endpoint was hit")
    logger.info(f"📥 Received input: {msg.input}")
    logger.info(f"📋 Session ID: {msg.session_id}")
    
    if agent is None:
        logger.error("❌ Agent not initialized")
        return {
            "response": "❌ Sorry, the calendar assistant is currently unavailable. Please try again later.",
            "error": "Agent not initialized"
        }
    
    try:
        logger.info("🤖 Processing with ConversationalCalendarAgent...")
        
        # Process the conversation using the new method
        response = agent.process_message(msg.input)
        
        # Get current conversation state for debugging
        current_state = agent.conversation_state
        logger.info(f"🔄 Conversation state: {current_state['mode']}")
        logger.info(f"📝 Booking info: {current_state['booking_info']}")
        
        logger.info(f"🤖 Agent response: {response}")
        
        return {
            "response": response,
            "conversation_state": {
                "mode": current_state['mode'],
                "current_task": current_state['current_task'],
                "booking_info": current_state['booking_info'],
                "confirmation_pending": current_state['confirmation_pending'],
                "pending_action": current_state['pending_action'],
                "conversation_memory_length": len(current_state['conversation_memory'])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Exception in chat_with_bot: {e}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return {
            "response": "❌ I apologize, but I encountered an error while processing your request. Please try again.",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/reset-conversation")
def reset_conversation(request: ResetRequest):
    """Reset the conversation state"""
    logger.info("🔄 Resetting conversation state")
    logger.info(f"📋 Session ID: {request.session_id}")
    
    if agent is None:
        logger.error("❌ Agent not initialized")
        return {"error": "Agent not initialized"}
    
    try:
        agent.reset_conversation()
        logger.info("✅ Conversation reset successfully")
        
        return {
            "status": "success",
            "message": "Conversation reset successfully. You can start a new booking process.",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error resetting conversation: {e}")
        return {
            "error": f"Failed to reset conversation: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/conversation-state")
def get_conversation_state():
    """Get current conversation state"""
    if agent is None:
        return {"error": "Agent not initialized"}
    
    try:
        state = agent.conversation_state
        return {
            "mode": state['mode'],
            "current_task": state['current_task'],
            "booking_info": state['booking_info'],
            "modification_info": state['modification_info'],
            "events_context": state['events_context'],
            "conversation_memory_length": len(state['conversation_memory']),
            "user_preferences": state['user_preferences'],
            "last_action": state['last_action'],
            "confirmation_pending": state['confirmation_pending'],
            "pending_action": state['pending_action'],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting conversation state: {e}")
        return {"error": str(e)}

@app.post("/direct-booking")
def direct_booking(booking: BookingInfo):
    """Direct booking endpoint (bypasses conversation)"""
    logger.info("📅 Direct booking request received")
    logger.info(f"📝 Booking details: {booking.dict()}")
    
    try:
        from tools import book_appointment
        
        result = book_appointment(
            name=booking.name,
            date=booking.date,
            time=booking.time,
            duration=booking.duration
        )
        
        logger.info(f"📅 Direct booking result: {result}")
        return {
            "booking_result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Direct booking failed: {e}")
        return {
            "error": f"Direct booking failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/available-slots/{date}")
def get_available_slots(date: str, duration: int = 30):
    """Get available time slots for a specific date"""
    logger.info(f"📅 Getting available slots for {date}")
    
    try:
        from tools import get_free_time_slots
        
        slots = get_free_time_slots(date, duration)
        
        logger.info(f"✅ Found {len(slots)} available slots")
        return {
            "date": date,
            "duration": duration,
            "available_slots": slots,
            "count": len(slots),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting available slots: {e}")
        return {
            "error": f"Failed to get available slots: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/upcoming-events")
def get_upcoming_events(days_ahead: int = 7):
    """Get upcoming events"""
    logger.info(f"📅 Getting upcoming events for next {days_ahead} days")
    
    try:
        from tools import get_upcoming_events
        
        events = get_upcoming_events(days_ahead)
        
        logger.info(f"✅ Found {len(events)} upcoming events")
        return {
            "upcoming_events": events,
            "days_ahead": days_ahead,
            "count": len(events),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting upcoming events: {e}")
        return {
            "error": f"Failed to get upcoming events: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/test-booking")
def test_booking():
    """Test booking endpoint for debugging"""
    logger.info("🧪 Testing booking directly...")
    
    try:
        from tools import book_appointment
        
        # Use tomorrow's date for testing
        from datetime import date, timedelta
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        result = book_appointment("Test User", tomorrow, "15:30", 30)
        logger.info(f"🧪 Direct booking result: {result}")
        
        return {
            "test_result": result,
            "test_date": tomorrow,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Direct booking test failed: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/test-calendar-connection")
def test_calendar_connection():
    """Test Google Calendar connection"""
    logger.info("🧪 Testing Google Calendar connection...")
    
    try:
        from tools import service
        
        if service is None:
            return {
                "status": "error",
                "message": "Google Calendar service not initialized",
                "timestamp": datetime.now().isoformat()
            }
        
        # Try to get calendar info
        calendar_info = service.calendars().get(calendarId='primary').execute()
        
        return {
            "status": "success",
            "message": "Google Calendar connection successful",
            "calendar_summary": calendar_info.get('summary', 'Unknown'),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Calendar connection test failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/conversation-history")
def get_conversation_history():
    """Get conversation history"""
    if agent is None:
        return {"error": "Agent not initialized"}
    
    try:
        memory = agent.conversation_state['conversation_memory']
        return {
            "conversation_history": memory,
            "total_interactions": len(memory),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting conversation history: {e}")
        return {"error": str(e)}

@app.post("/set-user-preferences")
def set_user_preferences(preferences: dict):
    """Set user preferences"""
    if agent is None:
        return {"error": "Agent not initialized"}
    
    try:
        agent.conversation_state['user_preferences'].update(preferences)
        return {
            "status": "success",
            "message": "User preferences updated successfully",
            "preferences": agent.conversation_state['user_preferences'],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error setting user preferences: {e}")
        return {"error": str(e)}

@app.get("/agent-capabilities")
def get_agent_capabilities():
    """Get agent capabilities and features"""
    return {
        "capabilities": {
            "booking": {
                "description": "Schedule new meetings with intelligent time suggestions",
                "features": [
                    "Natural language processing",
                    "Smart time slot suggestions",
                    "Conflict detection",
                    "Confirmation workflow"
                ]
            },
            "modification": {
                "description": "Modify existing meetings",
                "features": [
                    "Reschedule meetings",
                    "Change meeting details",
                    "Update attendees",
                    "Modify duration"
                ]
            },
            "cancellation": {
                "description": "Cancel existing meetings",
                "features": [
                    "Cancel single meetings",
                    "Cancel recurring meetings",
                    "Confirmation workflow"
                ]
            },
            "viewing": {
                "description": "View schedule and meetings",
                "features": [
                    "Show daily schedule",
                    "Show weekly schedule",
                    "Show upcoming meetings",
                    "Search meetings"
                ]
            },
            "conversation": {
                "description": "Natural conversation flow",
                "features": [
                    "Context awareness",
                    "Intent recognition",
                    "Multi-turn conversations",
                    "Memory retention"
                ]
            }
        },
        "supported_intents": [
            "book_meeting",
            "modify_meeting", 
            "cancel_meeting",
            "view_schedule",
            "general_chat",
            "confirm_action",
            "decline_action",
            "provide_info"
        ],
        "conversation_modes": [
            "idle",
            "booking",
            "modifying",
            "cancelling",
            "viewing"
        ],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")