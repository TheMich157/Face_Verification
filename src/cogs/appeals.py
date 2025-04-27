import discord
from discord.ext import commands
import json
import logging
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
from ..utils.database import Database

logger = logging.getLogger('age-verify-bot')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

class Appeals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.appeal_cooldowns = {}

    @app_commands.command(name="appeal")
    async def appeal_verification(self, interaction: discord.Interaction):
        """Submit an appeal for age verification ban"""
        
        # Check if user is in cooldown
        if interaction.user.id in self.appeal_cooldowns:
            cooldown_end = self.appeal_cooldowns[interaction.user.id]
            if datetime.now() < cooldown_end:
                days_left = (cooldown_end - datetime.now()).days
                await interaction.response.send_message(
                    f"You must wait {days_left} days before submitting another appeal.",
                    ephemeral=True
                )
                return

        # Create appeal form
        class AppealModal(discord.ui.Modal, title='Age Verification Appeal'):
            reason = discord.ui.TextInput(
                label='Why were you banned?',
                style=discord.TextStyle.paragraph,
                required=True
            )
            actual_age = discord.ui.TextInput(
                label='What is your actual age?',
                required=True
            )
            proof = discord.ui.TextInput(
                label='Provide proof of age (if possible)',
                style=discord.TextStyle.paragraph,
                required=False
            )
            reconsideration = discord.ui.TextInput(
                label='Why should we reconsider?',
                style=discord.TextStyle.paragraph,
                required=True
            )

            async def on_submit(self, modal_interaction: discord.Interaction):
                # Check for auto-deny keywords
                for keyword in config['appeals']['auto_deny_keywords']:
                    if keyword.lower() in self.reason.value.lower():
                        await modal_interaction.response.send_message(
                            "Your appeal has been automatically denied due to inappropriate content.",
                            ephemeral=True
                        )
                        return

                # Create appeal embed
                embed = discord.Embed(
                    title="New Verification Appeal",
                    color=discord.Color.yellow(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="User", value=f"{modal_interaction.user.mention} ({modal_interaction.user.id})", inline=False)
                embed.add_field(name="Reason for Ban", value=self.reason.value, inline=False)
                embed.add_field(name="Claimed Age", value=self.actual_age.value, inline=False)
                if self.proof.value:
                    embed.add_field(name="Proof Provided", value=self.proof.value, inline=False)
                embed.add_field(name="Reconsideration Reason", value=self.reconsideration.value, inline=False)

                # Send to appeals channel
                appeals_channel = discord.utils.get(
                    modal_interaction.guild.channels,
                    name=config['channels']['appeals']
                )
                if appeals_channel:
                    appeal_msg = await appeals_channel.send(
                        content="@here New verification appeal",
                        embed=embed,
                        view=AppealButtons()
                    )

                    # Store appeal in database
                    self.db.add_appeal(
                        user_id=str(modal_interaction.user.id),
                        appeal_msg_id=str(appeal_msg.id),
                        reason=self.reason.value,
                        claimed_age=self.actual_age.value,
                        proof=self.proof.value,
                        reconsideration=self.reconsideration.value
                    )

                await modal_interaction.response.send_message(
                    "Your appeal has been submitted and will be reviewed by our staff team.",
                    ephemeral=True
                )

        await interaction.response.send_modal(AppealModal())

    class AppealButtons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
        async def accept_appeal(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "You don't have permission to handle appeals.",
                    ephemeral=True
                )
                return

            embed = interaction.message.embeds[0]
            user_id = int(embed.fields[0].value.split('(')[1].strip(')'))
            
            try:
                # Unban user
                await interaction.guild.unban(
                    discord.Object(id=user_id),
                    reason="Appeal accepted"
                )
                
                # Update embed
                embed.color = discord.Color.green()
                embed.add_field(
                    name="Appeal Status",
                    value=f"Accepted by {interaction.user.mention}",
                    inline=False
                )
                await interaction.message.edit(embed=embed, view=None)

                # Notify user
                try:
                    user = await interaction.client.fetch_user(user_id)
                    await user.send(config['custom_messages']['appeal_accepted'])
                except discord.Forbidden:
                    logger.warning(f"Could not DM user {user_id} about appeal acceptance")

                await interaction.response.send_message(
                    f"Appeal accepted. User {user_id} has been unbanned.",
                    ephemeral=True
                )

            except discord.NotFound:
                await interaction.response.send_message(
                    "Error: User not found in ban list.",
                    ephemeral=True
                )

        @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
        async def deny_appeal(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "You don't have permission to handle appeals.",
                    ephemeral=True
                )
                return

            embed = interaction.message.embeds[0]
            user_id = int(embed.fields[0].value.split('(')[1].strip(')'))

            # Update embed
            embed.color = discord.Color.red()
            embed.add_field(
                name="Appeal Status",
                value=f"Denied by {interaction.user.mention}",
                inline=False
            )
            await interaction.message.edit(embed=embed, view=None)

            # Set cooldown
            cooldown_days = config['appeals']['cooldown_days']
            self.appeal_cooldowns[user_id] = datetime.now() + timedelta(days=cooldown_days)

            # Notify user
            try:
                user = await interaction.client.fetch_user(user_id)
                await user.send(
                    config['custom_messages']['appeal_denied'].format(days=cooldown_days)
                )
            except discord.Forbidden:
                logger.warning(f"Could not DM user {user_id} about appeal denial")

            await interaction.response.send_message(
                f"Appeal denied. User {user_id} has been notified.",
                ephemeral=True
            )

    @app_commands.command(name="appeal_stats")
    @app_commands.checks.has_permissions(administrator=True)
    async def appeal_stats(self, interaction: discord.Interaction):
        """View appeal statistics"""
        stats = self.db.get_appeal_stats()
        
        embed = discord.Embed(
            title="Appeal Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Total Appeals", value=str(stats['total']), inline=True)
        embed.add_field(name="Accepted", value=str(stats['accepted']), inline=True)
        embed.add_field(name="Denied", value=str(stats['denied']), inline=True)
        embed.add_field(name="Pending", value=str(stats['pending']), inline=True)
        
        if stats['total'] > 0:
            accept_rate = (stats['accepted'] / stats['total']) * 100
            embed.add_field(
                name="Acceptance Rate",
                value=f"{accept_rate:.1f}%",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Appeals(bot))
