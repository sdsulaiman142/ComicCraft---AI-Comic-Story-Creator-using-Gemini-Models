from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR, settings
from app.routes import router


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI comic story creator based on the ComicCraft "
        "project specification."
    ),
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)


app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mock_mode": settings.mock_mode
    }