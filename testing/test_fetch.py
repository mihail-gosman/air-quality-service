import httpx
import asyncio

LATITUDE = 51.5074
LONGITUDE = -0.1278
LOCATION_NAME = "London"

async def test_api_call():
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "pm10,pm2_5,european_aqi"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        current_data = data.get("current", {})
        normalized_record = {
            "location": LOCATION_NAME,
            "pm10": current_data.get("pm10"),
            "pm2_5": current_data.get("pm2_5"),
            "aqi": current_data.get("european_aqi"),
            "provider": "Open-Meteo",
            "timestamp": current_data.get("time")
        }
        for key, value in normalized_record.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_api_call())
