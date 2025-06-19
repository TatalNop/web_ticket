from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.database import engine, Base, SessionLocal
from app.crud import create_default_user
from app.auth import get_current_user, get_current_active_user, get_current_admin_user
from app.api import users, tickets, management
from app import schemas, models
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_default_user(db)
    finally:
        db.close()
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/static/uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

app.include_router(users.router)
app.include_router(tickets.router)
app.include_router(management.router)


'''
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = None
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response
'''

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", 
                                      {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", 
                                      {"request": request})

@app.get("/verify_token", response_model=schemas.UserOut)
def verify_token(current_user=Depends(get_current_active_user)):
    return current_user

@app.get("/dashboard")
def dashbord_page(request: Request, current_user=Depends(get_current_active_user)):
    return templates.TemplateResponse("dashboard.html", 
                                      {"request": request})

@app.get("/sidebar")
def sidebar_page(request: Request):
    return templates.TemplateResponse("sidebar.html", 
                                      {"request": request})

@app.get("/management")
def management_page(request: Request):
    return templates.TemplateResponse("management.html", 
                                      {"request": request})