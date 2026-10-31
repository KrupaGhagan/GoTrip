from sqlalchemy.orm import Session

from app.models import Trip
from app.schemas.trip import TripCreate


def create_trip(db: Session, trip_data: TripCreate) -> Trip:
    trip = Trip(**trip_data.model_dump())

    db.add(trip)
    db.commit()
    db.refresh(trip)

    return trip

def get_trips(db: Session) -> list[Trip]:
    return db.query(Trip).order_by(Trip.created_at.desc()).all()


def get_trip_by_id(db: Session, trip_id: str) -> Trip | None:
    return db.query(Trip).filter(Trip.id == trip_id).first()

def update_trip(db: Session, trip: Trip, updates: dict) -> Trip:
    for field, value in updates.items():
        setattr(trip, field, value)

    db.commit()
    db.refresh(trip)
    return trip


def delete_trip(db: Session, trip: Trip) -> None:
    db.delete(trip)
    db.commit()