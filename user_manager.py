# user_manager.py
from sqlalchemy import select
from db import AsyncSessionLocal
from models import User

async def get_user_by_discord_id(discord_id: str) -> User | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.discord_id == discord_id))
        return result.scalars().first()

async def get_user_by_pseudo(pseudo: str) -> User | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.pseudo == pseudo))
        return result.scalars().first()

async def set_user_pseudo(discord_id: str, pseudo: str) -> User:
    async with AsyncSessionLocal() as session:
        # upsert by discord_id
        user = await session.get(User, discord_id)
        if user:
            user.pseudo = pseudo
        else:
            user = User(discord_id=discord_id, pseudo=pseudo)
            session.add(user)
        await session.commit()
        return user
