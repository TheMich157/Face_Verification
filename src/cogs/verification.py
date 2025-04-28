import discord
from discord.ext import commands
import json
import logging
import asyncio
from datetime import datetime, timedelta
import io
import os
import sys

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the project root to Python path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.database import Database
from src.utils.face_detection import FaceDetector

logger = logging.getLogger('age-verify-bot')

# Load configuration
config_path = os.path.join(project_root, 'config', 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

class Verification(commands.Cog):
    """A cog for handling age verification"""
    
    def __init__(self, bot):
        """Initialize the verification cog"""
        self.bot = bot
        self.verification_cooldowns = {}
        self.db = Database()
        self.face_detector = FaceDetector()
        self.disabled_verifications = set()

    async def process_media(self, attachment, user_id, username):
        """Process image or video for age verification"""
        try:
            # Download the media content
            media_data = await attachment.read()
            media_type = 'video' if attachment.filename.lower().endswith(('.mp4', '.mov')) else 'photo'
            
            # Check for spoofing if it's a photo
            if media_type == 'photo':
                is_spoof, spoof_error = self.face_detector.is_spoof(media_data)
                if is_spoof:
                    return None, f"Verification failed: {spoof_error}"

            # Process media for age estimation
            if media_type == 'photo':
                estimated_age, error = self.face_detector.process_image(media_data)
            else:
                estimated_age, error = self.face_detector.process_video(media_data)

            if error:
                return None, f"Error in verification: {error}"

            if estimated_age is None:
                return None, "Could not estimate age from the provided media"

            # Store verification data in database
            verification_id = self.db.add_verification(
                user_id=str(user_id),
                username=username,
                media_data=media_data,
                media_type=media_type,
                estimated_age=estimated_age
            )

            return estimated_age, None

        except Exception as e:
            logger.error(f"Error processing media: {str(e)}")
            return None, f"Error processing verification: {str(e)}"

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle verification messages"""
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Only process DM messages with attachments
        if not isinstance(message.channel, discord.DMChannel) or not message.attachments:
            return

        user_id = message.author.id
        username = f"{message.author.name}#{message.author.discriminator}"

        # Check if verification is disabled
        if "13" in self.disabled_verifications and "18" in self.disabled_verifications:
            await message.channel.send("Verification is currently disabled. Please try again later.")
            return

        # Check cooldown
        if user_id in self.verification_cooldowns:
            cooldown_time = self.verification_cooldowns[user_id]
            if datetime.now() < cooldown_time:
                remaining = (cooldown_time - datetime.now()).seconds // 60
                await message.channel.send(
                    f"Please wait {remaining} minutes before attempting verification again."
                )
                return

        # Process verification
        for attachment in message.attachments:
            if not any(attachment.filename.lower().endswith(ext) 
                      for ext in ['.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mov']):
                await message.channel.send(
                    "Please send a valid image (PNG, JPG, GIF) or video (MP4, MOV) file."
                )
                continue

            await message.channel.send("Processing your verification... Please wait.")

            age, error = await self.process_media(attachment, user_id, username)

            if error:
                await message.channel.send(error)
                continue

            # Add awaiting review role and notify user
            for guild in message.author.mutual_guilds:
                member = guild.get_member(user_id)
                if member:
                    try:
                        # Add awaiting review role
                        awaiting_role = discord.utils.get(
                            guild.roles,
                            name=config['roles']['awaiting_review']
                        )
                        if awaiting_role:
                            await member.add_roles(awaiting_role)
                    except discord.Forbidden:
                        logger.error(f"Failed to add awaiting review role to {user_id} in {guild.name}")

            # Initial age check and notify moderators
            is_potentially_underage = age < config['verification_settings']['min_age']
            status_msg = (
                "⚠️ Initial age check suggests you may be under 13. "
                if is_potentially_underage else
                "✅ Initial age check passed. "
            ) + "Your submission is now awaiting staff review."

            await message.channel.send(status_msg)

            # Notify moderators
            for guild in message.author.mutual_guilds:
                try:
                    mod_channel = discord.utils.get(guild.channels, name=config['channels']['mod_logs'])
                    if mod_channel:
                        embed = discord.Embed(
                            title="⚠️ Age Verification Review Required" if is_potentially_underage else "Age Verification Review",
                            color=discord.Color.red() if is_potentially_underage else discord.Color.blue(),
                            timestamp=datetime.now()
                        )
                        embed.add_field(name="User", value=f"{username} ({user_id})", inline=False)
                        embed.add_field(name="Estimated Age", value=f"{age:.1f}", inline=True)
                        embed.add_field(name="Media Type", value=attachment.filename.split('.')[-1].upper(), inline=True)
                        embed.add_field(
                            name="Status",
                            value="⚠️ POTENTIAL UNDERAGE USER" if is_potentially_underage else "Awaiting Review",
                            inline=False
                        )
                        
                        await mod_channel.send(
                            content="@here - Urgent review required!" if is_potentially_underage else None,
                            embed=embed
                        )
                except Exception as e:
                    logger.error(f"Failed to notify moderators in {guild.name}: {e}")

            # Set cooldown
            self.verification_cooldowns[user_id] = datetime.now() + timedelta(
                minutes=config['verification_settings']['cooldown_minutes']
            )
            break

async def setup(bot):
    """Set up the Verification cog"""
    await bot.add_cog(Verification(bot))
</create_file>
