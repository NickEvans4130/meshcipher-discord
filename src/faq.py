import discord
from discord.ext import commands
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import *


class FAQ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_faq_data()

    def load_faq_data(self):
        try:
            with open('config/faq_data.json', 'r') as f:
                data = json.load(f)
                self.faqs = data['keywords']
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f'Failed to load FAQ data: {e}')
            self.faqs = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Only respond in support channels
        if message.channel.id not in [
            CHANNEL_GETTING_STARTED,
            CHANNEL_TROUBLESHOOTING
        ]:
            return

        message_lower = message.content.lower()

        for topic, faq in self.faqs.items():
            triggers = faq['triggers']

            if any(trigger in message_lower for trigger in triggers):
                await message.reply(faq['response'])
                await message.add_reaction('\u2705')
                break


async def setup(bot):
    await bot.add_cog(FAQ(bot))
