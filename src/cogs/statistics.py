import discord
from discord.ext import commands
import json
import logging
from discord import app_commands
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import numpy as np
from ..utils.database import Database

logger = logging.getLogger('age-verify-bot')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    def create_graph(self, data, title, xlabel, ylabel):
        """Create a graph from the provided data"""
        plt.figure(figsize=(10, 6))
        plt.plot(data[0], data[1], marker='o')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        
        # Save plot to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        return buf

    @app_commands.command(name="verification_stats")
    @app_commands.checks.has_permissions(administrator=True)
    async def verification_stats(self, interaction: discord.Interaction):
        """Show detailed verification statistics"""
        guild = interaction.guild
        
        # Get role counts
        verified_role = discord.utils.get(guild.roles, name=config['roles']['verified'])
        unverified_role = discord.utils.get(guild.roles, name=config['roles']['unverified'])
        awaiting_role = discord.utils.get(guild.roles, name=config['roles']['awaiting_review'])
        
        verified_count = len(verified_role.members) if verified_role else 0
        unverified_count = len(unverified_role.members) if unverified_role else 0
        awaiting_count = len(awaiting_role.members) if awaiting_role else 0
        
        # Calculate percentages
        total_members = guild.member_count
        verified_percent = (verified_count / total_members * 100) if total_members > 0 else 0
        
        # Get verification trends for the last 7 days
        now = datetime.now()
        daily_stats = []
        for i in range(7):
            date = now - timedelta(days=i)
            verifications = self.db.get_verifications_for_date(date)
            daily_stats.append((date, len(verifications)))
        
        # Create verification trend graph
        dates, counts = zip(*daily_stats)
        graph_buf = self.create_graph(
            (dates, counts),
            "Verification Trend - Last 7 Days",
            "Date",
            "Verifications"
        )

        # Create embed
        embed = discord.Embed(
            title="Detailed Verification Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # Current Status
        embed.add_field(
            name="Current Status",
            value=f"Total Members: {total_members}\n"
                  f"Verified: {verified_count} ({verified_percent:.1f}%)\n"
                  f"Unverified: {unverified_count}\n"
                  f"Awaiting Review: {awaiting_count}",
            inline=False
        )
        
        # Today's Stats
        today_stats = self.db.get_todays_stats()
        embed.add_field(
            name="Today's Activity",
            value=f"Submissions: {today_stats['submissions']}\n"
                  f"Approvals: {today_stats['approvals']}\n"
                  f"Rejections: {today_stats['rejections']}\n"
                  f"Pending: {today_stats['pending']}",
            inline=False
        )
        
        # Average Processing Time
        avg_time = self.db.get_average_processing_time()
        embed.add_field(
            name="Processing Time",
            value=f"Average: {avg_time:.1f} minutes",
            inline=False
        )

        # Create file from graph buffer
        graph_file = discord.File(graph_buf, filename="verification_trend.png")
        embed.set_image(url="attachment://verification_trend.png")

        await interaction.response.send_message(
            embed=embed,
            file=graph_file,
            ephemeral=True
        )

    @app_commands.command(name="age_distribution")
    @app_commands.checks.has_permissions(administrator=True)
    async def age_distribution(self, interaction: discord.Interaction):
        """Show age distribution of verified members"""
        # Get age data from database
        age_data = self.db.get_age_distribution()
        
        if not age_data:
            await interaction.response.send_message(
                "No age data available.",
                ephemeral=True
            )
            return

        # Create age distribution graph
        plt.figure(figsize=(10, 6))
        ages, counts = zip(*age_data)
        plt.bar(ages, counts)
        plt.title("Age Distribution of Verified Members")
        plt.xlabel("Estimated Age")
        plt.ylabel("Number of Members")
        
        # Save plot to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        # Create embed
        embed = discord.Embed(
            title="Age Distribution",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # Calculate statistics
        all_ages = [age for age, count in age_data for _ in range(count)]
        avg_age = np.mean(all_ages)
        median_age = np.median(all_ages)
        
        embed.add_field(
            name="Statistics",
            value=f"Average Age: {avg_age:.1f}\n"
                  f"Median Age: {median_age:.1f}\n"
                  f"Total Samples: {len(all_ages)}",
            inline=False
        )
        
        # Create file from graph buffer
        graph_file = discord.File(buf, filename="age_distribution.png")
        embed.set_image(url="attachment://age_distribution.png")
        
        await interaction.response.send_message(
            embed=embed,
            file=graph_file,
            ephemeral=True
        )

    @app_commands.command(name="staff_stats")
    @app_commands.checks.has_permissions(administrator=True)
    async def staff_stats(self, interaction: discord.Interaction):
        """Show staff review statistics"""
        # Get staff review data
        staff_data = self.db.get_staff_review_stats()
        
        if not staff_data:
            await interaction.response.send_message(
                "No staff review data available.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="Staff Review Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for staff_id, stats in staff_data.items():
            staff_member = interaction.guild.get_member(int(staff_id))
            if staff_member:
                embed.add_field(
                    name=f"Staff: {staff_member.display_name}",
                    value=f"Reviews: {stats['total']}\n"
                          f"Approvals: {stats['approvals']}\n"
                          f"Rejections: {stats['rejections']}\n"
                          f"Avg Time: {stats['avg_time']:.1f} min",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="export_stats")
    @app_commands.checks.has_permissions(administrator=True)
    async def export_stats(self, interaction: discord.Interaction):
        """Export verification statistics to CSV"""
        stats_data = self.db.export_verification_stats()
        
        # Create CSV in memory
        buf = io.StringIO()
        buf.write("Date,Submissions,Approvals,Rejections,Average Processing Time\n")
        for entry in stats_data:
            buf.write(f"{entry['date']},{entry['submissions']},"
                     f"{entry['approvals']},{entry['rejections']},"
                     f"{entry['avg_time']}\n")
        
        # Convert to bytes
        bytes_buf = io.BytesIO(buf.getvalue().encode())
        
        # Create file
        file = discord.File(bytes_buf, filename="verification_stats.csv")
        
        await interaction.response.send_message(
            "Here are the exported verification statistics:",
            file=file,
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Statistics(bot))
