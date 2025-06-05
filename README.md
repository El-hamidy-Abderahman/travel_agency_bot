# وكالة السفر الذكية - Travel Agency Chatbot

Arabic travel agency chatbot built with Rasa framework for booking flights and hotels.

## Features

- **Flight Booking**: Search and book flights between major cities
- **Hotel Reservations**: Find and reserve hotels with different categories
- **Arabic Language Support**: Full conversation in Arabic
- **Web Interface**: Professional chat interface
- **Booking Management**: Modify and confirm reservations

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/El-hamidy-Abderahman/travel_agency_bot.git
cd travel_agency_bot

# Create virtual environment (recommended to avoid dependency conflicts)
python3 -m venv rasa_env
source rasa_env/bin/activate  # Linux/Mac
# or rasa_env\Scripts\activate  # Windows

# Install Rasa and dependencies
pip install rasa

# Train the model
rasa train
```

## Usage

### Running the Bot
```bash
# Terminal 1: Start action server
rasa run actions

# Terminal 2: Start Rasa server
rasa run --enable-api --cors "*"

# Terminal 3: Serve the web interface
python3 -m http.server 8000

# Open http://localhost:8000 in your browser
```

### Web Interface
- Open `http://localhost:8000` in your browser after running the server
- Start chatting in Arabic
- Follow the bot's prompts for booking flights or hotels

## Project Structure

```
travel_agency_bot/
├── actions/
│   ├── __init__.py
│   └── actions.py          # Custom actions and API integrations
├── data/
│   ├── nlu.yml            # Training data for intent recognition
│   ├── rules.yml          # Conversation rules
│   └── stories.yml        # Training stories
├── models/                # Trained models directory
├── config.yml             # Rasa configuration
├── credentials.yml        # Channel credentials
├── domain.yml             # Domain configuration
├── endpoints.yml          # Endpoints configuration
└── index.html             # Web chat interface
```

## Example Conversation

```
User: مرحبا
Bot: مرحباً! يمكنني مساعدتك في حجز الطيران والفنادق

User: أريد حجز رحلة
Bot: من أي مدينة ترغب بالمغادرة؟

User: مراكش
Bot: إلى أي مدينة ترغب بالسفر؟

User: باريس
Bot: ما هو تاريخ المغادرة المفضل لديك؟
```

## Customization

### Adding New Cities
1. Update `data/nlu.yml` with new city examples
2. Modify city lists in `actions/actions.py`
3. Retrain: `rasa train`

### Modifying Responses
1. Edit response templates in `domain.yml`
2. Update dynamic responses in `actions/actions.py`

## API Integration

The bot is ready for integration with real travel APIs:
- **Flight APIs**: Amadeus, Skyscanner
- **Hotel APIs**: Booking.com, Expedia

Update `actions/actions.py` with your API credentials and endpoints.

## Troubleshooting

### Common Issues
- **Model training fails**: Run `rasa data validate`
- **Action server error**: Check if running on port 5055
- **CORS issues**: Ensure Rasa server started with `--cors "*"`
- **Web interface issues**: Serve HTML with `python -m http.server 8000`

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `rasa train` and `rasa test`
5. Submit a pull request