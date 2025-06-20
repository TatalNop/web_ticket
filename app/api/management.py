from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas, database, auth, crud, utils
from typing import List

router = APIRouter(prefix="/api", tags=["management"])

@router.get("/leagues", response_model=List[schemas.LeagueOut])
def get_leagues(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    leagues = crud.get_leagues(db)
    return leagues

@router.post("/leagues", response_model=schemas.LeagueOut)
def create_leagues(
    league_data: schemas.LeagueIn,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    leagues = crud.create_leagues(db,league_data.league_name)
    return leagues

@router.put("/leagues/{league_id}", response_model=schemas.LeagueOut)
def put_leagues(league_id: int,
                league_data: schemas.LeagueIn,
                current_user: models.User = Depends(auth.get_current_active_user),
                db: Session = Depends(database.get_db)):
    leagues = crud.update_leagues(db,league_id,league_data.league_name)
    return leagues

@router.get("/matches", response_model=List[schemas.MatchOut])
def get_matches(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    matches = crud.get_matches(db)
    return matches

@router.post("/matches", response_model=schemas.MatchOut)
def create_matches(
    match_create: schemas.MatchIn,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    matches = crud.create_match(db,
                                match_create.match_name,
                                match_create.match_date,
                                match_create.match_year,
                                match_create.league_id
                                )
    return matches

@router.put("/matches/{match_id}", response_model=schemas.MatchOut)
def put_matches(
    match_id: int,
    match_update: schemas.MatchIn,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    matches = crud.update_match(db,
                            match_id,
                            match_update.match_name,
                            match_update.match_date,
                            match_update.match_year,
                            match_update.league_id
                            )
    return matches
    