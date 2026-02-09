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

    @app_commands.command(name='guide', description='Post the bot guide embed')
    async def guide(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                'Only the server owner can use this command',
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(CHANNEL_BOT_GUIDE)
        if not channel:
            await interaction.response.send_message(
                'Could not find the bot-guide channel',
                ephemeral=True
            )
            return

        # Main welcome embed
        welcome = discord.Embed(
            title='MeshCipher Bot Guide',
            description=(
                'This bot helps manage the MeshCipher beta testing process. '
                'Below is everything you need to know.'
            ),
            color=COLOR_SUCCESS
        )

        # Bug reporting
        bugs = discord.Embed(
            title='Reporting Bugs',
            color=COLOR_ERROR
        )
        bugs.add_field(
            name='How to Report',
            value=(
                'Use the `/bug` command anywhere in the server. '
                'A form will pop up asking for your device model, Android version, '
                'a description of the bug, and steps to reproduce it.'
            ),
            inline=False
        )
        bugs.add_field(
            name='What Happens Next',
            value=(
                f'Your report gets posted in <#{CHANNEL_BUG_REPORTS}> with tracking reactions:\n'
                f'{EMOJI_SEEN} Seen | {EMOJI_INVESTIGATING} Investigating | '
                f'{EMOJI_FIXED} Fixed | {EMOJI_CANT_REPRODUCE} Can\'t Reproduce'
            ),
            inline=False
        )

        # Feature requests
        features = discord.Embed(
            title='Feature Requests',
            color=COLOR_INFO
        )
        features.add_field(
            name='How to Suggest',
            value=(
                f'Post your idea in <#{CHANNEL_FEATURE_REQUESTS}>. '
                'The bot will automatically add voting reactions so others can weigh in.'
            ),
            inline=False
        )
        features.add_field(
            name='Voting',
            value=(
                f'{EMOJI_UPVOTE} Want this | {EMOJI_DOWNVOTE} Don\'t need this | '
                f'{EMOJI_FIRE} High priority'
            ),
            inline=False
        )

        # FAQ / Support
        support = discord.Embed(
            title='Getting Help',
            color=COLOR_WARNING
        )
        support.add_field(
            name='Auto-Answers',
            value=(
                f'Ask questions in <#{CHANNEL_GETTING_STARTED}> or <#{CHANNEL_TROUBLESHOOTING}> '
                'and the bot will try to answer common questions automatically '
                '(adding contacts, connection modes, battery usage, encryption, etc).'
            ),
            inline=False
        )

        # Commands reference
        cmds = discord.Embed(
            title='All Commands',
            color=COLOR_INFO
        )
        cmds.add_field(name='/bug', value='Report a bug with a structured form', inline=False)
        cmds.add_field(name='/stats', value='View beta testing statistics', inline=False)
        cmds.add_field(name='/help', value='Quick list of available commands', inline=False)
        cmds.add_field(name='/release', value='Announce a new version (developers only)', inline=False)
        cmds.add_field(name='/gh-issue', value='Create a GitHub issue from a bug report (developers only)', inline=False)

        # Send all embeds
        await channel.send(embed=welcome)
        await channel.send(embed=bugs)
        await channel.send(embed=features)
        await channel.send(embed=support)
        await channel.send(embed=cmds)

        await interaction.response.send_message('Guide posted!', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Commands(bot))
