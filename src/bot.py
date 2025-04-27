import discord
from discord.ext import commands
import json
import logging
import os
from datetime import datetime
import aiohttp
from discord import app_commands

# Setup logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('age-verify-bot')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

class AgeVerificationBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.guild_messages = True
        intents.dm_messages = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='Advanced Age Verification Bot'
        )
        
        self.verification_sessions = {}
        self.startup_time = datetime.now()
        self.command_usage = {}
        
    async def setup_hook(self):
        """Set up bot and load all cogs"""
        try:
            # Load all cogs
            await self.load_extension('cogs.verification')
            await self.load_extension('cogs.admin')
            await self.load_extension('cogs.moderation')
            await self.load_extension('cogs.statistics')
            await self.load_extension('cogs.appeals')
            await self.load_extension('cogs.automod')
            
            logger.info("All cogs loaded successfully")
        except Exception as e:
            logger.error(f"Error loading cogs: {e}")
            raise
        
    async def on_ready(self):
        """Handle bot startup"""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info('------')
        
        # Sync commands with Discord
        try:
            await self.tree.sync()
            logger.info("Successfully synced command tree")
        except Exception as e:
            logger.error(f"Error syncing command tree: {e}")
        
        # Set up status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for verification requests | /help"
            ),
            status=discord.Status.online
        )
        
        # Initialize roles and channels in all guilds
        for guild in self.guilds:
            await self.initialize_guild(guild)

    async def initialize_guild(self, guild):
        """Initialize necessary roles and channels in a guild"""
        try:
            # Create roles if they don't exist
            for role_name in config['roles'].values():
                if not discord.utils.get(guild.roles, name=role_name):
                    await guild.create_role(name=role_name)
                    logger.info(f"Created role {role_name} in {guild.name}")

            # Create channels if they don't exist
            for channel_name in config['channels'].values():
                if not discord.utils.get(guild.channels, name=channel_name):
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True)
                    }
                    
                    # Add staff permissions
                    staff_role = discord.utils.get(guild.roles, name=config['roles']['staff'])
                    if staff_role:
                        overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True)

                    await guild.create_text_channel(channel_name, overwrites=overwrites)
                    logger.info(f"Created channel {channel_name} in {guild.name}")

        except discord.Forbidden:
            logger.error(f"Missing permissions to initialize {guild.name}")
        except Exception as e:
            logger.error(f"Error initializing guild {guild.name}: {e}")

    async def on_guild_join(self, guild):
        """Handle bot joining a new server"""
        logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        await self.initialize_guild(guild)

    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        error_msg = str(error)
        
        if isinstance(error, commands.MissingPermissions):
            error_msg = "You don't have permission to use this command."
        elif isinstance(error, commands.BotMissingPermissions):
            error_msg = "I don't have the necessary permissions to do that."
        elif isinstance(error, commands.MissingRole):
            error_msg = "You don't have the required role to use this command."
        elif isinstance(error, commands.CommandOnCooldown):
            error_msg = f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds."
        
        logger.error(f'Command error: {error_msg}')
        await ctx.send(f'Error: {error_msg}')

    @app_commands.command(name="help")
    async def help_command(self, interaction: discord.Interaction):
        """Show help information about the bot"""
        is_staff = any(role.name == config['roles']['staff'] for role in interaction.user.roles)
        is_senior_staff = any(role.name == config['roles']['senior_staff'] for role in interaction.user.roles)
        
        embed = discord.Embed(
            title="Age Verification Bot Help",
            color=discord.Color.blue(),
            description="Here are the available commands:"
        )
        
        # User Commands
        embed.add_field(
            name="User Commands",
            value="• `/verify` - Start the age verification process\n"
                  "• `/help` - Show this help message\n"
                  "• `/appeal` - Submit a verification appeal",
            inline=False
        )
        
        # Staff Commands
        if is_staff:
            staff_commands = (
                "• `/pending_reviews` - View pending verifications\n"
                "• `/view_verification <user>` - View a user's verification\n"
                "• `/review <user> <is_underage>` - Review a verification\n"
                "• `/18approve <user> <approved>` - Approve 18+ status\n"
                "• `/stats` - View verification statistics\n"
                "• `/verification_stats` - View detailed statistics\n"
                "• `/age_distribution` - View age distribution graph\n"
                "• `/staff_stats` - View staff review statistics"
            )
            embed.add_field(name="Staff Commands", value=staff_commands, inline=False)
        
        # Senior Staff Commands
        if is_senior_staff:
            senior_commands = (
                "• `/export_stats` - Export statistics to CSV\n"
                "• `/lockdown` - Toggle server lockdown\n"
                "• `/bulk_verify <role>` - Bulk verify users with role\n"
                "• `/profanity_settings` - View profanity filter settings\n"
                "• `/appeal_stats` - View appeal statistics"
            )
            embed.add_field(name="Senior Staff Commands", value=senior_commands, inline=False)

        # Add bot statistics
        uptime = datetime.now() - self.startup_time
        embed.add_field(
            name="Bot Statistics",
            value=f"Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m\n"
                  f"Servers: {len(self.guilds)}\n"
                  f"Commands Used: {sum(self.command_usage.values())}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="status")
    @app_commands.checks.has_permissions(administrator=True)
    async def status_command(self, interaction: discord.Interaction):
        """Show detailed bot status"""
        embed = discord.Embed(
            title="Bot Status",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # System Status
        embed.add_field(
            name="System",
            value=f"Uptime: {datetime.now() - self.startup_time}\n"
                  f"Latency: {round(self.latency * 1000)}ms",
            inline=False
        )
        
        # Feature Status
        features = []
        for feature, enabled in config['features'].items():
            status = "✅" if enabled else "❌"
            features.append(f"{status} {feature}")
        
        embed.add_field(
            name="Features",
            value="\n".join(features),
            inline=False
        )
        
        # Cog Status
        cogs = []
        for cog in self.cogs:
            cogs.append(f"✅ {cog}")
        
        embed.add_field(
            name="Loaded Cogs",
            value="\n".join(cogs),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def main():
    """Start the bot"""
    try:
        bot = AgeVerificationBot()
        bot.run(config['bot_token'])
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
