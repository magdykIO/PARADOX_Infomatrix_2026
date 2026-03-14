from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models

# 1. Змінюємо ім'я тут: з router на social_router
social_router = APIRouter(prefix="/social", tags=["social"])

# 2. Оновлюємо декоратор: @social_router замість @router
@social_router.post("/send-challenge")
def send_challenge(receiver_username: str, title: str, reward: int, db: Session = Depends(get_db)):
    # 1. Пошук відправника
    me = db.query(models.User).filter(models.User.id == 1).first() 
    
    # 2. Пошук отримувача
    receiver = db.query(models.User).filter(models.User.username == receiver_username).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Друга не знайдено!")

    # 3. Перевірка балансу горішків
    if me.nuts_amount < reward:
        raise HTTPException(status_code=400, detail="Недостатньо горішків для виклику!")

    # 4. Списання (заморозка) горішків у відправника
    me.nuts_amount -= reward

    # 5. Створення квесту
    new_quest = models.Quest(
        title=title,
        final_reward=reward,
        user_id=receiver.id, # Виконавець
        sender_id=me.id,     # Ти як спонсор
        from_who=me.username,
        is_started=True
    )
    
    db.add(new_quest)
    db.commit()
    
    return {"status": "success", "message": f"Виклик кинуто {receiver_username}!"}