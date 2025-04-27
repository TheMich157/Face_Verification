# Setup Guide for Age Verification Bot

## Prerequisites

1. **Discord Bot Token**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create New Application
   - Go to "Bot" section
   - Click "Add Bot"
   - Copy the token

2. **Required Bot Permissions**
   - Administrator (for full functionality)
   - Or these specific permissions:
     - Manage Roles
     - Manage Channels
     - Ban Members
     - Kick Members
     - Send Messages
     - Read Messages
     - Manage Messages
     - Attach Files
     - Read Message History
     - Add Reactions

3. **Python Requirements**
   - Python 3.8 or higher
   - pip (Python package manager)

## Installation Steps

1. **Install Dependencies**
   ```bash
   # Install all required packages
   pip install -r requirements.txt
   ```

2. **Configure Bot**
   - Open `config/config.json`
   - Replace "YOUR_DISCORD_BOT_TOKEN" with your bot token
   - Other settings can be left at default values initially

3. **Server Setup**

   a) **Create Required Roles** (in this order):
   ```
   - staff
   - senior_staff
   - trained_staff
   - staff_trainer
   - verified_18plus (or "18+")
   - verified_13plus (or "13+")
   - unverified
   - awaiting_staff_check
   - banned_appeals
   ```

   b) **Create Required Channels**:
   ```
   - mod-logs (private, staff only)
   - welcome (public)
   - verification-logs (private, staff only)
   - staff-chat (private, staff only)
   - verification-appeals (private, staff only)
   - 18plus-chat (age-restricted)
   - verification-analytics (private, staff only)
   - verification-queue (private, staff only)
   - staff-training (private, staff only)
   ```

4. **Bot Invitation**
   - Go to Discord Developer Portal
   - Select your application
   - Go to "OAuth2" → "URL Generator"
   - Select "bot" and "applications.commands"
   - Select required permissions
   - Copy and use the generated URL to invite bot

## First-Time Setup

1. **Initialize Database**
   ```bash
   # The bot will automatically create the database on first run
   python src/bot.py
   ```

2. **Verify Roles and Channels**
   - Bot will automatically create missing roles/channels
   - Check permissions are correct
   - Staff roles should have access to staff channels

3. **Staff Setup**
   - Assign staff roles to moderators
   - Have staff complete training modules
   - Review STAFF_GUIDE.md with team

## Configuration Options

Key settings in `config/config.json` you might want to customize:

```json
{
    "verification_settings": {
        "min_age": 13,              // Minimum age requirement
        "adult_age": 18,            // Adult verification age
        "cooldown_minutes": 60,     // Time between verification attempts
        "max_attempts": 3           // Maximum verification attempts
    },
    "queue_management": {
        "max_queue_size": 100,      // Maximum pending verifications
        "staff_max_workload": 5     // Max verifications per staff
    },
    "privacy": {
        "data_retention_days": 30,  // How long to keep verification data
        "encryption_enabled": true   // Enable data encryption
    }
}
```

## Security Setup

1. **Data Protection**
   - Verification media is automatically encrypted
   - Database is secured by default
   - Automatic cleanup of old data

2. **Staff Access**
   - Only staff roles can access moderation commands
   - Actions are logged in mod-logs
   - Performance tracking enabled

3. **Privacy**
   - Privacy policy available via `/privacy`
   - Data deletion available via `/delete_data`
   - Consent required for verification

## Testing the Setup

1. **Basic Functionality**
   ```bash
   # Start the bot
   python src/bot.py
   ```

2. **Verify Commands**
   - `/help` - Should show available commands
   - `/verify` - Should start verification process
   - `/privacy` - Should show privacy policy

3. **Staff Commands**
   - `/queue_status` - Check verification queue
   - `/staff_dashboard` - View staff dashboard
   - `/verification_status` - Check system status

## Troubleshooting

1. **Bot Won't Start**
   - Check bot token is correct
   - Verify Python version (3.8+)
   - Check all dependencies installed

2. **Missing Permissions**
   - Verify bot role is at top of role hierarchy
   - Check channel permissions
   - Verify bot has administrator or required permissions

3. **Database Issues**
   - Database auto-creates on first run
   - Check write permissions in directory
   - Verify SQLite is working

4. **Command Issues**
   - Use `/help` to verify commands are registered
   - Check bot has application.commands scope
   - Restart bot to sync commands

## Maintenance

1. **Regular Tasks**
   - Monitor log files
   - Check staff performance
   - Review verification queue
   - Update training materials

2. **Backup**
   - Database backs up automatically
   - Keep bot token secure
   - Save configuration changes

3. **Updates**
   - Check for dependency updates
   - Review bot performance
   - Update documentation

## Support

If you encounter issues:
1. Check error logs
2. Review configuration
3. Verify permissions
4. Check documentation

## Additional Notes

- Bot runs best with Administrator permissions
- Keep bot token secure and private
- Regular backups recommended
- Monitor staff performance
- Review privacy settings regularly

Remember to keep your bot token private and never share it. The bot will automatically handle most setup tasks, but you should review all settings and permissions after installation.
