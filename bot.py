import discord
from discord.ext import commands
import aiohttp
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
GUILD_ID = int(os.getenv('GUILD_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = discord.app_commands.CommandTree(bot)

STREAMERS_FILE = 'streamers.json'

def load_streamers():
    if os.path.exists(STREAMERS_FILE):
        with open(STREAMERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_streamers(streamers):
    with open(STREAMERS_FILE, 'w') as f:
        json.dump(streamers, f, indent=2)

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

async def is_streamer_live(streamer_name, oauth_token):
    url = f"https://api.twitch.tv/helix/streams?user_login={streamer_name}"
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {oauth_token}'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            return bool(data['data'])

async def check_streamers():
    oauth_token = await get_oauth_token()
    streamers = load_streamers()
    channel = bot.get_channel(CHANNEL_ID)

    for streamer in streamers:
        username = streamer["username"]
        message = streamer.get("message", f"@everyone {username} is live! Watch here: https://twitch.tv/{username}")

        if await is_streamer_live(username, oauth_token):
            embed = discord.Embed(
                title=f"{username} is LIVE!",
                description=message,
                color=discord.Color.purple()
            )
            await channel.send(embed=embed)

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

# Slash command: Add streamer (default message for now)
@tree.command(name="addstreamer", description="Add a streamer to tracking.", guild=discord.Object(id=GUILD_ID))
async def addstreamer(interaction: discord.Interaction, streamer: str):
    streamers = load_streamers()
    if any(s["username"].lower() == streamer.lower() for s in streamers):
        await interaction.response.send_message(f"{streamer} is already being tracked.", ephemeral=True)
    else:
        streamers.append({"username": streamer, "message": f"@everyone {streamer} is live! https://twitch.tv/{streamer}"})
        save_streamers(streamers)
        await interaction.response.send_message(f"Added {streamer} to tracking list.", ephemeral=True)

# Slash command: Remove streamer
@tree.command(name="removestreamer", description="Remove a streamer from tracking.", guild=discord.Object(id=GUILD_ID))
async def removestreamer(interaction: discord.Interaction, streamer: str):
    streamers = load_streamers()
    updated = [s for s in streamers if s["username"].lower() != streamer.lower()]
    if len(updated) != len(streamers):
        save_streamers(updated)
        await interaction.response.send_message(f"Removed {streamer} from tracking list.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{streamer} was not found.", ephemeral=True)

# Slash command: List streamers
@tree.command(name="liststreamers", description="List all tracked streamers.", guild=discord.Object(id=GUILD_ID))
async def liststreamers(interaction: discord.Interaction):
    streamers = load_streamers()
    if streamers:
        streamer_list = ', '.join([s["username"] for s in streamers])
        await interaction.response.send_message(f"Currently tracking: {streamer_list}", ephemeral=True)
    else:
        await interaction.response.send_message("No streamers are currently being tracked.", ephemeral=True)

bot.run(DISCORD_TOKEN)
