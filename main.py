#!/usr/bin/env python3
"""
AI Agent - Multi-interface conversational assistant.

This is the main entry point for the AI Agent application. It supports
both CLI and web interfaces with proper configuration management, logging,
and error handling.

Usage:
    Run CLI interface:
        python main.py cli

    Run web interface:
        python main.py web

    Run with custom config:
        WEB_PORT=5000 DEBUG=true python main.py web
"""

import sys
import asyncio
import logging

from agent import AIAgent
from interfaces import WebInterface, CLIInterface
from config import Config
from utils import setup_logging

logger = logging.getLogger(__name__)


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════╗
    ║         AI Agent v2.0.0               ║
    ║   Refactored & Production Ready       ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)


def print_usage():
    """Print usage information."""
    usage = """
Usage: python main.py [mode]

Modes:
    cli     Launch interactive command-line interface
    web     Launch web server with REST API

Environment Variables:
    AGENT_NAME                 Agent name (default: AI Assistant)
    AGENT_VERSION             Agent version (default: 2.0.0)
    WEB_HOST                  Web server host (default: 0.0.0.0)
    WEB_PORT                  Web server port (default: 8080)
    DEBUG                     Debug mode (default: False)
    LOG_LEVEL                 Logging level (default: INFO)
    MAX_MESSAGE_LENGTH        Max message length (default: 5000)
    MAX_CONVERSATION_HISTORY  Max history entries (default: 1000)

Examples:
    # Run CLI interface
    python main.py cli

    # Run web server on custom port
    WEB_PORT=5000 python main.py web

    # Run in debug mode with verbose logging
    DEBUG=true LOG_LEVEL=DEBUG python main.py web
    """
    print(usage)


async def run_cli():
    """Run the CLI interface."""
    logger.info("Starting CLI mode")

    # Create agent and interface
    agent = AIAgent(
        name=Config.AGENT_NAME,
        version=Config.AGENT_VERSION,
        max_history=Config.MAX_CONVERSATION_HISTORY
    )
    cli = CLIInterface(agent)

    # Start CLI
    await cli.start()


def run_web():
    """Run the web interface."""
    logger.info("Starting web mode")

    # Create agent and interface
    agent = AIAgent(
        name=Config.AGENT_NAME,
        version=Config.AGENT_VERSION,
        max_history=Config.MAX_CONVERSATION_HISTORY
    )
    web = WebInterface(agent)

    # Start web server
    web.run()


def main():
    """Main entry point."""
    print_banner()

    # Set up logging
    setup_logging()

    # Validate configuration
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
        logger.debug(f"Config summary: {Config.summary()}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nConfiguration Error: {e}\n")
        sys.exit(1)

    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("\nError: No mode specified.\n")
        print_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()

    try:
        if mode == 'cli':
            # Run CLI in async context
            asyncio.run(run_cli())

        elif mode == 'web':
            # Run web server
            run_web()

        else:
            print(f"\nError: Unknown mode '{mode}'\n")
            print_usage()
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n\nShutting down gracefully...\n")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal Error: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
