import os
from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel

# Твої модулі
import models
from database import get_db
from generate import RPGTaskArchitect

app = FastAPI()

# Налаштування шаблонів
templates = Jinja2Templates(directory="templates")

# Ініціалізація ШІ
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "ТВІЙ_КЛЮЧ_ТУТ")
architect = RPGTaskArchitect(GEMINI_KEY)

class DreamRequest(BaseModel):
    user_id: int
    dream: str

# --- ДОПОМІЖНА ФУНКЦІЯ ---
def parse_deadline_string(deadline_str: str):
    try:
        parts = str(deadline_str).split()
        amount = int(parts[0])
        unit = parts[1].lower()
        if "hour" in unit: return timedelta(hours=amount)
        if "day" in unit: return timedelta(days=amount)
        if "min" in unit: return timedelta(minutes=amount)
        return timedelta(hours=1)
    except:
        return timedelta(hours=1)

# --- 1. ПЕРЕГЛЯД СОЦІАЛЬНОГО ХАБУ (HTML) ---
@app.get("/social/hub", response_class=HTMLResponse)
async def social_hub(request: Request, db: Session = Depends(get_db)):
    # Тестовий юзер Igor (ID=1)
    current_user = db.query(models.User).filter(models.User.id == 1).first()
    if not current_user:
        return HTMLResponse(content="Register user first", status_code=404)

    all_users = db.query(models.User).all()
    incoming_quests = db.query(models.Quest).filter(
        models.Quest.user_id == current_user.id,
        models.Quest.sender_id != None,
        models.Quest.is_completed == False
    ).all()

    return templates.TemplateResponse("social.html", {
        "request": request,
        "user": current_user,
        "all_players": all_users,
        "incoming_quests": incoming_quests
    })

# --- 2. ВІДПРАВКА ВИКЛИКУ ДРУГУ ---
@app.post("/social/send-challenge")
async def send_challenge(
    receiver_username: str = Form(...), 
    title: str = Form(...), 
    reward: int = Form(...), 
    db: Session = Depends(get_db)
):
    me = db.query(models.User).filter(models.User.id == 1).first() 
    receiver = db.query(models.User).filter(models.User.username == receiver_username).first()

    if not receiver or me.nuts_amount < reward:
        return RedirectResponse(url="/social/hub?error=failed", status_code=303)

    me.nuts_amount -= reward
    new_quest = models.Quest(
        title=title,
        final_reward=reward,
        base_reward=reward,
        user_id=receiver.id,
        sender_id=me.id,
        from_who=me.username,
        is_started=True,
        is_completed=False
    )
    db.add(new_quest)
    db.commit()
    return RedirectResponse(url="/social/hub", status_code=303)

# --- 3. API ДЛЯ ГОЛОВНОЇ СТОРІНКИ (loadUserQuests) ---
@app.get("/api/quests/{username}")
async def get_user_quests(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return {"quests": []}
    quests = db.query(models.Quest).filter(models.Quest.user_id == user.id).all()
    return {"quests": quests}

# --- 4. API ГЕНЕРАЦІЇ (renderTasksForGoal) ---
@app.post("/api/generate_tasks")
async def api_generate_tasks(data: dict, db: Session = Depends(get_db)):
    goal = data.get("goal")
    username = data.get("username")
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ai_response = architect.generate_rpg_plan(goal)
    if "error" in ai_response:
        return {"error": ai_response["error"]}

    # Видаляємо старі незавершені ШІ-таски
    db.query(models.Quest).filter(
        models.Quest.user_id == user.id, 
        models.Quest.is_completed == False, 
        models.Quest.sender_id == None
    ).delete()

    new_tasks = []
    for task in ai_response["tasks"]:
        q = models.Quest(
            title=task["title"],
            description=task["description"],
            difficulty=task["complexity"],
            base_reward=task["base_reward"],
            category=task.get("attribute", "General"),
            from_who="Gemini Game Master",
            deadlines_config=task.get("deadlines_config") or task.get("deadlines"),
            multipliers_config=task.get("multipliers_config") or task.get("multipliers"),
            user_id=user.id,
            is_completed=False
        )
        db.add(q)
        db.flush() # Отримати ID для фронтенда
        new_tasks.append(q)

    db.commit()
    return {"status": "success", "tasks": new_tasks, "source": "Gemini AI"}

# --- 5. СТАРТ ТАСКИ (ГЕМБЛІНГ) ---
@app.post("/start-task/{quest_id}")
async def start_task(quest_id: int, mode: str = "none", db: Session = Depends(get_db)):
    quest = db.query(models.Quest).filter(models.Quest.id == quest_id).first()
    if not quest: raise HTTPException(status_code=404, detail="Quest not found")

    quest.is_started = True 
    quest.selected_difficulty_level = mode
    
    if mode != "none" and quest.deadlines_config:
        deadline_text = quest.deadlines_config.get(mode, "1 day")
        quest.deadline = datetime.now() + parse_deadline_string(deadline_text)
        
    db.commit()
    return {"status": "started", "deadline": quest.deadline}

# --- 6. ЗАВЕРШЕННЯ (ОБ'ЄДНАНЕ + API PATCH) ---
@app.post("/complete-task/{quest_id}")
@app.patch("/api/quest/{quest_id}")
async def complete_task(quest_id: int, db: Session = Depends(get_db)):
    quest = db.query(models.Quest).filter(models.Quest.id == quest_id).first()
    if not quest or quest.is_completed:
        return {"error": "Quest already finished or not found"}

    user = db.query(models.User).filter(models.User.id == quest.user_id).first()
    now = datetime.now()

    # Логіка винагороди
    if quest.sender_id:
        reward = quest.final_reward
        is_success = True
    else:
        mode = quest.selected_difficulty_level or "none"
        if mode == "none":
            reward = quest.base_reward
            is_success = True
        else:
            multiplier = quest.multipliers_config.get(mode, 0.0)
            if quest.deadline and now <= quest.deadline:
                reward = quest.base_reward + (quest.base_reward * multiplier)
                is_success = True
            else:
                reward = quest.base_reward - (quest.base_reward * multiplier)
                is_success = False

    reward = int(reward)
    user.nuts_amount += reward
    quest.is_completed = True
    quest.final_reward = reward
    db.commit()

    comment = architect.generate_comment(success=is_success)
    
    # Якщо запит від форми соціального хабу
    if quest.sender_id and not "/api/" in str(quest_id): 
        return RedirectResponse(url="/social/hub", status_code=303)
    
    return {"comment": comment, "reward": reward, "total_nuts": user.nuts_amount}