import os, discord, asyncio
from agno.agent import Agent
from agno.models.groq import Groq
from agno.memory import AgentMemory
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")          # Railway → add DISCORD_TOKEN var
GROQ_KEY = os.getenv("GROQ_API_KEY")        # Railway → add GROQ_API_KEY var

agent = Agent(
    model=Groq(id="llama-3.1-70b-versatile", api_key=GROQ_KEY),
    memory=AgentMemory(summary=True),
    description="You are a helpful TL;DR bot. Keep answers ≤ 200 chars.",
)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents, self_bot=True)

@bot.event
async def on_ready():
    print(f"[+] Self-bot logged in as {bot.user} (Railway)")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    # only answer DMs or when bot is mentioned
    if isinstance(msg.channel, discord.DMChannel) or bot.user.mentioned_in(msg):
        async with msg.channel.typing():
            answer = agent.run(msg.content, stream=False)
        await msg.reply(answer.content[:500])   # keep Discord msg limit safe

if __name__ == "__main__":
    bot.run(TOKEN, bot=False)   # self-bot flag
