from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./air_quality.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AirQualityRecord(Base):
    __tablename__ = "air_quality"
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    pm2_5 = Column(Float, nullable=True)
    pm10 = Column(Float, nullable=True)
    aqi = Column(Float, nullable=True)
    provider = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

Base.metadata.create_all(bind=engine)
