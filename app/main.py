from __future__ import annotations

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # connect to redis
    await redis_service.connect()
    logger.info("Application startup complete.")


@app.on_event("shutdown")
async def shutdown_event():
    await redis_service.disconnect()


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, log_level="info")
