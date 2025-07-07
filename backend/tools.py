
# # tools.py
# from datetime import datetime, timedelta
# import json
# import os
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from loguru import logger
# import logging

# logging.basicConfig(filename="debug.log", level=logging.INFO)
# logger.add("debug.log", level="DEBUG", rotation="1 MB")

# # Load credentials
# SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "service_account.json")
# SCOPES = ['https://www.googleapis.com/auth/calendar']
# CALENDAR_ID = "72242f9068b58274ff0a4ccc0764ec635d389192f507d39ffc74edf81719bb03@group.calendar.google.com"  # replace with actual calendar ID

# # Initialize Google Calendar service
# try:
#     creds = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#     service = build('calendar', 'v3', credentials=creds)
#     logger.info("✅ Google Calendar service initialized")
# except Exception as e:
#     logger.error(f"❌ Failed to initialize Google Calendar service: {e}")
#     service = None

# def check_calendar_availability(date: str, start_time: str, duration: int = 30):
#     """Check if a specific time slot is available"""
#     logger.info(f"🔍 Checking availability for {date} at {start_time} for {duration} minutes")
    
#     if service is None:
#         logger.error("❌ Google Calendar service not initialized")
#         return False
    
#     try:
#         # Parse the date and time
#         start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
#         end_datetime = start_datetime + timedelta(minutes=duration)
        
#         # Query for existing events in the time range
#         time_min = start_datetime.isoformat() + 'Z'
#         time_max = end_datetime.isoformat() + 'Z'
        
#         events_result = service.events().list(
#             calendarId=CALENDAR_ID,
#             timeMin=time_min,
#             timeMax=time_max,
#             singleEvents=True,
#             orderBy='startTime'
#         ).execute()
        
#         events = events_result.get('items', [])
        
#         # Check for conflicts
#         for event in events:
#             event_start = event.get('start', {})
#             event_end = event.get('end', {})
            
#             if event_start.get('dateTime') and event_end.get('dateTime'):
#                 # There's a conflict
#                 logger.info(f"❌ Time slot conflicts with existing event: {event.get('summary', 'Unnamed event')}")
#                 return False
        
#         logger.info(f"✅ Time slot is available")
#         return True
        
#     except Exception as e:
#         logger.error(f"❌ Error checking availability: {e}")
#         return False

# def get_free_time_slots(date: str, duration: int = 30, start_hour: int = 9, end_hour: int = 17):
#     """Get all available time slots for a given date"""
#     logger.info(f"🔍 Finding free time slots for {date}, duration: {duration} minutes")
    
#     if service is None:
#         logger.error("❌ Google Calendar service not initialized")
#         return []
    
#     try:
#         # Parse the date
#         target_date = datetime.strptime(date, "%Y-%m-%d").date()
        
#         # Create start and end times for the day
#         day_start = datetime.combine(target_date, datetime.min.time().replace(hour=start_hour))
#         day_end = datetime.combine(target_date, datetime.min.time().replace(hour=end_hour))
        
#         # Query for all events on that day
#         time_min = day_start.isoformat() + 'Z'
#         time_max = day_end.isoformat() + 'Z'
        
#         events_result = service.events().list(
#             calendarId=CALENDAR_ID,
#             timeMin=time_min,
#             timeMax=time_max,
#             singleEvents=True,
#             orderBy='startTime'
#         ).execute()
        
#         events = events_result.get('items', [])
        
#         # Extract busy periods
#         busy_periods = []
#         for event in events:
#             event_start = event.get('start', {})
#             event_end = event.get('end', {})
            
#             if event_start.get('dateTime') and event_end.get('dateTime'):
#                 start_dt = datetime.fromisoformat(event_start['dateTime'].replace('Z', '+00:00'))
#                 end_dt = datetime.fromisoformat(event_end['dateTime'].replace('Z', '+00:00'))
                
#                 # Convert to local time if needed
#                 start_dt = start_dt.replace(tzinfo=None)
#                 end_dt = end_dt.replace(tzinfo=None)
                
#                 busy_periods.append((start_dt, end_dt))
        
#         # Sort busy periods by start time
#         busy_periods.sort(key=lambda x: x[0])
        
#         # Find free slots
#         free_slots = []
#         current_time = day_start
        
#         for busy_start, busy_end in busy_periods:
#             # Check if there's a free slot before this busy period
#             if current_time + timedelta(minutes=duration) <= busy_start:
#                 # Find all possible slots in this free period
#                 while current_time + timedelta(minutes=duration) <= busy_start:
#                     slot_end = current_time + timedelta(minutes=duration)
#                     free_slots.append({
#                         'start_time': current_time.strftime('%H:%M'),
#                         'end_time': slot_end.strftime('%H:%M'),
#                         'start_datetime': current_time,
#                         'end_datetime': slot_end
#                     })
#                     current_time += timedelta(minutes=30)  # 30-minute intervals
            
#             # Move current time to after this busy period
#             current_time = max(current_time, busy_end)
        
#         # Check for free slots after the last busy period
#         while current_time + timedelta(minutes=duration) <= day_end:
#             slot_end = current_time + timedelta(minutes=duration)
#             free_slots.append({
#                 'start_time': current_time.strftime('%H:%M'),
#                 'end_time': slot_end.strftime('%H:%M'),
#                 'start_datetime': current_time,
#                 'end_datetime': slot_end
#             })
#             current_time += timedelta(minutes=30)
        
#         logger.info(f"✅ Found {len(free_slots)} free time slots")
#         return free_slots
        
#     except Exception as e:
#         logger.error(f"❌ Error finding free time slots: {e}")
#         return []

# def book_appointment(name: str, date: str, time: str, duration: int = 30):
#     """Create an event on Google Calendar"""
#     logger.info(f"📨 Attempting to book meeting: {name} on {date} at {time} for {duration} mins")
    
#     if service is None:
#         logger.error("❌ Google Calendar service not initialized")
#         return {
#             "status": "error",
#             "message": "❌ Google Calendar service not available"
#         }
    
#     # First check if the time slot is available
#     if not check_calendar_availability(date, time, duration):
#         logger.warning(f"⚠️ Time slot not available: {date} at {time}")
#         return {
#             "status": "error",
#             "message": "❌ This time slot is not available. Please choose a different time."
#         }
    
#     try:
#         start_str = f"{date} {time}"
#         start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
#         end_dt = start_dt + timedelta(minutes=duration)

#         logger.debug(f"📅 Parsed times - Start: {start_dt.isoformat()}, End: {end_dt.isoformat()}")

#         event = {
#             'summary': f"Meeting with {name}",
#             'description': f"Meeting scheduled via AI Calendar Assistant",
#             'start': {
#                 'dateTime': start_dt.isoformat(),
#                 'timeZone': 'Asia/Kolkata',
#             },
#             'end': {
#                 'dateTime': end_dt.isoformat(),
#                 'timeZone': 'Asia/Kolkata',
#             },
#             'attendees': [
#                 # You can add attendee emails here if needed
#                 # {'email': 'attendee@example.com'}
#             ],
#             'reminders': {
#                 'useDefault': False,
#                 'overrides': [
#                     {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
#                     {'method': 'popup', 'minutes': 15},       # 15 minutes before
#                 ],
#             },
#         }

#         created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
#         logger.info(f"✅ Event created successfully: {created_event.get('id')}")

#         return {
#             "status": "success",
#             "message": f"✅ Meeting with {name} successfully booked for {date} at {time} ({duration} minutes)",
#             "event_id": created_event.get("id"),
#             "event_link": created_event.get("htmlLink")
#         }

#     except Exception as e:
#         logger.error(f"❌ Google Calendar Error: {e}")
#         return {
#             "status": "error",
#             "message": f"❌ Failed to create event: {str(e)}"
#         }

# def get_upcoming_events(days_ahead: int = 7):
#     """Get upcoming events for the next N days"""
#     logger.info(f"📅 Getting upcoming events for next {days_ahead} days")
    
#     if service is None:
#         logger.error("❌ Google Calendar service not initialized")
#         return []
    
#     try:
#         # Calculate time range
#         now = datetime.now()
#         time_min = now.isoformat() + 'Z'
#         time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
        
#         events_result = service.events().list(
#             calendarId=CALENDAR_ID,
#             timeMin=time_min,
#             timeMax=time_max,
#             maxResults=50,
#             singleEvents=True,
#             orderBy='startTime'
#         ).execute()
        
#         events = events_result.get('items', [])
        
#         formatted_events = []
#         for event in events:
#             start = event.get('start', {})
#             end = event.get('end', {})
            
#             if start.get('dateTime'):
#                 start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
#                 end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                
#                 formatted_events.append({
#                     'summary': event.get('summary', 'No Title'),
#                     'start': start_dt.strftime('%Y-%m-%d %H:%M'),
#                     'end': end_dt.strftime('%Y-%m-%d %H:%M'),
#                     'id': event.get('id')
#                 })
        
#         logger.info(f"✅ Found {len(formatted_events)} upcoming events")
#         return formatted_events
        
#     except Exception as e:
#         logger.error(f"❌ Error getting upcoming events: {e}")
#         return []

# if __name__ == "__main__":
#     # Test the functions
#     print("Testing availability check...")
#     available = check_calendar_availability("2025-07-07", "15:30", 30)
#     print(f"Available: {available}")
    
#     print("\nTesting free time slots...")
#     slots = get_free_time_slots("2025-07-07", 30)
#     for slot in slots[:5]:  # Show first 5 slots
#         print(f"Free slot: {slot['start_time']} - {slot['end_time']}")
    
#     print("\nTesting booking...")
#     result = book_appointment("Test User", "2025-07-07", "15:30", 30)
#     print(result)









# #tools.py
# from datetime import datetime, timedelta
# import json
# import os
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from loguru import logger
# import logging
# from typing import Dict, List, Optional, Union

# logging.basicConfig(filename="debug.log", level=logging.INFO)
# logger.add("debug.log", level="DEBUG", rotation="1 MB")

# # Load credentials
# SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "service_account.json")
# SCOPES = ['https://www.googleapis.com/auth/calendar']
# CALENDAR_ID = "72242f9068b58274ff0a4ccc0764ec635d389192f507d39ffc74edf81719bb03@group.calendar.google.com"  # replace with actual calendar ID

# # Initialize Google Calendar service
# try:
#     creds = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#     service = build('calendar', 'v3', credentials=creds)
#     logger.info("✅ Google Calendar service initialized")
# except Exception as e:
#     logger.error(f"❌ Failed to initialize Google Calendar service: {e}")
#     service = None

# def check_calendar_availability(date: str, start_time: str, duration: int = 30) -> bool:
#     """Check if a specific time slot is available"""
#     logger.info(f"🔍 Checking availability for {date} at {start_time} for {duration} minutes")
    
#     if service is None:
#         logger.error("❌ Google Calendar service not initialized")
#         return False
    
#     try:
#         start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
#         end_datetime = start_datetime + timedelta(minutes=duration)
        
#         events_result = service.events().list(
#             calendarId=CALENDAR_ID,
#             timeMin=start_datetime.isoformat() + 'Z',
#             timeMax=end_datetime.isoformat() + 'Z',
#             singleEvents=True,
#             orderBy='startTime'
#         ).execute()
        
#         return len(events_result.get('items', [])) == 0
        
#     except HttpError as e:
#         logger.error(f"❌ Google API Error checking availability: {e}")
#         return False
#     except Exception as e:
#         logger.error(f"❌ Error checking availability: {e}")
#         return False

# def get_free_time_slots(date: str, duration: int = 30, 
#                        start_hour: int = 9, end_hour: int = 17,
#                        interval: int = 30) -> List[Dict[str, Union[str, datetime]]]:
#     """Get all available time slots for a given date with improved logic"""
#     logger.info(f"🔍 Finding free time slots for {date}, duration: {duration} minutes")
    
#     if service is None:
#         logger.error("❌ Google Calendar service not initialized")
#         return []
    
#     try:
#         target_date = datetime.strptime(date, "%Y-%m-%d").date()
#         day_start = datetime.combine(target_date, datetime.min.time().replace(hour=start_hour))
#         day_end = datetime.combine(target_date, datetime.min.time().replace(hour=end_hour))
        
#         # Get all events for the day
#         events_result = service.events().list(
#             calendarId=CALENDAR_ID,
#             timeMin=day_start.isoformat() + 'Z',
#             timeMax=day_end.isoformat() + 'Z',
#             singleEvents=True,
#             orderBy='startTime'
#         ).execute()
        
#         events = events_result.get('items', [])
        
#         # Convert events to time blocks
#         busy_blocks = []
#         for event in events:
#             start = event.get('start', {}).get('dateTime')
#             end = event.get('end', {}).get('dateTime')
#             if start and end:
#                 start_dt = datetime.fromisoformat(start.replace('Z', '+00:00')).replace(tzinfo=None)
#                 end_dt = datetime.fromisoformat(end.replace('Z', '+00:00')).replace(tzinfo=None)
#                 busy_blocks.append((start_dt, end_dt))
        
#         # Sort by start time
#         busy_blocks.sort(key=lambda x: x[0])
        
#         free_slots = []
#         current_time = day_start
        
#         for busy_start, busy_end in busy_blocks:
#             # Add free slots before this busy period
#             while current_time + timedelta(minutes=duration) <= busy_start:
#                 free_slots.append({
#                     'start_time': current_time.strftime('%H:%M'),
#                     'end_time': (current_time + timedelta(minutes=duration)).strftime('%H:%M'),
#                     'start_datetime': current_time,
#                     'end_datetime': current_time + timedelta(minutes=duration)
#                 })
#                 current_time += timedelta(minutes=interval)
            
#             # Move current_time to after busy period
#             current_time = max(current_time, busy_end)
        
#         # Add remaining free slots
#         while current_time + timedelta(minutes=duration) <= day_end:
#             free_slots.append({
#                 'start_time': current_time.strftime('%H:%M'),
#                 'end_time': (current_time + timedelta(minutes=duration)).strftime('%H:%M'),
#                 'start_datetime': current_time,
#                 'end_datetime': current_time + timedelta(minutes=duration)
#             })
#             current_time += timedelta(minutes=interval)
        
#         logger.info(f"✅ Found {len(free_slots)} free time slots")
#         return free_slots
        
#     except HttpError as e:
#         logger.error(f"❌ Google API Error finding free slots: {e}")
#         return []
#     except Exception as e:
#         logger.error(f"❌ Error finding free time slots: {e}")
#         return []

# def book_appointment(name: str, date: str, time: str, 
#                     duration: int = 30, description: str = "") -> Dict[str, str]:
#     """Create an event on Google Calendar with enhanced details"""
#     logger.info(f"📨 Booking meeting: {name} on {date} at {time} for {duration} mins")
    
#     if service is None:
#         return error_response("Google Calendar service not available")
    
#     try:
#         start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
#         end_dt = start_dt + timedelta(minutes=duration)
        
#         event = {
#             'summary': f"Meeting with {name}",
#             'description': description or f"Meeting scheduled via AI Calendar Assistant",
#             'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
#             'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
#             'attendees': [],
#             'reminders': {
#                 'useDefault': False,
#                 'overrides': [
#                     {'method': 'email', 'minutes': 24 * 60},
#                     {'method': 'popup', 'minutes': 15},
#                 ],
#             },
#             'guestsCanInviteOthers': False,
#             'guestsCanModify': False,
#             'guestsCanSeeOtherGuests': False,
#             'transparency': 'opaque'  # Show as busy
#         }

#         created_event = service.events().insert(
#             calendarId=CALENDAR_ID,
#             body=event,
#             sendUpdates='all'  # Notify attendees if any
#         ).execute()
        
#         logger.info(f"✅ Event created: {created_event.get('id')}")
#         return {
#             "status": "success",
#             "message": "Meeting successfully booked",
#             "event_id": created_event.get("id"),
#             "event_link": created_event.get("htmlLink"),
#             "start_time": start_dt.isoformat(),
#             "end_time": end_dt.isoformat()
#         }

#     except HttpError as e:
#         logger.error(f"❌ Google API Error creating event: {e}")
#         return error_response(f"Google API error: {e}")
#     except Exception as e:
#         logger.error(f"❌ Error creating event: {e}")
#         return error_response(str(e))

# def cancel_appointment(event_id: str, notify_attendees: bool = True) -> Dict[str, str]:
#     """Cancel an existing calendar event"""
#     logger.info(f"❌ Attempting to cancel event: {event_id}")
    
#     if service is None:
#         return error_response("Google Calendar service not available")
    
#     try:
#         # First verify the event exists
#         event = service.events().get(
#             calendarId=CALENDAR_ID,
#             eventId=event_id
#         ).execute()
        
#         if not event:
#             return error_response("Event not found")
        
#         # Proceed with cancellation
#         service.events().delete(
#             calendarId=CALENDAR_ID,
#             eventId=event_id,
#             sendUpdates='all' if notify_attendees else 'none'
#         ).execute()
        
#         logger.info(f"✅ Successfully canceled event: {event_id}")
#         return {
#             "status": "success",
#             "message": "Event successfully canceled",
#             "canceled_event": event.get('summary'),
#             "original_start": event.get('start', {}).get('dateTime')
#         }
        
#     except HttpError as e:
#         logger.error(f"❌ Google API Error canceling event: {e}")
#         return error_response(f"Google API error: {e}")
#     except Exception as e:
#         logger.error(f"❌ Error canceling event: {e}")
#         return error_response(str(e))

# def get_upcoming_events(days_ahead: int = 7, max_results: int = 50) -> List[Dict[str, str]]:
#     """Get upcoming events with improved formatting"""
#     logger.info(f"📅 Getting {max_results} events for next {days_ahead} days")
    
#     if service is None:
#         logger.error("❌ Google Calendar service not initialized")
#         return []
    
#     try:
#         now = datetime.now()
#         time_min = now.isoformat() + 'Z'
#         time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
        
#         events_result = service.events().list(
#             calendarId=CALENDAR_ID,
#             timeMin=time_min,
#             timeMax=time_max,
#             maxResults=max_results,
#             singleEvents=True,
#             orderBy='startTime'
#         ).execute()
        
#         events = []
#         for event in events_result.get('items', []):
#             start = event.get('start', {})
#             end = event.get('end', {})
            
#             if start.get('dateTime'):
#                 start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
#                 end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                
#                 events.append({
#                     'id': event.get('id'),
#                     'summary': event.get('summary', 'Untitled Event'),
#                     'start': start_dt.strftime('%Y-%m-%d %H:%M'),
#                     'end': end_dt.strftime('%Y-%m-%d %H:%M'),
#                     'organizer': event.get('organizer', {}).get('email'),
#                     'status': event.get('status'),
#                     'htmlLink': event.get('htmlLink')
#                 })
        
#         logger.info(f"✅ Found {len(events)} upcoming events")
#         return events
        
#     except HttpError as e:
#         logger.error(f"❌ Google API Error getting events: {e}")
#         return []
#     except Exception as e:
#         logger.error(f"❌ Error getting events: {e}")
#         return []

# def get_event_details(event_id: str) -> Dict[str, str]:
#     """Get complete details for a specific event"""
#     logger.info(f"🔍 Getting details for event: {event_id}")
    
#     if service is None:
#         return error_response("Google Calendar service not available")
    
#     try:
#         event = service.events().get(
#             calendarId=CALENDAR_ID,
#             eventId=event_id
#         ).execute()
        
#         if not event:
#             return error_response("Event not found")
        
#         start = event.get('start', {})
#         end = event.get('end', {})
        
#         return {
#             "status": "success",
#             "id": event.get('id'),
#             "summary": event.get('summary'),
#             "description": event.get('description'),
#             "start": start.get('dateTime') or start.get('date'),
#             "end": end.get('dateTime') or end.get('date'),
#             "location": event.get('location'),
#             "attendees": [a.get('email') for a in event.get('attendees', [])],
#             "organizer": event.get('organizer', {}).get('email'),
#             "htmlLink": event.get('htmlLink')
#         }
        
#     except HttpError as e:
#         logger.error(f"❌ Google API Error getting event: {e}")
#         return error_response(f"Google API error: {e}")
#     except Exception as e:
#         logger.error(f"❌ Error getting event: {e}")
#         return error_response(str(e))

# def error_response(message: str) -> Dict[str, str]:
#     """Standard error response format"""
#     return {
#         "status": "error",
#         "message": f"❌ {message}"
#     }

# if __name__ == "__main__":
#     # Test the functions
#     print("Testing upcoming events...")
#     events = get_upcoming_events(days_ahead=7)
#     for event in events[:3]:
#         print(f"{event['start']} - {event['summary']}")
    
#     if events:
#         print("\nTesting event details...")
#         details = get_event_details(events[0]['id'])
#         print(details)
        
#         print("\nTesting cancellation...")
#         cancel_result = cancel_appointment(events[0]['id'])
#         print(cancel_result)












#tools.py
from datetime import datetime, timedelta
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from loguru import logger
import logging
from typing import Dict, List, Optional, Union
import re
from dateutil import parser
import pytz
import traceback


logging.basicConfig(filename="debug.log", level=logging.INFO)
logger.add("debug.log", level="DEBUG", rotation="1 MB")

# Load credentials
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "service_account.json")
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = "72242f9068b58274ff0a4ccc0764ec635d389192f507d39ffc74edf81719bb03@group.calendar.google.com"  # replace with actual calendar ID

# Initialize Google Calendar service
try:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    logger.info("✅ Google Calendar service initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize Google Calendar service: {e}")
    service = None

def check_calendar_availability(date: str, start_time: str, duration: int = 30) -> bool:
    """Check if a specific time slot is available"""
    logger.info(f"🔍 Checking availability for {date} at {start_time} for {duration} minutes")
    
    if service is None:
        logger.error("❌ Google Calendar service not initialized")
        return False
    
    try:
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_datetime.isoformat() + 'Z',
            timeMax=end_datetime.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return len(events_result.get('items', [])) == 0
        
    except HttpError as e:
        logger.error(f"❌ Google API Error checking availability: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking availability: {e}")
        return False

def get_free_time_slots(date: str, duration: int = 30, 
                       start_hour: int = 9, end_hour: int = 17,
                       interval: int = 30) -> List[Dict[str, Union[str, datetime]]]:
    """Get all available time slots for a given date with improved logic"""
    logger.info(f"🔍 Finding free time slots for {date}, duration: {duration} minutes")
    
    if service is None:
        logger.error("❌ Google Calendar service not initialized")
        return []
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        day_start = datetime.combine(target_date, datetime.min.time().replace(hour=start_hour))
        day_end = datetime.combine(target_date, datetime.min.time().replace(hour=end_hour))
        
        # Get all events for the day
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=day_start.isoformat() + 'Z',
            timeMax=day_end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Convert events to time blocks
        busy_blocks = []
        for event in events:
            start = event.get('start', {}).get('dateTime')
            end = event.get('end', {}).get('dateTime')
            if start and end:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00')).replace(tzinfo=None)
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00')).replace(tzinfo=None)
                busy_blocks.append((start_dt, end_dt))
        
        # Sort by start time
        busy_blocks.sort(key=lambda x: x[0])
        
        free_slots = []
        current_time = day_start
        
        for busy_start, busy_end in busy_blocks:
            # Add free slots before this busy period
            while current_time + timedelta(minutes=duration) <= busy_start:
                free_slots.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': (current_time + timedelta(minutes=duration)).strftime('%H:%M'),
                    'start_datetime': current_time,
                    'end_datetime': current_time + timedelta(minutes=duration)
                })
                current_time += timedelta(minutes=interval)
            
            # Move current_time to after busy period
            current_time = max(current_time, busy_end)
        
        # Add remaining free slots
        while current_time + timedelta(minutes=duration) <= day_end:
            free_slots.append({
                'start_time': current_time.strftime('%H:%M'),
                'end_time': (current_time + timedelta(minutes=duration)).strftime('%H:%M'),
                'start_datetime': current_time,
                'end_datetime': current_time + timedelta(minutes=duration)
            })
            current_time += timedelta(minutes=interval)
        
        logger.info(f"✅ Found {len(free_slots)} free time slots")
        return free_slots
        
    except HttpError as e:
        logger.error(f"❌ Google API Error finding free slots: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Error finding free time slots: {e}")
        return []

def book_appointment(name: str, date: str, time: str, 
                    duration: int = 30, description: str = "",
                    location: str = "", attendee_emails: List[str] = None) -> Dict[str, str]:
    """Create an event on Google Calendar with enhanced details"""
    logger.info(f"📨 Booking meeting: {name} on {date} at {time} for {duration} mins")
    
    if service is None:
        return error_response("Google Calendar service not available")
    
    try:
        start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=duration)
        
        # Build attendees list
        attendees = []
        if attendee_emails:
            attendees = [{'email': email} for email in attendee_emails]
        
        event = {
            'summary': f"Meeting with {name}",
            'description': description or f"Meeting scheduled via AI Calendar Assistant\nParticipant: {name}",
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'attendees': attendees,
            'location': location,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 15},
                ],
            },
            'guestsCanInviteOthers': False,
            'guestsCanModify': False,
            'guestsCanSeeOtherGuests': False,
            'transparency': 'opaque'  # Show as busy
        }

        created_event = service.events().insert(
            calendarId=CALENDAR_ID,
            body=event,
            sendUpdates='all' if attendees else 'none'
        ).execute()
        
        logger.info(f"✅ Event created: {created_event.get('id')}")
        return {
            "status": "success",
            "message": "Meeting successfully booked",
            "event_id": created_event.get("id"),
            "event_link": created_event.get("htmlLink"),
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "summary": event['summary']
        }

    except HttpError as e:
        logger.error(f"❌ Google API Error creating event: {e}")
        return error_response(f"Google API error: {e}")
    except Exception as e:
        logger.error(f"❌ Error creating event: {e}")
        return error_response(str(e))





def modify_appointment(
    event_id: str = None,
    new_date: str = None,
    new_time: str = None,
    new_duration: int = None,
    **kwargs
) -> Dict[str, str]:
    # Validate inputs
    if not event_id:
        return error_response("Event ID is required")
    
    # Time validation
    if new_time:
        try:
            datetime.strptime(new_time, "%H:%M")
        except ValueError:
            return error_response("Invalid time format. Use HH:MM")
    
    # Date validation
    if new_date:
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
        except ValueError:
            return error_response("Invalid date format. Use YYYY-MM-DD")
    
    # Get the existing event
    try:
        target_event = service.events().get(
            calendarId=CALENDAR_ID,
            eventId=event_id
        ).execute()
    except HttpError as e:
        return error_response(f"Failed to fetch event: {e}")
    
    # Prepare updated event
    updated_event = target_event.copy()
    changes = []
    
    # Handle time/date changes
    if new_date or new_time:
        original_start = target_event['start'].get('dateTime')
        if not original_start:
            return error_response("Cannot modify all-day events")
            
        # Parse original datetime (with timezone handling)
        original_dt = datetime.fromisoformat(original_start.replace('Z', '+00:00'))
        new_dt = original_dt
        
        # Apply date change if provided
        if new_date:
            new_date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
            new_dt = new_dt.replace(year=new_date_obj.year, month=new_date_obj.month, day=new_date_obj.day)
            changes.append(f"date to {new_date}")
        
        # Apply time change if provided
        if new_time:
            new_time_obj = datetime.strptime(new_time, "%H:%M").time()
            new_dt = new_dt.replace(hour=new_time_obj.hour, minute=new_time_obj.minute)
            changes.append(f"time to {new_time}")
        
        # Calculate new end time
        duration = new_duration or int((datetime.fromisoformat(
            target_event['end']['dateTime'].replace('Z', '+00:00')
        ) - original_dt).total_seconds() / 60)
        
        new_end = new_dt + timedelta(minutes=duration)
        
        # Update event times
        updated_event['start']['dateTime'] = new_dt.isoformat()
        updated_event['end']['dateTime'] = new_end.isoformat()
    
    # Apply other changes (duration, name, etc.)
    # ... (rest of your existing modification logic)
    
    try:
        # Execute the update
        result = service.events().update(
            calendarId=CALENDAR_ID,
            eventId=event_id,
            body=updated_event,
            sendUpdates='all'
        ).execute()
        
        return {
            "status": "success",
            "message": f"Updated: {', '.join(changes)}",
            "event_id": event_id,
            "new_start": updated_event['start']['dateTime'],
            "new_end": updated_event['end']['dateTime']
        }
    except HttpError as e:
        return error_response(f"Google API error: {e}")
 

def find_event_by_reference(reference: str) -> Optional[Dict]:
    """Find an event by various references (name, time, partial match)"""
    logger.info(f"🔍 Searching for event by reference: {reference}")
    
    if service is None:
        return None
    
    try:
        # Get events from past 1 day to future 30 days to catch recently created events
        now = datetime.now()
        time_min = (now - timedelta(days=1)).isoformat() + 'Z'  # Include past day
        time_max = (now + timedelta(days=30)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=100,  # Increased to catch more events
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        reference_lower = reference.lower()
        
        # Try different matching strategies
        
        # 1. Check if reference is a number (position in upcoming events)
        if reference.isdigit():
            index = int(reference) - 1  # Convert to 0-based index
            if 0 <= index < len(events):
                return events[index]
        
        # 2. Exact summary match
        for event in events:
            summary = event.get('summary', '').lower()
            if reference_lower in summary:
                return event
        
        # 3. Check for name in summary (e.g., "Meeting with John")
        for event in events:
            summary = event.get('summary', '').lower()
            if reference_lower in summary or any(word in summary for word in reference_lower.split()):
                return event
        
        # 4. Check description
        for event in events:
            description = event.get('description', '').lower()
            if reference_lower in description:
                return event
        
        # 5. Check for date/time references
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}:\d{2}',        # HH:MM
            r'today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, reference_lower):
                for event in events:
                    start_time = event.get('start', {}).get('dateTime', '')
                    if re.search(pattern, start_time.lower()):
                        return event
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error finding event by reference: {e}")
        return None

def cancel_appointment(event_id: str = None, event_reference: str = None, 
                      notify_attendees: bool = True) -> Dict[str, str]:
    """Cancel an existing calendar event with flexible identification"""
    logger.info(f"❌ Attempting to cancel event - ID: {event_id}, Reference: {event_reference}")
    
    if service is None:
        return error_response("Google Calendar service not available")
    
    try:
        # Find the event to cancel
        target_event = None
        
        if event_id:
            # Direct event ID lookup
            try:
                target_event = service.events().get(
                    calendarId=CALENDAR_ID,
                    eventId=event_id
                ).execute()
            except HttpError as e:
                if e.resp.status == 404:
                    return error_response("Event not found")
                raise
        elif event_reference:
            # Search for event by reference
            target_event = find_event_by_reference(event_reference)
            if not target_event:
                return error_response(f"Could not find event matching: {event_reference}")
        else:
            return error_response("Either event_id or event_reference must be provided")
        
        # Store event details for response
        event_summary = target_event.get('summary', 'Untitled Event')
        event_start = target_event.get('start', {}).get('dateTime', '')
        
        # Cancel the event
        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=target_event['id'],
            sendUpdates='all' if notify_attendees else 'none'
        ).execute()
        
        logger.info(f"✅ Successfully canceled event: {target_event['id']}")
        return {
            "status": "success",
            "message": "Event successfully canceled",
            "canceled_event": event_summary,
            "original_start": event_start,
            "event_id": target_event['id']
        }
        
    except HttpError as e:
        logger.error(f"❌ Google API Error canceling event: {e}")
        return error_response(f"Google API error: {e}")
    except Exception as e:
        logger.error(f"❌ Error canceling event: {e}")
        return error_response(str(e))

def get_upcoming_events(days_ahead: int = 7, max_results: int = 50) -> List[Dict[str, str]]:
    """Get upcoming events with improved formatting"""
    logger.info(f"📅 Getting {max_results} events for next {days_ahead} days")
    
    if service is None:
        logger.error("❌ Google Calendar service not initialized")
        return []
    
    try:
        now = datetime.now()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = []
        for event in events_result.get('items', []):
            start = event.get('start', {})
            end = event.get('end', {})
            
            if start.get('dateTime'):
                start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                
                # Calculate duration
                duration = int((end_dt - start_dt).total_seconds() / 60)
                
                events.append({
                    'id': event.get('id'),
                    'summary': event.get('summary', 'Untitled Event'),
                    'start': start_dt.strftime('%Y-%m-%d %H:%M'),
                    'end': end_dt.strftime('%Y-%m-%d %H:%M'),
                    'duration': duration,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'organizer': event.get('organizer', {}).get('email'),
                    'status': event.get('status'),
                    'htmlLink': event.get('htmlLink'),
                    'attendees': [a.get('email') for a in event.get('attendees', [])]
                })
        
        logger.info(f"✅ Found {len(events)} upcoming events")
        return events
        
    except HttpError as e:
        logger.error(f"❌ Google API Error getting events: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Error getting events: {e}")
        return []

def get_event_details(event_id: str) -> Dict[str, str]:
    """Get complete details for a specific event"""
    logger.info(f"🔍 Getting details for event: {event_id}")
    
    if service is None:
        return error_response("Google Calendar service not available")
    
    try:
        event = service.events().get(
            calendarId=CALENDAR_ID,
            eventId=event_id
        ).execute()
        
        if not event:
            return error_response("Event not found")
        
        start = event.get('start', {})
        end = event.get('end', {})
        
        # Calculate duration if both start and end times exist
        duration = None
        if start.get('dateTime') and end.get('dateTime'):
            start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
            duration = int((end_dt - start_dt).total_seconds() / 60)
        
        return {
            "status": "success",
            "id": event.get('id'),
            "summary": event.get('summary'),
            "description": event.get('description'),
            "start": start.get('dateTime') or start.get('date'),
            "end": end.get('dateTime') or end.get('date'),
            "duration": duration,
            "location": event.get('location'),
            "attendees": [a.get('email') for a in event.get('attendees', [])],
            "organizer": event.get('organizer', {}).get('email'),
            "htmlLink": event.get('htmlLink'),
            "status": event.get('status')
        }
        
    except HttpError as e:
        logger.error(f"❌ Google API Error getting event: {e}")
        return error_response(f"Google API error: {e}")
    except Exception as e:
        logger.error(f"❌ Error getting event: {e}")
        return error_response(str(e))

def search_events(query: str, days_ahead: int = 30, max_results: int = 20) -> List[Dict[str, str]]:
    """Search for events matching a query"""
    logger.info(f"🔍 Searching events for: {query}")
    
    if service is None:
        logger.error("❌ Google Calendar service not initialized")
        return []
    
    try:
        now = datetime.now()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime',
            q=query  # Google Calendar API search query
        ).execute()
        
        events = []
        for event in events_result.get('items', []):
            start = event.get('start', {})
            end = event.get('end', {})
            
            if start.get('dateTime'):
                start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                
                events.append({
                    'id': event.get('id'),
                    'summary': event.get('summary', 'Untitled Event'),
                    'start': start_dt.strftime('%Y-%m-%d %H:%M'),
                    'end': end_dt.strftime('%Y-%m-%d %H:%M'),
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'status': event.get('status'),
                    'htmlLink': event.get('htmlLink')
                })
        
        logger.info(f"✅ Found {len(events)} events matching query")
        return events
        
    except HttpError as e:
        logger.error(f"❌ Google API Error searching events: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Error searching events: {e}")
        return []

def get_events_for_date(date: str) -> List[Dict[str, str]]:
    """Get all events for a specific date"""
    logger.info(f"📅 Getting events for date: {date}")
    
    if service is None:
        logger.error("❌ Google Calendar service not initialized")
        return []
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = datetime.combine(target_date, datetime.max.time())
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=day_start.isoformat() + 'Z',
            timeMax=day_end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = []
        for event in events_result.get('items', []):
            start = event.get('start', {})
            end = event.get('end', {})
            
            if start.get('dateTime'):
                start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                
                events.append({
                    'id': event.get('id'),
                    'summary': event.get('summary', 'Untitled Event'),
                    'start': start_dt.strftime('%H:%M'),
                    'end': end_dt.strftime('%H:%M'),
                    'full_start': start_dt.strftime('%Y-%m-%d %H:%M'),
                    'full_end': end_dt.strftime('%Y-%m-%d %H:%M'),
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'status': event.get('status')
                })
        
        logger.info(f"✅ Found {len(events)} events for {date}")
        return events
        
    except Exception as e:
        logger.error(f"❌ Error getting events for date: {e}")
        return []

def error_response(message: str) -> Dict[str, str]:
    """Standard error response format"""
    return {
        "status": "error",
        "message": f"❌ {message}"
    }

if __name__ == "__main__":
    # Test the enhanced functions
    print("Testing enhanced calendar tools...")
    
    # Test getting upcoming events
    print("\n=== Testing upcoming events ===")
    events = get_upcoming_events(days_ahead=7)
    for event in events[:3]:
        print(f"{event['start']} - {event['summary']} (ID: {event['id']})")
    
    if events:
        # Test event details
        print(f"\n=== Testing event details ===")
        details = get_event_details(events[0]['id'])
        print(f"Event: {details.get('summary')}")
        print(f"Start: {details.get('start')}")
        print(f"Duration: {details.get('duration')} minutes")
        
        # Test finding event by reference
        print(f"\n=== Testing event search by reference ===")
        found_event = find_event_by_reference("1")  # Find first event
        if found_event:
            print(f"Found event: {found_event.get('summary')}")
        
        # Test modification (uncomment to test)
        # print(f"\n=== Testing event modification ===")
        # modify_result = modify_appointment(
        #     event_id=events[0]['id'],
        #     new_time="15:30"
        # )
        # print(f"Modification result: {modify_result}")
        
        # Test cancellation (uncomment to test)
        # print(f"\n=== Testing event cancellation ===")
        # cancel_result = cancel_appointment(event_reference="1")
        # print(f"Cancellation result: {cancel_result}")
    
    # Test booking
    print(f"\n=== Testing booking ===")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    book_result = book_appointment(
        name="Test User",
        date=tomorrow,
        time="14:00",
        duration=30,
        description="Test meeting via enhanced tools"
    )
    print(f"Booking result: {book_result}")