import discord
from discord.ext import commands
import aiohttp
import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
GUILD_ID = int(os.getenv('GUILD_ID', 0))
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree  # No need to instantiate a new CommandTree

STREAMERS_FILE = 'streamers.json'
ANNOUNCED_FILE = 'announced_streams.json'

def load_streamers():
    if os.path.exists(STREAMERS_FILE):
        with open(STREAMERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_streamers(streamers):
    with open(STREAMERS_FILE, 'w') as f:
        json.dump(streamers, f, indent=2)

def load_announced():
    if os.path.exists(ANNOUNCED_FILE):
        with open(ANNOUNCED_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_announced(data):
    with open(ANNOUNCED_FILE, 'w') as f:
        json.dump(data, f, indent=2)

async def get_oauth_token():
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as resp:
            data = await resp.json()
            return data['access_token']

async def get_live_stream_info(streamer_name, oauth_token):
    url = f"https://api.twitch.tv/helix/streams?user_login={streamer_name}"
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {oauth_token}'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            return data['data'][0] if data['data'] else None

async def check_streamers():
    oauth_token = await get_oauth_token()
    streamers = load_streamers()
    announced = load_announced()
    channel = bot.get_channel(CHANNEL_ID)

    for streamer in streamers:
        username = streamer["username"]
        message = streamer.get("message", f"@everyone {username} is live! https://twitch.tv/{username}")

        stream_info = await get_live_stream_info(username, oauth_token)

        if stream_info:
            started_at = stream_info.get("started_at")
            if not started_at:
                continue

            stream_id = f"{username}:{started_at}"

            if stream_id not in announced:
                embed = discord.Embed(
                    title=f"{username} is LIVE!",
                    description=message,
                    color=discord.Color.purple(),
                    url=f"https://twitch.tv/{username}"
                )
                thumbnail = stream_info.get("thumbnail_url", "").replace("{width}", "1920").replace("{height}", "1080")
                if thumbnail:
                    embed.set_image(url=thumbnail)

                await channel.send(embed=embed)
                announced[stream_id] = True
                save_announced(announced)

async def auto_check_streamers():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            print("[AutoCheck] Checking live streamers...")
            await check_streamers()
        except Exception as e:
            print(f"[AutoCheck Error] {e}")
        await asyncio.sleep(300)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    bot.loop.create_task(auto_check_streamers())

@tree.command(name="addstreamer", description="Add a streamer with a custom message", guild=discord.Object(id=GUILD_ID))
async def addstreamer(interaction: discord.Interaction, streamer: str, message: str):
    streamers = load_streamers()
    if any(s["username"].lower() == streamer.lower() for s in streamers):
        await interaction.response.send_message(f"{streamer} is already being tracked.", ephemeral=True)
    else:
        streamers.append({"username": streamer, "message": message})
        save_streamers(streamers)
        await interaction.response.send_message(f"Added {streamer} with message: {message}", ephemeral=True)

@tree.command(name="removestreamer", description="Remove a streamer from tracking", guild=discord.Object(id=GUILD_ID))
async def removestreamer(interaction: discord.Interaction, streamer: str):
    streamers = load_streamers()
    updated = [s for s in streamers if s["username"].lower() != streamer.lower()]
    if len(updated) != len(streamers):
        save_streamers(updated)
        await interaction.response.send_message(f"Removed {streamer}.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{streamer} not found.", ephemeral=True)

@tree.command(name="liststreamers", description="List all currently tracked streamers", guild=discord.Object(id=GUILD_ID))
async def liststreamers(interaction: discord.Interaction):
    streamers = load_streamers()
    if streamers:
        listing = '\n'.join([f"- {s['username']}: {s['message']}" for s in streamers])
        await interaction.response.send_message(f"**Tracked Streamers:**\n{listing}", ephemeral=True)
    else:
        await interaction.response.send_message("No streamers currently being tracked.", ephemeral=True)

bot.run(DISCORD_TOKEN)
