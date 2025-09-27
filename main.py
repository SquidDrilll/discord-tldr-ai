#!/usr/bin/env python3
"""
Railway-ready Discord self-bot
Agno agent + memory + tools
"""
import os, discord, asyncio
from dotenv import load_dotenv

# --------- Agno imports ---------
from agno.agent import Agent
from agno.models.groq import Groq
from agno.memory.agent import AgentMemory          # fixed import
from agno.tools.duckduckgo import DuckDuckGoTools  # free search
from agno.tools.url import UrlTools                # fetch any URL

load_dotenv()
TOKEN   = os.getenv("DISCORD_TOKEN")
GROQ_KEY= os.getenv("GROQ_API_KEY")

# --------- build agent with memory + tools ---------
agent = Agent(
    model=Groq(id="llama-3.1-70b-versatile", api_key=GROQ_KEY),
    memory=AgentMemory(
        db_path="railway_chat.db",   # SQLite file, auto-created
        summarize_old_messages=True  # keeps context window small
    ),
    tools=[DuckDuckGoTools(), UrlTools()],
    description=(
        "You are a helpful Discord assistant. "
        "Answer shortly (≤300 chars) and use tools when you need real-time data."
    ),
    show_tool_calls=False            # cleaner replies
)

# --------- Discord self-bot ---------
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents, self_bot=True)

@bot.event
async def on_ready():
    print(f"[+] Railway bot logged in as {bot.user}")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    # reply only in DMs or when mentioned
    if isinstance(msg.channel, discord.DMChannel) or bot.user.mentioned_in(msg):
        async with msg.channel.typing():
            # strip bot mention if present
            text = msg.content.replace(f"<@{bot.user.id}>", "").strip()
            answer = agent.run(text, stream=False)
        await msg.reply(answer.content[:500])  # Discord limit safety

if __name__ == "__main__":
    bot.run(TOKEN, bot=False)
