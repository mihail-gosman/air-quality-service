import httpx
import asyncio
from datetime import datetime, timezone
from database import SessionLocal, AirQualityRecord

LOCATIONS = [
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "Bucharest", "lat": 44.4323, "lon": 26.1063},
    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
]

async def _fetch_single_location(client: httpx.AsyncClient, loc: dict):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": loc["lat"],
        "longitude": loc["lon"],
        "current": "pm10,pm2_5,european_aqi"
    }

    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        current_data = data.get("current", {})

        return AirQualityRecord(
            location=loc["name"],
            latitude=loc["lat"],
            longitude=loc["lon"],
            pm10=current_data.get("pm10"),
            pm2_5=current_data.get("pm2_5"),
            aqi=current_data.get("european_aqi"),
            provider="Open-Meteo",
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        print(f"[{datetime.now()}] Error fetching {loc['name']}: {e}")
        return None

async def fetch_all_locations():
    print(f"[{datetime.now()}] Starting multi-location data fetch...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [_fetch_single_location(client, loc) for loc in LOCATIONS]
        results = await asyncio.gather(*tasks)

    valid_records = [record for record in results if record is not None]

    if valid_records:
        db = SessionLocal()
        try:
            db.add_all(valid_records)
            db.commit()
            print(f"[{datetime.now()}] Saved data for {len(valid_records)} locations.")
        finally:
            db.close()

if __name__ == "__main__":
    asyncio.run(fetch_all_locations())
