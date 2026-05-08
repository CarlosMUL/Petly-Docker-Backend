import json
import logging

import aio_pika

from config import settings
from schemas.schemas import NotificacionCoincidenciaDTO

logger = logging.getLogger(__name__)

_connection: aio_pika.abc.AbstractConnection | None = None
_channel: aio_pika.abc.AbstractChannel | None = None


async def connect():
    global _connection, _channel
    _connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    _channel = await _connection.channel()
    logger.info("Publisher RabbitMQ conectado")


async def close():
    if _connection:
        await _connection.close()


async def publicar_notificacion(dto: NotificacionCoincidenciaDTO) -> None:
    if _channel is None:
        logger.error("Publisher no inicializado")
        return
    body = json.dumps(dto.model_dump()).encode()
    await _channel.default_exchange.publish(
        aio_pika.Message(body=body, content_type="application/json"),
        routing_key=settings.queue_notificacion,
    )
    logger.debug("Notificación publicada para coincidencia %d", dto.coincidencia_id)
