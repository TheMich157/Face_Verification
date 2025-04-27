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

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.lockdown = config['moderation']['lockdown_mode']
        self.raid_protection_triggered = False
        self.join_times = []
        self.background_tasks = []
        
        # Start background tasks
        if config['features']['auto_kick_unverified']:
            self.background_tasks.append(bot.loop.create_task(self.check_unverified_members()))
        if config['features']['verification_reminders']:
            self.background_tasks.append(bot.loop.create_task(self.send_verification_reminders()))

    def cog_unload(self):
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()

    async def check_unverified_members(self):
        """Background task to kick unverified members after specified days"""
        while True:
            try:
                for guild in self.bot.guilds:
                    unverified_role = discord.utils.get(
                        guild.roles,
                        name=config['roles']['unverified']
                    )
                    if unverified_role:
                        kick_days = config['verification_settings']['auto_kick_unverified_days']
                        cutoff_date = datetime.now() - timedelta(days=kick_days)
                        
                        for member in unverified_role.members:
                            if member.joined_at and member.joined_at < cutoff_date:
                                try:
                                    # Send kick message
                                    kick_msg = config['moderation']['kick_message'].format(days=kick_days)
                                    await member.send(kick_msg)
                                    # Kick member
                                    await member.kick(reason=f"Not verified within {kick_days} days")
                                    # Log action
                                    await self.log_mod_action(
                                        guild,
                                        f"Kicked {member} for not verifying within {kick_days} days"
                                    )
                                except discord.Forbidden:
                                    logger.error(f"Failed to kick unverified member {member.id}")
                
                # Check every 12 hours
                await asyncio.sleep(43200)
            except Exception as e:
                logger.error(f"Error in check_unverified_members: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def send_verification_reminders(self):
        """Background task to send verification reminders"""
        while True:
            try:
                reminder_days = config['moderation']['verification_reminder_days']
                for guild in self.bot.guilds:
                    unverified_role = discord.utils.get(
                        guild.roles,
                        name=config['roles']['unverified']
                    )
                    if unverified_role:
                        for member in unverified_role.members:
                            if member.joined_at:
                                days_since_join = (datetime.now() - member.joined_at).days
                                if days_since_join in reminder_days:
                                    try:
                                        await member.send(
                                            f"Reminder: You still need to complete age verification. "
                                            f"Use `/verify` to start the process. You have "
                                            f"{config['verification_settings']['auto_kick_unverified_days'] - days_since_join} "
                                            f"days remaining before automatic kick."
                                        )
                                    except discord.Forbidden:
                                        pass
                
                # Check every 12 hours
                await asyncio.sleep(43200)
            except Exception as e:
                logger.error(f"Error in send_verification_reminders: {e}")
                await asyncio.sleep(300)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle raid protection"""
        if config['features']['raid_protection']:
            now = datetime.now()
            self.join_times.append(now)
            
            # Remove join times older than 10 minutes
            self.join_times = [t for t in self.join_times if (now - t).seconds < 600]
            
            # Check for potential raid (10+ joins in 1 minute)
            recent_joins = len([t for t in self.join_times if (now - t).seconds < 60])
            if recent_joins >= 10 and not self.raid_protection_triggered:
                self.raid_protection_triggered = True
                await self.enable_lockdown(member.guild, "Raid protection triggered")
                
                # Reset after 30 minutes
                await asyncio.sleep(1800)
                self.raid_protection_triggered = False
                if self.lockdown:
                    await self.disable_lockdown(member.guild, "Raid protection cooldown ended")

    async def log_mod_action(self, guild, message):
        """Log moderation actions"""
        log_channel = discord.utils.get(
            guild.channels,
            name=config['channels']['mod_logs']
        )
        if log_channel:
            embed = discord.Embed(
                title="Moderation Action",
                description=message,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            await log_channel.send(embed=embed)

    @app_commands.command(name="lockdown")
    @app_commands.checks.has_permissions(administrator=True)
    async def toggle_lockdown(self, interaction: discord.Interaction):
        """Toggle server lockdown mode"""
        self.lockdown = not self.lockdown
        if self.lockdown:
            await self.enable_lockdown(interaction.guild, "Manual lockdown enabled")
        else:
            await self.disable_lockdown(interaction.guild, "Manual lockdown disabled")
        
        await interaction.response.send_message(
            f"Lockdown mode {'enabled' if self.lockdown else 'disabled'}",
            ephemeral=True
        )

    async def enable_lockdown(self, guild, reason):
        """Enable lockdown mode"""
        try:
            # Update verification settings
            config['moderation']['lockdown_mode'] = True
            
            # Disable verification commands
            self.bot.get_cog('Verification').verification_enabled = False
            
            # Log action
            await self.log_mod_action(guild, f"🔒 Lockdown enabled: {reason}")
            
            # Notify staff
            staff_channel = discord.utils.get(
                guild.channels,
                name=config['channels']['staff_chat']
            )
            if staff_channel:
                await staff_channel.send(
                    f"⚠️ Server lockdown enabled: {reason}\n"
                    "All verification attempts will be blocked until lockdown is lifted."
                )
        except Exception as e:
            logger.error(f"Error enabling lockdown: {e}")

    async def disable_lockdown(self, guild, reason):
        """Disable lockdown mode"""
        try:
            # Update verification settings
            config['moderation']['lockdown_mode'] = False
            
            # Enable verification commands
            self.bot.get_cog('Verification').verification_enabled = True
            
            # Log action
            await self.log_mod_action(guild, f"🔓 Lockdown disabled: {reason}")
            
            # Notify staff
            staff_channel = discord.utils.get(
                guild.channels,
                name=config['channels']['staff_chat']
            )
            if staff_channel:
                await staff_channel.send(
                    f"✅ Server lockdown disabled: {reason}\n"
                    "Verification system is now active again."
                )
        except Exception as e:
            logger.error(f"Error disabling lockdown: {e}")

    @app_commands.command(name="bulk_verify")
    @app_commands.checks.has_permissions(administrator=True)
    async def bulk_verify(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        """Bulk verify all members with a specific role"""
        if not config['features']['bulk_verification']:
            await interaction.response.send_message(
                "Bulk verification is disabled in config.",
                ephemeral=True
            )
            return

        verified_role = discord.utils.get(
            interaction.guild.roles,
            name=config['roles']['verified']
        )
        
        if not verified_role:
            await interaction.response.send_message(
                "Verified role not found.",
                ephemeral=True
            )
            return

        count = 0
        for member in role.members:
            if verified_role not in member.roles:
                try:
                    await member.add_roles(verified_role)
                    count += 1
                except discord.Forbidden:
                    continue

        await interaction.response.send_message(
            f"✅ Bulk verified {count} members with the {role.name} role.",
            ephemeral=True
        )
        
        # Log action
        await self.log_mod_action(
            interaction.guild,
            f"Bulk verification: {count} members verified from role {role.name} "
            f"by {interaction.user.mention}"
        )

async def setup(bot):
    await bot.add_cog(Moderation(bot))
