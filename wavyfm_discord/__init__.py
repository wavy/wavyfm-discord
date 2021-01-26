import datetime
import logging
import math
from typing import Union, Optional, Dict

import discord
import wavyfm
from discord.ext import tasks, commands
from discord.ext.commands import Bot, Cog
from discord.utils import escape_markdown

website_url = "https://wavy.fm"
default_album_art = "https://i.imgur.com/J1us30b.png"


class WavyDiscord(Cog):
    """The official wavy.fm Discord bot."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.presence_state = 0
        self.client = wavyfm.WavyClient(auth_manager=wavyfm.WavyClientCredentials())

        self.presence_task.start()

    @tasks.loop(seconds=30.0)
    async def presence_task(self):
        """Task that regularly updates the presence with global website metrics"""
        self.presence_state = (self.presence_state + 1) % 2

        try:
            if self.presence_state == 0:
                total_users = self.large_number(self.client.metrics.get_total_users())
                activity = discord.Game(f"{total_users} users and counting!")
            else:
                total_listens = self.large_number(self.client.metrics.get_total_listens())
                activity = discord.Game(f"{total_listens} listens and counting!")
            await self.bot.change_presence(activity=activity)
        except wavyfm.WavyException:
            logging.error("Failed to fetch API in presence task", exc_info=True)
        except:  # noqa
            logging.error("Failed to update presence", exc_info=True)

    @commands.command("now", brief="Prints what you or another user are listening to on wavy.fm")
    async def now_command(self, ctx: commands.Context, user: Union[discord.User, str] = None):
        await ctx.trigger_typing()
        profile = await self.get_wavyfm_user(ctx, user or ctx.author)
        if not profile:
            return

        try:
            currently_listening = self.client.users.by_uri(profile["uri"]) \
                .get_currently_listening().get("item")
            if currently_listening:
                await ctx.send(embed=self.create_listen_embed(profile, currently_listening))
            else:
                last_played = self.client.users.by_uri(profile["uri"]).get_recent_listens(1)["items"]
                last_played = last_played[0] if len(last_played) else None
                date = datetime.datetime.fromisoformat(last_played["date"].replace('Z', '+00:00'))
                if last_played:
                    await ctx.send(embed=self.create_listen_embed(profile, last_played, date))
                else:
                    await ctx.reply("The given profile has no listening history on wavy.fm.")
        except wavyfm.WavyException:
            logging.error("Error while getting currently listening", exc_info=True)
            await ctx.reply("Sorry, an internal error occurred. Please try again later.")

    @commands.command("profile", brief="Prints the wavy.fm profile of the given user (or yourself)")
    async def profile_command(self, ctx: commands.Context, user: Union[discord.User, str] = None):
        await ctx.trigger_typing()
        profile = await self.get_wavyfm_user(ctx, user or ctx.author)
        if not profile:
            return

        try:
            stats = self.client.users.by_uri(profile["uri"]).get_history_stats()
            total_listens = "{:,}".format(stats["total_listens"])
            total_artists = "{:,}".format(stats["total_artists"])

            username = escape_markdown(profile["username"])
            url = profile["profile"]["url"]
            bio = escape_markdown(escape_markdown(profile["profile"].get("biography") or ""))
            avatar = profile["profile"]["avatar"]

            embed = discord.Embed(type="rich")
            embed.set_author(name=f"{username} on wavy.fm",
                             url=url)
            embed.title = username
            embed.url = url
            embed.description = bio
            embed.set_thumbnail(url=avatar)

            embed.add_field(name="Listens", value=total_listens, inline=True)
            embed.add_field(name="Artists", value=total_artists, inline=True)

            await ctx.send(embed=embed)
        except wavyfm.WavyException:
            logging.error("Error while getting currently listening", exc_info=True)
            await ctx.reply("Sorry, an internal error occurred. Please try again later.")

    @commands.command("top", brief="Prints the top wavy.fm users by listen count")
    async def top_command(self, ctx: commands.Context):
        await ctx.trigger_typing()

        try:
            leaderboard = self.client.metrics.get_user_listens_leaderboard()
            global_listens = self.client.metrics.get_total_listens()

            lines = []
            for row in leaderboard:
                rank = len(lines) + 1
                count = self.large_number(row["count"])  # nb: we don't show the real number because this is cached
                username = row["username"]
                url = f"{website_url}/user/{username}"

                lines.append(f"{rank}. [{escape_markdown(username)}]({url}) ({count} listens)")

            embed = discord.Embed(type="rich")
            embed.set_author(name="Top wavy.fm users by listens",
                             url=website_url)
            embed.description = "\n".join(lines)
            embed.set_footer(text=f"{self.large_number(global_listens)} total listens")

            await ctx.send(embed=embed)
        except wavyfm.WavyException:
            logging.error("Error while getting currently listening", exc_info=True)
            await ctx.reply("Sorry, an internal error occurred. Please try again later.")

    @presence_task.before_loop
    async def wait_for_bot(self):
        """A coro for waiting until the bot is ready"""
        await self.bot.wait_until_ready()

    async def get_wavyfm_user(self, ctx: commands.Context, user: Union[discord.User, str]) -> Optional[Dict]:
        """Find the profile and return gracefully"""
        try:
            if isinstance(user, str):
                return self.client.users.by_username(user).get_profile()
            elif isinstance(user, discord.User) or isinstance(user, discord.Member):
                return self.client.users.by_discord_id(user.id).get_profile()
            else:
                logging.error("Got unexpected user type %s", type(user))
        except wavyfm.WavyException as e:
            if e.error_status == 404 or e.error_status == 400:
                await ctx.reply("Could not find wavy.fm profile for this user.")
            elif e.error_status == 403:
                await ctx.reply("This profile is private and cannot be displayed.")
            else:
                logging.error("Error while getting profile", exc_info=True)
                await ctx.reply("Sorry, an internal error occurred. Please try again later.")

    @staticmethod
    def create_listen_embed(profile: Dict, item: Dict, date: datetime.datetime = None) -> discord.Embed:
        """Create the embed when getting a listen (live or recent)"""
        username = escape_markdown(profile["username"])

        def _format_artist(artist: Dict) -> str:
            name = escape_markdown(artist["name"] or "Unknown Artist")
            artist_url = artist["source_url"]
            if artist_url:
                return f"[{name}]({artist_url})"
            else:
                return name

        artist_list = list(map(_format_artist, item["artists"]))
        if len(artist_list):
            artist_list[0] = f"**{artist_list[0]}**"
        artist_names = ", ".join(artist_list)

        album = item["album"]
        album_url = album["source_url"]
        album_name = escape_markdown(album["name"])
        album_art = album["art_url"] or default_album_art

        embed = discord.Embed(type="rich")
        embed.set_author(
            name=f"Listening now on Spotify - {username}" if date is None else f"Recently played - {username}",
            url=f"{website_url}/user/{profile['username']}",
            icon_url=profile["profile"]["avatar_small"],
        )
        embed.set_thumbnail(url=album_art)
        embed.url = item["song"]["source_url"]
        embed.title = escape_markdown(item["song"]["name"])

        description = artist_names
        if album_name:
            if album_url is None:
                description += f"\n\nAlbum: **{album_name}**"
            else:
                description += f"\n\nAlbum: **[{album_name}]({album_url})**"

        embed.description = description
        embed.timestamp = date or embed.Empty
        return embed

    @staticmethod
    def large_number(count: int) -> str:
        if count < 10000:
            return str(count)
        elif count < 100000:
            return "{0:.1f}k".format(count / 1000)
        elif count < 1000000:
            return f"{math.floor(count / 1000)}k"
        else:
            return "{0:.1f}M".format(count / 1000000)
