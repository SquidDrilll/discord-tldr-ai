#!/usr/bin/env python3
import os, discord
from dotenv import load_dotenv

# ----------  Agno (0.1.7 on PyPI) ----------
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools   # exists ✔

load_dotenv()
TOKEN    = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

agent = Agent(
    model=Groq(id="llama-3.1-70b-versatile", api_key=GROQ_KEY),
    tools=[DuckDuckGoTools()],          # search only – works ✔
    description="Concise Discord assistant.",
    show_tool_calls=False
)

# ---------- Discord self-bot ----------
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents, self_bot=True)

@bot.event
async def on_ready():
    print(f"[+] Bot alive: {bot.user}")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    if isinstance(msg.channel, discord.DMChannel) or bot.user.mentioned_in(msg):
        async with msg.channel.typing():
            text = msg.content.replace(f"<@{bot.user.id}>", "").strip()
            reply = agent.run(text, stream=False)
        await msg.reply(reply.content[:500])

if __name__ == "__main__":
    bot.run(TOKEN, bot=False)
