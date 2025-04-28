import discord
from discord.ext import commands
import json
import logging
from discord import app_commands
from datetime import datetime
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.database import Database

logger = logging.getLogger('age-verify-bot')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

class AdminControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
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
        """Toggle verification system for specific age group"""
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

async def setup(bot):
    await bot.add_cog(AdminControl(bot))
