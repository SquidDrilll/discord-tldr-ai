#!/usr/bin/env python3
"""
Agno-powered brain dropped into SquidDrill self-bot skeleton.
Keeps every original feature; only the LLM back-end is replaced.
"""
import os, discord, json, time, asyncio, aiohttp
from datetime import datetime as dt
from dotenv import load_dotenv

# ---------- Agno ----------
from agno.agent import Agent
from agno.models.groq import Groq
from agno.memory import Memory
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.url import UrlTools

# ---------- SquidDrill helpers ----------
from utils.config import cfg               # config.json loader
from utils.events import Events              # fancy event wrappers
from utils.logger import log                 # coloured console logger

load_dotenv()
TOKEN   = os.getenv("DISCORD_TOKEN")
GROQ_KEY= os.getenv("GROQ_API_KEY")

# ---------- Agno agent ----------
agent = Agent(
    model=Groq(id="llama-3.1-70b-versatile", api_key=GROQ_KEY),
    memory=Memory(db_path="agno_chat.db"),
    tools=[DuckDuckGoTools(), UrlTools()] if cfg.get("enable_tools", True) else [],
    description=(
        "You are a self-bot assistant. "
        "Answer briefly (≤300 chars) and use tools only when needed."
    ),
    show_tool_calls=False
)

# ---------- Discord client ----------
intents = discord.Intents.default()
intents.message_content = True
bot = Events(
    command_prefix=cfg.get("prefix", "."),
    case_insensitive=True,
    self_bot=True,
    intents=intents
)

# ---------- event hooks ----------
@bot.event
async def on_ready():
    log.info(f"[+] Logged in as {bot.user} (UID {bot.user.id})")
    await bot.change_presence(
        activity=discord.Game(name=cfg.get("status", "Agno 🤖"))
    )

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return

    # 1. Reply in DMs
    if isinstance(msg.channel, discord.DMChannel):
        async with msg.channel.typing():
            answer = agent.run(msg.content, stream=False)
        await msg.reply(answer.content[:500])

    # 2. Reply when mentioned
    elif bot.user.mentioned_in(msg):
        async with msg.channel.typing():
            text = msg.content.replace(f"<@{bot.user.id}>", "").strip()
            answer = agent.run(text, stream=False)
        await msg.reply(answer.content[:500])

    # 3. Keep original command processing intact
    await bot.process_commands(msg)

# ---------- run ----------
if __name__ == "__main__":
    bot.run(TOKEN, bot=False)
