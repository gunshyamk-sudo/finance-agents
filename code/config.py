"""Shared settings used by every script. Change the model name here only."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent      # the finance-agents-starter folder
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

load_dotenv(ROOT / ".env")
# If you get a "model not found" error, copy a current model name from
# https://docs.claude.com/en/docs/about-claude/models and put it in your .env file as MODEL=...
MODEL = os.getenv("MODEL", "claude-haiku-5-5")
