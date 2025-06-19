from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(10), default="user")

    tickets = relationship("Ticket", back_populates="owner", foreign_keys="Ticket.owner_id")
    updates = relationship("Ticket", back_populates="updater", foreign_keys="Ticket.update_by")

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)

    url = Column(String(750), nullable=False, unique=True)
    image_path = Column(String(256), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=func.now())
    update_at = Column(DateTime, default=func.now(), onupdate=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"))
    update_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="tickets", foreign_keys=[owner_id])
    updater = relationship("User", back_populates="updates", foreign_keys=[update_by])
    
    match = relationship("Match", back_populates="tickets")
    league = relationship("League", back_populates="tickets")

class League(Base):
    __tablename__ = "leagues"
    id = Column(Integer, primary_key=True, index=True)
    league_name = Column(String(50), nullable=False, unique=True)

    matches = relationship("Match", back_populates="league")
    tickets = relationship("Ticket", back_populates="league")

class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("match_name", "match_date", "league_id", name="uq_match_unique"),
    )
    id = Column(Integer, primary_key=True, index=True)
    match_name = Column(String(100), nullable=False)
    match_date = Column(DateTime)
    match_year = Column(Integer)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)

    league = relationship("League", back_populates="matches")
    tickets = relationship("Ticket", back_populates="match")

