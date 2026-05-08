"""
Extracción y normalización de features a partir de un ReporteEventoDTO.
Cada función retorna un valor float entre 0 y 1.
"""

from math import asin, cos, radians, sin, sqrt

from schemas.schemas import ReporteEventoDTO


def score_especie(a: ReporteEventoDTO, b: ReporteEventoDTO) -> float:
    if not a.especie or not b.especie:
        return 0.0
    return 1.0 if a.especie == b.especie else 0.0


def score_raza(a: ReporteEventoDTO, b: ReporteEventoDTO) -> float:
    if not a.raza or not b.raza:
        return 0.5  # dato ausente: incertidumbre, no penaliza completamente
    return 1.0 if a.raza.strip().lower() == b.raza.strip().lower() else 0.0


def score_color(a: ReporteEventoDTO, b: ReporteEventoDTO) -> float:
    if not a.color_principal or not b.color_principal:
        return 0.5
    tokens_a = set(a.color_principal.lower().split())
    tokens_b = set(b.color_principal.lower().split())
    if not tokens_a or not tokens_b:
        return 0.5
    interseccion = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(interseccion) / len(union)  # Jaccard


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))


def score_ubicacion(a: ReporteEventoDTO, b: ReporteEventoDTO, km_max: float) -> float:
    if None in (a.latitud, a.longitud, b.latitud, b.longitud):
        return 0.5
    distancia = _haversine_km(a.latitud, a.longitud, b.latitud, b.longitud)
    if distancia >= km_max:
        return 0.0
    return 1.0 - (distancia / km_max)


def score_temporal(a: ReporteEventoDTO, b: ReporteEventoDTO, dias_max: int) -> float:
    diff = abs((a.fecha_reporte - b.fecha_reporte).days)
    if diff >= dias_max:
        return 0.0
    return 1.0 - (diff / dias_max)


def score_descripcion(a: ReporteEventoDTO, b: ReporteEventoDTO) -> float:
    if not a.descripcion or not b.descripcion:
        return 0.5  # dato ausente: incertidumbre, no penaliza
    from matching.embeddings import similitud_coseno
    return similitud_coseno(a.descripcion, b.descripcion)
