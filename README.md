# AI Agent v2.0 - Refactored & Production Ready

A sophisticated AI assistant with multi-interface support (CLI and Web), now fully refactored with proper architecture, testing, and production-ready code.

## 🌐 Live Demo

Visit the static version at: [https://pmchrislee.github.io/ai-agent/](https://pmchrislee.github.io/ai-agent/)

## ✨ Features

### Core Features
- **Multi-Interface Support**: CLI and Web (Flask REST API)
- **Sophisticated Response System**: Pattern-matching with extensible handlers
- **Conversation Management**: History tracking with configurable limits
- **Input Validation**: Comprehensive validation and sanitization
- **Configuration Management**: Environment variable support
- **Comprehensive Logging**: Structured logging with configurable levels
- **Production Ready**: Error handling, testing, and proper async support

### Response Capabilities
- **Weather Information**: Realistic weather conditions with temperatures
- **Weather Jokes**: Meteorological humor with sophisticated wordplay
- **General Jokes**: Clever puns and humor
- **Greetings**: Friendly conversation starters
- **Help System**: Interactive help and command reference

## 🏗️ Architecture

The project is now organized into a modular, maintainable structure:

```
ai_agent/
├── agent/                    # Core agent logic
│   ├── __init__.py
│   ├── base.py              # AIAgent class
│   └── responses.py         # Response data and generator
├── interfaces/              # User interfaces
│   ├── __init__.py
│   ├── cli.py              # Rich-based CLI
│   └── web.py              # Flask REST API
├── utils/                   # Utilities
│   ├── __init__.py
│   ├── logger.py           # Logging setup
│   └── validators.py       # Input validation
├── static/                  # Static web assets
│   ├── css/
│   │   └── main.css        # Stylesheet
│   ├── js/
│   │   └── agent.js        # Client-side logic
│   └── data/
│       └── responses.json  # Response data
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_config.py
│   └── test_validators.py
├── config.py               # Configuration management
├── main.py                 # Entry point
├── index.html              # Static GitHub Pages version
├── requirements.txt        # Python dependencies
├── pytest.ini              # Test configuration
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/pmchrislee/ai-agent.git
cd ai-agent
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment (optional)**
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### Running the Application

#### CLI Mode
```bash
python main.py cli
```

Features:
- Interactive conversation interface
- Rich formatting with colors and panels
- Command support (help, status, history, clear, quit)
- Real-time response generation

#### Web API Mode
```bash
python main.py web
```

The API will be available at `http://localhost:8080`

API Endpoints:
- `GET /api/health` - Health check
- `GET /api/status` - Get agent status
- `POST /api/chat` - Send a message
- `GET /api/history` - Get conversation history
- `DELETE /api/history` - Clear history

Example API request:
```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a joke", "user_id": "user123"}'
```

### Static GitHub Pages Version

Simply open `index.html` in your browser or serve it:

```bash
python -m http.server 8000
# Visit http://localhost:8000
```

## ⚙️ Configuration

Configure the application using environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_NAME` | AI Assistant | Name of the agent |
| `AGENT_VERSION` | 2.0.0 | Version string |
| `WEB_HOST` | 0.0.0.0 | Web server host |
| `WEB_PORT` | 8080 | Web server port |
| `DEBUG` | False | Debug mode |
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CORS_ORIGINS` | * | Allowed CORS origins |
| `MAX_MESSAGE_LENGTH` | 5000 | Maximum message length |
| `MAX_CONVERSATION_HISTORY` | 1000 | Maximum history entries |

Example:
```bash
WEB_PORT=5000 DEBUG=true LOG_LEVEL=DEBUG python main.py web
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent --cov=interfaces --cov=utils

# Run specific test file
pytest tests/test_agent.py

# Run with verbose output
pytest -v
```

Test coverage includes:
- Agent core functionality
- Message processing and handlers
- Conversation history management
- Input validation
- Configuration management
- Response generation

## 📡 API Reference

### POST /api/chat

Send a message to the agent.

**Request:**
```json
{
  "message": "What's the weather like?",
  "user_id": "user123"  // optional, defaults to "default"
}
```

**Response:**
```json
{
  "content": "It's a beautiful sunny day at 78°F!",
  "type": "chat",
  "timestamp": "2024-01-15T10:30:00.000000",
  "user_id": "user123"
}
```

### GET /api/history

Retrieve conversation history.

**Query Parameters:**
- `user_id` (optional): Filter by user ID
- `limit` (optional): Limit number of entries

**Response:**
```json
{
  "history": [
    {
      "timestamp": "2024-01-15T10:30:00.000000",
      "user_id": "user123",
      "message": "Hello",
      "response": "Hello! How can I help you today?"
    }
  ],
  "count": 1
}
```

### GET /api/status

Get agent status.

**Response:**
```json
{
  "name": "AI Assistant",
  "version": "2.0.0",
  "status": "idle",
  "conversation_count": 42,
  "max_history": 1000
}
```

## 🎨 Refactoring Highlights

### What Was Improved

1. **Code Duplication Eliminated**
   - Consolidated duplicate `SimpleAIAgent` classes from `main.py` and `simple_agent.py`
   - Created single unified `AIAgent` base class
   - Extracted response data into separate module

2. **Proper Architecture**
   - Separated concerns: agent logic, interfaces, utilities
   - Modular structure with clear responsibilities
   - Extensible handler pattern for message processing

3. **Async/Sync Fixed**
   - Proper async handling in Flask with `asyncio.run_until_complete`
   - No more incompatible async Flask routes
   - Clean event loop management

4. **Input Validation & Security**
   - Comprehensive input validation with `ValidationError` exceptions
   - HTML sanitization to prevent XSS
   - User ID validation with character restrictions
   - Message length limits

5. **Configuration Management**
   - Environment variable support with `.env`
   - Validation of configuration values
   - Centralized config with `Config` class

6. **Logging & Error Handling**
   - Structured logging with configurable levels
   - Proper exception handling throughout
   - Informative error messages

7. **Testing**
   - Comprehensive test suite with pytest
   - Tests for agent, validators, and config
   - Async test support with pytest-asyncio

8. **Static Site Improvements**
   - Separated CSS, JavaScript, and data
   - Response data in JSON file
   - Cleaner, more maintainable code

## 📝 Usage Examples

### CLI Examples

```bash
# Start CLI
python main.py cli

# In the CLI:
> Hello
> Tell me a joke
> What's the weather like?
> Tell me a weather joke
> help
> status
> history
> quit
```

### Python API Usage

```python
from agent import AIAgent
import asyncio

# Create agent
agent = AIAgent(name="My Agent", max_history=500)

# Process message
async def chat():
    response = await agent.process_message("Hello!", "user123")
    print(response["content"])

asyncio.run(chat())

# Get status
status = agent.get_status()
print(f"Agent: {status['name']} v{status['version']}")

# Get history
history = agent.get_conversation_history(user_id="user123", limit=10)
```

## 🔧 Development

### Adding New Response Handlers

To add a new response type:

1. Add response data in `agent/responses.py`
2. Add generator method in `ResponseGenerator` class
3. Add handler in `AIAgent._init_handlers()` method

Example:
```python
# In agent/responses.py
CUSTOM_RESPONSES = ["Response 1", "Response 2"]

# In ResponseGenerator
@staticmethod
def get_custom_response():
    return random.choice(CUSTOM_RESPONSES)

# In AIAgent._init_handlers()
MessageHandler(
    keywords=['custom', 'keyword'],
    handler=lambda msg: self.response_gen.get_custom_response(),
    require_all=False
)
```

### Code Quality

```bash
# Format code (if black is installed)
black agent/ interfaces/ utils/ tests/

# Lint code (if flake8 is installed)
flake8 agent/ interfaces/ utils/

# Type checking (if mypy is installed)
mypy agent/ interfaces/ utils/
```

## 🎭 Example Interactions

**Weather:**
```
You: What's the weather like?
Agent: It's a beautiful sunny day at 78°F! Perfect weather for outdoor activities! ☀️
```

**Weather Joke:**
```
You: Tell me a weather joke
Agent: Why do clouds never get lonely? Because they're always in good company -
they're quite the cumulus crowd! Currently 77°F with scattered wit! ☁️😏
```

**General Joke:**
```
You: Tell me a joke
Agent: Why don't scientists trust atoms? Because they make up everything -
it's elementary, my dear Watson! ⚛️🔬
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Version 2.0.0** - Comprehensive refactoring with production-ready architecture
