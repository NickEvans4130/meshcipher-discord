import discord
from discord.ext import commands
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import *

# Setup logging
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MeshCipher')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(
    command_prefix=BOT_PREFIX,
    intents=intents,
    description='MeshCipher Beta Testing Assistant'
)


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} guilds')

    # Load extensions
    extensions = [
        'src.commands',
        'src.events',
        'src.faq',
        'src.github_sync'
    ]

    for extension in extensions:
        try:
            await bot.load_extension(extension)
            logger.info(f'Loaded extension: {extension}')
        except Exception as e:
            logger.error(f'Failed to load {extension}: {e}')

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f'Synced {len(synced)} slash commands')
    except Exception as e:
        logger.error(f'Failed to sync commands: {e}')

    # Set bot status
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name='for bugs'
    )
    await bot.change_presence(activity=activity)

    logger.info('Bot is ready!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You don\'t have permission to use this command.')
    else:
        logger.error(f'Command error: {error}')
        await ctx.send(f'An error occurred: {str(error)}')


def main():
    if not DISCORD_TOKEN:
        logger.error('DISCORD_TOKEN not set. Copy .env.example to .env and fill in your values.')
        sys.exit(1)

    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f'Failed to start bot: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
