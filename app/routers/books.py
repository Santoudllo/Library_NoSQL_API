import json
import httpx
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.config import settings
from app.database import get_mongo, get_redis

router = APIRouter()

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    author_name: Optional[str] = None
    isbn: Optional[str] = None
    subjects: list[str] = []
    publish_year: Optional[int] = None
    openlibrary_key: Optional[str] = None

@router.get("/books/search")
def search_books(q: str = Query(min_length=2), limit: int = Query(default=10, ge=1, le=20)):
    key = f"openlibrary:search:{q.lower()}:{limit}"
    cached = get_redis().get(key)
    if cached:
        return {"source": "redis-cache", "count": len(json.loads(cached)), "results": json.loads(cached)}
    try:
        response = httpx.get(
            f"{settings.open_library_base_url}/search.json",
            params={"q": q, "limit": limit},
            headers={"User-Agent": settings.open_library_user_agent},
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Open Library indisponible : {exc}")
    results = []
    for doc in payload.get("docs", []):
        item = {
            "openlibrary_key": doc.get("key"),
            "title": doc.get("title"),
            "author_name": (doc.get("author_name") or [None])[0],
            "first_publish_year": doc.get("first_publish_year"),
            "isbn": (doc.get("isbn") or [None])[0],
            "subjects": (doc.get("subject") or [])[:10],
            "cover_i": doc.get("cover_i"),
        }
        results.append(item)
        if item["openlibrary_key"] and item["title"]:
            get_mongo().books.update_one({"openlibrary_key": item["openlibrary_key"]}, {"$set": item}, upsert=True)
    get_redis().setex(key, settings.cache_ttl_seconds, json.dumps(results))
    return {"source": "open-library-api", "count": len(results), "results": results}

@router.post("/books", status_code=201)
def create_book(book: BookCreate):
    data = book.model_dump()
    if data.get("openlibrary_key"):
        get_mongo().books.update_one({"openlibrary_key": data["openlibrary_key"]}, {"$set": data}, upsert=True)
        saved = get_mongo().books.find_one({"openlibrary_key": data["openlibrary_key"]}, {"_id": 0})
    else:
        result = get_mongo().books.insert_one(data)
        saved = get_mongo().books.find_one({"_id": result.inserted_id}, {"_id": 0})
    return {"message": "Livre enregistré dans MongoDB", "book": saved}

@router.get("/books")
def list_books(limit: int = Query(default=20, ge=1, le=100)):
    return {"results": list(get_mongo().books.find({}, {"_id": 0}).limit(limit))}

@router.get("/books/{book_key}")
def get_book(book_key: str):
    book = get_mongo().books.find_one({"$or": [{"openlibrary_key": book_key}, {"isbn": book_key}]}, {"_id": 0})
    if not book: raise HTTPException(status_code=404, detail="Livre introuvable dans MongoDB")
    return book
