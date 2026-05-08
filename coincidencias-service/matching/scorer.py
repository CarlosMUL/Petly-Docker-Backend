"""
Combina los features individuales en un score final ponderado.
Los pesos provienen de config.settings para que sean ajustables sin tocar código.
"""

from config import settings
from matching.features import (
    score_color,
    score_descripcion,
    score_especie,
    score_raza,
    score_temporal,
    score_ubicacion,
)
from schemas.schemas import ReporteEventoDTO, ScoreDesglose


def calcular_score(nuevo: ReporteEventoDTO, candidato: ReporteEventoDTO) -> ScoreDesglose:
    s_especie = score_especie(nuevo, candidato)
    s_raza = score_raza(nuevo, candidato)
    s_color = score_color(nuevo, candidato)
    s_ubicacion = score_ubicacion(nuevo, candidato, settings.km_max_distancia)
    s_temporal = score_temporal(nuevo, candidato, settings.dias_max_diferencia)
    s_descripcion = score_descripcion(nuevo, candidato)

    total = (
        s_especie * settings.peso_especie
        + s_raza * settings.peso_raza
        + s_color * settings.peso_color
        + s_ubicacion * settings.peso_ubicacion
        + s_temporal * settings.peso_temporal
        + s_descripcion * settings.peso_descripcion
    )

    return ScoreDesglose(
        especie=round(s_especie, 4),
        raza=round(s_raza, 4),
        color=round(s_color, 4),
        ubicacion=round(s_ubicacion, 4),
        temporal=round(s_temporal, 4),
        descripcion=round(s_descripcion, 4),
        total=round(total, 4),
    )
