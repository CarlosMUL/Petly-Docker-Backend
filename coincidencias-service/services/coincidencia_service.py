"""
Capa de negocio: orquesta BD, motor ML y publicación de notificaciones.
"""

import asyncio
import logging

from sqlalchemy.orm import Session

from cache.redis_client import get_client
from config import settings
from db.models import Coincidencia, EstadoCoincidencia, TipoReporte
from matching.engine import ResultadoMatch, ejecutar_matching
from messaging.publisher import publicar_notificacion
from schemas.schemas import (
    ActualizarEstadoDTO,
    CoincidenciaResponse,
    NotificacionCoincidenciaDTO,
    ReporteEventoDTO,
)

logger = logging.getLogger(__name__)

_TIPOS_OPUESTOS = {
    TipoReporte.PERDIDA: {TipoReporte.ENCONTRADA, TipoReporte.AVISTAMIENTO},
    TipoReporte.ENCONTRADA: {TipoReporte.PERDIDA},
    TipoReporte.AVISTAMIENTO: {TipoReporte.PERDIDA},
}


async def registrar_reporte_en_cache(reporte: ReporteEventoDTO) -> None:
    r = get_client()
    async with r.pipeline(transaction=True) as pipe:
        pipe.setex(
            f"reporte:{reporte.reporte_id}",
            settings.redis_ttl_reporte,
            reporte.model_dump_json(),
        )
        pipe.sadd(f"reportes:tipo:{reporte.tipo_reporte.value}", str(reporte.reporte_id))
        await pipe.execute()


async def _candidatos_opuestos(nuevo: ReporteEventoDTO) -> list[ReporteEventoDTO]:
    r = get_client()
    tipos_opuestos = _TIPOS_OPUESTOS.get(nuevo.tipo_reporte, set())

    all_ids: set[str] = set()
    for tipo in tipos_opuestos:
        ids = await r.smembers(f"reportes:tipo:{tipo.value}")
        all_ids.update(ids)

    if not all_ids:
        return []

    # Obtener todos los reportes en un único round-trip
    valores = await r.mget(*[f"reporte:{id_}" for id_ in all_ids])

    return [
        ReporteEventoDTO.model_validate_json(v)
        for v in valores
        if v is not None
    ]


async def procesar_reporte_nuevo(reporte: ReporteEventoDTO, db: Session) -> None:
    await registrar_reporte_en_cache(reporte)
    candidatos = await _candidatos_opuestos(reporte)

    if not candidatos:
        logger.info("Sin candidatos para reporte %d", reporte.reporte_id)
        return

    resultados: list[ResultadoMatch] = await asyncio.to_thread(
        ejecutar_matching, reporte, candidatos, db
    )

    for r in resultados:
        coincidencia = (
            db.query(Coincidencia)
            .filter_by(
                reporte_perdido_id=r.reporte_perdido_id,
                reporte_encontrado_id=r.reporte_encontrado_id,
            )
            .order_by(Coincidencia.fecha_calculo.desc())
            .first()
        )
        if coincidencia:
            await publicar_notificacion(
                NotificacionCoincidenciaDTO(
                    coincidencia_id=coincidencia.id,
                    reporte_perdido_id=r.reporte_perdido_id,
                    reporte_encontrado_id=r.reporte_encontrado_id,
                    score=r.score,
                )
            )


def listar_por_reporte(reporte_id: int, db: Session) -> list[CoincidenciaResponse]:
    rows = (
        db.query(Coincidencia)
        .filter(
            (Coincidencia.reporte_perdido_id == reporte_id)
            | (Coincidencia.reporte_encontrado_id == reporte_id)
        )
        .order_by(Coincidencia.score.desc())
        .all()
    )
    return [CoincidenciaResponse.model_validate(r) for r in rows]


def actualizar_estado(
    coincidencia_id: int, dto: ActualizarEstadoDTO, db: Session
) -> CoincidenciaResponse | None:
    coincidencia = db.get(Coincidencia, coincidencia_id)
    if not coincidencia:
        return None
    coincidencia.estado = dto.estado
    if dto.estado == EstadoCoincidencia.CONFIRMADA:
        from datetime import datetime
        coincidencia.fecha_confirmacion = datetime.utcnow()
    db.commit()
    db.refresh(coincidencia)
    return CoincidenciaResponse.model_validate(coincidencia)
