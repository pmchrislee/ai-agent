"""
Command-line interface for the AI Agent using Rich.

This module provides an interactive CLI with formatted output
and conversation management.
"""

import asyncio
import logging
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.markdown import Markdown

from agent import AIAgent
from utils.validators import validate_message, ValidationError

logger = logging.getLogger(__name__)


class CLIInterface:
    """Rich-based command-line interface for the AI Agent."""

    def __init__(self, agent: AIAgent, user_id: str = "cli-user"):
        """
        Initialize the CLI interface.

        Args:
            agent: The AIAgent instance to use
            user_id: User identifier for this CLI session
        """
        self.agent = agent
        self.user_id = user_id
        self.console = Console()
        self.running = False

        logger.info("CLI interface initialized")

    def _show_welcome(self):
        """Display welcome message."""
        welcome_text = f"""
# Welcome to {self.agent.name}!

Version: {self.agent.version}

I'm here to help you with:
- General conversation
- Weather information
- Jokes and humor
- And more!

Type 'help' for commands, or 'quit' to exit.
        """

        self.console.print(
            Panel(
                Markdown(welcome_text),
                title="🤖 AI Assistant",
                border_style="blue"
            )
        )
        self.console.print()

    def _show_help(self):
        """Display help information."""
        help_table = Table(title="Available Commands", show_header=True)
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")

        commands = [
            ("help", "Show this help message"),
            ("status", "Show agent status"),
            ("history", "Show conversation history"),
            ("clear", "Clear conversation history"),
            ("quit/exit", "Exit the application"),
        ]

        for cmd, desc in commands:
            help_table.add_row(cmd, desc)

        self.console.print(help_table)
        self.console.print()

        # Also show agent capabilities
        self.console.print(
            Panel(
                self.agent.response_gen.get_help_text(),
                title="💡 What I Can Do",
                border_style="green"
            )
        )
        self.console.print()

    def _show_status(self):
        """Display agent status."""
        status = self.agent.get_status()

        status_table = Table(show_header=False, box=None)
        status_table.add_column("Property", style="cyan")
        status_table.add_column("Value", style="white")

        status_table.add_row("Name", status['name'])
        status_table.add_row("Version", status['version'])
        status_table.add_row("Status", status['status'])
        status_table.add_row("Conversation Count", str(status['conversation_count']))
        status_table.add_row("Max History", str(status['max_history']))

        self.console.print(
            Panel(
                status_table,
                title="📊 Agent Status",
                border_style="yellow"
            )
        )
        self.console.print()

    def _show_history(self):
        """Display conversation history."""
        history = self.agent.get_conversation_history(user_id=self.user_id)

        if not history:
            self.console.print(
                "[yellow]No conversation history yet.[/yellow]\n"
            )
            return

        for entry in history[-10:]:  # Show last 10 entries
            # User message
            self.console.print(
                Panel(
                    entry['message'],
                    title=f"👤 You ({entry['timestamp'][:19]})",
                    border_style="blue"
                )
            )

            # Agent response
            self.console.print(
                Panel(
                    entry['response'],
                    title="🤖 Assistant",
                    border_style="green"
                )
            )
            self.console.print()

    def _clear_history(self):
        """Clear conversation history."""
        self.agent.clear_history(user_id=self.user_id)
        self.console.print(
            "[green]✓ Conversation history cleared.[/green]\n"
        )

    async def _handle_command(self, user_input: str) -> bool:
        """
        Handle special commands.

        Args:
            user_input: The user's input

        Returns:
            bool: True if command was handled, False otherwise
        """
        command = user_input.lower().strip()

        if command in ['quit', 'exit']:
            self.running = False
            return True

        elif command == 'help':
            self._show_help()
            return True

        elif command == 'status':
            self._show_status()
            return True

        elif command == 'history':
            self._show_history()
            return True

        elif command == 'clear':
            self._clear_history()
            return True

        return False

    async def _process_message(self, message: str):
        """
        Process and display a message response.

        Args:
            message: The user's message
        """
        try:
            # Validate message
            try:
                _, message = validate_message(message)
            except ValidationError as e:
                self.console.print(f"[red]Error: {e}[/red]\n")
                return

            # Show processing indicator
            with self.console.status("[bold blue]Thinking...", spinner="dots"):
                response = await self.agent.process_message(message, self.user_id)

            # Display response
            if response.get('type') == 'error':
                self.console.print(
                    Panel(
                        response['content'],
                        title="❌ Error",
                        border_style="red"
                    )
                )
            else:
                self.console.print(
                    Panel(
                        response['content'],
                        title="🤖 Assistant",
                        border_style="green"
                    )
                )
            self.console.print()

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            self.console.print(
                f"[red]An error occurred: {e}[/red]\n"
            )

    async def _run_loop(self):
        """Run the main conversation loop."""
        while self.running:
            try:
                # Get user input
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: Prompt.ask("\n[bold cyan]You[/bold cyan]")
                )

                if not user_input.strip():
                    continue

                # Check if it's a command
                is_command = await self._handle_command(user_input)

                if not is_command:
                    # Process as a regular message
                    await self._process_message(user_input)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted. Type 'quit' to exit.[/yellow]")
                continue
            except EOFError:
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in CLI loop: {e}", exc_info=True)
                self.console.print(f"[red]Error: {e}[/red]\n")

    async def start(self):
        """Start the CLI interface."""
        self.running = True

        try:
            self._show_welcome()
            await self._run_loop()

        except Exception as e:
            logger.error(f"CLI error: {e}", exc_info=True)
            self.console.print(f"[red]Fatal error: {e}[/red]")

        finally:
            self._show_goodbye()

    def _show_goodbye(self):
        """Display goodbye message."""
        self.console.print(
            Panel(
                "Thanks for chatting! Goodbye! 👋",
                title="🤖 AI Assistant",
                border_style="blue"
            )
        )
        self.console.print()
