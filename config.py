# config.py
import os
from pathlib import Path
from datetime import timedelta
BASE_DIR = Path(__file__).resolve().parent

# Dossier où arrivent les replays bruts
WEBHOOK_CHANNEL_ID = 1366449779122634802
RAW_REPLAYS_DIR = os.getenv("RAW_REPLAYS_DIR", "/home/RocketStatsBot/saved_replays")
# Dossier où stocker les JSON après parsing
PARSED_REPLAYS_DIR = os.getenv("PARSED_REPLAYS_DIR", "/home/RocketStatsBot/parsed_replays")
# Mot-clé à conserver
#KEYWORD = "Ranked_Doubles"
KEYWORD = "Casual_Doubles"

# Chemin vers l’exécutable rrrocket (doit être déjà installé)
RRROCKET_CMD = os.getenv("RRROCKET_CMD", "rrrocket")

# Fichier de la base SQLite
#DATABASE_URL = "sqlite+aiosqlite:///./rocketstats.db"
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'rocketstats.db'}"

# Discord bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "MTM2NTM3OTc1OTU0NjA0NDYwOA.G5wAs4.70mnBu3Jt0Qp-ZRRzgqhgvJXPpa_Id0u8UkY70")
DM_TIMEOUT = 300  # sec
BATCH_SIZE = 5
MAX_WINDOW = timedelta(minutes=45)