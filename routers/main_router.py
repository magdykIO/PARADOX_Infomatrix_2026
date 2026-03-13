from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

main_router = APIRouter()

# Вказуємо шлях до папки з html
templates = Jinja2Templates(directory="templates")


@main_router.get("/main/{username}", response_class=HTMLResponse)
async def chats_page(request: Request):

    return templates.TemplateResponse("main-page.html", {"request": request})
