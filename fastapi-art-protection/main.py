from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database import engine, get_db
from routers import protection


ALLOWED_ORIGINS = ["http://localhost:5173"]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(protection.router)

@app.get("/")
def read_root():
    return {"message": "FastAPI is running"}


@app.get("/healthz")
def health_check(db=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "ok"}


@app.on_event("startup")
def setup_database():
    # Ensure the pgvector extension exists before serving requests; tables are managed by Alembic migrations.
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
