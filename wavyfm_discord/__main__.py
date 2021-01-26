import logging
import os

import discord
import sentry_sdk
from discord.ext.commands import Bot

from wavyfm_discord import WavyDiscord


def run():
    init_logging(os.getenv("WAVYFM_DISCORD_SENTRY_URL"))
    bot_token = os.getenv("WAVYFM_DISCORD_BOT_TOKEN")

    if not bot_token:
        logging.error("Missing WAVYFM_DISCORD_BOT_TOKEN!")
        return exit(1)

    bot = Bot(command_prefix="!", intents=discord.Intents.default())
    bot.add_cog(WavyDiscord(bot))
    bot.run(bot_token)


def init_logging(sentry_url: str = None):
    """Initialize logger and optional Sentry support"""
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d -- %(message)s',
                        level=logging.DEBUG)
    if sentry_url:
        logging.info("Enabling Sentry support")
        sentry_sdk.init(sentry_url)
    else:
        logging.warning("Sentry support is disabled")


if __name__ == '__main__':
    run()
