import discord
from discord.ext import commands
from datetime import datetime
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import *


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_log_channel(self, guild):
        return guild.get_channel(CHANNEL_LOGS)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Log to audit channel
        log_channel = self.get_log_channel(member.guild)
        if log_channel:
            embed = discord.Embed(
                title='Member Joined',
                color=COLOR_SUCCESS,
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name='User', value=f'{member.mention} ({member})', inline=True)
            embed.add_field(name='Account Created', value=discord.utils.format_dt(member.created_at, 'R'), inline=True)
            embed.add_field(name='Member Count', value=str(member.guild.member_count), inline=True)
            embed.set_footer(text=f'ID: {member.id}')
            await log_channel.send(embed=embed)

        # Welcome DM (existing)
        """Welcome new beta testers."""
        try:
            embed = discord.Embed(
                title='Welcome to MeshCipher Beta!',
                description='Thanks for helping test MeshCipher!',
                color=COLOR_SUCCESS
            )

            embed.add_field(
                name='1. Get Started',
                value=f'Check <#{CHANNEL_GETTING_STARTED}> for setup instructions',
                inline=False
            )

            embed.add_field(
                name='2. Download APK',
                value=f'Latest build: https://github.com/NickEvans4130/MeshCipher/releases/latest',
                inline=False
            )

            embed.add_field(
                name='3. Test Everything',
                value='Try all features and report bugs!',
                inline=False
            )

            embed.add_field(
                name='4. Report Bugs',
                value=f'Use `/bug` or post in <#{CHANNEL_BUG_REPORTS}>',
                inline=False
            )

            embed.add_field(
                name='Need Help?',
                value=f'Ask in <#{CHANNEL_TROUBLESHOOTING}>',
                inline=False
            )

            await member.send(embed=embed)
        except discord.Forbidden:
            pass

        guild = member.guild
        role = guild.get_role(ROLE_BETA_TESTER)
        if role:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_channel = self.get_log_channel(member.guild)
        if log_channel:
            embed = discord.Embed(
                title='Member Left',
                color=COLOR_ERROR,
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name='User', value=f'{member.mention} ({member})', inline=True)
            roles = [r.mention for r in member.roles if r.name != '@everyone']
            embed.add_field(name='Roles', value=', '.join(roles) if roles else 'None', inline=True)
            embed.add_field(name='Member Count', value=str(member.guild.member_count), inline=True)
            embed.set_footer(text=f'ID: {member.id}')
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.content == after.content:
            return

        log_channel = self.get_log_channel(before.guild)
        if log_channel:
            embed = discord.Embed(
                title='Message Edited',
                color=COLOR_WARNING,
                timestamp=datetime.utcnow()
            )
            embed.set_author(name=str(before.author), icon_url=before.author.display_avatar.url)
            embed.add_field(name='Channel', value=before.channel.mention, inline=True)
            embed.add_field(name='Author', value=before.author.mention, inline=True)
            embed.add_field(
                name='Before',
                value=before.content[:1024] if before.content else '*empty*',
                inline=False
            )
            embed.add_field(
                name='After',
                value=after.content[:1024] if after.content else '*empty*',
                inline=False
            )
            embed.add_field(name='Jump', value=f'[Go to message]({after.jump_url})', inline=False)
            embed.set_footer(text=f'Message ID: {before.id}')
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        log_channel = self.get_log_channel(message.guild)
        if log_channel:
            embed = discord.Embed(
                title='Message Deleted',
                color=COLOR_ERROR,
                timestamp=datetime.utcnow()
            )
            embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            embed.add_field(name='Channel', value=message.channel.mention, inline=True)
            embed.add_field(name='Author', value=message.author.mention, inline=True)
            embed.add_field(
                name='Content',
                value=message.content[:1024] if message.content else '*no text content*',
                inline=False
            )
            if message.attachments:
                files = '\n'.join(a.filename for a in message.attachments)
                embed.add_field(name='Attachments', value=files, inline=False)
            embed.set_footer(text=f'Message ID: {message.id}')
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Feature request voting
        if message.channel.id == CHANNEL_FEATURE_REQUESTS:
            await message.add_reaction(EMOJI_UPVOTE)
            await message.add_reaction(EMOJI_DOWNVOTE)
            await message.add_reaction(EMOJI_FIRE)

            save_feature(message.id, {
                'author': str(message.author),
                'content': message.content,
                'timestamp': message.created_at.isoformat(),
                'votes': {'up': 0, 'down': 0, 'fire': 0}
            })

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        # Bug tracking reactions
        if reaction.message.channel.id == CHANNEL_BUG_REPORTS:
            if str(reaction.emoji) == EMOJI_INVESTIGATING:
                await reaction.message.reply(
                    f'{user.mention} is investigating this bug',
                    delete_after=10
                )
            elif str(reaction.emoji) == EMOJI_FIXED:
                await reaction.message.reply(
                    f'Marked as fixed by {user.mention}',
                    delete_after=30
                )

        # Feature request voting
        elif reaction.message.channel.id == CHANNEL_FEATURE_REQUESTS:
            update_feature_votes(reaction.message.id, str(reaction.emoji), 1)


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


def update_feature_votes(feature_id, emoji, delta):
    try:
        with open('data/features.json', 'r') as f:
            features = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    feature_id = str(feature_id)
    if feature_id not in features:
        return

    if emoji == EMOJI_UPVOTE:
        features[feature_id]['votes']['up'] += delta
    elif emoji == EMOJI_DOWNVOTE:
        features[feature_id]['votes']['down'] += delta
    elif emoji == EMOJI_FIRE:
        features[feature_id]['votes']['fire'] += delta

    with open('data/features.json', 'w') as f:
        json.dump(features, f, indent=2)


async def setup(bot):
    await bot.add_cog(Events(bot))
