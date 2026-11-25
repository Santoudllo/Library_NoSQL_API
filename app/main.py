from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import initialize_connections, close_connections
from app.routers import books, history, graph, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_connections()
    yield
    close_connections()

app = FastAPI(title="Library NoSQL API", version="1.0.0",
              description="API pédagogique : MongoDB, Redis, Cassandra, Neo4j et Open Library.",
              lifespan=lifespan)
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(books.router, prefix="/api/v1", tags=["Books"])
app.include_router(history.router, prefix="/api/v1", tags=["History - Cassandra"])
app.include_router(graph.router, prefix="/api/v1", tags=["Graph - Neo4j"])

@app.get("/")
def root():
    return {"message": "Library NoSQL API", "docs": "/docs", "health": "/api/v1/health"}
