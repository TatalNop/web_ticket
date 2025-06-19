from pydantic import BaseModel, HttpUrl, field_serializer
from typing import Optional, List
from enum import Enum
from datetime import datetime
from fastapi import Form

class UserRole(str, Enum):
    admin = "admin"
    user = "user"

class TicketStatus(str, Enum):
    pending = "pending"
    activate = "activate"
    inactivate = "inactivate"

class UserCreate(BaseModel):
    username: str
    password: str
    role:UserRole

class UserOut(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TicketBase(BaseModel):
    league_id: int
    match_id: int
    url: HttpUrl

class TicketCreate(TicketBase):
    pass
    @classmethod
    def as_form(cls, league_id: int = Form(...), match_id: int = Form(...), url: HttpUrl = Form(...)):
        return cls(league_id=league_id, match_id=match_id, url=url)
    
class TicketUpdateStatus(BaseModel):
    status: TicketStatus

class LeagueIn(BaseModel):
    league_name: str

class MatchIn(BaseModel):
    match_name: str
    match_date: datetime
    match_year: int
    league_id:int

class LeagueOut(BaseModel):
    id: int
    league_name: str

    class Config:
        from_attributes = True

class MatchOut(BaseModel):
    id: int
    match_name: str
    match_date: Optional[datetime]
    match_year: Optional[int]
    league: LeagueOut

    @field_serializer("match_date")
    def serialize_datetime(self, dt: datetime, _info):
        return dt.strftime("%Y-%m-%d %H:%M")
    
    class Config:
        from_attributes = True


class TicketOut(BaseModel):
    id: int
    url: HttpUrl
    image_path: str
    status: TicketStatus
    created_at: datetime
    owner_id: int
    update_at: datetime
    update_by: Optional[int]
    league: LeagueOut
    match: MatchOut
    owner: UserOut
    updater: Optional[UserOut]

    @field_serializer("created_at", "update_at")
    def serialize_datetime(self, dt: datetime, _info):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True