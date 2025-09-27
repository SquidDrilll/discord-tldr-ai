#!/usr/bin/env python3
import os, discord, aiohttp, json
from dotenv import load_dotenv

load_dotenv()
TOKEN   = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("GROQ_API_KEY")

URL   = "https://api.groq.com/openai/v1/chat/completions"
HEAD  = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

bot = discord.Client(self_bot=True)
# ---- gateway crash fix ----
discord.state.Payment = type('Payment', (), {'__init__': lambda *a, **k: None})

async def tldr(text: str) -> str:
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": f"TL;DR in one sentence:\n{text}"}],
        "max_tokens": 60,
        "temperature": 0.3
    }
    async with aiohttp.ClientSession() as ses:
        async with ses.post(URL, headers=HEAD, data=json.dumps(payload)) as r:
            r.raise_for_status()
            data = await r.json()
            return data["choices"][0]["message"]["content"].strip()

@bot.event
async def on_ready():
    print(f"[+] TL;DR bot ready: {bot.user}")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return

    # ----- .tldr X (0–1000) -----
    if msg.content.startswith(".tldr"):
        parts = msg.content.split()
        limit = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 20
        limit = max(0, min(limit, 1000))
        async with msg.channel.typing():
            msgs = [m async for m in msg.channel.history(limit=limit)]
            corpus = "\n".join(m.content for m in reversed(msgs) if m.content)
            summary = await tldr(corpus or "empty")
        await msg.reply(summary[:300])
        return

    # ----- DM / mention -----
    if isinstance(msg.channel, discord.DMChannel) or bot.user.mentioned_in(msg):
        async with msg.channel.typing():
            text = msg.content.replace(f"<@{bot.user.id}>", "").strip()
            summary = await tldr(text or msg.content)
        await msg.reply(summary[:300])

if __name__ == "__main__":
    bot.run(TOKEN)
