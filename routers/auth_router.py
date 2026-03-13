from fastapi import APIRouter, Form, status, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from auth_logic import hash_password, verify_password
import models


auth_router = APIRouter()

# Tells FastAPI where html files are
templates = Jinja2Templates(directory="templates")


# Opens "welcome" page
@auth_router.get("/")
async def welcome_page(request: Request):
    return templates.TemplateResponse("welcome-page.html", {"request": request})


# Opens "sign-in" page
@auth_router.get("/signin")
async def signin_page(request: Request):
    return templates.TemplateResponse("sign-in.html", {"request": request})


# Actions after pressing send button in signin form
@auth_router.post("/signin")
async def handle_signing_in(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        return RedirectResponse(
            url="/signin?error=user_not_found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if not verify_password(password, user.hashed_password):
        return RedirectResponse(
            url="/signin?error=invalid_credentials",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    print(f"User {user.username} logged in successfully!")

    return RedirectResponse(
        url=f"/main/{user.username}", status_code=status.HTTP_303_SEE_OTHER
    )


# Opens "sign-up" page
@auth_router.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("sign-up.html", {"request": request})


# Actions after pressing send button in signin form
@auth_router.post("/signup")
async def handle_registration(
    full_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):

    if len(password) > 71:
        return RedirectResponse(
            url="/signup?error=password_is_too_long",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    elif len(password) < 4:  # Changed to 4 characters for easier production
        # Change back to 8 characters after production
        return RedirectResponse(
            url="/signup?error=password_is_too_short",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # TODO: Pydantic validator logic

    hashed_password = hash_password(password)

    if password != confirm_password:
        return RedirectResponse(
            url="/signup?error=passwords_dont_match",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    default_appearance = {
        "hat": "regular",
        "squirrel": "regular",
        "background": "regular",
        "tail": "regular",
        "left-hand": "regular",
        "right-hand": "regular",
    }

    # Create a new User object using your SQLAlchemy model
    new_user = models.User(
        full_name=full_name,
        username=username,
        email=email,
        hashed_password=hashed_password,
        current_skin=default_appearance,
        # Додаємо ці початкові частини в список розблокованих,
        # щоб юзер міг повернутися до них пізніше
        unlocked_skins=[
            "hat_regular",
            "squirrel_regular",
            "background_regular",
            "tail_regular",
            "left_hand_regular",
            "right_hand_regular",
        ],
        nuts_amount=0,
    )

    # Add to session and save to database
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # Refresh to get the generated ID from the DB
    except Exception as e:
        db.rollback()
        return {"error": f"Could not create user: {str(e)}"}

    print(
        f"""User {username} created successfully!
          all info on user:
          full_name: {full_name},
          username: {username},
          email: {email},
          password: {password}"""
    )

    return RedirectResponse(
        url=f"/main/{new_user.username}", status_code=status.HTTP_303_SEE_OTHER
    )
