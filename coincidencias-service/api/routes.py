import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from cache.redis_client import get_client
from config import settings
from db.database import get_db
from schemas.schemas import ActualizarEstadoDTO, CoincidenciaResponse
from services.coincidencia_service import actualizar_estado, listar_por_reporte

router = APIRouter(prefix="/coincidencias", tags=["Coincidencias"])

_CACHE_KEY = "coincidencias:reporte:{}"


@router.get("/reporte/{reporte_id}", response_model=list[CoincidenciaResponse])
async def get_por_reporte(reporte_id: int, db: Session = Depends(get_db)):
    """Retorna todas las coincidencias asociadas a un reporte (perdido o encontrado)."""
    r = get_client()
    cache_key = _CACHE_KEY.format(reporte_id)

    cached = await r.get(cache_key)
    if cached:
        return [CoincidenciaResponse.model_validate(item) for item in json.loads(cached)]

    resultado = listar_por_reporte(reporte_id, db)
    await r.setex(
        cache_key,
        settings.redis_ttl_query,
        json.dumps([item.model_dump(mode="json") for item in resultado]),
    )
    return resultado


@router.patch("/{coincidencia_id}/estado", response_model=CoincidenciaResponse)
async def patch_estado(
    coincidencia_id: int,
    dto: ActualizarEstadoDTO,
    db: Session = Depends(get_db),
):
    """Permite confirmar o descartar una coincidencia manualmente."""
    resultado = actualizar_estado(coincidencia_id, dto, db)
    if not resultado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coincidencia no encontrada")

    # Invalidar caché para ambos reportes involucrados
    r = get_client()
    async with r.pipeline() as pipe:
        pipe.delete(_CACHE_KEY.format(resultado.reporte_perdido_id))
        pipe.delete(_CACHE_KEY.format(resultado.reporte_encontrado_id))
        await pipe.execute()

    return resultado
