# models.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    discord_id = Column(String, primary_key=True, index=True)
    pseudo     = Column(String, unique=True, index=True, nullable=False)

    replays = relationship("Replay", back_populates="user")
    reports = relationship("Report", back_populates="user")

class Replay(Base):
    __tablename__ = "replays"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    filename      = Column(String, unique=True, nullable=False)
    user_pseudo   = Column(String, ForeignKey("users.pseudo"), index=True)
    parsed_data   = Column(JSON, nullable=False)
    timestamp     = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="replays")

class Report(Base):
    __tablename__ = "reports"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    user_pseudo   = Column(String, ForeignKey("users.pseudo"), index=True)
    created_at    = Column(DateTime, nullable=False)
    content       = Column(JSON, nullable=False)

    user = relationship("User", back_populates="reports")
