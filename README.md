<p align="center">
  <br />
  <a href="https://wavy.fm" target="_blank" align="center">
    <img src="https://wavy.fm/_assets/wavy-logo.png" width="280">
  </a>
  <br />
</p>

# wavyfm-discord

**A Discord bot for [wavy.fm](https://wavy.fm), officially maintained by Wavy Labs.**
This bot serves as a showcase for our Python [client library](https://github.com/wavy/wavyfm-python).

 [![Discord](https://img.shields.io/discord/742178434243100752?color=%237289DA&label=discord)](https://wavy.fm/discord)

## Running the bot

You must install Python 3.8 and Pipenv to run this bot.

If you haven't already, [create an app on Discord](https://discord.com/developers/applications) for your bot. Once the
app is created, enable Bot usage in the "Bot" tab. Copy and save the token somewhere safe.

To add the bot to your server, go to the "OAuth2" tab, check "bot" in the list of scopes, and copy-and-paste the
resulting URL in your browser.

You will also need the credentials for a [wavy.fm app](https://wavy.fm/developers/apps) (Client ID and Client Secret).

Download this repository and create a file named `.env` at the root. Inside, set the following environment variables:

```bash
# REQUIRED: wavy.fm app credentials (from previous instructions)
WAVYFM_CLIENT_ID=pub_...
WAVYFM_CLIENT_SECRET=priv_...

# REQUIRED: Discord bot token (from previous instructions)
WAVYFM_DISCORD_BOT_TOKEN=...

# OPTIONAL: Sentry.io support, for error monitoring.
# WAVYFM_DISCORD_SENTRY_URL=https://...
```

You can now run the bot using Pipenv:

```bash
# Install dependencies first
pipenv install

# Run the bot
pipenv run bot
```

## Contributing

See [CONTRIBUTING.md](https://github.com/wavy/wavyfm-discord/blob/master/CONTRIBUTING.md)

## License

This project is licenced under the MIT License.

