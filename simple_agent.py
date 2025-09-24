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
        
        # Simple response logic
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            response = "Hello! How can I help you today?"
        elif "weather" in message_lower:
            response = "The weather is sunny and 22°C today! ☀️"
        elif "news" in message_lower:
            response = "Here are the latest headlines: AI technology advances, Climate research updates, and Tech industry growth."
        elif "joke" in message_lower:
            response = "Why don't scientists trust atoms? Because they make up everything! 😄"
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
