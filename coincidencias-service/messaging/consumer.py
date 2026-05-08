"""
Escucha la cola `reporte.nuevo` publicada por mascotas-service.
Al recibir un evento, dispara el proceso de matching.
"""

import json
import logging

import aio_pika

from config import settings
from schemas.schemas import ReporteEventoDTO

logger = logging.getLogger(__name__)


async def iniciar_consumer(on_reporte_nuevo):
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    queue = await channel.declare_queue(
        settings.queue_reporte_nuevo, durable=True
    )

    logger.info("Consumer escuchando cola '%s'", settings.queue_reporte_nuevo)

    async with queue.iterator() as msgs:
        async for message in msgs:
            async with message.process(requeue_on_error=True):
                try:
                    data = json.loads(message.body)
                    reporte = ReporteEventoDTO.model_validate(data)
                    await on_reporte_nuevo(reporte)
                except Exception:
                    logger.exception("Error procesando mensaje de reporte nuevo")
