# stats_manager.py

from sqlalchemy import select
from datetime import datetime, timedelta
from db import AsyncSessionLocal
from models import Replay

async def get_last_replays(pseudo: str, n: int, within: timedelta | None = None):
    """
    Récupère les n derniers replays d'un utilisateur, optionnellement dans une fenêtre.
    """
    async with AsyncSessionLocal() as session:
        q = select(Replay) \
            .where(Replay.user_pseudo == pseudo) \
            .order_by(Replay.timestamp.desc()) \
            .limit(n)
        if within:
            cutoff = datetime.utcnow() - within
            q = q.where(Replay.timestamp >= cutoff)
        res = await session.execute(q)
        return res.scalars().all()


async def aggregate_stats(replays: list[Replay]) -> dict:
    """
    Pour une liste de replays, calcule :
      - victoires / défaites (avec défaites = total - victoires)
      - delta MMR total si possible, sinon None
      - total buts et saves
    """
    total = len(replays)
    wins = 0
    mmr_total_delta = 0.0
    mmr_values_found = 0
    total_goals = 0
    total_saves = 0

    for r in replays:
        props = r.parsed_data.get("properties", {})
        score0 = props.get("Team0Score", 0)
        score1 = props.get("Team1Score", 0)

        # Récupère les stats du joueur
        stats_list = props.get("PlayerStats", [])
        stats = next((p for p in stats_list if p.get("Name") == r.user_pseudo), None)
        if not stats:
            continue
        team_id = stats.get("Team", 0)

        # Victoire ?
        if (team_id == 0 and score0 > score1) or (team_id == 1 and score1 > score0):
            wins += 1

        # Cumuler buts/saves
        total_goals += stats.get("Goals", 0)
        total_saves += stats.get("Saves", 0)

        # Tenter de lire MMR pré/post
        pre = None
        post = None
        for entry in r.parsed_data.get("debug_info", []):
            user_field = entry.get("user", "")
            text_field = entry.get("text", "")
            # Cherche PRE
            if user_field.endswith(":PRE"):
                try:
                    pre = float(text_field.split("|")[0])
                except:
                    pass
            # Cherche POST
            if user_field.endswith(":POST"):
                try:
                    post = float(text_field.split("|")[0])
                except:
                    pass
        if pre is not None and post is not None:
            mmr_total_delta += (post - pre)
            mmr_values_found += 1

    losses = total - wins
    mmr_delta = round(mmr_total_delta, 2) if mmr_values_found > 0 else None

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "mmr_delta": mmr_delta,
        "goals": total_goals,
        "saves": total_saves
    }
