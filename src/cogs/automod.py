import discord
from discord.ext import commands
import json
import logging
from discord import app_commands
import re
from datetime import datetime
import asyncio

logger = logging.getLogger('age-verify-bot')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warning_counts = {}
        self.profanity_cache = {}
        self.last_message_times = {}
        self.spam_detection = {}
        
        # Start background tasks
        self.bg_tasks = [
            bot.loop.create_task(self.clear_warning_counts()),
            bot.loop.create_task(self.update_channel_permissions())
        ]

    def cog_unload(self):
        for task in self.bg_tasks:
            task.cancel()

    async def clear_warning_counts(self):
        """Clear warning counts every 24 hours"""
        while True:
            await asyncio.sleep(86400)  # 24 hours
            self.warning_counts.clear()

    async def update_channel_permissions(self):
        """Update channel permissions based on age roles"""
        while True:
            try:
                for guild in self.bot.guilds:
                    # Get roles
                    role_18plus = discord.utils.get(guild.roles, name=config['roles']['verified_18plus'])
                    role_13plus = discord.utils.get(guild.roles, name=config['roles']['verified_13plus'])
                    
                    if role_18plus and role_13plus:
                        # Update 18+ channels
                        for channel_name in config['profanity_levels']['18plus']['channels']:
                            channel = discord.utils.get(guild.channels, name=channel_name)
                            if channel:
                                await channel.set_permissions(role_18plus, read_messages=True, send_messages=True)
                                await channel.set_permissions(role_13plus, read_messages=False)
                                
                        # Update 13+ channels
                        for channel_name in config['profanity_levels']['13plus']['channels']:
                            channel = discord.utils.get(guild.channels, name=channel_name)
                            if channel:
                                await channel.set_permissions(role_13plus, read_messages=True, send_messages=True)
                
            except Exception as e:
                logger.error(f"Error updating channel permissions: {e}")
            
            await asyncio.sleep(300)  # Check every 5 minutes

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle message moderation"""
        if message.author.bot:
            return

        try:
            # Get user's roles
            is_18plus = any(role.name == config['roles']['verified_18plus'] for role in message.author.roles)
            is_13plus = any(role.name == config['roles']['verified_13plus'] for role in message.author.roles)
            
            # Check spam
            if await self.check_spam(message):
                await message.delete()
                await self.warn_user(message.author, message.channel, "spam detection")
                return

            # Check profanity levels
            if is_18plus:
                # 18+ can use any language in appropriate channels
                if message.channel.name not in config['profanity_levels']['18plus']['channels']:
                    if await self.check_strong_profanity(message):
                        await message.delete()
                        await self.warn_user(message.author, message.channel, "strong language in non-adult channel")
            elif is_13plus:
                # 13+ can only use moderate language
                if await self.check_strong_profanity(message):
                    await message.delete()
                    await self.warn_user(message.author, message.channel, "strong language")
            else:
                # Unverified users can't use any profanity
                if await self.check_any_profanity(message):
                    await message.delete()
                    await self.warn_user(message.author, message.channel, "profanity while unverified")

        except Exception as e:
            logger.error(f"Error in message moderation: {e}")

    async def check_spam(self, message):
        """Check for spam messages"""
        author_id = message.author.id
        now = datetime.now()
        
        # Initialize spam detection for new users
        if author_id not in self.spam_detection:
            self.spam_detection[author_id] = {
                'messages': [],
                'repeated_content': set()
            }
        
        # Add message to history
        self.spam_detection[author_id]['messages'].append(now)
        
        # Remove old messages (older than 10 seconds)
        self.spam_detection[author_id]['messages'] = [
            msg_time for msg_time in self.spam_detection[author_id]['messages']
            if (now - msg_time).seconds < 10
        ]
        
        # Check message frequency
        if len(self.spam_detection[author_id]['messages']) > 5:  # More than 5 messages in 10 seconds
            return True
            
        # Check repeated content
        if message.content in self.spam_detection[author_id]['repeated_content']:
            return True
        
        self.spam_detection[author_id]['repeated_content'].add(message.content)
        
        # Clear old content from set periodically
        if len(self.spam_detection[author_id]['repeated_content']) > 10:
            self.spam_detection[author_id]['repeated_content'].clear()
        
        return False

    async def check_strong_profanity(self, message):
        """Check for strong profanity in message"""
        # This would be replaced with a more comprehensive profanity detection system
        strong_profanity = ['example_word1', 'example_word2']  # Replace with actual words
        return any(word in message.content.lower() for word in strong_profanity)

    async def check_any_profanity(self, message):
        """Check for any profanity in message"""
        # This would be replaced with a more comprehensive profanity detection system
        any_profanity = ['example_word1', 'example_word2', 'example_word3']  # Replace with actual words
        return any(word in message.content.lower() for word in any_profanity)

    async def warn_user(self, user, channel, reason):
        """Handle user warnings"""
        if user.id not in self.warning_counts:
            self.warning_counts[user.id] = 0
        
        self.warning_counts[user.id] += 1
        
        # Send warning message
        warning_msg = await channel.send(
            f"{user.mention} Warning ({self.warning_counts[user.id]}/3): {reason}. "
            "Continued violations may result in a mute or ban."
        )
        
        # Auto-delete warning after 5 seconds
        await asyncio.sleep(5)
        await warning_msg.delete()
        
        # Handle multiple warnings
        if self.warning_counts[user.id] >= 3:
            try:
                # Mute user for 1 hour
                muted_role = discord.utils.get(channel.guild.roles, name="Muted")
                if muted_role:
                    await user.add_roles(muted_role)
                    await channel.send(
                        f"{user.mention} has been muted for 1 hour due to multiple violations.",
                        delete_after=10
                    )
                    
                    # Remove mute after 1 hour
                    await asyncio.sleep(3600)
                    await user.remove_roles(muted_role)
                    
                # Reset warning count
                self.warning_counts[user.id] = 0
                
            except discord.Forbidden:
                logger.error(f"Failed to mute user {user.id}")

    @app_commands.command(name="profanity_settings")
    @app_commands.checks.has_permissions(administrator=True)
    async def view_profanity_settings(self, interaction: discord.Interaction):
        """View current profanity filter settings"""
        embed = discord.Embed(
            title="Profanity Filter Settings",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for level, settings in config['profanity_levels'].items():
            embed.add_field(
                name=f"{level} Settings",
                value=f"Level: {settings['allowed']}\n"
                      f"Description: {settings['description']}\n"
                      f"Channels: {', '.join(settings['channels'])}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
