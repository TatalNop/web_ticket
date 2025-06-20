from sqlalchemy.orm import Session
from . import models, schemas, auth
from fastapi import HTTPException
from typing import Optional
from datetime import datetime

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, role="user")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_default_user(db: Session)-> bool:
    default_username = "admin"
    default_password = "admin"
    default_role = "admin"

    user = db.query(models.User).filter(models.User.username == default_username).first()
    if not user:
        hashed_password = auth.hash_password(default_password)
        user = models.User(username=default_username, hashed_password=hashed_password, role=default_role)
        db.add(user)
        db.commit()
        return True
    else:
        return False

def create_admin_user(db: Session, username: str, password: str):
    hashed_password = auth.hash_password(password)
    db_user = models.User(username=username, hashed_password=hashed_password, role="admin")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_ticket(db: Session, url: str, image_path: str, owner_id: int, league_id: int, match_id: int):
    db_ticket = get_ticket_by_url(db, url)
    if db_ticket:
        raise HTTPException(status_code=400, detail="URL already exists")
    
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    league = db.query(models.League).filter(models.League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    ticket = models.Ticket(
        url=url,
        image_path=image_path,
        owner_id=owner_id,
        match_id=match_id,
        league_id=league_id
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def get_tickets(db: Session):
    return db.query(models.Ticket).all()

def get_tickets_by_owner(db: Session, owner_id: int):
    return db.query(models.Ticket).filter(models.Ticket.owner_id == owner_id).all()

def get_tickets_by_league(db: Session, league_id: int):
    return db.query(models.Ticket).filter(models.Ticket.league_id == league_id).all()

def get_tickets_by_match(db: Session, match_id: int):
    return db.query(models.Ticket).filter(models.Ticket.league_id == match_id).all()

def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

def update_ticket_status(db: Session, ticket_id: int, status: str, update_by : str):
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket.status == status:
        raise HTTPException(status_code=400, detail="Status has not changed")
    '''
    if ticket.status in {"rejected", "verified"}:
        raise HTTPException(status_code=400, detail=f"Cannot change status once it's {ticket.status}")
    '''
    ticket.status = status
    ticket.update_by = update_by
    db.commit()
    db.refresh(ticket)
    return ticket

def get_ticket_by_url(db: Session, url: str):
    return db.query(models.Ticket).filter(models.Ticket.url == url).first()

def get_tickets_filtered(
    db: Session,
    league_id: Optional[int] = None,
    match_id: Optional[int] = None,
    status: Optional[str] = None
):
    query = db.query(models.Ticket)

    if league_id is not None:
        query = query.filter(models.Ticket.league_id == league_id)
    if match_id is not None:
        query = query.filter(models.Ticket.match_id == match_id)
    if status is not None:
        query = query.filter(models.Ticket.status == status)
    return query.all()

def get_leagues(db: Session):
    return db.query(models.League).all()

def get_leagues_by_name(db: Session, league_name):
    return db.query(models.League).filter(models.League.league_name == league_name).first()

def create_leagues(db: Session, league_name: str, ):
    db_leagues = get_leagues_by_name(db, league_name)
    if db_leagues:
        raise HTTPException(status_code=400, detail="League already exists")
    
    league = models.League(
        league_name=league_name
    )
    db.add(league)
    db.commit()
    db.refresh(league)
    return league

def update_leagues(db: Session, league_id: int, league_name: str):
    league = db.query(models.League).filter(models.League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=400, detail="League not found")
    league.league_name = league_name
    db.commit()
    db.refresh(league)
    return league

def get_matches(db: Session):
    return db.query(models.Match).all()

def get_match_by_unique(db: Session, match_name: str, match_date: datetime, league_id: int):
    return db.query(models.Match).filter(
        models.Match.match_name == match_name,
        models.Match.match_date == match_date,
        models.Match.league_id == league_id
    ).first()

def create_match(db: Session, match_name: str, match_date: datetime, match_year: int, league_id: int):
    
    league = db.query(models.League).filter(models.League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=400, detail="League does not exist")
    
    db_match = get_match_by_unique(db, match_name, match_date, league_id)
    if db_match:
        raise HTTPException(status_code=400, detail="Match already exists")

    match = models.Match(
        match_name=match_name,
        match_date=match_date,
        league_id=league_id,
        match_year=match_year
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match

def update_match(db: Session, match_id: int ,match_name: str, match_date: datetime, match_year: int, league_id: int):
    db_match = db.query(models.Match).filter(
        models.Match.id == match_id
    ).first()

    if not db_match:
        raise HTTPException(status_code=400, detail="Match not found")
    
    db_match.match_name=match_name
    db_match.match_date=match_date
    db_match.league_id=league_id
    db_match.match_year=match_year

    db.commit()
    db.refresh(db_match)
    return db_match