from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.database import get_neo4j

router = APIRouter()

class Interaction(BaseModel):
    book_key: str
    title: str = Field(min_length=1)
    author_name: str | None = None

@router.post("/graph/users/{user_id}/interactions", status_code=201)
def add_interaction(user_id: str, interaction: Interaction):
    try:
        with get_neo4j().session() as session:
            session.run(
                '''
                MERGE (u:Reader {user_id: $user_id})
                MERGE (b:Book {book_key: $book_key})
                SET b.title = $title
                MERGE (u)-[:VIEWED]->(b)
                ''',
                user_id=user_id, book_key=interaction.book_key, title=interaction.title
            ).consume()
            if interaction.author_name:
                session.run(
                    '''
                    MERGE (b:Book {book_key: $book_key})
                    MERGE (a:Author {name: $author_name})
                    MERGE (b)-[:WRITTEN_BY]->(a)
                    ''',
                    book_key=interaction.book_key, author_name=interaction.author_name
                ).consume()
        return {"message": "Interaction enregistrée dans Neo4j", "user_id": user_id,
                "book_key": interaction.book_key, "title": interaction.title}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/recommendations/{user_id}")
def recommendations(user_id: str, limit: int = 10):
    if not 1 <= limit <= 50:
        raise HTTPException(status_code=400, detail="limit doit être compris entre 1 et 50")
    query = '''
    MATCH (u:Reader {user_id: $user_id})-[:VIEWED]->(:Book)<-[:VIEWED]-(other:Reader)
    MATCH (other)-[:VIEWED]->(candidate:Book)
    WHERE NOT (u)-[:VIEWED]->(candidate)
    RETURN candidate.book_key AS book_key, candidate.title AS title,
           count(DISTINCT other) AS shared_readers
    ORDER BY shared_readers DESC LIMIT $limit
    '''
    try:
        with get_neo4j().session() as session:
            rows = session.run(query, user_id=user_id, limit=limit)
            return {"user_id": user_id, "recommendations": [dict(r) for r in rows]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
