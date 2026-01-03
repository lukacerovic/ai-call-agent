"""Clinic AI Agent - Intelligent medical receptionist using OpenAI"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    print("OpenAI library not installed. Install with: pip install openai")

load_dotenv()

logger = logging.getLogger(__name__)


class ClinicAgent:
    """AI receptionist agent for medical clinic"""
    
    def __init__(self):
        """Initialize the clinic agent"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        
        # Session management
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Load services data
        self.services = self._load_services()
        self.reservations = self._load_reservations()
        
        # Agent configuration
        self.model = "gpt-4o-mini"
        self.temperature = 0.7
        self.max_tokens = 150
        
        logger.info(f"🧠 Clinic Agent initialized with model: {self.model}")
    
    def _load_services(self) -> List[Dict[str, Any]]:
        """Load available services from JSON"""
        try:
            services_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "services.json"
            )
            with open(services_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading services: {e}")
            return []
    
    def _load_reservations(self) -> List[Dict[str, Any]]:
        """Load existing reservations from JSON"""
        try:
            reservations_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "reservations.json"
            )
            with open(reservations_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading reservations: {e}")
            return []
    
    def get_greeting(self) -> str:
        """Get the initial greeting message"""
        clinic_name = os.getenv("CLINIC_NAME", "Medical Clinic")
        return f"""Hello, thank you for calling {clinic_name}. I'm an AI assistant.
        
I can help you schedule appointments and answer questions about our services.
        
Please note: I'm an AI and cannot provide medical diagnosis or emergency care.
        
How can I assist you today?"""
    
    def get_farewell(self) -> str:
        """Get the farewell message"""
        return """Thank you for calling. Have a great day!"""
    
    def should_end_call(self, user_message: str) -> bool:
        """Check if user wants to end the call"""
        end_phrases = [
            "goodbye",
            "bye",
            "thank you",
            "thanks",
            "that's all",
            "that is all",
            "no more",
            "nothing else",
            "see you",
            "take care",
            "have a good day",
            "hang up",
            "end call"
        ]
        
        user_lower = user_message.lower().strip()
        return any(phrase in user_lower for phrase in end_phrases)
    
    def process_message(
        self,
        user_message: str,
        session_id: str
    ) -> str:
        """Process user message and generate response"""
        try:
            # Initialize or get session
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "messages": [],
                    "patient_name": None,
                    "patient_dob": None,
                    "selected_service": None,
                    "booking_date": None,
                    "booking_time": None,
                }
            
            session = self.sessions[session_id]
            session["messages"].append({
                "role": "user",
                "content": user_message
            })
            
            # Build system prompt
            system_prompt = self._build_system_prompt(session)
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *session["messages"]
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            assistant_message = response.choices[0].message.content.strip()
            
            # Store assistant response
            session["messages"].append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Limit conversation history
            max_history = int(os.getenv("MAX_CONVERSATION_LENGTH", 50))
            if len(session["messages"]) > max_history:
                session["messages"] = session["messages"][-max_history:]
            
            logger.info(f"Agent response: {assistant_message}")
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I apologize, I'm having technical difficulties. Please try again."
    
    def _build_system_prompt(self, session: Dict[str, Any]) -> str:
        """Build the system prompt for the agent"""
        clinic_name = os.getenv("CLINIC_NAME", "Medical Clinic")
        
        services_info = self._format_services_info()
        
        prompt = f"""You are a professional and friendly medical receptionist AI for {clinic_name}.

Your role:
- Greet patients warmly and professionally
- Help schedule appointments
- Answer questions about available services
- Collect patient information (name, date of birth)
- Confirm appointment details clearly

Available Services:
{services_info}

IMPORTANT SAFETY RULES:
1. You CANNOT provide medical diagnosis or advice
2. You CANNOT prescribe medications
3. If a patient describes emergency symptoms (chest pain, difficulty breathing, severe bleeding, etc.), immediately suggest:
   "Please call 911 or go to the nearest emergency room immediately. This requires urgent medical attention."
4. Always be calm, professional, and empathetic
5. Ask one question at a time
6. Listen completely to the patient before responding
7. Confirm all details (name, appointment date/time) slowly and clearly

Conversation Guidelines:
- Keep responses concise (1-2 sentences)
- Use natural, conversational language
- Pause between responses to let the patient speak
- If patient mentions health concerns, listen but do NOT diagnose
- Suggest appropriate services based on their needs
- Always offer to book an appointment

Current Session Info:
- Patient Name: {session.get('patient_name', 'Not provided')}
- Selected Service: {session.get('selected_service', 'None')}

Respond naturally as a medical receptionist would in a phone conversation."""
        
        return prompt
    
    def _format_services_info(self) -> str:
        """Format services information for the prompt"""
        if not self.services:
            return "No services available at this time."
        
        formatted = ""
        for service in self.services:
            formatted += f"\n- {service.get('name', 'Unknown')}: {service.get('description', '')} (${service.get('price', 'N/A')}, {service.get('durationMinutes', 'N/A')} minutes)"
        
        return formatted
    
    def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get the current conversation context for debugging"""
        if session_id in self.sessions:
            return self.sessions[session_id]
        return {"error": "Session not found"}
    
    def end_session(self, session_id: str):
        """End a session and clean up"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            logger.info(f"Session {session_id} ended. Messages: {len(session['messages'])}")
            del self.sessions[session_id]
    
    async def process_message_async(
        self,
        user_message: str,
        session_id: str
    ) -> str:
        """Async version of process_message"""
        try:
            # Initialize or get session
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "messages": [],
                    "patient_name": None,
                    "patient_dob": None,
                    "selected_service": None,
                    "booking_date": None,
                    "booking_time": None,
                }
            
            session = self.sessions[session_id]
            session["messages"].append({
                "role": "user",
                "content": user_message
            })
            
            # Build system prompt
            system_prompt = self._build_system_prompt(session)
            
            # Get response from OpenAI
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *session["messages"]
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            assistant_message = response.choices[0].message.content.strip()
            
            # Store assistant response
            session["messages"].append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Limit conversation history
            max_history = int(os.getenv("MAX_CONVERSATION_LENGTH", 50))
            if len(session["messages"]) > max_history:
                session["messages"] = session["messages"][-max_history:]
            
            logger.info(f"Agent response (async): {assistant_message}")
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error processing message (async): {e}")
            return "I apologize, I'm having technical difficulties. Please try again."
