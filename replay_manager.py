# replay_manager.py

import os
import asyncio
import json
import logging
from datetime import datetime

from config import RAW_REPLAYS_DIR, PARSED_REPLAYS_DIR, KEYWORD, RRROCKET_CMD
from db import AsyncSessionLocal
from models import Replay
from discord import TextChannel

# Configuration du logger pour tout le module
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


async def download_last_replays(channel: TextChannel, limit: int = 50) -> list[str]:
    """
    Télécharge les `limit` derniers messages du canal,
    sauvegarde tous les fichiers *.replay* et renvoie la liste des chemins.
    """
    os.makedirs(RAW_REPLAYS_DIR, exist_ok=True)
    saved_files = []

    logger.debug(f"Downloading up to {limit} replays from channel {channel.id}")
    async for msg in channel.history(limit=limit):
        for att in msg.attachments:
            if att.filename.lower().endswith(".replay"):
                dest = os.path.join(RAW_REPLAYS_DIR, att.filename)
                if not os.path.exists(dest):
                    await att.save(dest)
                    logger.info(f"Downloaded replay: {att.filename}")
                else:
                    logger.debug(f"Already exists, skipping: {att.filename}")
                saved_files.append(dest)

    logger.debug(f"Total replay files in RAW_DIR: {len(saved_files)}")
    return saved_files


async def process_new_replays(pseudo: str):
    """
    Parcourt RAW_REPLAYS_DIR et traite tous les .replay* contenant le pseudo spécifié :
    - supprime les fichiers sans extension .replay
    - supprime les fichiers ne correspondant pas au mot-clé général KEYWORD
    - ignore les replays d'autres joueurs
    - parse les replays valides avec rrrocket, stocke en BDD, et supprime l'original
    """
    os.makedirs(PARSED_REPLAYS_DIR, exist_ok=True)
    files = os.listdir(RAW_REPLAYS_DIR)
    logger.debug(f"process_new_replays: Found {len(files)} files in RAW_REPLAYS_DIR")

    for fname in files:
        raw_path = os.path.join(RAW_REPLAYS_DIR, fname)

        # 1) extension .replay
        if not fname.endswith(".replay"):
            logger.debug(f"  → Skipping non-.replay, deleting: {fname}")
            os.remove(raw_path)
            continue

        # 2) mot-clé global
        if KEYWORD not in fname:
            logger.debug(f"  → Skipping (no KEYWORD), deleting: {fname}")
            os.remove(raw_path)
            continue

        # 3) ne traiter que les fichiers contenant le pseudo
        if f"_{pseudo}_" not in fname:
            logger.debug(f"  → Ignoring replay for autre joueur, keeping file: {fname}")
            continue

        logger.info(f"  → Parsing replay for {pseudo}: {fname}")

        # 4) appel rrrocket et capture stdout JSON
        proc = await asyncio.create_subprocess_exec(
            RRROCKET_CMD, raw_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error(f"rrrocket failed on {fname}: {stderr.decode().strip()}")
            continue

        # 5) écrire le JSON dans PARSED_REPLAYS_DIR
        json_fname = fname.replace(".replay", ".json")
        json_path = os.path.join(PARSED_REPLAYS_DIR, json_fname)
        try:
            with open(json_path, "w", encoding="utf-8") as jf:
                jf.write(stdout.decode())
            logger.debug(f"Wrote parsed JSON: {json_fname}")
        except Exception as e:
            logger.error(f"Failed writing JSON {json_fname}: {e}")
            continue

        # 6) charger le JSON
        try:
            with open(json_path, "r", encoding="utf-8") as jf:
                data = json.load(jf)
            logger.debug(f"Loaded JSON data for {fname}")
        except Exception as e:
            logger.error(f"Error loading JSON for {fname}: {e}")
            # on peut conserver le replay brut pour debug ultérieur
            continue

        # 7) calculer le timestamp
        try:
            ts = datetime.fromtimestamp(int(data["properties"]["MatchStartEpoch"]))
        except Exception as e:
            logger.error(f"Invalid MatchStartEpoch in {fname}: {e}")
            continue

        # 8) insertion en base
        replay = Replay(
            filename=fname,
            user_pseudo=pseudo,
            parsed_data=data,
            timestamp=ts
        )
        async with AsyncSessionLocal() as session:
            try:
                session.add(replay)
                await session.commit()
                logger.info(f"Inserted into DB: {fname}")
            except Exception as e:
                logger.error(f"DB insert error {fname}: {e}", exc_info=True)
                await session.rollback()

        # 9) suppression du .replay original
        try:
            os.remove(raw_path)
            logger.debug(f"Deleted raw replay file: {fname}")
        except Exception as e:
            logger.error(f"Failed to delete raw file {fname}: {e}")
