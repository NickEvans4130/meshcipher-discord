import discord
from discord.ext import commands
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import *


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
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
