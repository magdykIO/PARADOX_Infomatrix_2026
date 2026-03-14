from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
from generate import RPGTaskArchitect
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()
# ... (Middleware остается как был)

architect = RPGTaskArchitect("YOUR_GEMINI_API_KEY")

class DreamRequest(BaseModel):
    user_id: int
    dream: str

@app.post("/generate-quest")
async def create_quest(request: DreamRequest, db: Session = Depends(get_db)):
    # 1. Проверяем пользователя
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Генерируем план через ИИ
    ai_response = architect.generate_rpg_plan(request.dream)
    if "error" in ai_response:
        raise HTTPException(status_code=500, detail=ai_response["error"])

    # 3. Обновляем цель пользователя
    user.goal = request.dream

    # 4. Удаляем старые невыполненные квесты (если нужно начать новую мечту)
    db.query(models.Quest).filter(models.Quest.user_id == user.id, models.Quest.is_completed == False).delete()

    # 5. Сохраняем новые квесты в базу
    new_quests = []
    for task in ai_response["tasks"]:
        quest_entry = models.Quest(
            title=task["title"],
            description=task["description"],
            difficulty=task["complexity"],
            base_reward=task["base_reward"],
            category=task.get("attribute", "General"),
            from_who="Gemini Game Master",
            # Сохраняем конфиги как JSON
            deadlines_config=task["deadlines"],
            multipliers_config=task["multipliers"],
            user_id=user.id,
            is_completed=False
        )
        new_quests.append(quest_entry)

    db.add_all(new_quests)
    db.commit()

    return {"status": "success", "message": "Quests generated and saved to DB", "tasks": ai_response["tasks"]}

from datetime import datetime

@app.post("/complete-task/{quest_id}")
async def complete_task(quest_id: int, db: Session = Depends(get_db)):
    # 1. Ищем квест и пользователя
    quest = db.query(models.Quest).filter(models.Quest.id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    if quest.is_completed:
        raise HTTPException(status_code=400, detail="Quest already finished")

    user = db.query(models.User).filter(models.User.id == quest.user_id).first()
    
    # 2. Проверяем дедлайн
    now = datetime.now()
    # Если дедлайн не был установлен (пользователь не делал ставку), считаем как успех
    is_on_time = True
    if quest.deadline and now > quest.deadline:
        is_on_time = False

    # 3. Извлекаем коэффициент (multiplier)
    # selected_difficulty_level может быть 'easy', 'medium' или 'hard'
    level = quest.selected_difficulty_level or "easy" 
    multiplier = quest.multipliers_config.get(level, 0.0)

    # 4. Считаем награду по твоей формуле
    if is_on_time:
        # Уложился: Base + (Base * Coeff)
        reward = quest.base_reward + (quest.base_reward * multiplier)
    else:
        # Опоздал: Base - (Base * Coeff)
        reward = quest.base_reward - (quest.base_reward * multiplier)
    
    reward = int(reward) # Округляем до целого числа орехов

    # 5. Обновляем базу данных
    user.nuts_amount += reward
    quest.is_completed = True
    quest.final_reward = reward # Сохраняем, сколько реально получил

    db.commit()

    # 6. Генерируем мгновенный комментарий через ИИ
    comment = architect.generate_comment(success=is_on_time)

    return {
        "status": "success" if is_on_time else "failed",
        "comment": comment,
        "reward_received": reward,
        "new_balance": user.nuts_amount
    }

# Вспомогательная функция для парсинга дедлайнов от ИИ (например, "2 hours" -> timedelta)
def parse_deadline_string(deadline_str: str):
    parts = deadline_str.split()
    amount = int(parts[0])
    unit = parts[1].lower()
    if "hour" in unit: return timedelta(hours=amount)
    if "day" in unit: return timedelta(days=amount)
    if "min" in unit: return timedelta(minutes=amount)
    return timedelta(hours=1) # Default

@app.post("/start-task/{quest_id}")
async def start_task(quest_id: int, mode: str = "none", db: Session = Depends(get_db)):
    quest = db.query(models.Quest).filter(models.Quest.id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")

    quest.is_started = True 
    
    quest.selected_difficulty_level = mode
    
    if mode == "none":
        quest.deadline = None
        quest.final_reward = quest.base_reward
    else:
        deadline_text = quest.deadlines_config.get(mode, "1 day")
        quest.deadline = datetime.now() + parse_deadline_string(deadline_text)
        
        multiplier = quest.multipliers_config.get(mode, 0.0)
        quest.final_reward = int(quest.base_reward + (quest.base_reward * multiplier))

    db.commit()
    return {"status": "started", "mode": mode, "deadline": quest.deadline, "is_started": True}

@app.post("/complete-task/{quest_id}")
async def complete_task(quest_id: int, db: Session = Depends(get_db)):
    quest = db.query(models.Quest).filter(models.Quest.id == quest_id).first()
    user = db.query(models.User).filter(models.User.id == quest.user_id).first()

    if not quest.selected_difficulty_level:
        raise HTTPException(status_code=400, detail="Task was not started")

    now = datetime.now()
    
    # ЛОГИКА НАГРАДЫ
    if quest.selected_difficulty_level == "none":
        # Сценарий БЕЗ дедлайна: просто базовая награда
        actual_reward = quest.base_reward
        is_success = True
    else:
        # Сценарий С ГЕМБЛИНГОМ
        multiplier = quest.multipliers_config.get(quest.selected_difficulty_level, 0.0)
        
        if quest.deadline and now <= quest.deadline:
            # Уложился: Base + (Base * Coeff)
            actual_reward = quest.base_reward + (quest.base_reward * multiplier)
            is_success = True
        else:
            # Провал дедлайна: Base - (Base * Coeff)
            actual_reward = quest.base_reward - (quest.base_reward * multiplier)
            is_success = False

    # Обновляем баланс и статус
    actual_reward = int(actual_reward)
    user.nuts_amount += actual_reward
    quest.is_completed = True
    quest.final_reward = actual_reward
    
    db.commit()

    # Генерация комментария
    comment = architect.generate_comment(success=is_success)

    return {
        "comment": comment,
        "reward": actual_reward,
        "total_nuts": user.nuts_amount
    }