import discord
from discord.ext import commands
import logging
from discord import app_commands
import io
from datetime import datetime
from ..utils.database import Database

logger = logging.getLogger('age-verify-bot')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @app_commands.command(name="pending_reviews")
    @app_commands.checks.has_permissions(administrator=True)
    async def pending_reviews(self, interaction: discord.Interaction):
        """Show pending verification reviews"""
        # Get all members with awaiting_review role
        awaiting_role = discord.utils.get(
            interaction.guild.roles,
            name=config['roles']['awaiting_review']
        )
        
        if not awaiting_role or not awaiting_role.members:
            await interaction.response.send_message(
                "No pending verifications to review.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Pending Age Verification Reviews",
            color=discord.Color.blue(),
            description=f"Total pending reviews: {len(awaiting_role.members)}"
        )

        for member in awaiting_role.members[:10]:  # Show first 10 pending reviews
            verification = self.db.get_latest_verification(str(member.id))
            if verification:
                embed.add_field(
                    name=f"User: {member.name}#{member.discriminator}",
                    value=f"ID: {member.id}\n"
                          f"Estimated Age: {verification.estimated_age:.1f}\n"
                          f"Joined: {member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}",
                    inline=False
                )

        if len(awaiting_role.members) > 10:
            embed.set_footer(text=f"And {len(awaiting_role.members) - 10} more...")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="view_verification")
    @app_commands.checks.has_permissions(administrator=True)
    async def view_verification(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """View a user's verification submission"""
        verification = self.db.get_latest_verification(str(user.id))
        
        if not verification:
            await interaction.response.send_message(
                "No verification submission found for this user.",
                ephemeral=True
            )
            return

        # Create file object from stored media
        file = discord.File(
            io.BytesIO(verification.media_data),
            filename=f"verification_{verification.id}.{verification.media_type}"
        )

        embed = discord.Embed(
            title=f"Verification Review - {user.name}#{user.discriminator}",
            color=discord.Color.blue()
        )
        embed.add_field(name="User ID", value=user.id, inline=True)
        embed.add_field(name="Estimated Age", value=f"{verification.estimated_age:.1f}", inline=True)
        embed.add_field(
            name="Submitted",
            value=verification.submission_date.strftime('%Y-%m-%d %H:%M:%S'),
            inline=True
        )

        # Create review buttons
        class ReviewButtons(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)  # 5 minute timeout

            @discord.ui.button(label="Not Underage", style=discord.ButtonStyle.green)
            async def verify(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await self.handle_review(button_interaction, False)

            @discord.ui.button(label="Underage - Ban", style=discord.ButtonStyle.red)
            async def ban(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await self.handle_review(button_interaction, True)

            async def handle_review(self, button_interaction: discord.Interaction, is_underage: bool):
                # Use the review command from verification cog
                verification_cog = button_interaction.client.get_cog('Verification')
                if verification_cog:
                    await verification_cog.review_user(button_interaction, user, is_underage)
                else:
                    await button_interaction.response.send_message(
                        "❌ Error: Verification system not available.",
                        ephemeral=True
                    )

        await interaction.response.send_message(
            embed=embed,
            file=file,
            view=ReviewButtons(),
            ephemeral=True
        )

    @app_commands.command(name="stats")
    @app_commands.checks.has_permissions(administrator=True)
    async def verification_stats(self, interaction: discord.Interaction):
        """Show verification statistics"""
        guild = interaction.guild
        
        # Get role counts
        verified_role = discord.utils.get(guild.roles, name=config['roles']['verified'])
        awaiting_role = discord.utils.get(guild.roles, name=config['roles']['awaiting_review'])
        
        verified_count = len(verified_role.members) if verified_role else 0
        awaiting_count = len(awaiting_role.members) if awaiting_role else 0
        
        # Get ban count for today
        ban_entries = []
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=None):
            if (datetime.now() - entry.created_at).days < 1:
                ban_entries.append(entry)

        embed = discord.Embed(
            title="Age Verification Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Verified Members", value=str(verified_count), inline=True)
        embed.add_field(name="Awaiting Review", value=str(awaiting_count), inline=True)
        embed.add_field(name="Bans Today", value=str(len(ban_entries)), inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
