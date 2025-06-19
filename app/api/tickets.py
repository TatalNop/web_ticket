from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.responses import StreamingResponse
import io
import csv

from app import models, schemas, database, auth, crud, utils

router = APIRouter(prefix="/api", tags=["tickets"])

@router.post("/tickets", response_model=schemas.TicketOut)
def create_ticket(
    url_data: schemas.TicketCreate = Depends(schemas.TicketCreate.as_form),
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only JPEG, PNG, and WEBP are allowed.",
        )
    url = str(url_data.url)

    ticket_in_db = crud.get_ticket_by_url(db, url)
    
    if ticket_in_db:
        raise HTTPException(status_code=400, detail="URL already exists")
    try:
        image_path = utils.save_and_compress_image(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image error: {str(e)}")

    ticket = crud.create_ticket(db, url=url, 
                                image_path=image_path, 
                                owner_id=current_user.id,
                                league_id=url_data.league_id,
                                match_id=url_data.match_id,
                                )
    return ticket

@router.get("/tickets", response_model=List[schemas.TicketOut])
def list_tickets(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    tickets = crud.get_tickets(db)
    # user เห็นเฉพาะ ticket ของตัวเอง ยกเว้น admin เห็นทั้งหมด
    if current_user.role != schemas.UserRole.admin:
        tickets = [t for t in tickets if t.owner_id == current_user.id]
    return tickets

@router.get("/tickets/filter", response_model=List[schemas.TicketOut])
def read_tickets(
    db: Session = Depends(database.get_db),
    league_id: Optional[int] = Query(None),
    match_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
):
    tickets = crud.get_tickets_filtered(db,
                                        league_id, 
                                        match_id, 
                                        status)
    return tickets

@router.patch("/tickets/{ticket_id}", response_model=schemas.TicketOut)
def update_ticket_status(
    ticket_id: int,
    status_update: schemas.TicketUpdateStatus,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(database.get_db),
):
    ticket = crud.update_ticket_status(db, 
                                       ticket_id, 
                                       status_update.status, 
                                       current_user.id)
    return ticket

@router.get("/tickets/export/csv")
def export_tickets_to_csv(
        db: Session = Depends(database.get_db),
        league_id: Optional[int] = Query(None),
        match_id: Optional[int] = Query(None),
        status: Optional[str] = Query(None),
):
    tickets = crud.get_tickets_filtered(db, league_id, match_id, status)
    rows = []
    
    for t in tickets:
        rows.append([
            t.league.league_name,
            t.match.match_name,
            t.match.match_date.strftime("%Y-%m-%d %H:%M"),
            t.url,
            t.status.capitalize(),
            t.owner.username.capitalize(),
            t.created_at.strftime("%Y-%m-%d %H:%M"),
            t.updater.username.capitalize() if t.updater else "-"
        ])

    return StreamingResponse(utils.generate_csv(rows), 
                            media_type="text/csv", 
                            headers={
                            "Content-Disposition": "attachment; filename=tickets.csv"
                })