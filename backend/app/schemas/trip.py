from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class TripCreate(BaseModel):
    start_location: str = Field(min_length=1, max_length=150)
    destination: str = Field(min_length=1, max_length=150)
    start_date: date
    number_of_days: int = Field(gt=0)
    budget: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

    @field_validator("start_date")
    @classmethod
    def start_date_must_be_today_or_future(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("start_date must be today or a future date")
        return value


class TripResponse(TripCreate):
    id: str


class TripUpdate(BaseModel):
    start_location: str | None = Field(default=None, min_length=1, max_length=150)
    destination: str | None = Field(default=None, min_length=1, max_length=150)
    start_date: date | None = None
    number_of_days: int | None = Field(default=None, gt=0)
    budget: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)