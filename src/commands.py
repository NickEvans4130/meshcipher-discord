import discord
from discord import app_commands
from discord.ext import commands
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import *


class BugModal(discord.ui.Modal, title='Report a Bug'):
    device = discord.ui.TextInput(
        label='Device Model',
        placeholder='e.g., Samsung Galaxy S23',
        required=True
    )

    android_version = discord.ui.TextInput(
        label='Android Version',
        placeholder='e.g., Android 14',
        required=True
    )

    description = discord.ui.TextInput(
        label='What happened?',
        style=discord.TextStyle.paragraph,
        placeholder='Describe the bug...',
        required=True,
        max_length=1000
    )

    steps = discord.ui.TextInput(
        label='Steps to Reproduce',
        style=discord.TextStyle.paragraph,
        placeholder='1. Open app\n2. Tap...\n3. Bug occurs',
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title='Bug Report',
            description=self.description.value,
            color=COLOR_ERROR,
            timestamp=datetime.now()
        )
        embed.add_field(name='Device', value=self.device.value, inline=True)
        embed.add_field(name='Android', value=self.android_version.value, inline=True)
        embed.add_field(name='Reporter', value=interaction.user.mention, inline=True)

        if self.steps.value:
            embed.add_field(name='Steps to Reproduce', value=self.steps.value, inline=False)

        embed.set_footer(text=f'Bug ID: {interaction.id}')

        channel = interaction.guild.get_channel(CHANNEL_BUG_REPORTS)
        if channel:
            message = await channel.send(embed=embed)

            await message.add_reaction(EMOJI_SEEN)
            await message.add_reaction(EMOJI_INVESTIGATING)
            await message.add_reaction(EMOJI_FIXED)
            await message.add_reaction(EMOJI_CANT_REPRODUCE)

            save_bug(interaction.id, {
                'reporter': str(interaction.user),
                'device': self.device.value,
                'android': self.android_version.value,
                'description': self.description.value,
                'steps': self.steps.value,
                'timestamp': datetime.now().isoformat(),
                'message_id': message.id
            })

            await interaction.response.send_message(
                f'Bug report submitted! Check <#{CHANNEL_BUG_REPORTS}>',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                'Could not find bug reports channel',
                ephemeral=True
            )


def save_bug(bug_id, data):
    os.makedirs('data', exist_ok=True)
    try:
        with open('data/bugs.json', 'r') as f:
            bugs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bugs = {}

    bugs[str(bug_id)] = data

    with open('data/bugs.json', 'w') as f:
        json.dump(bugs, f, indent=2)


def save_feature(feature_id, data):
    os.makedirs('data', exist_ok=True)
    try:
        with open('data/features.json', 'r') as f:
            features = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        features = {}

    features[str(feature_id)] = data

    with open('data/features.json', 'w') as f:
        json.dump(features, f, indent=2)


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='bug', description='Report a bug')
    async def bug(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BugModal())

    @app_commands.command(name='release', description='Announce a new version')
    @app_commands.describe(
        version='Version number (e.g., v1.0.1)',
        changes='What changed? (separate with newlines)'
    )
    async def release(self, interaction: discord.Interaction, version: str, changes: str):
        if ROLE_DEVELOPER not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(
                'Only developers can use this command',
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f'MeshCipher {version} Released',
            color=COLOR_SUCCESS,
            timestamp=datetime.now()
        )

        change_lines = [line.strip() for line in changes.split('\n') if line.strip()]
        if change_lines:
            embed.add_field(
                name='What\'s New',
                value='\n'.join(f'- {line}' for line in change_lines),
                inline=False
            )

        embed.add_field(
            name='Download',
            value='https://github.com/NickEvans4130/MeshCipher/releases/latest',
            inline=False
        )

        embed.add_field(
            name='Found a Bug?',
            value=f'Use `/bug` or post in <#{CHANNEL_BUG_REPORTS}>',
            inline=False
        )

        embed.set_footer(text='MeshCipher Beta')

        channel = interaction.guild.get_channel(CHANNEL_ANNOUNCEMENTS)
        if channel:
            role = interaction.guild.get_role(ROLE_BETA_TESTER)
            await channel.send(
                content=role.mention if role else '@everyone',
                embed=embed
            )

            await interaction.response.send_message(
                'Release announcement posted!',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                'Could not find announcements channel',
                ephemeral=True
            )

    @app_commands.command(name='stats', description='Show beta testing statistics')
    async def stats(self, interaction: discord.Interaction):
        try:
            with open('data/bugs.json', 'r') as f:
                bugs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            bugs = {}

        try:
            with open('data/features.json', 'r') as f:
                features = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            features = {}

        guild = interaction.guild
        beta_testers = len([m for m in guild.members if ROLE_BETA_TESTER in [r.id for r in m.roles]])

        embed = discord.Embed(
            title='MeshCipher Beta Stats',
            color=COLOR_INFO,
            timestamp=datetime.now()
        )

        embed.add_field(name='Beta Testers', value=str(beta_testers), inline=True)
        embed.add_field(name='Bug Reports', value=str(len(bugs)), inline=True)
        embed.add_field(name='Feature Requests', value=str(len(features)), inline=True)

        embed.set_footer(text='Thanks for testing!')

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='help', description='Show bot commands')
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title='MeshCipher Bot Commands',
            description='Available commands for beta testers',
            color=COLOR_INFO
        )

        embed.add_field(
            name='`/bug`',
            value='Report a bug with structured form',
            inline=False
        )

        embed.add_field(
            name='`/stats`',
            value='Show beta testing statistics',
            inline=False
        )

        embed.add_field(
            name='`/release` (Dev only)',
            value='Announce a new version',
            inline=False
        )

        embed.add_field(
            name='`/gh-issue` (Dev only)',
            value='Create GitHub issue from a bug report',
            inline=False
        )

        embed.add_field(
            name='Tip',
            value='Just ask questions in support channels - I auto-respond to common questions!',
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='guide', description='Post guide embeds in their relevant channels')
    async def guide(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                'Only the server owner can use this command',
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        posted = []

        # Bug reporting -> #bug-reports
        ch = guild.get_channel(CHANNEL_BUG_REPORTS)
        if ch:
            embed = discord.Embed(
                title='How Bug Reporting Works',
                color=COLOR_ERROR
            )
            embed.add_field(
                name='Reporting a Bug',
                value=(
                    'Use the `/bug` command anywhere in the server. '
                    'A form will pop up asking for your device model, Android version, '
                    'a description of the bug, and steps to reproduce it.'
                ),
                inline=False
            )
            embed.add_field(
                name='Tracking',
                value=(
                    'Each report gets these status reactions:\n'
                    f'{EMOJI_SEEN} Seen | {EMOJI_INVESTIGATING} Investigating | '
                    f'{EMOJI_FIXED} Fixed | {EMOJI_CANT_REPRODUCE} Can\'t Reproduce\n\n'
                    'Developers will react to update the status. '
                    'You can also use `/gh-issue` (dev only) to create a GitHub issue from a report.'
                ),
                inline=False
            )
            await ch.send(embed=embed)
            posted.append(f'<#{CHANNEL_BUG_REPORTS}>')

        # Feature requests -> #feature-requests
        ch = guild.get_channel(CHANNEL_FEATURE_REQUESTS)
        if ch:
            embed = discord.Embed(
                title='How Feature Requests Work',
                color=COLOR_INFO
            )
            embed.add_field(
                name='Suggesting a Feature',
                value=(
                    'Post your idea as a message in this channel. '
                    'The bot will automatically add voting reactions.'
                ),
                inline=False
            )
            embed.add_field(
                name='Voting',
                value=(
                    f'{EMOJI_UPVOTE} Want this | {EMOJI_DOWNVOTE} Don\'t need this | '
                    f'{EMOJI_FIRE} High priority\n\n'
                    'The most popular requests help shape what gets built next.'
                ),
                inline=False
            )
            await ch.send(embed=embed)
            posted.append(f'<#{CHANNEL_FEATURE_REQUESTS}>')

        # Getting started -> #getting-started
        ch = guild.get_channel(CHANNEL_GETTING_STARTED)
        if ch:
            embed = discord.Embed(
                title='Welcome to MeshCipher Beta',
                color=COLOR_SUCCESS
            )
            embed.add_field(
                name='1. Download the APK',
                value='Grab the latest build from https://github.com/NickEvans4130/MeshCipher/releases/latest',
                inline=False
            )
            embed.add_field(
                name='2. Set Up Your Identity',
                value='Open the app and your hardware-bound encryption keys are generated automatically.',
                inline=False
            )
            embed.add_field(
                name='3. Add a Contact',
                value='Scan each other\'s QR codes in person to exchange keys securely.',
                inline=False
            )
            embed.add_field(
                name='4. Start Messaging',
                value='Choose a transport mode (Direct, Tor, WiFi Direct, Bluetooth Mesh, or P2P Tor) and send.',
                inline=False
            )
            embed.add_field(
                name='Got Questions?',
                value='Just ask here or in the troubleshooting channel - the bot auto-answers common questions.',
                inline=False
            )
            await ch.send(embed=embed)
            posted.append(f'<#{CHANNEL_GETTING_STARTED}>')

        # Troubleshooting -> #troubleshooting
        ch = guild.get_channel(CHANNEL_TROUBLESHOOTING)
        if ch:
            embed = discord.Embed(
                title='Troubleshooting & Support',
                color=COLOR_WARNING
            )
            embed.add_field(
                name='Auto-Answers',
                value=(
                    'Ask your question here and the bot will try to answer automatically. '
                    'It covers common topics like adding contacts, connection modes, '
                    'battery usage, messages not sending, crashes, encryption, and more.'
                ),
                inline=False
            )
            embed.add_field(
                name='Still Stuck?',
                value='If the bot can\'t help, a developer will follow up manually.',
                inline=False
            )
            await ch.send(embed=embed)
            posted.append(f'<#{CHANNEL_TROUBLESHOOTING}>')

        # Announcements -> #announcements
        ch = guild.get_channel(CHANNEL_ANNOUNCEMENTS)
        if ch:
            embed = discord.Embed(
                title='Release Announcements',
                color=COLOR_SUCCESS
            )
            embed.add_field(
                name='Stay Updated',
                value=(
                    'New version announcements are posted here by developers using the `/release` command. '
                    'You\'ll be pinged with a changelog and download link.'
                ),
                inline=False
            )
            await ch.send(embed=embed)
            posted.append(f'<#{CHANNEL_ANNOUNCEMENTS}>')

        if posted:
            await interaction.followup.send(
                f'Guide embeds posted in: {", ".join(posted)}',
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                'No channels found - check your .env channel IDs',
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Commands(bot))
