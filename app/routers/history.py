from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.database import get_cassandra
router = APIRouter()

class HistoryEvent(BaseModel):
    book_key: str
    title: str = Field(min_length=1)
    action: str = Field(default="view", pattern="^(view|search|borrow|favorite)$")

@router.post("/users/{user_id}/history", status_code=201)
def add_history(user_id: str, event: HistoryEvent):
    now = datetime.now(timezone.utc)
    try:
        get_cassandra().execute(
            "INSERT INTO user_history (user_id,event_time,book_key,action,title) VALUES (%s,%s,%s,%s,%s)",
            (user_id, now, event.book_key, event.action, event.title))
        return {"message": "Événement enregistré dans Cassandra", "user_id": user_id, "event_time": now.isoformat()}
    except Exception as exc: raise HTTPException(status_code=500, detail=str(exc))

@router.get("/users/{user_id}/history")
def get_history(user_id: str, limit: int = 20):
    if not 1 <= limit <= 100: raise HTTPException(status_code=400, detail="limit doit être compris entre 1 et 100")
    rows = get_cassandra().execute(
        "SELECT user_id,event_time,book_key,action,title FROM user_history WHERE user_id=%s LIMIT %s",
        (user_id, limit))
    return {"user_id": user_id, "events": [dict(row) for row in rows]}
