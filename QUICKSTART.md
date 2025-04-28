# Quick Start Guide

## 1. Prerequisites
- Python 3.8-3.11 installed
- pip (Python package manager)

## 2. Installation (5 minutes)

### Windows
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install package in development mode
pip install -e .
```

### Linux/Mac
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install package in development mode
pip install -e .
```

## 3. Configuration
1. Get your Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)
2. Edit config/config.json:
```json
{
    "bot_token": "YOUR_BOT_TOKEN_HERE"
}
```

## 4. Run the Bot
```bash
# From the project root directory
python src/bot.py
```

## 5. Server Setup
The bot will automatically:
- Create required roles
- Set up necessary channels
- Initialize database
- Start verification system

## 6. Basic Commands
- `/verify` - Start verification process
- `/help` - Show available commands
- `/privacy` - View privacy policy

## Troubleshooting

If you encounter installation issues:
```bash
# Clean install
pip uninstall age_verification_bot -y
pip install -e .

# Verify installation
python -c "from src.utils import database, face_detection"
```

Common Issues:
1. Import errors: Make sure you're in the project root directory
2. Package not found: Verify the installation with `pip list`
3. Module not found: Check that all __init__.py files exist

For detailed setup instructions, see INSTALLATION.md
For complete documentation, see README.md
