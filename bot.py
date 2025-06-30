import discord
import aiohttp
import asyncio
import os
import json
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

STREAMERS_FILE = "streamers.json"
ANNOUNCED_FILE = "announced_streams.json"

# Load streamers
def load_streamers():
    if os.path.exists(STREAMERS_FILE):
        with open(STREAMERS_FILE, "r") as f:
            return json.load(f)
    return {}

# Load announced state
def load_announced():
    if os.path.exists(ANNOUNCED_FILE):
        with open(ANNOUNCED_FILE, "r") as f:
            return json.load(f)
    return {}

# Save announced state
def save_announced(announced):
    with open(ANNOUNCED_FILE, "w") as f:
        json.dump(announced, f)

streamers = load_streamers()
announced = load_announced()

# Twitch token fetch
async def get_app_access_token(session):
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    async with session.post(url, params=params) as resp:
        return (await resp.json())["access_token"]

# Check for live streamers
async def check_live():
    async with aiohttp.ClientSession() as session:
        token = await get_app_access_token(session)
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {token}"
        }

        user_logins = list(streamers.keys())
        if not user_logins:
            return

        url = "https://api.twitch.tv/helix/streams"
        params = [("user_login", login) for login in user_logins]
        async with session.get(url, headers=headers, params=params) as resp:
            data = await resp.json()

        for stream in data.get("data", []):
            login = stream["user_login"]
            started_at = stream["started_at"]

            # Skip if already announced for this session
            if login in announced and announced[login] == started_at:
                continue

            announced[login] = started_at
            save_announced(announced)

            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                title = stream["title"]
                thumbnail = stream["thumbnail_url"].format(width=1280, height=720)
                url = f"https://twitch.tv/{login}"

                embed = discord.Embed(
                    title=f"{login} is live!",
                    description=streamers[login],
                    url=url,
                    color=discord.Color.purple()
                )
                embed.set_image(url=thumbnail)
                embed.add_field(name="Stream Title", value=title, inline=False)
                embed.set_footer(text="Go show some support!")

                await channel.send(embed=embed)

@tasks.loop(minutes=1)
async def stream_check_loop():
    await check_live()

@tasks.loop(hours=24)
async def daily_cleanup():
    print("Clearing announced_streams.json for new day...")
    save_announced({})

@bot.event
async def on_ready():
    stream_check_loop.start()
    daily_cleanup.start()
    await tree.sync()
    print(f"Logged in as {bot.user}")

@tree.command(name="addstreamer", description="Add a streamer and custom message")
@app_commands.describe(username="Twitch username", message="Message to display when live")
async def addstreamer(interaction: discord.Interaction, username: str, message: str):
    streamers[username.lower()] = message
    with open(STREAMERS_FILE, "w") as f:
        json.dump(streamers, f)
    await interaction.response.send_message(f"Added streamer {username} with message: {message}", ephemeral=True)

@tree.command(name="removestreamer", description="Remove a streamer from the list")
@app_commands.describe(username="Twitch username")
async def removestreamer(interaction: discord.Interaction, username: str):
    removed = streamers.pop(username.lower(), None)
    with open(STREAMERS_FILE, "w") as f:
        json.dump(streamers, f)
    if removed:
        await interaction.response.send_message(f"Removed streamer {username}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Streamer {username} not found", ephemeral=True)

@tree.command(name="liststreamers", description="List all tracked streamers")
async def liststreamers(interaction: discord.Interaction):
    if not streamers:
        await interaction.response.send_message("No streamers are currently being tracked.", ephemeral=True)
    else:
        msg = "\n".join(f"- {u}: {m}" for u, m in streamers.items())
        await interaction.response.send_message(f"Tracked streamers:\n{msg}", ephemeral=True)

bot.run(DISCORD_TOKEN)
