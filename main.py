#!/usr/bin/env python3
"""
Simple AI Agent - Ready to Run!
"""
import asyncio
import sys
from datetime import datetime

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

class WebInterface:
    def __init__(self, agent, config):
        self.agent = agent
        self.config = config
        self.app = None
        self._setup_flask()
    
    def _setup_flask(self):
        """Setup Flask web interface"""
        try:
            from flask import Flask, render_template, request, jsonify
            from flask_cors import CORS
            
            self.app = Flask(__name__, 
                            template_folder='templates',
                            static_folder='static')
            CORS(self.app)
            self._setup_routes()
            print("✅ Flask web interface ready")
        except ImportError:
            print("❌ Flask not installed. Run: pip install flask")
            self.app = None
    
    def _setup_routes(self):
        """Setup Flask routes"""
        from flask import render_template, request, jsonify
        
        @self.app.route('/')
        def index():
            return render_template('index.html', 
                                 agent_name=self.agent.name,
                                 agent_version=self.agent.version)
        
        @self.app.route('/api/chat', methods=['POST'])
        async def chat():
            try:
                data = request.get_json()
                message = data.get('message', '')
                user_id = data.get('user_id', 'web_user')
                
                if not message:
                    return jsonify({'error': 'No message provided'}), 400
                
                response = await self.agent.process_message(message, user_id)
                return jsonify(response)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/status')
        def status():
            return jsonify(self.agent.get_status())
        
        @self.app.route('/api/history')
        def history():
            user_id = request.args.get('user_id', 'web_user')
            limit = int(request.args.get('limit', 10))
            history = self.agent.get_conversation_history(user_id, limit)
            return jsonify(history)
    
    async def start(self):
        """Start the web interface"""
        if not self.app:
            print("❌ Cannot start web interface - Flask not available")
            return
        
        print(f"🚀 Starting web interface on {self.config['WEB_HOST']}:{self.config['WEB_PORT']}")
        print(f"📱 Open your browser to: http://localhost:{self.config['WEB_PORT']}")
        
        # Run Flask in a separate thread
        import threading
        flask_thread = threading.Thread(
            target=self.app.run,
            kwargs={
                'host': self.config['WEB_HOST'],
                'port': self.config['WEB_PORT'],
                'debug': self.config['DEBUG'],
                'use_reloader': False
            }
        )
        flask_thread.daemon = True
        flask_thread.start()
        
        # Keep the main thread alive
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Web interface stopped")

class CLIInterface:
    def __init__(self, agent):
        self.agent = agent
        self.running = False
        self._setup_rich()
    
    def _setup_rich(self):
        """Setup Rich console"""
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.prompt import Prompt, Confirm
            self.console = Console()
            self.Prompt = Prompt
            self.Confirm = Confirm
            self.Panel = Panel
            print("✅ Rich CLI interface ready")
        except ImportError:
            print("❌ Rich not installed. Run: pip install rich")
            self.console = None
    
    async def start(self):
        """Start the CLI interface"""
        if not self.console:
            print("❌ Cannot start CLI interface - Rich not available")
            return
        
        self.console.print(self.Panel.fit(
            f"[bold blue]🤖 {self.agent.name} v{self.agent.version}[/bold blue]\n"
            f"[green]AI Agent CLI Interface[/green]\n"
            f"Type 'help' for commands or 'quit' to exit",
            title="Welcome"
        ))
        
        self.running = True
        
        while self.running:
            try:
                user_input = self.Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    if self.Confirm.ask("Are you sure you want to quit?"):
                        self.running = False
                        break
                
                elif user_input.lower() == 'help':
                    self._show_help()
                
                elif user_input.lower() == 'status':
                    self._show_status()
                
                elif user_input.lower() == 'history':
                    self._show_history()
                
                elif user_input.lower() == 'clear':
                    self._clear_history()
                
                else:
                    await self._process_message(user_input)
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'quit' to exit properly[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")
        
        self.console.print("[green]Goodbye! 👋[/green]")
    
    async def _process_message(self, message: str):
        """Process a user message"""
        try:
            with self.console.status("[bold green]Thinking..."):
                response = await self.agent.process_message(message)
            
            self._display_response(response)
            
        except Exception as e:
            self.console.print(f"[red]Error processing message: {str(e)}[/red]")
    
    def _display_response(self, response):
        """Display agent response"""
        content = response.get("content", "No response")
        response_type = response.get("type", "unknown")
        
        color = "red" if response_type == "error" else "white"
        
        self.console.print(self.Panel(
            f"[{color}]{content}[/{color}]",
            title=f"[bold]🤖 {self.agent.name}[/bold]",
            border_style=color
        ))
    
    def _show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
• help     - Show this help message
• status   - Show agent status
• history  - Show conversation history
• clear    - Clear conversation history
• quit     - Exit the CLI

You can also just type messages to chat with the agent!
        """
        self.console.print(self.Panel(help_text, title="[bold]Help[/bold]"))
    
    def _show_status(self):
        """Show agent status"""
        status = self.agent.get_status()
        
        from rich.table import Table
        table = Table(title="Agent Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Name", status["name"])
        table.add_row("Version", status["version"])
        table.add_row("Status", status["status"])
        table.add_row("Memory Size", str(status["memory_size"]))
        
        self.console.print(table)
    
    def _show_history(self):
        """Show conversation history"""
        history = self.agent.get_conversation_history(limit=5)
        
        if not history:
            self.console.print("[yellow]No conversation history found.[/yellow]")
            return
        
        for item in history:
            self.console.print(f"\n[dim]{item['timestamp']}[/dim]")
            self.console.print(f"[cyan]You:[/cyan] {item['message']}")
            self.console.print(f"[green]Agent:[/green] {item['response']}")
    
    def _clear_history(self):
        """Clear conversation history"""
        if self.Confirm.ask("Are you sure you want to clear the conversation history?"):
            self.agent.conversation_history = []
            self.console.print("[green]Conversation history cleared.[/green]")

async def main():
    """Main entry point"""
    try:
        # Initialize the AI Agent
        agent = SimpleAIAgent()
        
        # Default configuration
        config = {
            'WEB_HOST': '0.0.0.0',
            'WEB_PORT': 8080,
            'DEBUG': False
        }
        
        # Check command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode == "cli":
                # Start CLI interface
                cli = CLIInterface(agent)
                await cli.start()
                
            elif mode == "web":
                # Start web interface
                web = WebInterface(agent, config)
                await web.start()
                
            else:
                print(f"Unknown mode: {mode}")
                print("Available modes: cli, web")
                sys.exit(1)
        else:
            # Default: start web interface
            print("🤖 Starting AI Agent...")
            print("Available modes:")
            print("  python3 main.py cli  - Command Line Interface")
            print("  python3 main.py web  - Web Interface")
            print("\nStarting web interface by default...")
            
            web = WebInterface(agent, config)
            await web.start()
            
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
