# import streamlit as st
# import requests
# import json
# from datetime import datetime, timedelta, date
# import pandas as pd
# import time
# from typing import Dict, Any
# import uuid

# # Configuration
# API_BASE_URL = "http://localhost:8000"  # Change this to your deployed backend URL
# CHAT_ENDPOINT = f"{API_BASE_URL}/chat"
# RESET_ENDPOINT = f"{API_BASE_URL}/reset-conversation"
# HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
# AVAILABLE_SLOTS_ENDPOINT = f"{API_BASE_URL}/available-slots"
# UPCOMING_EVENTS_ENDPOINT = f"{API_BASE_URL}/upcoming-events"
# DIRECT_BOOKING_ENDPOINT = f"{API_BASE_URL}/direct-booking"

# # Page configuration
# st.set_page_config(
#     page_title="AI Calendar Assistant",
#     page_icon="📅",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # Custom CSS for better styling
# st.markdown("""
# <style>
#     .main-header {
#         text-align: center;
#         padding: 1rem 0;
#         background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         border-radius: 10px;
#         margin-bottom: 2rem;
#     }
    
#     # .chat-container {
#     #     max-height: 600px;
#     #     overflow-y: auto;
#     #     padding: 1rem;
#     #     border: 1px solid #e0e0e0;
#     #     border-radius: 10px;
#     #     background-color: #f8f9fa;
#     # }
    
#     # .user-message {
#     #     background-color: #007bff;
#     #     color: white;
#     #     padding: 0.75rem 1rem;
#     #     border-radius: 18px;
#     #     margin: 0.5rem 0;
#     #     margin-left: 20%;
#     #     text-align: right;
#     # }
    
#     # .bot-message {
#     #     background-color: #e9ecef;
#     #     color: #333;
#     #     padding: 0.75rem 1rem;
#     #     border-radius: 18px;
#     #     margin: 0.5rem 0;
#     #     margin-right: 20%;
#     #     text-align: left;
#     # }
    
#     # .timestamp {
#     #     font-size: 0.8rem;
#     #     color: #666;
#     #     margin-top: 0.25rem;
#     # }
    
#     # .status-indicator {
#     #     padding: 0.25rem 0.75rem;
#     #     border-radius: 20px;
#     #     font-size: 0.8rem;
#     #     font-weight: bold;
#     #     margin: 0.5rem 0;
#     # }
    
#     # .status-success {
#     #     background-color: #d4edda;
#     #     color: #155724;
#     # }
    
#     # .status-error {
#     #     background-color: #f8d7da;
#     #     color: #721c24;
#     # }
    
#     # .status-info {
#     #     background-color: #d1ecf1;
#     #     color: #0c5460;
#     # }
    
#     # .booking-info {
#     #     background-color: #fff3cd;
#     #     color: #856404;
#     #     padding: 1rem;
#     #     border-radius: 8px;
#     #     border-left: 4px solid #ffc107;
#     #     margin: 1rem 0;
#     # }
    
#     # .sidebar-section {
#     #     background-color: #f8f9fa;
#     #     padding: 1rem;
#     #     border-radius: 8px;
#     #     margin: 1rem 0;
#     # }
# </style>
# """, unsafe_allow_html=True)

# # Initialize session state
# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = []
# if 'session_id' not in st.session_state:
#     st.session_state.session_id = str(uuid.uuid4())
# if 'booking_info' not in st.session_state:
#     st.session_state.booking_info = {}
# if 'conversation_step' not in st.session_state:
#     st.session_state.conversation_step = 'initial'

# def check_api_health():
#     """Check if the API is running"""
#     try:
#         response = requests.get(HEALTH_ENDPOINT, timeout=5)
#         if response.status_code == 200:
#             return True, response.json()
#         else:
#             return False, {"error": f"API returned status {response.status_code}"}
#     except requests.RequestException as e:
#         return False, {"error": f"Cannot connect to API: {str(e)}"}

# def send_message(message: str) -> Dict[str, Any]:
#     """Send message to the chat API"""
#     try:
#         payload = {
#             "input": message,
#             "session_id": st.session_state.session_id
#         }
        
#         response = requests.post(
#             CHAT_ENDPOINT, 
#             json=payload, 
#             timeout=30
#         )
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {
#                 "response": f"❌ Error: API returned status {response.status_code}",
#                 "error": True
#             }
#     except requests.RequestException as e:
#         return {
#             "response": f"❌ Connection error: {str(e)}",
#             "error": True
#         }

# def reset_conversation():
#     """Reset the conversation"""
#     try:
#         payload = {"session_id": st.session_state.session_id}
#         response = requests.post(RESET_ENDPOINT, json=payload, timeout=10)
        
#         if response.status_code == 200:
#             st.session_state.chat_history = []
#             st.session_state.booking_info = {}
#             st.session_state.conversation_step = 'initial'
#             return True
#         else:
#             return False
#     except requests.RequestException:
#         return False

# def get_available_slots(date_str: str, duration: int = 30):
#     """Get available time slots for a date"""
#     try:
#         url = f"{AVAILABLE_SLOTS_ENDPOINT}/{date_str}?duration={duration}"
#         response = requests.get(url, timeout=10)
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return None
#     except requests.RequestException:
#         return None

# def get_upcoming_events(days_ahead: int = 7):
#     """Get upcoming events"""
#     try:
#         url = f"{UPCOMING_EVENTS_ENDPOINT}?days_ahead={days_ahead}"
#         response = requests.get(url, timeout=10)
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return None
#     except requests.RequestException:
#         return None

# def direct_booking(name: str, date_str: str, time_str: str, duration: int):
#     """Make a direct booking"""
#     try:
#         payload = {
#             "name": name,
#             "date": date_str,
#             "time": time_str,
#             "duration": duration
#         }
        
#         response = requests.post(DIRECT_BOOKING_ENDPOINT, json=payload, timeout=15)
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"error": f"Booking failed with status {response.status_code}"}
#     except requests.RequestException as e:
#         return {"error": f"Connection error: {str(e)}"}

# def format_message_time(timestamp=None):
#     """Format timestamp for messages"""
#     if timestamp:
#         try:
#             dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
#             return dt.strftime("%H:%M")
#         except:
#             pass
#     return datetime.now().strftime("%H:%M")

# import streamlit.components.v1 as components

# def display_chat_history():
#     """Render full chat UI using raw HTML via Streamlit components"""

#     if st.session_state.chat_history:
#         # Build messages
#         messages_html = ""
#         for msg in st.session_state.chat_history:
#             user_time = format_message_time(msg.get('timestamp'))
#             bot_time = format_message_time(msg.get('timestamp'))

#             messages_html += f"""
#             <div class="user-message">
#                 <div class="message-content">{msg['user']}</div>
#                 <div class="timestamp">{user_time}</div>
#             </div>
#             <div class="bot-message">
#                 <div class="message-content">{msg['bot']}</div>
#                 <div class="timestamp">{bot_time}</div>
#             </div>
#             """

#         html_code = f"""
#         <html>
#         <head>
#         <style>
#         body {{
#             margin: 0;
#             font-family: 'Segoe UI', sans-serif;
#         }}
#         .chat-container {{
#             height: 600px;
#             overflow: hidden;
#             background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
#             padding: 24px;
#             border-radius: 20px;
#             display: flex;
#             flex-direction: column;
#         }}
#         .messages-wrapper {{
#             flex: 1;
#             overflow-y: auto;
#             display: flex;
#             flex-direction: column;
#             gap: 12px;
#         }}
#         .user-message {{
#             align-self: flex-end;
#             background: #3b82f6;
#             color: white;
#             padding: 12px 16px;
#             border-radius: 16px 16px 4px 16px;
#             max-width: 70%;
#             font-size: 14px;
#         }}
#         .bot-message {{
#             align-self: flex-start;
#             background: #4b5563;
#             color: #f3f4f6;
#             padding: 12px 16px;
#             border-radius: 16px 16px 16px 4px;
#             max-width: 70%;
#             font-size: 14px;
#             border-left: 3px solid #10b981;
#         }}
#         .timestamp {{
#             font-size: 10px;
#             opacity: 0.6;
#             margin-top: 4px;
#             font-style: italic;
#         }}
#         </style>
#         </head>
#         <body>
#         <div class="chat-container">
#             <div class="messages-wrapper" id="messages-wrapper">
#                 {messages_html}
#             </div>
#         </div>

#         <script>
#         const wrapper = document.getElementById('messages-wrapper');
#         if (wrapper) {{
#             wrapper.scrollTop = wrapper.scrollHeight;
#         }}
#         </script>
#         </body>
#         </html>
#         """

#         components.html(html_code, height=620, scrolling=False)

#     else:
#             st.info("💬 Say something to start the conversation!")

# # Main header
# st.markdown("""
#     <div class="main-header">
#         <h1>🤖 AI Calendar Assistant</h1>
#         <p>Your intelligent assistant for scheduling meetings and managing appointments</p>
#     </div>
# """, unsafe_allow_html=True)

# # Check API health
# api_healthy, health_info = check_api_health()

# if not api_healthy:
#     st.error(f"⚠️ Cannot connect to the backend API: {health_info.get('error', 'Unknown error')}")
#     st.info("Please make sure the FastAPI backend is running on the correct URL.")
#     st.stop()



# # Enhanced Sidebar with Modern Dark Theme

# with st.sidebar:
#     # Custom CSS for modern dark sidebar
#     st.markdown("""
#     <style>
#     /* Sidebar container */
#     .stSidebar > div {
#         background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
#         border-right: 1px solid rgba(71, 85, 105, 0.3) !important;
#     }
    
   
#     /* Status indicators */
#     .status-indicator {
#         padding: 12px 16px !important;
#         border-radius: 12px !important;
#         font-weight: 600 !important;
#         font-size: 14px !important;
#         text-align: center !important;
#         margin: 8px 0 !important;
#         transition: all 0.3s ease !important;
#         position: relative !important;
#         overflow: hidden !important;
#     }
    
#     .status-success {
#         background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
#         color: white !important;
#         animation: pulse-success 2s infinite !important;
#     }
    
#     .status-error {
#         background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
#         color: white !important;
#         animation: pulse-error 2s infinite !important;
#     }
    
#     @keyframes pulse-success {
#         0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
#         50% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
#     }
    
#     @keyframes pulse-error {
#         0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
#         50% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
#     }
    
#     /* Sidebar buttons */
#     .stSidebar .stButton > button {
#         background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
#         border: none !important;
#         border-radius: 12px !important;
#         color: white !important;
#         font-weight: 600 !important;
#         font-size: 14px !important;
#         padding: 12px 20px !important;
#         transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
#         box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
#         position: relative !important;
#         overflow: hidden !important;
#         width: 100% !important;
#     }
    
#     .stSidebar .stButton > button:hover {
#         transform: translateY(-2px) !important;
#         box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
#         background: linear-gradient(135deg, #4338ca 0%, #312e81 100%) !important;
#     }
    
#     .stSidebar .stButton > button:active {
#         transform: translateY(0px) !important;
#     }
    
#     /* Reset button special styling */
#     .stSidebar .stButton > button[title*="Reset"] {
#         background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
#     }
    
#     .stSidebar .stButton > button[title*="Reset"]:hover {
#         background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
#     }
    
#     /* Headers */
#     .stSidebar h1 {
#         color: #f1f5f9 !important;
#         font-size: 24px !important;
#         font-weight: 700 !important;
#         margin-bottom: 24px !important;
#         text-align: center !important;
#         background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
#         -webkit-background-clip: text !important;
#         -webkit-text-fill-color: transparent !important;
#         background-clip: text !important;
#     }
    
#     .stSidebar h2 {
#         color: #e2e8f0 !important;
#         font-size: 16px !important;
#         font-weight: 600 !important;
#         margin-bottom: 12px !important;
#         display: flex !important;
#         align-items: center !important;
#         gap: 8px !important;
#     }
    
#     .stSidebar h3 {
#         color: #cbd5e1 !important;
#         font-size: 14px !important;
#         font-weight: 500 !important;
#         margin-bottom: 8px !important;
#     }
    
#     /* Info cards */
#     .info-card {
#         background: rgba(30, 41, 59, 0.8) !important;
#         border: 1px solid rgba(71, 85, 105, 0.3) !important;
#         border-radius: 10px !important;
#         padding: 12px !important;
#         margin: 8px 0 !important;
#         color: #e2e8f0 !important;
#         font-size: 13px !important;
#         transition: all 0.3s ease !important;
#     }
    
#     .info-card:hover {
#         border-color: rgba(99, 102, 241, 0.4) !important;
#         transform: translateX(4px) !important;
#     }
    
#     /* Booking info styling */
#     .booking-info {
#         background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%) !important;
#         border: 1px solid rgba(59, 130, 246, 0.3) !important;
#         border-radius: 12px !important;
#         padding: 16px !important;
#         margin: 12px 0 !important;
#     }
    
#     .booking-info strong {
#         color: #60a5fa !important;
#     }
    
#     /* Event list styling */
#     .event-item {
#         background: rgba(34, 197, 94, 0.1) !important;
#         border-left: 3px solid #22c55e !important;
#         padding: 8px 12px !important;
#         margin: 4px 0 !important;
#         border-radius: 0 8px 8px 0 !important;
#         color: #86efac !important;
#         font-size: 12px !important;
#     }
    
#     .slot-item {
#         background: rgba(168, 85, 247, 0.1) !important;
#         border-left: 3px solid #a855f7 !important;
#         padding: 8px 12px !important;
#         margin: 4px 0 !important;
#         border-radius: 0 8px 8px 0 !important;
#         color: #c4b5fd !important;
#         font-size: 12px !important;
#     }
    
#     /* Scrollbar styling */
#     .stSidebar::-webkit-scrollbar {
#         width: 6px !important;
#     }
    
#     .stSidebar::-webkit-scrollbar-track {
#         background: rgba(15, 23, 42, 0.5) !important;
#     }
    
#     .stSidebar::-webkit-scrollbar-thumb {
#         background: linear-gradient(180deg, #4f46e5, #3730a3) !important;
#         border-radius: 3px !important;
#     }
    
#     .stSidebar::-webkit-scrollbar-thumb:hover {
#         background: linear-gradient(180deg, #4338ca, #312e81) !important;
#     }
#     </style>
#     """, unsafe_allow_html=True)
    
#     # Main header with gradient effect
#     st.markdown("""
#     <div style="text-align: center; padding: 20px 0;">
#         <h1 style="margin: 0; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
#             🎛️ Controls
#         </h1>
#     </div>
#     """, unsafe_allow_html=True)
    
#     # API Status Section
#     st.subheader("📡 API Status")
#     if api_healthy:
#         st.markdown('<div class="status-indicator status-success">✅ Connected & Ready</div>', unsafe_allow_html=True)
#         st.markdown('<div class="info-card">🟢 All systems operational</div>', unsafe_allow_html=True)
#     else:
#         st.markdown('<div class="status-indicator status-error">❌ Connection Lost</div>', unsafe_allow_html=True)
#         st.markdown('<div class="info-card">🔴 Attempting to reconnect...</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)
    
    
#      # Quick Actions Section
#     st.subheader("⚡ Quick Actions")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         if st.button("📅 Today's Schedule", use_container_width=True, help="View today's events"):
#             events = get_upcoming_events(1)
#             if events and events.get('upcoming_events'):
#                 st.markdown("**Today's Events:**")
#                 for event in events['upcoming_events']:
#                     st.markdown(f'<div class="event-item">📅 {event["summary"]}<br>🕐 {event["start"]} - {event["end"]}</div>', unsafe_allow_html=True)
#             else:
#                 st.markdown('<div class="info-card">📅 No events scheduled for today</div>', unsafe_allow_html=True)
    
#     with col2:
#         if st.button("🔍 Available Slots", use_container_width=True, help="Check tomorrow's availability"):
#             tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
#             slots = get_available_slots(tomorrow)
#             if slots and slots.get('available_slots'):
#                 st.markdown(f"**Available slots for {tomorrow}:**")
#                 for slot in slots['available_slots'][:5]:  # Show first 5
#                     st.markdown(f'<div class="slot-item">🕐 {slot["start_time"]} - {slot["end_time"]}</div>', unsafe_allow_html=True)
#             else:
#                 st.markdown('<div class="info-card">🔍 No available slots found</div>', unsafe_allow_html=True)
    
   

#     # Conversation Controls Section
#     st.subheader("💬 Conversation")
    
#     if st.button("🔄 Reset Conversation", use_container_width=True, help="Clear all chat history"):
#         if reset_conversation():
#             st.success("✅ Conversation reset!")
#             st.rerun()
#         else:
#             st.error("❌ Failed to reset conversation")
    
#     # Enhanced info cards
#     st.markdown(f'<div class="info-card"><strong>Session ID:</strong> <code>{st.session_state.session_id[:8]}...</code></div>', unsafe_allow_html=True)
#     st.markdown(f'<div class="info-card"><strong>Messages:</strong> {len(st.session_state.chat_history)} total</div>', unsafe_allow_html=True)
#     st.markdown(f'<div class="info-card"><strong>Status:</strong> {st.session_state.conversation_step}</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)
    
#     # Current Booking Info Section
#     if st.session_state.booking_info:
#         st.subheader("📋 Current Booking")
#         st.markdown('<div class="booking-info">', unsafe_allow_html=True)
#         for key, value in st.session_state.booking_info.items():
#             st.markdown(f"**{key.title()}:** {value}")
#         st.markdown('</div>', unsafe_allow_html=True)
#         st.markdown('</div>', unsafe_allow_html=True)
    
   
#     # Footer with version info
#     st.markdown("""
#     <div style="text-align: center; padding: 20px 0; color: #64748b; font-size: 12px; border-top: 1px solid rgba(71, 85, 105, 0.3); margin-top: 20px;">
#         <p>🤖 AI Assistant v2.0<br>
#         🌙 Dark Theme Optimized</p>
#     </div>
#     """, unsafe_allow_html=True)

# # Main chat interface
# col1, col2 = st.columns([3, 1])

# with col1:
#     st.subheader("💬 Chat with Assistant")
    
#     # Display chat history
#     display_chat_history()
    
#     # Chat input

# # Enhanced chat form with modern dark theme styling
# with st.form(key="chat_form", clear_on_submit=True):
#     # Custom CSS for modern dark theme
#     st.markdown("""
#     <style>
#     /* Chat input container */
#     .stTextInput > div > div > input {
#         background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
#         border: 2px solid #475569 !important;
#         border-radius: 16px !important;
#         color: #f1f5f9 !important;
#         font-size: 16px !important;
#         padding: 16px 20px !important;
#         transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
#         box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
#     }
    
#     .stTextInput > div > div > input:focus {
#         border-color: #3b82f6 !important;
#         box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1), 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
#         transform: translateY(-2px) !important;
#     }
    
#     .stTextInput > div > div > input::placeholder {
#         color: #94a3b8 !important;
#         font-style: italic !important;
#     }
    
#     /* Button styling */
#     .stButton > button {
#         background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
#         border: none !important;
#         border-radius: 12px !important;
#         color: white !important;
#         font-weight: 600 !important;
#         font-size: 15px !important;
#         padding: 12px 24px !important;
#         transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
#         box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
#         position: relative !important;
#         overflow: hidden !important;
#     }
    
#     .stButton > button:hover {
#         transform: translateY(-2px) !important;
#         box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
#         background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%) !important;
#     }
    
#     .stButton > button:active {
#         transform: translateY(0px) !important;
#     }
    
#     /* Example button styling */
#     .stButton > button[data-testid*="example"] {
#         background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
#     }
    
#     .stButton > button[data-testid*="example"]:hover {
#         background: linear-gradient(135deg, #5b21b6 0%, #4c1d95 100%) !important;
#     }
    
#     /* Form container */
#     .stForm {
#         background: rgba(15, 23, 42, 0.6) !important;
#         border-radius: 20px !important;
#         padding: 24px !important;
#         border: 1px solid rgba(71, 85, 105, 0.3) !important;
#         backdrop-filter: blur(10px) !important;
#         box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
#     }
    
#     /* Column spacing */
#     .stColumns {
#         gap: 16px !important;
#     }
    
#     /* Pulse animation for send button */
#     @keyframes pulse {
#         0%, 100% { opacity: 1; }
#         50% { opacity: 0.8; }
#     }
    
#     .stButton > button::before {
#         content: '';
#         position: absolute;
#         top: 0;
#         left: -100%;
#         width: 100%;
#         height: 100%;
#         background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
#         transition: left 0.5s;
#     }
    
#     .stButton > button:hover::before {
#         left: 100%;
#     }
#     </style>
#     """, unsafe_allow_html=True)
    
#     # Enhanced text input with better UX
#     user_input = st.text_input(
#         "Type your message here...",
#         placeholder="✨ Ask me anything... e.g., 'Schedule a meeting with Sarah tomorrow at 3 PM'",
#         label_visibility="collapsed",
#         help="Press Enter to send or use the button below"
#     )
    
#     # Modern button layout with improved spacing
#     col_send, col_spacer, col_example = st.columns([2, 0.5, 3])
    
#     with col_send:
#         send_button = st.form_submit_button(
#             "Send 🚀", 
#             use_container_width=True,
#             help="Send your message"
#         )
    
#     with col_example:
#         if st.form_submit_button(
#             "💡 Try Example Query", 
#             use_container_width=True,
#             help="Load a sample query to get started"
#         ):
#             user_input = "I need to schedule a meeting with John Doe next Monday at 2 PM"
#             send_button = True

# # Add some modern UI enhancements
# st.markdown("""
# <div style="text-align: center; padding: 10px; color: #64748b; font-size: 14px;">
#     <p>💬 <strong>Pro Tips:</strong> Be specific with dates and times • Use natural language • Try voice-to-text</p>
# </div>
# """, unsafe_allow_html=True)

# # Optional: Add a subtle animation or loading state
# if send_button and user_input:
#     st.markdown("""
#     <div style="text-align: center; padding: 20px;">
#         <div style="display: inline-block; animation: pulse 2s infinite; color: #3b82f6;">
#             🤖 Processing your request...
#         </div>
#     </div>
#     """, unsafe_allow_html=True)
    
#     # Process message
#     if send_button and user_input:
#         with st.spinner("🤖 Assistant is thinking..."):
#             response = send_message(user_input)
            
#             # Add to chat history
#             chat_message = {
#                 "user": user_input,
#                 "bot": response.get("response", "No response received"),
#                 "timestamp": datetime.now().isoformat()
#             }
#             st.session_state.chat_history.append(chat_message)
            
#             # Update booking info and conversation step
#             if "conversation_state" in response:
#                 conv_state = response["conversation_state"]
#                 st.session_state.booking_info = conv_state.get("booking_info", {})
#                 st.session_state.conversation_step = conv_state.get("step", "initial")
            
#             st.rerun()

# with col2:
#     st.subheader("🛠️ Tools")
    
#     # Create tabs for better organization
#     tab1, tab2, tab3 = st.tabs(["📅 Quick Book", "📋 Events", "🔍 Availability"])
    
#     with tab1:
#         st.markdown("#### Skip the conversation and book directly")
        
#         # Use columns for better layout
#         col_left, col_right = st.columns([1, 1])
        
#         with col_left:
#             name = st.text_input("👤 Name", placeholder="Enter your full name")
#             booking_date = st.date_input("📅 Date", min_value=date.today())
            
#         with col_right:
#             booking_time = st.time_input("🕐 Time", value=datetime.now().time())
#             duration = st.selectbox("⏱️ Duration", 
#                                   options=[15, 30, 45, 60, 90, 120],
#                                   format_func=lambda x: f"{x} minutes",
#                                   index=1)
        
#         # Add some spacing
#         st.write("")
        
#         # Validation feedback
#         if name and booking_date and booking_time:
#             st.success("✅ All fields completed - ready to book!")
#         else:
#             missing_fields = []
#             if not name: missing_fields.append("Name")
#             if not booking_date: missing_fields.append("Date")
#             if not booking_time: missing_fields.append("Time")
#             if missing_fields:
#                 st.info(f"ℹ️ Please fill in: {', '.join(missing_fields)}")
        
#         # Book button with better styling
#         if st.button("🚀 Book Appointment", 
#                     type="primary", 
#                     use_container_width=True,
#                     disabled=not (name and booking_date and booking_time)):
            
#             date_str = booking_date.strftime("%Y-%m-%d")
#             time_str = booking_time.strftime("%H:%M")
            
#             with st.spinner("⏳ Processing your booking..."):
#                 result = direct_booking(name, date_str, time_str, duration)
                
#                 if "error" in result:
#                     st.error(f"❌ {result['error']}")
#                 else:
#                     booking_result = result.get("booking_result", {})
#                     if booking_result.get("status") == "success":
#                         st.success(f"🎉 {booking_result.get('message', 'Booking confirmed!')}")
#                         st.balloons()  # Add celebration
#                     else:
#                         st.error(f"❌ {booking_result.get('message', 'Booking failed')}")
    
#     with tab2:
#         st.markdown("#### View your upcoming schedule")
        
#         # Better control layout
#         col_days, col_refresh = st.columns([2, 1])
        
#         with col_days:
#             days = st.selectbox("📆 Show events for next:", 
#                               options=[1, 3, 7, 14, 30],
#                               format_func=lambda x: f"{x} {'day' if x == 1 else 'days'}",
#                               index=2)
        
#         with col_refresh:
#             st.write("")  # Add space to align with selectbox
#             refresh_clicked = st.button("🔄 Refresh", use_container_width=True)
        
#         # Auto-load events on tab selection or refresh
#         if refresh_clicked or st.session_state.get('events_tab_opened', False):
#             st.session_state['events_tab_opened'] = True
            
#             with st.spinner("📡 Loading events..."):
#                 events = get_upcoming_events(days)
                
#                 if events and events.get("upcoming_events"):
#                     st.success(f"📅 Found {len(events['upcoming_events'])} upcoming events")
                    
#                     # Better event display with cards
#                     for i, event in enumerate(events["upcoming_events"]):
#                         with st.container():
#                             st.markdown(f"""
#                             <div style="
#                                 background-color: #f0f2f6;
#                                 padding: 15px;
#                                 border-radius: 10px;
#                                 margin: 10px 0;
#                                 border-left: 4px solid #1f77b4;
#                             ">
#                                 <h4 style="margin: 0 0 10px 0; color: #1f77b4;">{event['summary']}</h4>
#                                 <p style="margin: 0; color: #666;">📅 {event['start']} ➜ {event['end']}</p>
#                             </div>
#                             """, unsafe_allow_html=True)
#                 else:
#                     st.info("📭 No upcoming events found")
    
#     with tab3:
#         st.markdown("#### Find available time slots")
        
#         # Better layout for availability checker
#         col_date, col_duration = st.columns([1, 1])
        
#         with col_date:
#             check_date = st.date_input("📅 Check Date", 
#                                      min_value=date.today(),
#                                      help="Select a date to check availability")
        
#         with col_duration:
#             check_duration = st.selectbox("⏱️ Meeting Duration", 
#                                         options=[15, 30, 45, 60, 90],
#                                         format_func=lambda x: f"{x} minutes",
#                                         index=1)
        
#         st.write("")
        
#         if st.button("🔍 Check Available Slots", 
#                     type="secondary", 
#                     use_container_width=True):
            
#             date_str = check_date.strftime("%Y-%m-%d")
            
#             with st.spinner("🔍 Searching for available slots..."):
#                 slots = get_available_slots(date_str, check_duration)
                
#                 if slots and slots.get("available_slots"):
#                     st.success(f"✅ Found {len(slots['available_slots'])} available slots")
                    
#                     # Display slots in a more organized way
#                     st.markdown(f"**Available {check_duration}-minute slots for {check_date.strftime('%B %d, %Y')}:**")
                    
#                     # Group slots by time of day
#                     morning_slots = []
#                     afternoon_slots = []
#                     evening_slots = []
                    
#                     for slot in slots["available_slots"]:
#                         start_hour = int(slot['start_time'].split(':')[0])
#                         if start_hour < 12:
#                             morning_slots.append(slot)
#                         elif start_hour < 17:
#                             afternoon_slots.append(slot)
#                         else:
#                             evening_slots.append(slot)
                    
#                     # Display categorized slots
#                     if morning_slots:
#                         st.markdown("**🌅 Morning (Before 12 PM):**")
#                         for slot in morning_slots:
#                             st.markdown(f"&nbsp;&nbsp;• {slot['start_time']} - {slot['end_time']}")
                    
#                     if afternoon_slots:
#                         st.markdown("**☀️ Afternoon (12 PM - 5 PM):**")
#                         for slot in afternoon_slots:
#                             st.markdown(f"&nbsp;&nbsp;• {slot['start_time']} - {slot['end_time']}")
                    
#                     if evening_slots:
#                         st.markdown("**🌆 Evening (After 5 PM):**")
#                         for slot in evening_slots:
#                             st.markdown(f"&nbsp;&nbsp;• {slot['start_time']} - {slot['end_time']}")
                            
#                     # Add helpful tip
#                     st.info("💡 Tip: Use the Quick Book tab to instantly book any of these slots!")
                    
#                 else:
#                     st.warning("⚠️ No available slots found for this date and duration")
#                     st.info("💡 Try checking a different date or shorter duration")


# # Footer
# st.markdown("---")
# st.markdown("""
#     <div style="text-align: center; color: #666; padding: 1rem;">
#         🤖 AI Calendar Assistant powered by FastAPI & Streamlit<br>
#         <small>Session ID: {}</small>
#     </div>
# """.format(st.session_state.session_id), unsafe_allow_html=True)







import streamlit as st
import requests
import json
from datetime import datetime, timedelta, date
import pandas as pd
import time
from typing import Dict, Any
import uuid
import streamlit.components.v1 as components

# Configuration
API_BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE_URL}/chat"
RESET_ENDPOINT = f"{API_BASE_URL}/reset-conversation"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
AVAILABLE_SLOTS_ENDPOINT = f"{API_BASE_URL}/available-slots"
UPCOMING_EVENTS_ENDPOINT = f"{API_BASE_URL}/upcoming-events"
DIRECT_BOOKING_ENDPOINT = f"{API_BASE_URL}/direct-booking"

# Page configuration
st.set_page_config(
    page_title="Nexus Calendar AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ultra-modern dark theme
st.markdown("""
<style>
    /* Main app background */
    .main {
        background-color: #0a0a0a;
    }
    
    /* Header styling with glass morphism effect */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        color: white;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.36);
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
    }
    
    /* Perfect chat container with fixed height and auto-scroll */
    .chat-container {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 16px;
        padding: 0;
        height: 65vh;
        display: flex;
        flex-direction: column;
        border: 1px solid rgba(255, 255, 255, 0.1);
        overflow: hidden;
        box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.3);
    }
    
    .messages-wrapper {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
        scroll-behavior: smooth;
    }
    
    /* Modern message bubbles with subtle glow */
    .message {
        padding: 0.85rem 1.25rem;
        border-radius: 18px;
        margin-bottom: 0.85rem;
        max-width: 75%;
        font-size: 0.95rem;
        line-height: 1.5;
        position: relative;
        animation: fadeIn 0.3s ease-out;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .bot-message {
        background: rgba(30, 41, 59, 0.9);
        color: #e2e8f0;
        margin-right: auto;
        border-bottom-left-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Timestamp styling */
    .timestamp {
        font-size: 0.7rem;
        opacity: 0.6;
        margin-top: 0.35rem;
        display: block;
        text-align: right;
        font-feature-settings: "tnum";
    }
    
    /* Input area with glass effect */
    .input-area {
        background: rgba(15, 23, 42, 0.7);
        padding: 1.25rem;
        border-radius: 0 0 16px 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    
    /* Premium button styling */
    .stButton>button {
        border-radius: 12px !important;
        padding: 0.65rem 1.25rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
        font-weight: 500 !important;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(99, 102, 241, 0.25) !important;
    }
    
    /* Card styling with glass effect */
    .card {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.36);
    }
    
    .card-title {
        font-weight: 600;
        color: #818cf8;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.65rem;
        font-size: 1rem;
    }
    
    /* Status indicators with animation */
    .status-indicator {
        padding: 0.65rem 1rem;
        border-radius: 12px;
        font-weight: 500;
        font-size: 0.85rem;
        text-align: center;
        margin-bottom: 1rem;
        border: 1px solid;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.9; }
        50% { opacity: 1; }
        100% { opacity: 0.9; }
    }
    
    .status-success {
        background: rgba(16, 185, 129, 0.15);
        color: #a7f3d0;
        border-color: rgba(16, 185, 129, 0.3);
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        border-color: rgba(239, 68, 68, 0.3);
    }
    
    /* Tool section styling */
    .tool-section {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.36);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.4);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 4px;
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
    }
    
    /* Select box styling */
    .stSelectbox>div>div>select {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Date input styling */
    .stDateInput>div>div>input {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Time input styling */
    .stTimeInput>div>div>input {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Tab styling */
    .stTabs [role="tablist"] {
        gap: 0.5rem;
        border-bottom: none !important;
    }
    
    .stTabs [role="tab"] {
        background: rgba(30, 41, 59, 0.6) !important;
        color: #94a3b8 !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border-color: transparent !important;
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.25) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 1px;
        background: rgba(255, 255, 255, 0.05);
        margin: 1.5rem 0;
    }
    
    /* Loading spinner styling */
    .stSpinner>div {
        border-top-color: #818cf8 !important;
    }
    
    /* Notification styling */
    .stNotification {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'booking_info' not in st.session_state:
    st.session_state.booking_info = {}
if 'conversation_step' not in st.session_state:
    st.session_state.conversation_step = 'initial'
if 'events_tab_opened' not in st.session_state:
    st.session_state.events_tab_opened = False

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"API returned status {response.status_code}"}
    except requests.RequestException as e:
        return False, {"error": f"Cannot connect to API: {str(e)}"}

def send_message(message: str) -> Dict[str, Any]:
    """Send message to the chat API"""
    try:
        payload = {
            "input": message,
            "session_id": st.session_state.session_id
        }
        
        response = requests.post(
            CHAT_ENDPOINT, 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": f"❌ Error: API returned status {response.status_code}",
                "error": True
            }
    except requests.RequestException as e:
        return {
            "response": f"❌ Connection error: {str(e)}",
            "error": True
        }

def reset_conversation():
    """Reset the conversation"""
    try:
        payload = {"session_id": st.session_state.session_id}
        response = requests.post(RESET_ENDPOINT, json=payload, timeout=10)
        
        if response.status_code == 200:
            st.session_state.chat_history = []
            st.session_state.booking_info = {}
            st.session_state.conversation_step = 'initial'
            return True
        else:
            return False
    except requests.RequestException:
        return False

def get_available_slots(date_str: str, duration: int = 30):
    """Get available time slots for a date"""
    try:
        url = f"{AVAILABLE_SLOTS_ENDPOINT}/{date_str}?duration={duration}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None

def get_upcoming_events(days_ahead: int = 7):
    """Get upcoming events"""
    try:
        url = f"{UPCOMING_EVENTS_ENDPOINT}?days_ahead={days_ahead}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None

def direct_booking(name: str, date_str: str, time_str: str, duration: int):
    """Make a direct booking"""
    try:
        payload = {
            "name": name,
            "date": date_str,
            "time": time_str,
            "duration": duration
        }
        
        response = requests.post(DIRECT_BOOKING_ENDPOINT, json=payload, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Booking failed with status {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}

def format_message_time(timestamp=None):
    """Format timestamp for messages"""
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%H:%M")
        except:
            pass
    return datetime.now().strftime("%H:%M")

def display_chat_history():
    """Display the chat history with perfect scrolling behavior"""
    chat_html = """
    <html>
    <head>
    <style>
        .chat-container {
            height: 65vh;
            background: rgba(15, 23, 42, 0.6);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        .messages-wrapper {
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem;
            scroll-behavior: smooth;
        }
        
        .message {
            padding: 0.85rem 1.25rem;
            border-radius: 18px;
            margin-bottom: 0.85rem;
            max-width: 75%;
            font-size: 0.95rem;
            line-height: 1.5;
            position: relative;
            animation: fadeIn 0.3s ease-out;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .bot-message {
            background: rgba(30, 41, 59, 0.9);
            color: #e2e8f0;
            margin-right: auto;
            border-bottom-left-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .timestamp {
            font-size: 0.7rem;
            opacity: 0.6;
            margin-top: 0.35rem;
            display: block;
            text-align: right;
            font-feature-settings: "tnum";
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(15, 23, 42, 0.4);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            border-radius: 4px;
        }
    </style>
    </head>
    <body>
    <div class="chat-container">
        <div class="messages-wrapper" id="messages-wrapper">
    """
    
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            chat_html += f"""
            <div class="message user-message">
                {msg["user"]}
                <span class="timestamp">{format_message_time(msg.get("timestamp"))}</span>
            </div>
            <div class="message bot-message">
                {msg["bot"]}
                <span class="timestamp">{format_message_time(msg.get("timestamp"))}</span>
            </div>
            """
    else:
        chat_html += """
        <div style="text-align: center; padding: 2rem; color: #64748b;">
            <h3 style="color: #e2e8f0;">💬 Start a conversation</h3>
            <p>Ask me to schedule a meeting, check availability, or view your calendar</p>
        </div>
        """
    
    chat_html += """
        </div>
    </div>
    <script>
        // Auto-scroll to bottom
        const wrapper = document.getElementById('messages-wrapper');
        if (wrapper) {
            wrapper.scrollTop = wrapper.scrollHeight;
        }
        
        // Smooth scroll for new messages
        let observer = new MutationObserver(function(mutations) {
            wrapper.scrollTo({
                top: wrapper.scrollHeight,
                behavior: 'smooth'
            });
        });
        
        observer.observe(wrapper, {
            childList: true,
            subtree: true
        });
    </script>
    </body>
    </html>
    """
    
    components.html(chat_html, height=700)

# Main header with glass morphism effect
st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">Nexus Calendar AI</h1>
        <p style="margin: 0.5rem 0 0; opacity: 0.8; color: #cbd5e1;">Your intelligent scheduling companion</p>
    </div>
""", unsafe_allow_html=True)

# Check API health
api_healthy, health_info = check_api_health()

if not api_healthy:
    st.error(f"⚠️ Cannot connect to the backend API: {health_info.get('error', 'Unknown error')}")
    st.info("Please make sure the FastAPI backend is running on the correct URL.")
    st.stop()

# Main layout
col1, col2 = st.columns([3, 1], gap="large")

with col1:
    # Chat interface
    st.markdown("### 💬 Conversation")
    display_chat_history()
    
    # Chat input form with glass effect
    with st.form(key="chat_form", clear_on_submit=True):
        st.markdown('<div class="input-area">', unsafe_allow_html=True)
        
        user_input = st.text_input(
            "Type your message...",
            placeholder="E.g., 'Schedule a meeting with John tomorrow at 2pm'",
            label_visibility="collapsed",
            key="chat_input"
        )
        
        col_submit, col_example = st.columns([1, 3])
        with col_submit:
            submit_button = st.form_submit_button(
                "Send",
                type="primary",
                use_container_width=True
            )
        with col_example:
            if st.form_submit_button(
                "💡 Example: Show my schedule this week",
                use_container_width=True,
                help="Try this example query"
            ):
                user_input = "Show my schedule this week"
                submit_button = True
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Process message
    if submit_button and user_input:
        with st.spinner("🤖 Processing your request..."):
            response = send_message(user_input)
            
            # Add to chat history
            chat_message = {
                "user": user_input,
                "bot": response.get("response", "No response received"),
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.chat_history.append(chat_message)
            
            # Update booking info and conversation step
            if "conversation_state" in response:
                conv_state = response["conversation_state"]
                st.session_state.booking_info = conv_state.get("booking_info", {})
                st.session_state.conversation_step = conv_state.get("step", "initial")
            
            st.rerun()

with col2:
    # Sidebar content
    st.markdown("### 🛠️ Tools & Controls")
    
    # API Status Card
    with st.container():
        st.markdown('<div class="card-title">📡 Connection Status</div>', unsafe_allow_html=True)
        
        if api_healthy:
            st.markdown('<div class="status-indicator status-success">🟢 Connected & Operational</div>', unsafe_allow_html=True)
            st.markdown(f'<small style="color: #94a3b8;">Session ID: <code>{st.session_state.session_id[:8]}...</code></small>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-indicator status-error">🔴 Connection Error</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Actions Card
    with st.container():
        st.markdown('<div class="card-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Reset Conversation", use_container_width=True):
            if reset_conversation():
                st.success("Conversation reset!")
                st.rerun()
            else:
                st.error("Failed to reset conversation")
        
        if st.button("📅 Today's Schedule", use_container_width=True):
            events = get_upcoming_events(1)
            if events and events.get('upcoming_events'):
                st.markdown('<div style="margin-top: 0.5rem; color: #e2e8f0; font-size: 0.9rem;">Today\'s Events:</div>', unsafe_allow_html=True)
                for event in events['upcoming_events']:
                    st.markdown(f"""
                    <div style="padding: 0.75rem; margin: 0.5rem 0; background: rgba(30, 41, 59, 0.6); border-radius: 12px; border-left: 3px solid #818cf8;">
                        <div style="font-weight: 500; color: #e2e8f0;">{event["summary"]}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">{event["start"]} - {event["end"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No events scheduled for today", icon="📭")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Booking Tool
    with st.container():
        st.markdown('<div class="card-title">📅 Quick Book</div>', unsafe_allow_html=True)
        
        name = st.text_input("Your Name", key="quick_book_name", placeholder="Enter your name")
        booking_date = st.date_input("Date", min_value=date.today(), key="quick_book_date")
        booking_time = st.time_input("Time", key="quick_book_time")
        duration = st.selectbox(
            "Duration", 
            options=[15, 30, 45, 60, 90, 120],
            format_func=lambda x: f"{x} minutes",
            index=1,
            key="quick_book_duration"
        )
        
        if st.button("Book Appointment", type="primary", use_container_width=True):
            if not name:
                st.warning("Please enter your name", icon="⚠️")
            else:
                date_str = booking_date.strftime("%Y-%m-%d")
                time_str = booking_time.strftime("%H:%M")
                
                with st.spinner("Booking your appointment..."):
                    result = direct_booking(name, date_str, time_str, duration)
                    
                    if "error" in result:
                        st.error(f"Booking failed: {result['error']}", icon="❌")
                    else:
                        booking_result = result.get("booking_result", {})
                        if booking_result.get("status") == "success":
                            st.success("✅ Booking confirmed!", icon="🎉")
                            st.balloons()
                            st.session_state.booking_info = {
                                "Name": name,
                                "Date": date_str,
                                "Time": time_str,
                                "Duration": f"{duration} minutes"
                            }
                        else:
                            st.error(f"❌ {booking_result.get('message', 'Booking failed')}", icon="❌")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Premium footer
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0; color: #64748b; font-size: 0.85rem;">
    <div style="margin-bottom: 0.5rem;">
        <span style="color: #818cf8; font-weight: 500;">Nexus Calendar AI</span> • Powered by Streamlit & FastAPI
    </div>
    <div style="display: flex; justify-content: center; gap: 1rem;">
        <span>v2.1.0</span>
        <span>•</span>
        <span>Dark Mode</span>
        <span>•</span>
        <span>Premium</span>
    </div>
</div>
""", unsafe_allow_html=True)