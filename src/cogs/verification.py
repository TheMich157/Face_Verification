import discord
from discord.ext import commands
import json
import logging
import asyncio
from datetime import datetime, timedelta
import io
from ..utils.database import Database
from ..utils.face_detection import FaceDetector

logger = logging.getLogger('age-verify-bot')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification_cooldowns = {}
        self.db = Database()
        self.face_detector = FaceDetector()

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
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Only process DM messages with attachments
        if not isinstance(message.channel, discord.DMChannel) or not message.attachments:
            return

        user_id = message.author.id
        username = f"{message.author.name}#{message.author.discriminator}"

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
            is_potentially_adult = age >= config['verification_settings']['adult_age']
            
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
                            value=(
                                "⚠️ POTENTIAL UNDERAGE USER" if is_potentially_underage else
                                "🔞 POTENTIAL 18+ USER" if is_potentially_adult else
                                "Awaiting Review"
                            ),
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

    @app_commands.command(name="review")
    @app_commands.checks.has_permissions(administrator=True)
    async def review_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        is_underage: bool
    ):
        """Review a user's age verification status"""
        try:
            if is_underage:
                # Ban user if underage
                reason = "User does not meet minimum age requirement (13+)"
                await user.send(config['moderation']['ban_message'])
                await user.ban(reason=reason)
                
                await interaction.response.send_message(
                    f"✅ User {user.mention} has been banned for being underage.",
                    ephemeral=True
                )
            else:
                # Remove awaiting review role and add 13+ role
                awaiting_role = discord.utils.get(
                    interaction.guild.roles,
                    name=config['roles']['awaiting_review']
                )
                verified_role = discord.utils.get(
                    interaction.guild.roles,
                    name=config['roles']['verified_13plus']
                )
                
                if awaiting_role in user.roles:
                    await user.remove_roles(awaiting_role)
                if verified_role:
                    await user.add_roles(verified_role)
                
                # Notify user
                await user.send(
                    "✅ Your age verification has been approved! "
                    "You now have access to 13+ content. "
                    "If you are 18+, staff may review your verification for additional access."
                )
                
                await interaction.response.send_message(
                    f"✅ User {user.mention} has been verified as 13+.",
                    ephemeral=True
                )
            
            # Log the action
            mod_channel = discord.utils.get(
                interaction.guild.channels,
                name=config['channels']['mod_logs']
            )
            if mod_channel:
                action = "banned (underage)" if is_underage else "verified (13+)"
                embed = discord.Embed(
                    title="Age Verification Review Complete",
                    description=f"User has been {action}",
                    color=discord.Color.red() if is_underage else discord.Color.green(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
                await mod_channel.send(embed=embed)
                
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to perform this action.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in review command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while processing the review.",
                ephemeral=True
            )

    @app_commands.command(name="18approve")
    @app_commands.checks.has_permissions(administrator=True)
    async def approve_18plus(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        approved: bool
    ):
        """Approve or deny 18+ status for a user"""
        try:
            if approved:
                # Add 18+ role and remove 13+ role
                role_18plus = discord.utils.get(
                    interaction.guild.roles,
                    name=config['roles']['verified_18plus']
                )
                role_13plus = discord.utils.get(
                    interaction.guild.roles,
                    name=config['roles']['verified_13plus']
                )
                
                if role_18plus and role_13plus:
                    await user.remove_roles(role_13plus)
                    await user.add_roles(role_18plus)
                    
                    # Notify user
                    await user.send(
                        "✅ You have been approved for 18+ access! "
                        f"Profanity Level: {config['profanity_levels']['18plus']['description']}"
                    )
                    
                    await interaction.response.send_message(
                        f"✅ User {user.mention} has been approved for 18+ access.",
                        ephemeral=True
                    )
            else:
                await interaction.response.send_message(
                    f"User {user.mention} will remain with 13+ access.",
                    ephemeral=True
                )
            
            # Log the action
            mod_channel = discord.utils.get(
                interaction.guild.channels,
                name=config['channels']['mod_logs']
            )
            if mod_channel:
                embed = discord.Embed(
                    title="18+ Review Complete",
                    description=f"User {'approved' if approved else 'denied'} for 18+ access",
                    color=discord.Color.green() if approved else discord.Color.blue(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
                await mod_channel.send(embed=embed)
                
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to perform this action.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in 18+ approval: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while processing the approval.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Verification(bot))
