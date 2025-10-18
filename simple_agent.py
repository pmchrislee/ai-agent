#!/usr/bin/env python3
"""
Simple AI Agent - Working Version
"""
import asyncio
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

class SimpleAIAgent:
    def __init__(self):
        self.name = "AI Assistant"
        self.version = "1.0.0"
        self.status = "idle"
        self.conversation_history = []
    
    async def process_message(self, message: str, user_id: str = "default"):
        """Process a user message and return a response"""
        self.status = "processing"
        
        # Enhanced response logic with better keyword detection
        message_lower = message.lower()
        
        # Check for combined requests first
        if "weather" in message_lower and "joke" in message_lower:
            response = self._get_weather_joke()
        elif "weather" in message_lower:
            response = self._get_weather_info()
        elif "joke" in message_lower:
            response = self._get_general_joke()
        elif "hello" in message_lower or "hi" in message_lower:
            response = "Hello! How can I help you today?"
        elif "news" in message_lower:
            response = "Here are the latest headlines: AI technology advances, Climate research updates, and Tech industry growth."
        elif "help" in message_lower:
            response = "I can help with weather, news, jokes, or just chat! What would you like to know?"
        else:
            response = f"I understand you said: '{message}'. How can I assist you further?"
        
        # Store in history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "message": message,
            "response": response
        })
        
        self.status = "idle"
        return {
            "content": response,
            "type": "chat",
            "metadata": {"confidence": 0.8}
        }
    
    def get_status(self):
        """Get current agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "memory_size": len(self.conversation_history),
            "uptime": datetime.now().isoformat()
        }
    
    def get_conversation_history(self, user_id: str = "default", limit: int = 10):
        """Get conversation history for a user"""
        user_history = [h for h in self.conversation_history if h["user_id"] == user_id]
        return user_history[-limit:]
    
    def _get_weather_joke(self):
        """Get a sophisticated weather-related joke with temperature in Fahrenheit"""
        import random
        
        weather_jokes = [
            "The meteorologist's favorite type of music? Heavy metal - especially when it's hailing! Today's forecast: 74°F with a 90% chance of sophisticated wordplay! 🎵⚡",
            "Why do clouds never get lonely? Because they're always in good company - they're quite the cumulus crowd! Currently 77°F with scattered wit and variable humor! ☁️😏",
            "What did the barometric pressure say to the thermometer? 'I'm feeling quite under pressure today, but you seem to be rising to the occasion!' It's 72°F with high-pressure humor! 📊🌡️",
            "The wind's favorite type of literature? Gust-ave Flaubert novels, naturally! Today's reading: 79°F with light winds and a chance of literary references! 📚💨",
            "Why did the dew point become a philosopher? Because it was always questioning the humidity of existence! Current conditions: 75°F with existential clarity! 🤔💧",
            "What's a tornado's favorite dance? The twist, obviously - though it prefers to waltz through the countryside! Today's forecast: 73°F with a chance of meteorological metaphors! 🌪️💃"
        ]
        
        return random.choice(weather_jokes)
    
    def _get_weather_info(self):
        """Get current weather information in Fahrenheit"""
        import random
        
        # Simulate different weather conditions with Fahrenheit temperatures
        weather_conditions = [
            "It's a beautiful sunny day at 78°F! Perfect weather for outdoor activities! ☀️",
            "Currently 72°F with partly cloudy skies and a gentle breeze. Great day to be outside! 🌤️",
            "The temperature is 75°F with clear skies. Ideal weather for a walk in the park! ☀️",
            "It's 80°F and sunny with low humidity. A perfect summer day! ☀️",
            "Currently 68°F with some clouds rolling in. Pleasant weather for the afternoon! ☁️",
            "The temperature is 82°F with bright sunshine. Don't forget your sunscreen! ☀️🧴"
        ]
        
        return random.choice(weather_conditions)
    
    def _get_general_joke(self):
        """Get a sophisticated joke with clever wordplay"""
        import random
        
        general_jokes = [
            "I told my wife she was drawing her eyebrows too high. She looked surprised. 🎭",
            "Why don't scientists trust atoms? Because they make up everything - it's elementary, my dear Watson! ⚛️🔬",
            "I'm reading a book about anti-gravity. It's impossible to put down! 📚⬆️",
            "What do you call a can opener that doesn't work? A can't opener! 🥫🔧",
            "I used to be a baker, but I couldn't make enough dough. Now I'm a banker - the interest is much better! 🥖💰",
            "Why did the math book look so sad? Because it had too many problems! 📖😢",
            "What do you call a fish wearing a bowtie? So-fish-ticated! 🐟🎀",
            "I told my computer I needed a break, and now it won't stop sending me Kit-Kat ads! 💻🍫",
            "Why don't oysters donate to charity? Because they are shellfish! 🦪💸",
            "What do you call a bear with no teeth? A gummy bear - though I prefer the sour variety! 🐻🍬"
        ]
        
        return random.choice(general_jokes)

# Initialize the agent
agent = SimpleAIAgent()

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html', 
                         agent_name=agent.name,
                         agent_version=agent.version)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'web_user')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(agent.process_message(message, user_id))
        loop.close()
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    return jsonify(agent.get_status())

@app.route('/api/history')
def history():
    user_id = request.args.get('user_id', 'web_user')
    limit = int(request.args.get('limit', 10))
    history = agent.get_conversation_history(user_id, limit)
    return jsonify(history)

if __name__ == "__main__":
    print("🤖 Starting AI Agent...")
    print("📱 Web interface will be available at: http://localhost:8080")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")
