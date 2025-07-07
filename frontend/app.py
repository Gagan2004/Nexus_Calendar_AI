
import streamlit as st
import requests
import json
from datetime import datetime, timedelta, date
import pandas as pd
import time
from typing import Dict, Any
import uuid
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv

load_dotenv()
# os.environ.get("API_BASE_URL")
# Configuration
API_BASE_URL = "https://nexus-calendar-agent.onrender.com/"
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