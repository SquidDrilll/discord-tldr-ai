#!/usr/bin/env python3
"""
Railway-ready self-bot – Agno brain, SquidDrill skeleton
Works with ANY agno>=0.1  (memory is built-in, no manual import needed)
"""
import os, discord
from dotenv import load_dotenv

# ---------- Agno ----------
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.url_toolkit import UrlToolkit   # <-- NEW import

# ---------- agent ----------
agent = Agent(
    model=Groq(id="llama-3.1-70b-versatile", api_key=GROQ_KEY),
    tools=[DuckDuckGoTools(), UrlToolkit()] if cfg.get("enable_tools", True) else [],
    description="Helpful self-bot. Keep answers ≤300 chars.",
    show_tool_calls=False
)

# ---------- SquidDrill ----------
from utils.config import cfg
from utils.events import Events
from utils.logger import log

load_dotenv()
TOKEN    = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")


# ---------- Discord ----------
intents = discord.Intents.default()
intents.message_content = True
bot = Events(
    command_prefix=cfg.get("prefix", "."),
    case_insensitive=True,
    self_bot=True,
    intents=intents
)

@bot.event
async def on_ready():
    log.info(f"[+] Agno self-bot ready – {bot.user}")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    # DM or mention -> reply
    if isinstance(msg.channel, discord.DMChannel) or bot.user.mentioned_in(msg):
        async with msg.channel.typing():
            text = msg.content.replace(f"<@{bot.user.id}>", "").strip()
            reply = agent.run(text, stream=False)
        await msg.reply(reply.content[:500])
    await bot.process_commands(msg)

if __name__ == "__main__":
    bot.run(TOKEN, bot=False)
