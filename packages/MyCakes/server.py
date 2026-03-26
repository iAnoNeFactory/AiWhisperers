import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from database import init_db
from routers import layers, frostings, decorations, cakes, reviews, photos, calculator

BASE_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="MyCakes API", lifespan=lifespan)

# API routes
app.include_router(layers.router,      prefix="/api/layers",      tags=["layers"])
app.include_router(frostings.router,   prefix="/api/frostings",   tags=["frostings"])
app.include_router(decorations.router, prefix="/api/decorations", tags=["decorations"])
app.include_router(cakes.router,       prefix="/api/cakes",       tags=["cakes"])
app.include_router(reviews.router,     prefix="/api/reviews",     tags=["reviews"])
app.include_router(photos.router,      prefix="/api/photos",      tags=["photos"])
app.include_router(calculator.router,  prefix="/api/calculator",  tags=["calculator"])

# Static files (photos)
app.mount("/photos", StaticFiles(directory=BASE_DIR / "static" / "photos"), name="photos")

# Serve SPA
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(BASE_DIR / "static" / "index.html")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
