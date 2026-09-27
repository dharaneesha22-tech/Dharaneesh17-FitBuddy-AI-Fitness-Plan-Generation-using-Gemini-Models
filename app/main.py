from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create all database tables when the application starts
    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="AI powered fitness and workout plan generator",
    version="1.0.0",
    lifespan=lifespan
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


app.include_router(router)


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "application": "FitBuddy"
    }