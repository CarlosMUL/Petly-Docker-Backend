import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.routes import router
from cache import redis_client
from config import settings
from db.database import Base, SessionLocal, engine
from messaging.consumer import iniciar_consumer
from messaging.publisher import close as publisher_close
from messaging.publisher import connect as publisher_connect
from services.coincidencia_service import procesar_reporte_nuevo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _on_reporte_nuevo(reporte):
    db = SessionLocal()
    try:
        await procesar_reporte_nuevo(reporte, db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    await redis_client.connect()
    await publisher_connect()
    consumer_task = asyncio.create_task(iniciar_consumer(_on_reporte_nuevo))
    logger.info("coincidencias-service iniciado en puerto %d", settings.app_port)
    yield
    consumer_task.cancel()
    await publisher_close()
    await redis_client.close()


app = FastAPI(
    title="Coincidencias Service",
    description="Motor de matching ML entre reportes de mascotas perdidas y encontradas.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port, reload=False)
