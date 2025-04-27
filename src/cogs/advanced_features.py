import discord
from discord.ext import commands
import json
import logging
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import matplotlib.pyplot as plt
import io
import numpy as np
from collections import defaultdict
from ..utils.database import Database

logger = logging.getLogger('age-verify-bot')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

class AdvancedFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.verification_queue = []
        self.staff_workload = defaultdict(int)
        self.staff_performance = defaultdict(lambda: {'total': 0, 'accurate': 0})
        self.training_progress = defaultdict(dict)
        
        # Start background tasks
        self.bg_tasks = [
            bot.loop.create_task(self.update_queue_status()),
            bot.loop.create_task(self.analyze_staff_performance()),
            bot.loop.create_task(self.check_training_requirements())
        ]

    def cog_unload(self):
        for task in self.bg_tasks:
            task.cancel()

    async def update_queue_status(self):
        """Update queue status and notify users of wait times"""
        while True:
            try:
                if self.verification_queue:
                    avg_wait_time = self.calculate_average_wait_time()
                    for position, user_id in enumerate(self.verification_queue, 1):
                        user = self.bot.get_user(int(user_id))
                        if user:
                            est_wait = avg_wait_time * position
                            await user.send(
                                f"Queue Update:\n"
                                f"Position: {position}/{len(self.verification_queue)}\n"
                                f"Estimated wait: {est_wait:.1f} minutes"
                            )
            except Exception as e:
                logger.error(f"Error updating queue status: {e}")
            await asyncio.sleep(300)  # Update every 5 minutes

    def calculate_average_wait_time(self):
        """Calculate average verification wait time"""
        recent_verifications = self.db.get_recent_verifications(hours=24)
        if not recent_verifications:
            return 15  # Default estimate
        
        wait_times = [v.review_time - v.submit_time for v in recent_verifications]
        return sum(wait_times, timedelta()).total_seconds() / (60 * len(wait_times))

    @app_commands.command(name="queue_status")
    async def show_queue_status(self, interaction: discord.Interaction):
        """Show current verification queue status"""
        embed = discord.Embed(
            title="Verification Queue Status",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        queue_length = len(self.verification_queue)
        avg_wait = self.calculate_average_wait_time()
        
        embed.add_field(
            name="Queue Length",
            value=f"{queue_length} pending verifications",
            inline=False
        )
        embed.add_field(
            name="Average Wait Time",
            value=f"{avg_wait:.1f} minutes",
            inline=True
        )
        embed.add_field(
            name="Active Staff",
            value=f"{len(self.staff_workload)} reviewing",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="staff_dashboard")
    @app_commands.checks.has_permissions(administrator=True)
    async def show_staff_dashboard(self, interaction: discord.Interaction):
        """Show staff performance dashboard"""
        embed = discord.Embed(
            title="Staff Performance Dashboard",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for staff_id, stats in self.staff_performance.items():
            staff_member = interaction.guild.get_member(int(staff_id))
            if staff_member:
                accuracy = (stats['accurate'] / stats['total'] * 100) if stats['total'] > 0 else 0
                embed.add_field(
                    name=staff_member.display_name,
                    value=f"Reviews: {stats['total']}\n"
                          f"Accuracy: {accuracy:.1f}%\n"
                          f"Current Load: {self.staff_workload[staff_id]}",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="training_module")
    @app_commands.checks.has_permissions(administrator=True)
    async def start_training_module(self, interaction: discord.Interaction):
        """Start staff training module"""
        class TrainingView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.current_module = 0
                self.modules = [
                    "Age Verification Guidelines",
                    "Privacy and Data Handling",
                    "Decision Making Process",
                    "Handling Edge Cases"
                ]

            @discord.ui.button(label="Next Module", style=discord.ButtonStyle.primary)
            async def next_module(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                self.current_module += 1
                if self.current_module >= len(self.modules):
                    await button_interaction.response.edit_message(
                        content="Training completed! You can now review verifications.",
                        view=None
                    )
                    return

                await button_interaction.response.edit_message(
                    content=f"Module {self.current_module + 1}: {self.modules[self.current_module]}",
                    view=self
                )

        await interaction.response.send_message(
            "Welcome to Staff Training!\n"
            f"Module 1: {TrainingView().modules[0]}",
            view=TrainingView(),
            ephemeral=True
        )

    @app_commands.command(name="analytics")
    @app_commands.checks.has_permissions(administrator=True)
    async def show_analytics(self, interaction: discord.Interaction):
        """Show advanced analytics"""
        # Create analytics graphs
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        # Verification trends
        dates, counts = zip(*self.db.get_verification_trends())
        ax1.plot(dates, counts)
        ax1.set_title("Verification Trends")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Verifications")
        
        # Age distribution
        ages, age_counts = zip(*self.db.get_age_distribution())
        ax2.bar(ages, age_counts)
        ax2.set_title("Age Distribution")
        ax2.set_xlabel("Age")
        ax2.set_ylabel("Count")
        
        # Save plot to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        # Create file
        file = discord.File(buf, filename="analytics.png")
        
        # Create embed
        embed = discord.Embed(
            title="Advanced Analytics",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_image(url="attachment://analytics.png")
        
        # Add statistics
        stats = self.db.get_advanced_stats()
        embed.add_field(
            name="Peak Hours",
            value=stats['peak_hours'],
            inline=True
        )
        embed.add_field(
            name="Average Processing Time",
            value=f"{stats['avg_processing_time']:.1f} minutes",
            inline=True
        )
        embed.add_field(
            name="Approval Rate",
            value=f"{stats['approval_rate']:.1f}%",
            inline=True
        )
        
        await interaction.response.send_message(
            embed=embed,
            file=file,
            ephemeral=True
        )

    async def analyze_staff_performance(self):
        """Analyze and update staff performance metrics"""
        while True:
            try:
                for staff_id in self.staff_performance:
                    recent_reviews = self.db.get_staff_reviews(staff_id, hours=24)
                    accurate = sum(1 for r in recent_reviews if r.accurate)
                    self.staff_performance[staff_id].update({
                        'total': len(recent_reviews),
                        'accurate': accurate
                    })
            except Exception as e:
                logger.error(f"Error analyzing staff performance: {e}")
            await asyncio.sleep(3600)  # Update hourly

    async def check_training_requirements(self):
        """Check and notify staff about training requirements"""
        while True:
            try:
                staff_role = discord.utils.get(
                    self.bot.guilds[0].roles,
                    name=config['roles']['staff']
                )
                if staff_role:
                    for member in staff_role.members:
                        if member.id not in self.training_progress:
                            await member.send(
                                "You have pending staff training modules. "
                                "Use `/training_module` to begin."
                            )
            except Exception as e:
                logger.error(f"Error checking training requirements: {e}")
            await asyncio.sleep(86400)  # Check daily

async def setup(bot):
    await bot.add_cog(AdvancedFeatures(bot))
