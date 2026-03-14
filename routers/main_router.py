from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import get_db

main_router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Вказуємо шлях до папки з html
templates = Jinja2Templates(directory="templates")


@main_router.get("/main/{username}", response_class=HTMLResponse)
async def chats_page(request: Request):

    return templates.TemplateResponse("main-page.html", {"request": request})


@main_router.get("/wardrobe/{username}", response_class=HTMLResponse)
async def wardrobe_page(username: str, request: Request, db: Session = Depends(get_db)):
    # Шукаємо користувача в базі за юзернеймом
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    # Тимчасовий список доступних скінів для магазину
    available_skins = [
        {"id": "regular", "name": "Classic Squirrel", "price": 0},
        {"id": "cyberpunk", "name": "Cyberpunk", "price": 50},
        {"id": "knight", "name": "Knight", "price": 33},
        {"id": "space_explorer", "name": "Space Explorer", "price": 81},
        {"id": "forest_druid", "name": "Forest Druid", "price": 150},
        {"id": "backend_developer", "name": "Backend Developer", "price": 25},
        {"id": "pirate_captain", "name": "Pirate Captain", "price": 30},
        {"id": "sensei", "name": "Sensei", "price": 25},
    ]

    return templates.TemplateResponse(
        "wardrobe-page.html",
        {"request": request, "user": user, "available_skins": available_skins},
    )
