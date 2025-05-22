# main.py
import asyncio
from bot import run_bot
from replay_manager import process_new_replays
from config import RAW_REPLAYS_DIR
import time
import os

async def watch_and_run():
    # Lance le bot dans une tâche
    bot_task = asyncio.create_task(asyncio.to_thread(run_bot))
    # Boucle de surveillance
    while True:
        await process_new_replays()
        await asyncio.sleep(10)  # vérifie toutes les 10 sec

if __name__ == "__main__":
    # Assure que le dossier existe
    os.makedirs(RAW_REPLAYS_DIR, exist_ok=True)
    asyncio.run(watch_and_run())
