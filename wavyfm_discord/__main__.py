import logging
import os

import discord
from discord.ext.commands import Bot

from wavyfm_discord import init_logging, WavyDiscord


def run():
    init_logging(os.getenv("WAVYFM_DISCORD_SENTRY_URL"))
    bot_token = os.getenv("WAVYFM_DISCORD_BOT_TOKEN")

    if not bot_token:
        logging.error("Missing WAVYFM_DISCORD_BOT_TOKEN!")
        return exit(1)

    bot = Bot(command_prefix="!", intents=discord.Intents.default())
    bot.add_cog(WavyDiscord(bot))
    bot.run(bot_token)


if __name__ == '__main__':
    run()
