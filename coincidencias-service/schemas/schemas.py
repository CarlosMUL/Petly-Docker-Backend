from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from db.models import (
    Especie,
    EstadoCoincidencia,
    EstadoReporte,
    Sexo,
    Tamanio,
    TipoReporte,
)


class ReporteEventoDTO(BaseModel):
    """
    Evento recibido desde reportes-service vía RabbitMQ al crear un reporte.
    Los alias en camelCase corresponden a los nombres de campo que Jackson
    serializa por defecto desde el modelo Java.
    """

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    reporte_id: int
    tipo_reporte: TipoReporte
    especie: Especie
    raza: str | None = None
    color_principal: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    fecha_reporte: datetime
    imagen_url: str | None = None
    descripcion: str | None = None
    tamanio: Tamanio | None = None
    sexo: Sexo | None = None
    edad_aproximada: int | None = None
    contacto: str | None = None
    run_usuario: int | None = None
    otra_especie: str | None = None
    estado_reporte: EstadoReporte | None = None


class ScoreDesglose(BaseModel):
    especie: float = Field(ge=0, le=1)
    raza: float = Field(ge=0, le=1)
    color: float = Field(ge=0, le=1)
    ubicacion: float = Field(ge=0, le=1)
    temporal: float = Field(ge=0, le=1)
    descripcion: float = Field(ge=0, le=1)
    total: float = Field(ge=0, le=1)


class CoincidenciaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    reporte_perdido_id: int
    reporte_encontrado_id: int
    score: float
    score_especie: float
    score_raza: float
    score_color: float
    score_ubicacion: float
    score_temporal: float
    score_descripcion: float
    estado: EstadoCoincidencia
    fecha_calculo: datetime
    fecha_confirmacion: datetime | None = None


class ActualizarEstadoDTO(BaseModel):
    estado: EstadoCoincidencia


class NotificacionCoincidenciaDTO(BaseModel):
    """Mensaje publicado a notificaciones-service cuando hay match relevante."""

    coincidencia_id: int
    reporte_perdido_id: int
    reporte_encontrado_id: int
    score: float
