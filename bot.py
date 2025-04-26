import discord
from discord.ext import commands, tasks
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

STREAMERS_FILE = 'streamers.json'

def load_streamers():
    if os.path.exists(STREAMERS_FILE):
        with open(STREAMERS_FILE, 'r') as f:
            return json.load(f)
    return []

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
        if await is_streamer_live(streamer, oauth_token):
            embed = discord.Embed(
                title=f"{streamer} is LIVE!",
                description=f"Check out the stream: https://twitch.tv/{streamer}",
                color=discord.Color.purple()
            )
            await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(auto_check_streamers())

async def auto_check_streamers():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            print("[AutoCheck] Checking live streamers...")
            await check_streamers()
        except Exception as e:
            print(f"[AutoCheck Error] {e}")
        await asyncio.sleep(300)  # 5 minutes

bot.run(DISCORD_TOKEN)
