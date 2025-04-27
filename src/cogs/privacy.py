import discord
from discord.ext import commands
import json
import logging
from discord import app_commands
from datetime import datetime, timedelta
import io
from ..utils.database import Database

logger = logging.getLogger('age-verify-bot')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

class Privacy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.deletion_requests = {}

    @app_commands.command(name="privacy")
    async def show_privacy_policy(self, interaction: discord.Interaction):
        """Show the bot's privacy policy"""
        try:
            with open('PRIVACY_POLICY.md', 'r') as f:
                policy = f.read()

            # Split policy into chunks of 2000 characters (Discord's limit)
            chunks = [policy[i:i+1900] for i in range(0, len(policy), 1900)]
            
            await interaction.response.send_message(
                "Here's our privacy policy. Please read it carefully:",
                ephemeral=True
            )
            
            for chunk in chunks:
                await interaction.followup.send(chunk, ephemeral=True)

        except Exception as e:
            logger.error(f"Error showing privacy policy: {e}")
            await interaction.response.send_message(
                "Error loading privacy policy. Please contact an administrator.",
                ephemeral=True
            )

    @app_commands.command(name="delete_data")
    async def request_data_deletion(self, interaction: discord.Interaction):
        """Request deletion of your verification data"""
        user_id = str(interaction.user.id)

        # Check cooldown
        if user_id in self.deletion_requests:
            last_request = self.deletion_requests[user_id]
            cooldown = timedelta(hours=config['privacy']['deletion_request_cooldown_hours'])
            if datetime.now() < last_request + cooldown:
                hours_left = ((last_request + cooldown) - datetime.now()).total_seconds() / 3600
                await interaction.response.send_message(
                    f"Please wait {hours_left:.1f} hours before making another deletion request.",
                    ephemeral=True
                )
                return

        # Create confirmation view
        class ConfirmDeletion(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)  # 5 minute timeout

            @discord.ui.button(label="Confirm Deletion", style=discord.ButtonStyle.red)
            async def confirm(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                try:
                    # Delete verification data
                    deleted = self.db.delete_user_data(user_id)
                    
                    if deleted:
                        # Log deletion
                        mod_channel = discord.utils.get(
                            button_interaction.guild.channels,
                            name=config['channels']['mod_logs']
                        )
                        if mod_channel:
                            embed = discord.Embed(
                                title="Data Deletion Request",
                                description=f"User data deleted for {button_interaction.user.mention}",
                                color=discord.Color.red(),
                                timestamp=datetime.now()
                            )
                            await mod_channel.send(embed=embed)

                        # Update cooldown
                        self.deletion_requests[user_id] = datetime.now()

                        await button_interaction.response.send_message(
                            "✅ Your verification data has been deleted. "
                            "Note that you may need to verify again to access certain channels.",
                            ephemeral=True
                        )
                    else:
                        await button_interaction.response.send_message(
                            "No verification data found to delete.",
                            ephemeral=True
                        )

                except Exception as e:
                    logger.error(f"Error deleting user data: {e}")
                    await button_interaction.response.send_message(
                        "An error occurred while deleting your data. Please try again later.",
                        ephemeral=True
                    )

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
            async def cancel(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await button_interaction.response.send_message(
                    "Data deletion request cancelled.",
                    ephemeral=True
                )

        await interaction.response.send_message(
            "⚠️ **Data Deletion Confirmation**\n\n"
            "Are you sure you want to delete your verification data?\n"
            "This will:\n"
            "• Remove all your verification photos/videos\n"
            "• Delete your verification history\n"
            "• Require re-verification for access\n\n"
            "This action cannot be undone.",
            view=ConfirmDeletion(),
            ephemeral=True
        )

    @app_commands.command(name="data_info")
    async def show_data_info(self, interaction: discord.Interaction):
        """Show what data is stored about you"""
        user_id = str(interaction.user.id)
        user_data = self.db.get_user_data(user_id)

        if not user_data:
            await interaction.response.send_message(
                "No verification data found for your account.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Your Data Information",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        embed.add_field(
            name="Verification Status",
            value=user_data['status'],
            inline=False
        )

        embed.add_field(
            name="Last Verification",
            value=user_data['last_verification'].strftime("%Y-%m-%d %H:%M:%S"),
            inline=True
        )

        embed.add_field(
            name="Data Retention",
            value=f"Media will be deleted on {user_data['deletion_date'].strftime('%Y-%m-%d')}",
            inline=True
        )

        embed.add_field(
            name="Your Rights",
            value="• Request data deletion with `/delete_data`\n"
                  "• View privacy policy with `/privacy`\n"
                  "• Submit concerns to staff",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="consent_status")
    async def check_consent_status(self, interaction: discord.Interaction):
        """Check your current consent status"""
        user_id = str(interaction.user.id)
        consent_status = self.db.get_consent_status(user_id)

        embed = discord.Embed(
            title="Consent Status",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        if consent_status:
            embed.description = (
                "✅ You have provided consent for:\n"
                "• Data collection for age verification\n"
                "• Secure storage of verification media\n"
                "• Staff review of verification\n\n"
                "You can withdraw consent at any time using `/delete_data`"
            )
            embed.add_field(
                name="Consent Date",
                value=consent_status['consent_date'].strftime("%Y-%m-%d %H:%M:%S"),
                inline=True
            )
        else:
            embed.description = (
                "❌ No consent record found.\n"
                "You will need to provide consent during verification."
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Privacy(bot))
