
# V1ewerBot

> A Python-based Discord bot designed to automatically announce when Twitch streamers go live. Built for community servers that want seamless, automated Twitch integration with minimal setup.



## Table of Contents
- [Project Description](#project-description)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [Lessons Learned](#lessons-learned)
- [Future Roadmap](#future-roadmap)
- [Author](#author)
- [License](#license)

## Project Description
**V1ewerBot** monitors a list of Twitch streamers and automatically posts Discord announcements when they go live.  
It uses the Twitch API to track real-time stream status and Discord webhooks or bot messages to deliver rich embedded notifications that include:
- Stream title and category
- Direct link to the live channel
- Optional thumbnail and game information

This project was an early version of **Wrathbot**, focusing specifically on Twitch live notifications and multi-streamer tracking, with later improvements for Docker containerization and config persistence.

## Tech Stack
- **Language:** Python 3.10+
- **Libraries:**
  - `discord.py` — for Discord bot commands and embeds
  - `requests` — to query the Twitch API
  - `dotenv` — for environment variable management
  - `json` — for data persistence
- **Deployment:** Docker & docker-compose
- **Data Files:**
  - `streamers.json` — list of streamers to monitor
  - `announced_streams.json` — stores which streams have been announced
  - `settings.json` — holds server and channel configuration

## Installation

### Prerequisites
- Python 3.10 or higher  
- Discord Bot Token  
- Twitch API credentials (Client ID & Secret)  
- (Optional) Docker installed on your system  

### Local Setup
```bash
# Clone the repository
git clone https://github.com/Anhender1993/V1ewerBot.git
cd V1ewerBot
```

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
```bash
pip install -r requirements.txt
```
Usage

1. Configure your environment

Create a .env file or update settings.json with:
```bash 
DISCORD_TOKEN=your_discord_bot_token
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
GUILD_ID=your_discord_server_id
CHANNEL_ID=announcement_channel_id
```

2. Add streamers to monitor

Edit streamers.json:
```bash
{
  "streamers": ["example_streamer1", "example_streamer2"]
}
```
3. Run the bot
```bash
python bot.py
```
Or, if you’re on Windows:
```bash
start_all.bat
```

The bot will now:
	•	Poll the Twitch API at regular intervals
	•	Announce when listed streamers go live
	•	Prevent duplicate announcements by tracking them in announced_streams.json

## Configuration
File           Purpose
settings.json  |  Stores channel IDs and guild configuration
streamers.json | List of Twitch usernames to monitor
announced_streams.json |  Prevents duplicate live notifications
.env  |  Contains private tokens and API credentials

## Docker Deployment

V1ewerBot includes a ready-to-use docker-compose.yml for containerized execution.
```bash
# Build and start
docker compose up --build -d
```
# View logs
```bash
docker compose logs -f
```
This setup is ideal for running the bot persistently on a VPS or Raspberry Pi without manual Python environment management.

Lessons Learned
	•	Managing API rate limits and duplicate notifications requires stateful data handling.
	•	Dockerization simplified deployment across machines and ensured consistent behavior.
	•	Integrating Twitch OAuth securely required strict handling of credentials.
	•	Testing async Discord events highlighted the importance of structured logging.


Future Roadmap
	•	Add moderator commands to dynamically add/remove streamers
	•	Implement slash commands for configuration
	•	Include live thumbnail previews in Discord embeds
	•	Integrate XP and leaderboard systems (completed in Wrathbot successor)


Author

Andrew Henderson
	•	GitHub: Anhender1993￼
	•	Portfolio: Github.com/Anhender1993
	•	LinkedIn: https://www.linkedin.com/in/andrew-v-henderson/
	•	Email: andrew.henderson@atlasstudents.com
