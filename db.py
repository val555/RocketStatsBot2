# db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from models import Base

# Création du moteur asynchrone
engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Crée les tables si besoin."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
