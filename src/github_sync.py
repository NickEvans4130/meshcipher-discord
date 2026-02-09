import discord
from discord import app_commands
from discord.ext import commands
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import *

try:
    from github import Github
except ImportError:
    Github = None


class GitHubSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gh = None
        self.repo = None

        if Github and GITHUB_TOKEN and GITHUB_REPO:
            try:
                self.gh = Github(GITHUB_TOKEN)
                self.repo = self.gh.get_repo(GITHUB_REPO)
            except Exception as e:
                print(f'GitHub initialization failed: {e}')

    @app_commands.command(name='gh-issue', description='Create GitHub issue from bug report')
    @app_commands.describe(message_id='Message ID of the bug report')
    async def gh_issue(self, interaction: discord.Interaction, message_id: str):
        if ROLE_DEVELOPER not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(
                'Only developers can use this command',
                ephemeral=True
            )
            return

        if not self.repo:
            await interaction.response.send_message(
                'GitHub integration not configured. Set GITHUB_TOKEN and GITHUB_REPO in .env',
                ephemeral=True
            )
            return

        try:
            channel = interaction.guild.get_channel(CHANNEL_BUG_REPORTS)
            message = await channel.fetch_message(int(message_id))
        except Exception:
            await interaction.response.send_message(
                'Could not find bug report message',
                ephemeral=True
            )
            return

        if not message.embeds:
            await interaction.response.send_message(
                'Message is not a bug report (no embed found)',
                ephemeral=True
            )
            return

        embed = message.embeds[0]

        title = embed.description[:100] if embed.description else 'Bug Report from Discord'

        body_parts = ['## Bug Report', '']

        if embed.description:
            body_parts.append('### Description')
            body_parts.append(embed.description)
            body_parts.append('')

        for field in embed.fields:
            if field.name == 'Steps to Reproduce':
                body_parts.append('### Steps to Reproduce')
                body_parts.append(field.value)
                body_parts.append('')
            elif field.name == 'Device':
                body_parts.append(f'**Device:** {field.value}')
            elif field.name == 'Android':
                body_parts.append(f'**Android Version:** {field.value}')
            elif field.name == 'Reporter':
                body_parts.append(f'**Reported by:** Discord user')

        body_parts.append('')
        body_parts.append(
            f'**Discord Message:** https://discord.com/channels/'
            f'{interaction.guild.id}/{channel.id}/{message.id}'
        )
        body_parts.append('')
        body_parts.append('*Created from Discord bug report via MeshCipher Bot*')

        body = '\n'.join(body_parts)

        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=['bug', 'from-discord']
            )

            await message.reply(
                f'Created GitHub issue: {issue.html_url}',
                mention_author=False
            )

            await interaction.response.send_message(
                f'Created issue #{issue.number}: {issue.html_url}',
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f'Failed to create issue: {str(e)}',
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(GitHubSync(bot))
