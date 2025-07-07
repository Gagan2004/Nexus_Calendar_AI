#conversational_agent.py
import os
import re
import json
from difflib import get_close_matches
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv


from tools import (
    book_appointment, check_calendar_availability, get_free_time_slots,
    cancel_appointment, get_upcoming_events, get_event_details , modify_appointment
)
from loguru import logger
import logging

logging.basicConfig(filename="debug.log", level=logging.DEBUG)
logger.add("debug.log", level="DEBUG", rotation="1 MB")

# Set API key
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')


class ConversationalCalendarAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.2,  # Slightly higher for more natural responses
            api_key=GROQ_API_KEY
        )
        
        # Enhanced conversation state
        self.conversation_state = {
            'mode': 'idle',  # idle, booking, modifying, cancelling, viewing
            'current_task': None,
            'booking_info': {},
            'modification_info': {},
            'events_context': [],
            'conversation_memory': [],
            'user_preferences': {},
            'last_action': None,
            'context_window': 5,  # Remember last 5 interactions
            'confirmation_pending': False,
            'pending_action': None
        }
        
        # Natural language patterns for better understanding
        self.patterns = {
            'booking_keywords': [
                'book', 'schedule', 'set up', 'arrange', 'plan', 'meet', 'meeting',
                'appointment', 'call', 'catch up', 'discussion', 'session'
            ],
            'modification_keywords': [
                'change', 'modify', 'update', 'move', 'reschedule', 'shift', 'edit',
                'adjust', 'postpone', 'bring forward', 'earlier', 'later'
            ],
            'cancellation_keywords': [
                'cancel', 'delete', 'remove', 'drop', 'abort', 'scratch', 'nevermind'
            ],
            'viewing_keywords': [
                'show', 'see', 'view', 'list', 'what', 'when', 'schedule', 'calendar',
                'upcoming', 'today', 'tomorrow', 'week', 'events'
            ],
            'time_expressions': [
                'morning', 'afternoon', 'evening', 'noon', 'midnight', 'lunch',
                'early', 'late', 'asap', 'soon', 'today', 'tomorrow', 'next week'
            ],
            'confirmation_positive': [
                'yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'correct', 'right',
                'confirm', 'go ahead', 'proceed', 'book it', 'do it', 'sounds good'
            ],
            'confirmation_negative': [
                'no', 'nope', 'not', 'wrong', 'different', 'change', 'cancel'
            ]
        }
        
        logger.info("✅ Enhanced Calendar Agent initialized")
    
    def add_to_memory(self, user_input: str, agent_response: str, context: Dict = None):
        """Add interaction to conversation memory with context"""
        memory_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'agent_response': agent_response,
            'context': context or {},
            'mode': self.conversation_state['mode']
        }
        
        self.conversation_state['conversation_memory'].append(memory_entry)
        
        # Keep only recent interactions
        if len(self.conversation_state['conversation_memory']) > self.conversation_state['context_window']:
            self.conversation_state['conversation_memory'].pop(0)
    
    def get_conversation_context(self) -> str:
        """Get formatted conversation context for the LLM"""
        if not self.conversation_state['conversation_memory']:
            return ""
        
        context = "Recent conversation:\n"
        for entry in self.conversation_state['conversation_memory'][-3:]:
            context += f"User: {entry['user_input']}\n"
            context += f"Assistant: {entry['agent_response']}\n\n"
        
        return context
    
    def understand_intent(self, user_input: str) -> Dict[str, Any]:
        """Advanced intent understanding using LLM with context"""
        
        conversation_context = self.get_conversation_context()
        current_state = self.conversation_state
        
        # Get recent events for context
        recent_events = get_upcoming_events(days_ahead=14, max_results=10)
        events_context = ""
        if recent_events:
            events_context = "User's upcoming events:\n"
            for event in recent_events[:5]:
                events_context += f"- {event['start']}: {event['summary']}\n"
        
        intent_prompt = f"""
You are an intelligent calendar assistant. Analyze the user's message and determine their intent.

Current conversation context:
{conversation_context}

Current agent state:
- Mode: {current_state['mode']}
- Current task: {current_state['current_task']}
- Booking info: {current_state['booking_info']}
- Confirmation pending: {current_state['confirmation_pending']}

{events_context}

User's message: "{user_input}"

Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Analyze and respond with a JSON object containing:
{{
    "primary_intent": "book_meeting|modify_meeting|cancel_meeting|view_schedule|general_chat|confirm_action|decline_action|provide_info",
    "confidence": 0.0-1.0,
    "extracted_info": {{
        "name": "person's name or null",
        "date": "YYYY-MM-DD format or null",
        "time": "HH:MM format or null", 
        "duration": "number in minutes or null",
        "event_reference": "reference to existing event or null",
        "modification_type": "time|date|duration|cancel|null"
    }},
    "context_clues": {{
        "is_followup": true/false,
        "references_previous": true/false,
        "urgency_level": "low|medium|high",
        "politeness_level": "casual|formal|urgent"
    }},
    "suggested_response_style": "informative|confirmatory|questioning|conversational",
    "missing_information": ["list of missing details needed"],
    "user_emotion": "neutral|excited|frustrated|confused|happy"
}}

Be especially attentive to:
- References to "it", "that", "the meeting" (referring to previous context)
- Time expressions like "later", "earlier", "next week"
- Implicit confirmations like "sounds good", "perfect"
- Modifications like "can we make it earlier"
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=intent_prompt)])
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                intent_data = json.loads(json_match.group())
                logger.info(f"🧠 Intent analysis: {intent_data}")
                return intent_data
            else:
                logger.warning("❌ Could not extract JSON from intent analysis")
                return self.fallback_intent_analysis(user_input)
                
        except Exception as e:
            logger.error(f"❌ Intent analysis failed: {e}")
            return self.fallback_intent_analysis(user_input)
    
    def fallback_intent_analysis(self, user_input: str) -> Dict[str, Any]:
        """Fallback intent analysis using keyword matching"""
        user_lower = user_input.lower()
        
        # Simple keyword-based intent detection
        if any(word in user_lower for word in self.patterns['booking_keywords']):
            intent = "book_meeting"
        elif any(word in user_lower for word in self.patterns['modification_keywords']):
            intent = "modify_meeting"
        elif any(word in user_lower for word in self.patterns['cancellation_keywords']):
            intent = "cancel_meeting"
        elif any(word in user_lower for word in self.patterns['viewing_keywords']):
            intent = "view_schedule"
        elif any(word in user_lower for word in self.patterns['confirmation_positive']):
            intent = "confirm_action"
        elif any(word in user_lower for word in self.patterns['confirmation_negative']):
            intent = "decline_action"
        else:
            intent = "general_chat"
        
        return {
            "primary_intent": intent,
            "confidence": 0.7,
            "extracted_info": {},
            "context_clues": {"is_followup": False},
            "suggested_response_style": "conversational",
            "missing_information": [],
            "user_emotion": "neutral"
        }
    
    def generate_smart_response(self, intent_data: Dict[str, Any], user_input: str) -> str:
        """Generate contextually appropriate response"""
        
        conversation_context = self.get_conversation_context()
        current_state = self.conversation_state
        
        response_prompt = f"""
You are a highly capable calendar assistant. Generate a natural, helpful response based on the analysis.

Conversation context:
{conversation_context}

Current state:
- Mode: {current_state['mode']}
- Pending confirmation: {current_state['confirmation_pending']}
- Current booking info: {current_state['booking_info']}

User's message: "{user_input}"

Intent analysis:
{json.dumps(intent_data, indent=2)}

Guidelines:
1. Be conversational and natural
2. Show you understand the context
3. Be proactive in helping
4. Handle ambiguity gracefully
5. Confirm important details
6. Be empathetic to user's needs
7. Keep responses concise but complete

Response style should be: {intent_data.get('suggested_response_style', 'conversational')}
User emotion detected: {intent_data.get('user_emotion', 'neutral')}

Generate a helpful response that moves the conversation forward effectively.
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=response_prompt)])
            return response.content.strip()
        except Exception as e:
            logger.error(f"❌ Response generation failed: {e}")
            return "I'm here to help with your calendar. What would you like to do?"
    
    def process_message(self, user_input: str) -> str:
        """Main message processing pipeline"""
        logger.info(f"🔄 Processing: {user_input}")
        
        # Understand intent
        intent_data = self.understand_intent(user_input)
        primary_intent = intent_data.get('primary_intent', 'general_chat')
        
        # Route to appropriate handler
        if primary_intent == 'book_meeting':
            response = self.handle_booking_flow(intent_data, user_input)
        elif primary_intent == 'modify_meeting':
            response = self.handle_modification_flow(intent_data, user_input)
        elif primary_intent == 'cancel_meeting':
            response = self.handle_cancellation_flow(intent_data, user_input)
        elif primary_intent == 'view_schedule':
            response = self.handle_viewing_flow(intent_data, user_input)
        elif primary_intent == 'confirm_action':
            response = self.handle_confirmation(intent_data, user_input)
        elif primary_intent == 'decline_action':
            response = self.handle_decline(intent_data, user_input)
        elif primary_intent == 'provide_info':
            response = self.handle_info_provision(intent_data, user_input)
        else:
            response = self.handle_general_conversation(intent_data, user_input)
        
        # Add to memory
        self.add_to_memory(user_input, response, {
            'intent': primary_intent,
            'confidence': intent_data.get('confidence', 0.0)
        })
        
        return response
    
    def handle_booking_flow(self, intent_data: Dict[str, Any], user_input: str) -> str:
        """Handle booking requests with dynamic flow"""
        self.conversation_state['mode'] = 'booking'
        
        # Extract and update booking info
        extracted_info = intent_data.get('extracted_info', {})
        booking_info = self.conversation_state['booking_info']
        
        # Update booking info with extracted data
        for key, value in extracted_info.items():
            if value:
                booking_info[key] = value
        
        # Check what's missing
        missing_info = []
        if not booking_info.get('name'):
            missing_info.append('name')
        if not booking_info.get('date'):
            missing_info.append('date')
        if not booking_info.get('time'):
            missing_info.append('time')
        
        if missing_info:
            return self.request_missing_info(missing_info, booking_info)
        else:
            return self.process_booking_request(booking_info)
    
    def handle_modification_flow(self, intent_data: Dict[str, Any], user_input: str) -> str:
        """Handle meeting modifications"""
        self.conversation_state['mode'] = 'modifying'
        
        # Get upcoming events for context
        events = get_upcoming_events(days_ahead=14, max_results=10)
        
        if not events:
            return "I don't see any upcoming meetings to modify. Would you like to schedule a new meeting instead?"
        
        # Try to identify which event to modify
        event_reference = intent_data.get('extracted_info', {}).get('event_reference')
        
        if not event_reference:
            # Show recent events and ask for clarification
            events_list = "Here are your upcoming meetings:\n"
            for i, event in enumerate(events[:5], 1):
                events_list += f"{i}. {event['start']} - {event['summary']}\n"
            
            return f"{events_list}\nWhich meeting would you like to modify? You can refer to it by number or name."
        
        # Process the modification
        return self.process_modification_request(intent_data, events)
    
    def handle_cancellation_flow(self, intent_data: Dict[str, Any], user_input: str) -> str:
        """Handle meeting cancellations"""
        self.conversation_state['mode'] = 'cancelling'
        
        events = get_upcoming_events(days_ahead=14, max_results=10)
        
        if not events:
            return "You don't have any upcoming meetings to cancel."
        
        # Try to identify which event to cancel
        event_reference = intent_data.get('extracted_info', {}).get('event_reference')
        
        if not event_reference:
            events_list = "Here are your upcoming meetings:\n"
            for i, event in enumerate(events[:5], 1):
                events_list += f"{i}. {event['start']} - {event['summary']}\n"
            
            return f"{events_list}\nWhich meeting would you like to cancel? You can refer to it by number or name."
        
        return self.process_cancellation_request(intent_data, events)
    
    def handle_viewing_flow(self, intent_data: Dict[str, Any], user_input: str) -> str:
        """Handle schedule viewing requests"""
        self.conversation_state['mode'] = 'viewing'
        
        # Determine time range based on user input
        user_lower = user_input.lower()
        
        if 'today' in user_lower:
            days_ahead = 1
            time_description = "today"
        elif 'tomorrow' in user_lower:
            days_ahead = 2
            time_description = "tomorrow"
        elif 'week' in user_lower:
            days_ahead = 7
            time_description = "this week"
        else:
            days_ahead = 14
            time_description = "the next two weeks"
        
        events = get_upcoming_events(days_ahead=days_ahead, max_results=20)
        
        if not events:
            return f"You don't have any meetings scheduled for {time_description}."
        
        # Format events nicely
        events_list = f"Here are your meetings for {time_description}:\n\n"
        
        current_date = None
        for event in events:
            event_date = event['start'].split(' ')[0]
            if event_date != current_date:
                current_date = event_date
                events_list += f"📅 {current_date}\n"
            
            event_time = event['start'].split(' ')[1]
            events_list += f"  🕐 {event_time} - {event['summary']}\n"
        
        return events_list
    
    def handle_confirmation(self, intent_data: Dict[str, Any], user_input: str) -> str:
        """Handle user confirmations"""
        if not self.conversation_state['confirmation_pending']:
            return "I'm not sure what you're confirming. Could you please clarify?"
        
        pending_action = self.conversation_state['pending_action']
        
        if pending_action == 'book_meeting':
            return self.execute_booking()
        elif pending_action == 'modify_meeting':
            return self.execute_modification()
        elif pending_action == 'cancel_meeting':
            return self.execute_cancellation()
        else:
            return "I'm not sure what action to confirm. Could you please clarify?"
    
    def handle_decline(self, intent_data: Dict[str, Any], user_input: str) -> str:
        """Handle user declinations"""
        self.conversation_state['confirmation_pending'] = False
        self.conversation_state['pending_action'] = None
        
        return "No problem! Is there anything else I can help you with?"
    
    def handle_info_provision(self, intent_data: Dict[str, Any], user_input: str) -> str:
        """Handle when user provides additional information"""
        if self.conversation_state['mode'] == 'booking':
            return self.handle_booking_flow(intent_data, user_input)
        elif self.conversation_state['mode'] == 'modifying':
            return self.handle_modification_flow(intent_data, user_input)
        elif self.conversation_state['mode'] == 'cancelling':
            return self.handle_cancellation_flow(intent_data, user_input)
        else:
            return self.generate_smart_response(intent_data, user_input)
    
    def handle_general_conversation(self, intent_data: Dict[str, Any], user_input: str) -> str:
        """Handle general conversation"""
        return self.generate_smart_response(intent_data, user_input)
    
    def request_missing_info(self, missing_info: List[str], booking_info: Dict) -> str:
        """Request missing information naturally"""
        if len(missing_info) == 3:  # All info missing
            return "I'd love to help you schedule a meeting! Could you tell me who you'd like to meet with and when?"
        elif 'name' in missing_info and 'date' in missing_info:
            return "Great! Who would you like to meet with, and what date works best?"
        elif 'name' in missing_info and 'time' in missing_info:
            return f"Perfect! Who are you meeting with on {booking_info.get('date')}, and what time works best?"
        elif 'date' in missing_info and 'time' in missing_info:
            return f"Excellent! What date and time would work for your meeting with {booking_info.get('name')}?"
        elif 'name' in missing_info:
            return f"Got it! Who are you meeting with on {booking_info.get('date')} at {booking_info.get('time')}?"
        elif 'date' in missing_info:
            return f"Perfect! What date works for your meeting with {booking_info.get('name')}?"
        elif 'time' in missing_info:
            return self.suggest_times_for_date(booking_info.get('date'), booking_info.get('duration', 30))
        else:
            return "I have all the details. Let me check availability!"
    
    def suggest_times_for_date(self, date: str, duration: int = 30) -> str:
        """Suggest available times for a specific date"""
        available_slots = get_free_time_slots(date, duration)
        
        if not available_slots:
            return f"I'm sorry, but {date} appears to be fully booked. Could you suggest an alternative date?"
        
        suggestions = []
        for slot in available_slots[:4]:  # Show top 4 options
            suggestions.append(f"• {slot['start_time']} - {slot['end_time']}")
        
        return f"Here are some available times for {date}:\n" + "\n".join(suggestions) + "\n\nWhich time works best for you?"
    
    def process_booking_request(self, booking_info: Dict) -> str:
        """Process complete booking request"""
        # Check availability
        is_available = check_calendar_availability(
            booking_info['date'],
            booking_info['time'],
            booking_info.get('duration', 30)
        )
        
        if is_available:
            # Set up confirmation
            self.conversation_state['confirmation_pending'] = True
            self.conversation_state['pending_action'] = 'book_meeting'
            
            return f"Perfect! I can book your meeting with {booking_info['name']} on {booking_info['date']} at {booking_info['time']}. Shall I go ahead and book it?"
        else:
            # Suggest alternative times
            return self.suggest_times_for_date(booking_info['date'], booking_info.get('duration', 30))
    
    def execute_booking(self) -> str:
        """Execute the actual booking"""
        booking_info = self.conversation_state['booking_info']
        
        try:
            result = book_appointment(
                name=booking_info['name'],
                date=booking_info['date'],
                time=booking_info['time'],
                duration=booking_info.get('duration', 30)
            )
            
            if result['status'] == 'success':
                self.conversation_state['confirmation_pending'] = False
                self.conversation_state['pending_action'] = None
                self.conversation_state['mode'] = 'idle'
                self.conversation_state['booking_info'] = {}
                
                return f"✅ Excellent! I've booked your meeting with {booking_info['name']} on {booking_info['date']} at {booking_info['time']}. You'll receive a calendar invitation shortly!"
            else:
                return f"I'm sorry, there was an issue booking the meeting: {result['message']}"
                
        except Exception as e:
            logger.error(f"❌ Booking execution failed: {e}")
            return "I'm sorry, there was an error while booking. Please try again."
    
    def validate_time_format(self, time_str: str) -> bool:
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    


    def process_modification_request(self, intent_data: Dict[str, Any], events: List[Dict]) -> str:
        # Enhanced event matching
        user_input = (intent_data.get('extracted_info', {}).get('event_reference') or "").lower().strip()
        matched_event = None
        
        # 1. Handle numbered references (including ordinals)
        ordinal_map = {'first':1, 'second':2, 'third':3, 'fourth':4, 'fifth':5}
        if user_input.split()[0] in ordinal_map:
            idx = ordinal_map[user_input.split()[0]] - 1
            if 0 <= idx < len(events):
                matched_event = events[idx]
        
        # 2. Try exact number reference (e.g., "meeting 2")
        if not matched_event and user_input.replace("meeting", "").strip().isdigit():
            idx = int(user_input.replace("meeting", "").strip()) - 1
            if 0 <= idx < len(events):
                matched_event = events[idx]
        
        # 3. Fuzzy match with lower threshold
        if not matched_event:
            event_titles = [e['summary'].lower() for e in events]
            matches = get_close_matches(user_input, event_titles, n=3, cutoff=0.4)
            if matches:
                matched_event = next((e for e in events if e['summary'].lower() == matches[0]), None)
        
        # 4. Fallback to listing events
        if not matched_event:
            events_list = "Which meeting would you like to modify?\n"
            for i, event in enumerate(events[:5], 1):
                event_time = event['start'].split()[1][:5]  # Extract HH:MM
                events_list += f"{i}. {event['summary']} at {event_time}\n"
            return events_list + "\nPlease specify by number or name."
    
    # Rest of the method remains the same...
        # 5. Save match and lock in that we’re modifying
        self.conversation_state['confirmation_pending'] = True
        self.conversation_state['pending_action'] = 'modify_meeting'
        self.conversation_state['modification_info'] = {'event': matched_event}

        # 6. Extract requested new date/time and stash it
        new_date = intent_data['extracted_info'].get('date')
        new_time = intent_data['extracted_info'].get('time')
        self.conversation_state['booking_info'] = {}
        if new_date:
            self.conversation_state['booking_info']['date'] = new_date
        if new_time:
            self.conversation_state['booking_info']['time'] = new_time

        # 7. Prompt user to confirm
        if new_date or new_time:
            return (
                f"You're asking to modify **{matched_event['summary']}** on {matched_event['start']}. "
                f"Do you want to reschedule it to {new_date or ''} {new_time or ''}?"
            )
        else:
            return (
                f"You want to modify **{matched_event['summary']}** on {matched_event['start']}. "
                "What changes would you like to make?"
            )



    

    def process_cancellation_request(self, intent_data: Dict[str, Any], events: List[Dict]) -> str:
        """Process meeting cancellation request with fuzzy + numbered match"""
        user_input = intent_data.get('extracted_info', {}).get('event_reference') or ""
        user_input = user_input.lower()

        # 1. Try fuzzy match with titles
        event_titles = [event['summary'] for event in events]
        best_matches = get_close_matches(user_input, event_titles, n=1, cutoff=0.6)

        matched_event = None
        if best_matches:
            for event in events:
                if event['summary'] == best_matches[0]:
                    matched_event = event
                    break

        # 2. If not found, try number-based matching (e.g., "3rd", "meeting 2")
        if not matched_event:
            match = re.search(r'(?:meeting\s*)?(\d+)(?:st|nd|rd|th)?', user_input)
            if match:
                index = int(match.group(1)) - 1
                if 0 <= index < len(events):
                    matched_event = events[index]

        if not matched_event:
            return f"I couldn’t find a meeting matching '{user_input}'. Can you clarify the name or number?"

        # Ask for confirmation
        self.conversation_state['confirmation_pending'] = True
        self.conversation_state['pending_action'] = 'cancel_meeting'
        self.conversation_state['modification_info'] = {'event': matched_event}

        return f"You're asking to cancel: **{matched_event['summary']}** on {matched_event['start']}. Should I go ahead?"

    
    

    def execute_modification(self) -> str:
        mod_info = self.conversation_state['modification_info']
        booking_info = self.conversation_state['booking_info']
        
        # Validation checks
        if not mod_info.get('event'):
            self.reset_conversation()
            return "I lost track of which meeting to modify. Please start over."
        
        if not any(k in booking_info for k in ['date', 'time', 'duration']):
            return "Please specify what you want to change (time, date, or duration)."
        
        # Get event details
        event = mod_info['event']
        event_id = event.get('id')
        if not event_id:
            return "This meeting cannot be modified (missing ID)."
        
        # Call modification function
        result = modify_appointment(
            event_id=event_id,
            new_date=booking_info.get('date'),
            new_time=booking_info.get('time'),
            new_duration=booking_info.get('duration'),
            new_name=booking_info.get('name')
        )
        
        # Handle result
        if result.get('status') == 'success':
            # Clear modification state
            self.conversation_state.update({
                'mode': 'idle',
                'confirmation_pending': False,
                'pending_action': None,
                'modification_info': {},
                'booking_info': {}
            })
            return f"✅ Successfully updated meeting!\nNew time: {result['new_start']}"
        else:
            return f"❌ Failed to update meeting: {result.get('message', 'Unknown error')}"

    
    def execute_cancellation(self) -> str:
        """Execute meeting cancellation"""
        event = self.conversation_state['modification_info'].get('event')
        if not event:
            return "I couldn't identify which meeting to cancel."

        try:
            result = cancel_appointment(event['id'])  # Assuming `event['id']` is passed
            if result.get('status') == 'success':
                self.reset_conversation()
                return f"✅ Your meeting '{event['summary']}' on {event['start']} has been canceled."
            else:
                return f"⚠️ I couldn't cancel the meeting: {result.get('message')}"
        except Exception as e:
            logger.error(f"❌ Cancellation failed: {e}")
            return "Something went wrong while trying to cancel the meeting. Please try again."
    
    
    
    def reset_conversation(self):
        """Reset conversation state"""
        self.conversation_state = {
            'mode': 'idle',
            'current_task': None,
            'booking_info': {},
            'modification_info': {},
            'events_context': [],
            'conversation_memory': [],
            'user_preferences': {},
            'last_action': None,
            'context_window': 5,
            'confirmation_pending': False,
            'pending_action': None
        }


# Example usage and testing
if __name__ == "__main__":
    agent = ConversationalCalendarAgent()
    
    # Test conversation flow
    test_messages = [
        "Hi, I need to schedule a meeting with John",
        "How about tomorrow at 2 PM?",
        "Yes, book it",
        "What meetings do I have today?",
        "Can you move my meeting with John to 3 PM?",
        "Yes, confirm the change"
    ]
    
    print("=== Testing Enhanced Calendar Agent ===")
    for message in test_messages:
        print(f"\nUser: {message}")
        response = agent.process_message(message)
        print(f"Agent: {response}")
        print("-" * 50)






