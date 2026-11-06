from datetime import datetime, timedelta, timezone
from database import SessionLocal, AirQualityRecord

RETENTION_DAYS = 7

def delete_old_records():
    db = SessionLocal()
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
        deleted_count = db.query(AirQualityRecord).filter(
            AirQualityRecord.timestamp < cutoff_time
        ).delete()

        db.commit()
        print(f"[{datetime.now()}] Cleanup complete: {deleted_count} record(s) older than {RETENTION_DAYS} days removed.")
        return deleted_count
    except Exception as e:
        db.rollback()
        print(f"[{datetime.now()}] Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_old_records()
