# report_manager.py
from datetime import datetime
from db import AsyncSessionLocal
from models import Report
from stats_manager import get_last_replays, aggregate_stats

async def check_and_generate_report(pseudo: str):
    replays = await get_last_replays(pseudo, 5)
    if len(replays) < 5:
        return None

    stats = await aggregate_stats(replays)
    content = {
        "wins": stats["wins"],
        "losses": stats["losses"],
        "mmr_delta": stats["mmr_delta"],
        "goals": stats["goals"],
        "saves": stats["saves"]
    }
    async with AsyncSessionLocal() as session:
        rpt = Report(user_pseudo=pseudo, created_at=datetime.utcnow(), content=content)
        session.add(rpt)
        await session.commit()
    return content
