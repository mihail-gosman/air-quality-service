from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import SessionLocal, AirQualityRecord
from fetcher import fetch_all_locations
from cleanup import delete_old_records

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

@app.get("/")
def health_check():
    return {"status": "online", "service": "Air Quality API"}
@app.get("/api/air-quality/latest")
def get_latest_air_quality(
    location: str = Query(..., description="Name of the city, e.g. London, Bucharest, New York, Tokyo"),
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
