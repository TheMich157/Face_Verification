# Quick Start Guide - Age Verification Bot

## Minimum Setup (5 Minutes)

### 1. Get Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "Bot" section → "Add Bot"
4. Click "Reset Token" and copy it
5. Under "Privileged Gateway Intents", enable:
   - PRESENCE INTENT
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT

### 2. Invite Bot
1. Go to "OAuth2" → "URL Generator"
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select permissions:
   - `Administrator` (recommended for easiest setup)
4. Copy generated URL and invite bot to your server

### 3. Configure Bot
1. Open `config/config.json`
2. Replace only this line:
   ```json
   "bot_token": "YOUR_DISCORD_BOT_TOKEN"
   ```
   with your actual bot token:
   ```json
   "bot_token": "MTEx...your-token-here..."
   ```

### 4. Install & Run
```bash
# Install requirements
pip install -r requirements.txt

# Start bot
python src/bot.py
```

That's it! The bot will automatically:
- Create required roles
- Set up necessary channels
- Initialize database
- Start verification system

## First Verification
1. Type `/verify` in any channel
2. Follow bot's instructions
3. Submit photo/video for verification

## Basic Commands
- `/help` - Show all commands
- `/verify` - Start verification
- `/privacy` - View privacy policy

## Need More?
See full setup in SETUP_GUIDE.md for:
- Custom configuration
- Advanced features
- Staff training
- Security settings

## Troubleshooting
If bot doesn't start:
1. Check bot token is correct
2. Verify Python 3.8+ is installed
3. Confirm all requirements are installed
4. Ensure bot has administrator permissions

For help: See SETUP_GUIDE.md
