"""
Web interface for the AI Agent using Flask.

This module provides a REST API for interacting with the AI agent
through HTTP requests.
"""

import asyncio
import logging
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from agent import AIAgent
from config import Config
from utils.validators import validate_message, validate_user_id, ValidationError

logger = logging.getLogger(__name__)


class WebInterface:
    """Flask-based web interface for the AI Agent."""

    def __init__(self, agent: AIAgent):
        """
        Initialize the web interface.

        Args:
            agent: The AIAgent instance to use
        """
        self.agent = agent
        # Configure Flask to use templates from project root
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
        self.app = Flask(__name__, template_folder=template_dir)

        # Configure CORS
        CORS(self.app, origins=Config.get_cors_origins())

        # Register routes
        self._register_routes()

        logger.info("Web interface initialized")

    def _register_routes(self):
        """Register Flask routes."""

        @self.app.route('/', methods=['GET'])
        def index():
            """Serve the main web interface."""
            status = self.agent.get_status()
            return render_template(
                'index.html',
                agent_name=status.get('name', 'AI Assistant'),
                agent_version=status.get('version', '2.0.0')
            )

        @self.app.route('/api/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "agent": self.agent.get_status()
            })

        @self.app.route('/api/status', methods=['GET'])
        def status():
            """Get agent status."""
            return jsonify(self.agent.get_status())

        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """
            Process a chat message.

            Expected JSON body:
            {
                "message": "User's message",
                "user_id": "optional-user-id",
                "location": {
                    "lat": latitude,
                    "lon": longitude,
                    "city": "optional city name"
                },
                "context": {
                    "type": "weather|news|joke",
                    "lastMessage": "previous message"
                }
            }
            """
            try:
                # Get request data
                data = request.get_json()

                if not data:
                    return jsonify({
                        "error": "Invalid JSON body"
                    }), 400

                message = data.get('message', '')
                user_id = data.get('user_id', 'default')
                location = data.get('location')  # Optional location data
                context = data.get('context')  # Optional conversation context

                # Validate inputs
                try:
                    _, message = validate_message(message)
                    _, user_id = validate_user_id(user_id)
                except ValidationError as e:
                    return jsonify({
                        "error": str(e)
                    }), 400

                # Process message using asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(
                        self.agent.process_message(message, user_id, location=location, context=context)
                    )
                finally:
                    loop.close()

                return jsonify(response)

            except Exception as e:
                logger.error(f"Error in chat endpoint: {e}", exc_info=True)
                return jsonify({
                    "error": "Internal server error",
                    "message": str(e)
                }), 500

        @self.app.route('/api/history', methods=['GET'])
        def history():
            """
            Get conversation history.

            Query parameters:
            - user_id: Optional filter by user ID
            - limit: Optional limit number of entries
            """
            try:
                user_id = request.args.get('user_id')
                limit = request.args.get('limit', type=int)

                # Validate user_id if provided
                if user_id:
                    try:
                        _, user_id = validate_user_id(user_id)
                    except ValidationError as e:
                        return jsonify({
                            "error": str(e)
                        }), 400

                history_data = self.agent.get_conversation_history(
                    user_id=user_id,
                    limit=limit
                )

                return jsonify({
                    "history": history_data,
                    "count": len(history_data)
                })

            except Exception as e:
                logger.error(f"Error in history endpoint: {e}", exc_info=True)
                return jsonify({
                    "error": "Internal server error"
                }), 500

        @self.app.route('/api/history', methods=['DELETE'])
        def clear_history():
            """
            Clear conversation history.

            Query parameters:
            - user_id: Optional clear only for specific user
            """
            try:
                user_id = request.args.get('user_id')

                # Validate user_id if provided
                if user_id:
                    try:
                        _, user_id = validate_user_id(user_id)
                    except ValidationError as e:
                        return jsonify({
                            "error": str(e)
                        }), 400

                self.agent.clear_history(user_id=user_id)

                return jsonify({
                    "message": "History cleared successfully",
                    "user_id": user_id if user_id else "all"
                })

            except Exception as e:
                logger.error(f"Error clearing history: {e}", exc_info=True)
                return jsonify({
                    "error": "Internal server error"
                }), 500

        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors."""
            return jsonify({
                "error": "Endpoint not found"
            }), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors."""
            logger.error(f"Internal server error: {error}", exc_info=True)
            return jsonify({
                "error": "Internal server error"
            }), 500

    def run(self, host: str = None, port: int = None, debug: bool = None):
        """
        Run the Flask web server.

        Args:
            host: Host to bind to (defaults to Config.WEB_HOST)
            port: Port to bind to (defaults to Config.WEB_PORT)
            debug: Debug mode (defaults to Config.DEBUG)
        """
        host = host or Config.WEB_HOST
        port = port or Config.WEB_PORT
        debug = debug if debug is not None else Config.DEBUG

        logger.info(f"Starting web server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")

        self.app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # Disable reloader to avoid issues with async
        )
