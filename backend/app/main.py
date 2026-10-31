from fastapi import FastAPI

from dotenv import load_dotenv

load_dotenv()

from app.core.config import settings
from app.api.routes.health import router as health_router

from app.api.routes.trips import router as trips_router

from app.api.routes.weather import router as weather_router

from app.api.routes.places import router as places_router

from app.api.routes.hotels import router as hotels_router

from app.api.routes.route import router as route_router

from app.api.routes import food

from app.api.routes import planner


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.include_router(trips_router, prefix="/api/trips", tags=["Trips"])

app.include_router(
    health_router,
    prefix="/api",
    tags=["Health"]
)

app.include_router(weather_router, prefix="/api/weather", tags=["Weather"])

app.include_router(
    places_router,
    prefix="/api/places",
    tags=["Places"],
)

app.include_router(
    hotels_router,
    prefix="/api/hotels",
    tags=["Hotels"],
)

app.include_router(
    route_router,
    prefix="/api/routes",
    tags=["Routes"],
)

app.include_router(food.router, prefix="/api/food", tags=["Food"])

app.include_router(
    planner.router,
    prefix="/api/planner",
    tags=["Trip Planner"],
)

@app.get("/")
def root():
    return {
        "message": "Welcome to GoTrip API"
    }

