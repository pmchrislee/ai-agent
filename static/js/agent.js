/**
 * Static AI Agent - Client-side conversational AI
 *
 * This class handles message processing, conversation management,
 * and response generation for the GitHub Pages static version.
 */

// Known location coordinates for better accuracy with wttr.in API
const LOCATION_COORDINATES = {
    "queens,ny": "40.7282,-73.7949",
    "queens": "40.7282,-73.7949",
    "new york,ny": "40.7128,-74.0060",  // Manhattan coordinates
    "new york": "40.7128,-74.0060",
    "manhattan,ny": "40.7831,-73.9712",
    "manhattan": "40.7831,-73.9712",
    "brooklyn,ny": "40.6782,-73.9442",
    "brooklyn": "40.6782,-73.9442",
    "bronx,ny": "40.8448,-73.8648",
    "bronx": "40.8448,-73.8648",
    "staten island,ny": "40.5795,-74.1502",
    "staten island": "40.5795,-74.1502",
};

class StaticAIAgent {
    constructor() {
        this.messageCount = 0;
        this.conversationHistory = [];
        this.isLoading = false;
        this.responses = null;

        // Load response data
        this.loadResponses().then(() => {
            this.initializeEventListeners();
            this.updateStats();
        });
    }

    /**
     * Load response data from JSON file
     */
    async loadResponses() {
        try {
            const response = await fetch('static/data/responses.json');
            this.responses = await response.json();
        } catch (error) {
            console.error('Error loading responses:', error);
            // Fallback to basic responses
            this.responses = {
                weatherJokes: ["It's a joke about weather! 🌤️"],
                weatherConditions: ["It's nice outside! ☀️"],
                generalJokes: ["Why did the chicken cross the road? To get to the other side! 🐔"],
                greetings: ["Hello! How can I help you today?"],
                newsResponses: ["I don't have access to real-time news."],
                helpText: "I can help with weather, news, jokes, or just chat!"
            };
        }
    }

    /**
     * Initialize event listeners for user interactions
     */
    initializeEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendButton.addEventListener('click', () => this.sendMessage());

        document.getElementById('clearButton').addEventListener('click', () => this.clearChat());
        document.getElementById('historyButton').addEventListener('click', () => this.showHistory());
        document.getElementById('statusButton').addEventListener('click', () => this.showStatus());

        document.querySelectorAll('.quick-action').forEach(button => {
            button.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    /**
     * Send a message and get a response
     */
    sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message || this.isLoading) return;

        this.addMessage(message, 'user');
        messageInput.value = '';

        this.setLoading(true);

        // Process message (may be async for weather requests)
        (async () => {
            try {
                const response = await this.processMessage(message);
                this.addMessage(response, 'agent');
                this.setLoading(false);
                this.messageCount++;
                this.updateStats();
            } catch (error) {
                console.error('Error processing message:', error);
                this.addMessage('Sorry, I encountered an error processing your message. Please try again.', 'agent');
                this.setLoading(false);
            }
        })();
    }

    /**
     * Format location name for display
     * @param {string} location - Location string (e.g., "queens,ny")
     * @returns {string} - Formatted location name (e.g., "Queens, NY")
     */
    formatLocationName(location) {
        // Map of known locations to their display names
        const locationNames = {
            "queens,ny": "Queens, NY",
            "queens": "Queens, NY",
            "new york,ny": "New York, NY",
            "new york": "New York, NY",
            "manhattan,ny": "Manhattan, NY",
            "manhattan": "Manhattan, NY",
            "brooklyn,ny": "Brooklyn, NY",
            "brooklyn": "Brooklyn, NY",
            "bronx,ny": "Bronx, NY",
            "bronx": "Bronx, NY",
            "staten island,ny": "Staten Island, NY",
            "staten island": "Staten Island, NY",
        };
        
        const locationLower = location.toLowerCase().trim();
        if (locationNames[locationLower]) {
            return locationNames[locationLower];
        }
        
        // Otherwise, capitalize properly
        return location.split(',').map(part => {
            return part.trim().split(' ').map(word => {
                return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
            }).join(' ');
        }).join(', ');
    }

    /**
     * Parse location from a user message
     * @param {string} message - The user's message
     * @returns {string|null} - Parsed location or null
     */
    parseLocation(message) {
        const messageLower = message.toLowerCase();
        
        // Patterns to match location - improved to handle commas and state abbreviations
        const patterns = [
            // Match "What's the weather in [location]?" or "weather in [location]"
            // This handles: "What's the weather in Queens, NY?" or "weather in Queens, NY"
            /(?:what'?s|what|tell|show|get).*?weather\s+(?:in|at|for)\s+([^?!]*?)(?:\s+(?:weather|joke)|[?!]|$)/i,
            // Match "weather in/at/for [location]" - capture everything until end or weather/joke keyword
            /weather\s+(?:in|at|for)\s+([^?!]*?)(?:\s+(?:weather|joke)|[?!]|$)/i,
            // Match "[location] weather" - capture everything before "weather"
            /(.+?)\s+weather/i,
            // Match "weather in/at/for [location]" to end of string
            /weather\s+(?:in|at|for)\s+(.+?)$/i
        ];
        
        for (const pattern of patterns) {
            const match = messageLower.match(pattern);
            if (match) {
                let location = match[1].trim();
                // Clean up common words
                location = location.replace(/\s+(weather|joke|like|today|now|current)/gi, '').trim();
                
                // Remove trailing punctuation
                location = location.replace(/[.,!?]+$/, '');
                
                // Normalize location format: "Queens, NY" -> "Queens,NY" for API compatibility
                location = location.replace(/,\s+/g, ',');
                
                // Skip if location is too short or common words
                if (location.length > 2 && !['the', 'a', 'an', 'what', 'how', 'tell', 'me', 'is', 'it'].includes(location)) {
                    return location;
                }
            }
        }
        
        return null;
    }

    /**
     * Process a message and generate a response
     * @param {string} message - The user's message
     * @returns {Promise<string>} - The generated response
     */
    async processMessage(message) {
        const messageLower = message.toLowerCase();

        // Check for combined requests first (most specific)
        if (messageLower.includes('weather') && messageLower.includes('joke')) {
            const location = this.parseLocation(message);
            return await this.getWeatherJoke(location);
        } else if (messageLower.includes('weather')) {
            const location = this.parseLocation(message);
            return await this.getWeatherInfo(location);
        } else if (messageLower.includes('joke')) {
            return this.getGeneralJoke();
        } else if (messageLower.includes('hello') || messageLower.includes('hi')) {
            return this.getGreeting();
        } else if (messageLower.includes('news')) {
            return this.getNewsResponse();
        } else if (messageLower.includes('help')) {
            return this.responses.helpText;
        } else {
            return `I understand you said: '${message}'. How can I assist you further?`;
        }
    }

    /**
     * Get a weather joke with real weather data
     * @param {string|null} location - Location to get weather for (default: Queens, NY)
     */
    async getWeatherJoke(location = null) {
        try {
            // Default to Queens, NY if no location specified
            let locationQuery = location ? location.toLowerCase().trim() : 'queens,ny';
            let displayLocation = location ? this.formatLocationName(location) : 'Queens, NY';
            
            // Check if we have coordinates for this location
            if (LOCATION_COORDINATES[locationQuery]) {
                locationQuery = LOCATION_COORDINATES[locationQuery];
            } else {
                // Capitalize first letter of each word for better API recognition
                // "queens,ny" -> "Queens,NY"
                locationQuery = locationQuery.split(',').map(part => {
                    return part.trim().split(' ').map(word => {
                        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
                    }).join(' ');
                }).join(',');
                displayLocation = locationQuery;
            }
            
            // Use wttr.in API (free, no API key required)
            // wttr.in accepts coordinates in format: lat,lon
            const response = await fetch(`https://wttr.in/${encodeURIComponent(locationQuery)}?format=j1`);
            
            if (!response.ok) {
                throw new Error(`Weather API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            const current = data.current_condition[0];
            const tempF = current.temp_F;
            const condition = current.weatherDesc[0].value;
            // Use the requested location name instead of API's returned location
            const locationName = displayLocation;
            
            // Weather emoji mapping
            const emojiMap = {
                'Clear': '☀️',
                'Sunny': '☀️',
                'Partly cloudy': '⛅',
                'Cloudy': '☁️',
                'Overcast': '☁️',
                'Rain': '🌧️',
                'Light rain': '🌦️',
                'Heavy rain': '🌧️',
                'Thunderstorm': '⛈️',
                'Snow': '❄️',
                'Mist': '🌫️',
                'Fog': '🌫️'
            };
            
            let emoji = '🌤️';
            for (const [key, value] of Object.entries(emojiMap)) {
                if (condition.toLowerCase().includes(key.toLowerCase())) {
                    emoji = value;
                    break;
                }
            }
            
            const jokes = [
                `The meteorologist's favorite type of music? Heavy metal - especially when it's hailing! Currently in ${locationName}: ${tempF}°F with ${condition.toLowerCase()}! ${emoji}`,
                `Why do clouds never get lonely? Because they're always in good company - they're quite the cumulus crowd! Right now in ${locationName} it's ${tempF}°F with ${condition.toLowerCase()}! ${emoji}`,
                `What did the barometric pressure say to the thermometer? 'I'm feeling quite under pressure today, but you seem to be rising to the occasion!' In ${locationName}: ${tempF}°F with ${condition.toLowerCase()}! ${emoji}`,
                `The wind's favorite type of literature? Gust-ave Flaubert novels, naturally! Today in ${locationName}: ${tempF}°F with ${condition.toLowerCase()} and light winds! ${emoji}`,
                `Why did the dew point become a philosopher? Because it was always questioning the humidity of existence! Current conditions in ${locationName}: ${tempF}°F with ${condition.toLowerCase()}! ${emoji}`,
                `What's a tornado's favorite dance? The twist, obviously! But don't worry, in ${locationName} it's just ${tempF}°F with ${condition.toLowerCase()}! ${emoji}`
            ];
            
            return jokes[Math.floor(Math.random() * jokes.length)];
        } catch (error) {
            console.error('Error fetching weather:', error);
            // Fallback to static response
            return this.responses.weatherJokes[
                Math.floor(Math.random() * this.responses.weatherJokes.length)
            ];
        }
    }

    /**
     * Get real weather information for a location
     * @param {string|null} location - Location to get weather for (default: Queens, NY)
     */
    async getWeatherInfo(location = null) {
        try {
            // Default to Queens, NY if no location specified
            let locationQuery = location ? location.toLowerCase().trim() : 'queens,ny';
            let displayLocation = location ? this.formatLocationName(location) : 'Queens, NY';
            
            // Check if we have coordinates for this location
            if (LOCATION_COORDINATES[locationQuery]) {
                locationQuery = LOCATION_COORDINATES[locationQuery];
            } else {
                // Capitalize first letter of each word for better API recognition
                // "queens,ny" -> "Queens,NY"
                locationQuery = locationQuery.split(',').map(part => {
                    return part.trim().split(' ').map(word => {
                        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
                    }).join(' ');
                }).join(',');
                displayLocation = locationQuery;
            }
            
            // Use wttr.in API (free, no API key required)
            // wttr.in accepts coordinates in format: lat,lon
            const response = await fetch(`https://wttr.in/${encodeURIComponent(locationQuery)}?format=j1`);
            
            if (!response.ok) {
                throw new Error(`Weather API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            const current = data.current_condition[0];
            const tempF = current.temp_F;
            const condition = current.weatherDesc[0].value;
            const humidity = current.humidity;
            const windSpeed = current.windspeedMiles;
            const feelsLike = current.FeelsLikeF;
            // Use the requested location name instead of API's returned location
            const locationName = displayLocation;
            
            // Weather emoji mapping
            const emojiMap = {
                'Clear': '☀️',
                'Sunny': '☀️',
                'Partly cloudy': '⛅',
                'Cloudy': '☁️',
                'Overcast': '☁️',
                'Rain': '🌧️',
                'Light rain': '🌦️',
                'Heavy rain': '🌧️',
                'Thunderstorm': '⛈️',
                'Snow': '❄️',
                'Mist': '🌫️',
                'Fog': '🌫️'
            };
            
            let emoji = '🌤️';
            for (const [key, value] of Object.entries(emojiMap)) {
                if (condition.toLowerCase().includes(key.toLowerCase())) {
                    emoji = value;
                    break;
                }
            }
            
            let responseText = `Current weather in ${locationName}: ${tempF}°F`;
            if (feelsLike !== tempF) {
                responseText += ` (feels like ${feelsLike}°F)`;
            }
            responseText += ` with ${condition.toLowerCase()}. ${emoji}`;
            
            if (humidity > 70) {
                responseText += ` It's quite humid (${humidity}% humidity).`;
            } else if (humidity < 30) {
                responseText += ` The air is dry (${humidity}% humidity).`;
            }
            
            if (windSpeed > 15) {
                responseText += ` Windy conditions with ${windSpeed} mph winds.`;
            } else if (windSpeed > 5) {
                responseText += ` Light breeze at ${windSpeed} mph.`;
            }
            
            return responseText;
        } catch (error) {
            console.error('Error fetching weather:', error);
            // Fallback to static response
            return this.responses.weatherConditions[
                Math.floor(Math.random() * this.responses.weatherConditions.length)
            ];
        }
    }

    /**
     * Get a random general joke
     */
    getGeneralJoke() {
        return this.responses.generalJokes[
            Math.floor(Math.random() * this.responses.generalJokes.length)
        ];
    }

    /**
     * Get a random greeting
     */
    getGreeting() {
        return this.responses.greetings[
            Math.floor(Math.random() * this.responses.greetings.length)
        ];
    }

    /**
     * Get a news response
     */
    getNewsResponse() {
        return this.responses.newsResponses[
            Math.floor(Math.random() * this.responses.newsResponses.length)
        ];
    }

    /**
     * Add a message to the chat display
     * @param {string} content - Message content
     * @param {string} sender - 'user' or 'agent'
     */
    addMessage(content, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const time = new Date().toLocaleTimeString();

        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(content)}</p>
            </div>
            <div class="message-time">${time}</div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Store in history
        this.conversationHistory.push({
            timestamp: new Date().toISOString(),
            sender: sender,
            message: content
        });
    }

    /**
     * Set loading state
     * @param {boolean} loading - Whether loading is active
     */
    setLoading(loading) {
        this.isLoading = loading;
        const sendButton = document.getElementById('sendButton');
        const messageInput = document.getElementById('messageInput');

        if (loading) {
            sendButton.innerHTML = '<div class="loading"></div>';
            sendButton.disabled = true;
            messageInput.disabled = true;
        } else {
            sendButton.innerHTML = 'Send';
            sendButton.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
        }
    }

    /**
     * Clear the chat
     */
    clearChat() {
        if (confirm('Are you sure you want to clear the chat?')) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="message agent-message">
                    <div class="message-content">
                        <p>Chat cleared. How can I help you?</p>
                    </div>
                    <div class="message-time">${new Date().toLocaleTimeString()}</div>
                </div>
            `;
            this.conversationHistory = [];
            this.messageCount = 0;
            this.updateStats();
        }
    }

    /**
     * Show conversation history
     */
    showHistory() {
        if (this.conversationHistory.length === 0) {
            alert('No conversation history found.');
        } else {
            let historyText = 'Conversation History:\n\n';
            this.conversationHistory.forEach(item => {
                const time = new Date(item.timestamp).toLocaleString();
                const sender = item.sender === 'user' ? 'You' : 'Agent';
                historyText += `[${time}] ${sender}: ${item.message}\n\n`;
            });
            alert(historyText);
        }
    }

    /**
     * Show agent status
     */
    showStatus() {
        const statusText = `Agent Status:
Name: AI Assistant
Version: 2.0.0 (Static)
Status: Ready
Messages Processed: ${this.messageCount}
Mode: Client-side (GitHub Pages compatible)`;

        alert(statusText);
    }

    /**
     * Handle quick action buttons
     * @param {string} action - The action type
     */
    handleQuickAction(action) {
        const actions = {
            weather: 'What\'s the weather like today?',
            news: 'Show me the latest news',
            joke: 'Tell me a joke',
            help: 'What can you help me with?'
        };

        const message = actions[action];
        if (message) {
            document.getElementById('messageInput').value = message;
            this.sendMessage();
        }
    }

    /**
     * Update the statistics display
     */
    updateStats() {
        document.getElementById('messageCount').textContent = this.messageCount;
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} - Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the agent when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StaticAIAgent();
    document.getElementById('welcomeTime').textContent = new Date().toLocaleTimeString();
});
