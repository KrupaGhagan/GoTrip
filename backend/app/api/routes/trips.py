from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.trip import TripCreate, TripResponse, TripUpdate
from app.services.trip_service import (
    create_trip,
    get_trips,
    get_trip_by_id,
    update_trip,
    delete_trip,
)

router = APIRouter()


@router.post(
    "/",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_trip_endpoint(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
):
    trip = create_trip(db, trip_data)

    return {
        **trip_data.model_dump(),
        "id": str(trip.id),
    }


@router.get("/", response_model=list[TripResponse])
def list_trips(db: Session = Depends(get_db)):
    trips = get_trips(db)

    return [
        {
            "id": str(trip.id),
            "start_location": trip.start_location,
            "destination": trip.destination,
            "start_date": trip.start_date,
            "number_of_days": trip.number_of_days,
            "budget": trip.budget,
        }
        for trip in trips
    ]


@router.get("/{trip_id}", response_model=TripResponse)
def read_trip(trip_id: str, db: Session = Depends(get_db)):
    trip = get_trip_by_id(db, trip_id)

    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    return {
        "id": str(trip.id),
        "start_location": trip.start_location,
        "destination": trip.destination,
        "start_date": trip.start_date,
        "number_of_days": trip.number_of_days,
        "budget": trip.budget,
    }


@router.patch("/{trip_id}", response_model=TripResponse)
def edit_trip(
    trip_id: str,
    updates: TripUpdate,
    db: Session = Depends(get_db),
):
    trip = get_trip_by_id(db, trip_id)

    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    updated_trip = update_trip(
        db,
        trip,
        updates.model_dump(exclude_unset=True),
    )

    return {
        "id": str(updated_trip.id),
        "start_location": updated_trip.start_location,
        "destination": updated_trip.destination,
        "start_date": updated_trip.start_date,
        "number_of_days": updated_trip.number_of_days,
        "budget": updated_trip.budget,
    }


@router.delete("/{trip_id}", status_code=204)
def remove_trip(
    trip_id: str,
    db: Session = Depends(get_db),
):
    trip = get_trip_by_id(db, trip_id)

    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    delete_trip(db, trip)