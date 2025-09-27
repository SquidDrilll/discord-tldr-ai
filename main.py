#!/usr/bin/env python3
"""
Railway-ready TL;DR self-bot – discord.py-self-reborn (no crash)
"""
import os, discord
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools

load_dotenv()
TOKEN    = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

agent = Agent(
    model=Groq(id="llama-3.1-8b-instant", api_key=GROQ_KEY),
    tools=[DuckDuckGoTools()],
    description="Reply with a one-sentence TL;DR."
)

bot = discord.Client(self_bot=True)

@bot.event
async def on_ready():
    print(f"[+] TL;DR bot ready: {bot.user}")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return

    # ----- .tldr N -----
    if msg.content.startswith(".tldr"):
        parts = msg.content.split()
        limit = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 20
        limit = min(limit, 100)
        async with msg.channel.typing():
            msgs = [m async for m in msg.channel.history(limit=limit)]
            corpus = "\n".join(m.content for m in reversed(msgs) if m.content)
            summary = agent.run(f"Summarise this chat in one sentence:\n{corpus}", stream=False)
        await msg.reply(summary.content[:300])
        return

    # ----- DM / mention -----
    if isinstance(msg.channel, discord.DMChannel) or bot.user.mentioned_in(msg):
        async with msg.channel.typing():
            text = msg.content.replace(f"<@{bot.user.id}>", "").strip()
            summary = agent.run(text or msg.content, stream=False)
        await msg.reply(summary.content[:300])

if __name__ == "__main__":
    bot.run(TOKEN)
