from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine
from app.api.auth import router as auth_router
from app.api.wallet import router as wallet_router

app = FastAPI(
    title="Lifestyle OS API",
    version="0.1.0"
)

app.include_router(auth_router)
app.include_router(wallet_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "running",
        "message": "Lifestyle OS API is online"
    }


@app.get("/api/db-test")
def test_database():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        )

        row = result.one()

        return {
            "status": "connected",
            "database": row[0],
            "user": row[1]
        }