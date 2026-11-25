from fastapi import APIRouter
from app.database import get_mongo, get_redis, get_cassandra, get_neo4j
router = APIRouter()

@router.get("/health")
def health():
    checks = {}
    try: get_mongo().command("ping"); checks["mongodb"] = "ok"
    except Exception as e: checks["mongodb"] = f"error: {e}"
    try: get_redis().ping(); checks["redis"] = "ok"
    except Exception as e: checks["redis"] = f"error: {e}"
    try: get_cassandra().execute("SELECT now() FROM system.local"); checks["cassandra"] = "ok"
    except Exception as e: checks["cassandra"] = f"error: {e}"
    try:
        with get_neo4j().session() as s: s.run("RETURN 1").single()
        checks["neo4j"] = "ok"
    except Exception as e: checks["neo4j"] = f"error: {e}"
    return {"status": "ok" if all(v == "ok" for v in checks.values()) else "degraded", "databases": checks}
