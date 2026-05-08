"""
Singleton del modelo de embeddings multilingüe.
Se carga una sola vez en memoria al primer uso.
"""

import logging

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from config import settings

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Cargando modelo de embeddings '%s'...", settings.embedding_model)
        _model = SentenceTransformer(settings.embedding_model)
        logger.info("Modelo cargado.")
    return _model


def similitud_coseno(texto_a: str, texto_b: str) -> float:
    """Retorna similitud coseno entre dos textos, en rango [0, 1]."""
    model = get_model()
    emb_a, emb_b = model.encode([texto_a, texto_b], convert_to_tensor=True)
    score = cos_sim(emb_a, emb_b).item()
    return max(0.0, min(1.0, float(score)))
