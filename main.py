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
from agno.tools.url import UrlTools

# ---------- SquidDrill ----------
from utils.config import cfg
from utils.events import Events
from utils.logger import log

load_dotenv()
TOKEN    = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

# ---------- agent (memory=ON by default) ----------
agent = Agent(
    model=Groq(id
