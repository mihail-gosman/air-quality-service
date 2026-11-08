import hmac
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

from database import SessionLocal, AirQualityRecord
from fetcher import fetch_all_locations
from cleanup import delete_old_records

API_TOKEN_ENV = "AIR_QUALITY_API_TOKEN"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await fetch_all_locations()
    scheduler.add_job(fetch_all_locations, "interval", minutes=15)
    scheduler.add_job(delete_old_records, "cron", hour=0, minute=0)

    scheduler.start()
    yield
    scheduler.shutdown()
app = FastAPI(title="Air Quality Service", lifespan=lifespan)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_api_key(api_key: str | None = Depends(api_key_header)):
    expected_api_key = os.getenv(API_TOKEN_ENV)
    if not expected_api_key or not expected_api_key.strip():
        raise HTTPException(
            status_code=503,
            detail=f"API access is unavailable: {API_TOKEN_ENV} is not configured",
        )
    if api_key is None or not hmac.compare_digest(
        api_key.encode("utf-8"), expected_api_key.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@app.get("/")
def health_check():
    return {"status": "online", "service": "Air Quality API"}

@app.get("/api/air-quality/latest")
def get_latest_air_quality(
    location: str = Query(..., description="Name of the city, e.g. London, Bucharest, New York, Tokyo"),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db)
):
    record = (
        db.query(AirQualityRecord)
        .filter(AirQualityRecord.location.ilike(location))
        .order_by(AirQualityRecord.timestamp.desc())
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for location: '{location}'. Available locations: London, Bucharest, New York, Tokyo"
        )
    return {
        "location": record.location,
        "latitude": record.latitude,
        "longitude": record.longitude,
        "pm10": record.pm10,
        "pm2_5": record.pm2_5,
        "aqi": record.aqi,
        "provider": record.provider,
        "timestamp": record.timestamp
    }
