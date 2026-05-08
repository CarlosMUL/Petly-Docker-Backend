import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class EstadoCoincidencia(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    DESCARTADA = "DESCARTADA"


class TipoReporte(str, enum.Enum):
    PERDIDA = "PERDIDA"
    ENCONTRADA = "ENCONTRADA"
    AVISTAMIENTO = "AVISTAMIENTO"


class EstadoReporte(str, enum.Enum):
    ACTIVO = "ACTIVO"
    EN_PROCESO = "EN_PROCESO"
    RESUELTO = "RESUELTO"
    CERRADO = "CERRADO"


class Especie(str, enum.Enum):
    PERRO = "PERRO"
    GATO = "GATO"
    OTRO = "OTRO"


class Tamanio(str, enum.Enum):
    PEQUENO = "PEQUENO"
    MEDIANO = "MEDIANO"
    GRANDE = "GRANDE"


class Sexo(str, enum.Enum):
    MACHO = "MACHO"
    HEMBRA = "HEMBRA"
    DESCONOCIDO = "DESCONOCIDO"


class Coincidencia(Base):
    __tablename__ = "coincidencias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reporte_perdido_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    reporte_encontrado_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    score_especie: Mapped[float] = mapped_column(Float, nullable=False)
    score_raza: Mapped[float] = mapped_column(Float, nullable=False)
    score_color: Mapped[float] = mapped_column(Float, nullable=False)
    score_ubicacion: Mapped[float] = mapped_column(Float, nullable=False)
    score_temporal: Mapped[float] = mapped_column(Float, nullable=False)
    score_descripcion: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estado: Mapped[EstadoCoincidencia] = mapped_column(
        Enum(EstadoCoincidencia), default=EstadoCoincidencia.PENDIENTE, nullable=False
    )
    fecha_calculo: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    fecha_confirmacion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
