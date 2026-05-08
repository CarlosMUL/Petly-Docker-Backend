from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "coincidencias_db"
    db_user: str = "coincidencias_user"
    db_password: str = "secret"

    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    queue_reporte_nuevo: str = "reporte.nuevo"
    queue_matching_resultado: str = "matching.resultado"
    queue_notificacion: str = "notificacion.coincidencia"

    redis_url: str = "redis://localhost:6379"
    redis_ttl_reporte: int = 604800   # 7 días en segundos
    redis_ttl_query: int = 60         # caché de respuestas REST

    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    score_threshold: float = 0.55
    max_candidatos: int = 100
    dias_max_diferencia: int = 60
    km_max_distancia: float = 50.0

    peso_especie: float = 0.30
    peso_raza: float = 0.20
    peso_color: float = 0.15
    peso_ubicacion: float = 0.15
    peso_temporal: float = 0.10
    peso_descripcion: float = 0.10

    app_port: int = 8085


settings = Settings()
