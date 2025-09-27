#!/usr/bin/env python3
"""
Railway-ready TL;DR self-bot – minimal, tested 2024-06-14
"""
import os, discord, textwrap
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq

load_dotenv()
TOKEN    = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

agent = Agent(
    model=Groq(id="llama-3.1-8b-instant", api_key=GROQ_KEY),
    description="Reply with a one-sentence TL;DR of the user's text."
)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents, self_bot=True)

@bot.event
async def on_ready():
    print(f"[+] TL;DR bot alive: {bot.user}")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return

    # 1. DM -> direct TL;DR
    if isinstance(msg.channel, discord.DMChannel):
        async with msg.channel.typing():
            summary = agent.run(msg.content, stream=False)
        await msg.reply(summary.content[:300])

    # 2. Mention -> TL;DR of the message
    elif bot.user.mentioned_in(msg):
        async with msg.channel.typing():
            text = msg.content.replace(f"<@{bot.user.id}>", "").strip()
            summary = agent.run(text or msg.content, stream=False)
        await msg.reply(summary.content[:300])

    # 3. Channel command "tldr" -> TL;DR last 20 messages
    elif msg.content.lower().strip() == "tldr":
        async with msg.channel.typing():
            msgs = [m async for m in msg.channel.history(limit=20)]
            corpus = "\n".join(m.content for m in reversed(msgs) if m.content)
            prompt = f"Summarise this chat in one sentence:\n{corpus}"
            summary = agent.run(prompt, stream=False)
        await msg.reply(summary.content[:300])

if __name__ == "__main__":
    bot.run(TOKEN, bot=False)
