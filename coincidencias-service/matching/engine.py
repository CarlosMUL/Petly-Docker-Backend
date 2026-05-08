"""
Orquesta el proceso de matching:
1. Recibe un reporte nuevo.
2. Busca candidatos del tipo opuesto en la BD.
3. Calcula scores y filtra por umbral.
4. Retorna los pares ordenados por score descendente.
"""

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from config import settings
from db.models import Coincidencia, EstadoCoincidencia, TipoReporte
from matching.scorer import calcular_score
from schemas.schemas import ReporteEventoDTO

logger = logging.getLogger(__name__)


@dataclass
class ResultadoMatch:
    reporte_perdido_id: int
    reporte_encontrado_id: int
    score: float
    score_especie: float
    score_raza: float
    score_color: float
    score_ubicacion: float
    score_temporal: float
    score_descripcion: float


def ejecutar_matching(
    nuevo_reporte: ReporteEventoDTO,
    candidatos: list[ReporteEventoDTO],
    db: Session,
) -> list[ResultadoMatch]:
    resultados: list[ResultadoMatch] = []

    for candidato in candidatos:
        desglose = calcular_score(nuevo_reporte, candidato)

        if desglose.total < settings.score_threshold:
            continue

        if nuevo_reporte.tipo_reporte == TipoReporte.PERDIDA:
            perdido_id, encontrado_id = nuevo_reporte.reporte_id, candidato.reporte_id
        else:
            perdido_id, encontrado_id = candidato.reporte_id, nuevo_reporte.reporte_id

        coincidencia = Coincidencia(
            reporte_perdido_id=perdido_id,
            reporte_encontrado_id=encontrado_id,
            score=desglose.total,
            score_especie=desglose.especie,
            score_raza=desglose.raza,
            score_color=desglose.color,
            score_ubicacion=desglose.ubicacion,
            score_temporal=desglose.temporal,
            score_descripcion=desglose.descripcion,
            estado=EstadoCoincidencia.PENDIENTE,
        )
        db.add(coincidencia)

        resultados.append(
            ResultadoMatch(
                reporte_perdido_id=perdido_id,
                reporte_encontrado_id=encontrado_id,
                score=desglose.total,
                score_especie=desglose.especie,
                score_raza=desglose.raza,
                score_color=desglose.color,
                score_ubicacion=desglose.ubicacion,
                score_temporal=desglose.temporal,
                score_descripcion=desglose.descripcion,
            )
        )

    db.commit()
    logger.info(
        "Matching para reporte %s: %d candidatos evaluados, %d coincidencias guardadas",
        nuevo_reporte.reporte_id,
        len(candidatos),
        len(resultados),
    )
    return sorted(resultados, key=lambda r: r.score, reverse=True)
