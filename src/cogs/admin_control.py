import discord
from discord.ext import commands
import json
import logging
from discord import app_commands
from datetime import datetime

logger = logging.getLogger('age-verify-bot')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

class AdminControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification_states = {
            "13": True,
            "18": True
        }

    @app_commands.command(name="verification")
    @app_commands.checks.has_permissions(administrator=True)
    async def toggle_verification(
        self,
        interaction: discord.Interaction,
        age_type: str,
        state: str,
        reason: str = None
    ):
        """
        Toggle verification system for specific age group
        
        Parameters
        ----------
        age_type: The age group to modify (13/18)
        state: New state (Enabled/Disabled)
        reason: Optional reason for the change
        """
        # Validate inputs
        if age_type not in ["13", "18"]:
            await interaction.response.send_message(
                "❌ Invalid age type. Must be '13' or '18'.",
                ephemeral=True
            )
            return

        if state.lower() not in ["enabled", "disabled"]:
            await interaction.response.send_message(
                "❌ Invalid state. Must be 'Enabled' or 'Disabled'.",
                ephemeral=True
            )
            return

        is_enabled = state.lower() == "enabled"
        self.verification_states[age_type] = is_enabled

        # Create embed for response and logging
        embed = discord.Embed(
            title="Verification System Update",
            color=discord.Color.green() if is_enabled else discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Change",
            value=f"{age_type}+ Verification {'Enabled' if is_enabled else 'Disabled'}",
            inline=False
        )
        
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        
        embed.add_field(
            name="Administrator",
            value=interaction.user.mention,
            inline=False
        )

        # Update verification status in all relevant channels
        status_msg = (
            f"⚠️ {age_type}+ verification has been "
            f"{'enabled' if is_enabled else 'disabled'}"
        )
        if reason:
            status_msg += f"\nReason: {reason}"

        # Send to mod logs
        mod_channel = discord.utils.get(
            interaction.guild.channels,
            name=config['channels']['mod_logs']
        )
        if mod_channel:
            await mod_channel.send(embed=embed)

        # Send to staff chat
        staff_channel = discord.utils.get(
            interaction.guild.channels,
            name=config['channels']['staff_chat']
        )
        if staff_channel:
            await staff_channel.send(
                f"@here {status_msg}",
                embed=embed
            )

        # Update verification channels if disabled
        if not is_enabled:
            verification_cog = self.bot.get_cog('Verification')
            if verification_cog:
                verification_cog.disabled_verifications.add(age_type)

        await interaction.response.send_message(
            f"✅ Successfully {state.lower()} {age_type}+ verification.",
            embed=embed,
            ephemeral=True
        )

    @app_commands.command(name="verification_status")
    @app_commands.checks.has_permissions(administrator=True)
    async def check_verification_status(self, interaction: discord.Interaction):
        """Check the current status of verification systems"""
        embed = discord.Embed(
            title="Verification System Status",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        for age_type in ["13", "18"]:
            status = self.verification_states.get(age_type, True)
            embed.add_field(
                name=f"{age_type}+ Verification",
                value=f"{'✅ Enabled' if status else '❌ Disabled'}",
                inline=False
            )

        # Add lockdown status
        moderation_cog = self.bot.get_cog('Moderation')
        if moderation_cog:
            embed.add_field(
                name="Server Lockdown",
                value=f"{'🔒 Active' if moderation_cog.lockdown else '🔓 Inactive'}",
                inline=False
            )

        # Add queue information
        verification_cog = self.bot.get_cog('Verification')
        if verification_cog:
            pending_count = len(verification_cog.verification_sessions)
            embed.add_field(
                name="Pending Verifications",
                value=str(pending_count),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clear_verification_queue")
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_verification_queue(
        self,
        interaction: discord.Interaction,
        reason: str
    ):
        """
        Clear all pending verifications from the queue
        
        Parameters
        ----------
        reason: Reason for clearing the queue
        """
        verification_cog = self.bot.get_cog('Verification')
        if not verification_cog:
            await interaction.response.send_message(
                "❌ Verification system not available.",
                ephemeral=True
            )
            return

        # Count pending verifications
        pending_count = len(verification_cog.verification_sessions)
        
        # Clear the queue
        for user_id in verification_cog.verification_sessions.copy():
            try:
                user = await self.bot.fetch_user(int(user_id))
                await user.send(
                    f"Your verification has been cancelled by an administrator.\n"
                    f"Reason: {reason}\n"
                    f"You may submit a new verification request."
                )
            except:
                logger.error(f"Failed to notify user {user_id} about queue clear")

        verification_cog.verification_sessions.clear()

        # Create embed for logging
        embed = discord.Embed(
            title="Verification Queue Cleared",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Administrator", value=interaction.user.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Cleared Verifications", value=str(pending_count), inline=False)

        # Log to mod channel
        mod_channel = discord.utils.get(
            interaction.guild.channels,
            name=config['channels']['mod_logs']
        )
        if mod_channel:
            await mod_channel.send(embed=embed)

        await interaction.response.send_message(
            f"✅ Successfully cleared {pending_count} pending verifications.",
            embed=embed,
            ephemeral=True
        )

    @app_commands.command(name="verification_config")
    @app_commands.checks.has_permissions(administrator=True)
    async def view_verification_config(self, interaction: discord.Interaction):
        """View current verification configuration"""
        embed = discord.Embed(
            title="Verification Configuration",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        # Add verification settings
        embed.add_field(
            name="Age Requirements",
            value=f"Minimum Age: {config['verification_settings']['min_age']}\n"
                  f"Adult Age: {config['verification_settings']['adult_age']}",
            inline=False
        )

        # Add cooldown settings
        embed.add_field(
            name="Cooldowns",
            value=f"Verification: {config['verification_settings']['cooldown_minutes']} minutes\n"
                  f"Appeal: {config['appeals']['cooldown_days']} days",
            inline=False
        )

        # Add role configuration
        roles_text = ""
        for role_type, role_name in config['roles'].items():
            roles_text += f"{role_type}: {role_name}\n"
        embed.add_field(name="Roles", value=roles_text, inline=False)

        # Add channel configuration
        channels_text = ""
        for channel_type, channel_name in config['channels'].items():
            channels_text += f"{channel_type}: {channel_name}\n"
        embed.add_field(name="Channels", value=channels_text, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminControl(bot))
