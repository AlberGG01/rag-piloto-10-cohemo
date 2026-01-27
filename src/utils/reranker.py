# -*- coding: utf-8 -*-
"""
Re-ranking local usando BAAI/bge-reranker-v2-m3 (Sentence Transformers).
Elimina coste de OpenAI y reduce latencia tras carga inicial.
"""

import logging
import torch
from typing import List, Dict

# Intentar importar sentence_transformers
try:
    from sentence_transformers import CrossEncoder
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class LocalReranker:
    """
    Clase Singleton para manejo del modelo de re-ranking.
    Carga el modelo solo una vez en memoria.
    """
    _instance = None
    _model = None
    _model_name = "BAAI/bge-reranker-v2-m3"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalReranker, cls).__new__(cls)
        return cls._instance

    def _get_model(self):
        """Lazy loading del modelo."""
        if self._model is None:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.error("sentence-transformers no está instalado. Usando fallback.")
                return None
            
            try:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Cargando modelo de re-ranking local ({self._model_name}) en {device}...")
                self._model = CrossEncoder(self._model_name, device=device)
                logger.info("Modelo de re-ranking cargado exitosamente.")
            except Exception as e:
                logger.error(f"Error cargando modelo de re-ranking: {e}")
                return None
        return self._model

    def rerank(self, query: str, chunks: List[Dict], top_k: int = 10) -> List[Dict]:
        """
        Re-rankea chunks usando CrossEncoder.
        
        Args:
            query: Query del usuario
            chunks: Lista de chunks candidatos
            top_k: Top K a retornar
            
        Returns:
            Lista de chunks ordenados por relevancia
        """
        if not chunks:
            return []
            
        model = self._get_model()
        if not model:
            # Fallback: devolver orden original (o por score vectorial si existe)
            return chunks[:top_k]
        
        # Preparar pares [Query, Documento]
        # Usamos 'contenido' del chunk
        pairs = [[query, chunk.get("contenido", "")] for chunk in chunks]
        
        try:
            # Predecir scores
            scores = model.predict(pairs)
            
            # Asignar scores
            for i, chunk in enumerate(chunks):
                chunk["metadata"]["rerank_score"] = float(scores[i])
            
            # Ordenar (Mayor score = más relevante)
            sorted_chunks = sorted(chunks, key=lambda x: x["metadata"]["rerank_score"], reverse=True)
            
            logger.info(f"Reranked {len(chunks)} -> top {top_k}. Top score: {sorted_chunks[0]['metadata']['rerank_score']:.4f}")
            return sorted_chunks[:top_k]
            
        except Exception as e:
            logger.error(f"Fallo durante predicción de re-ranking: {e}")
            return chunks[:top_k]

# Instancia global (lazy)
_reranker_instance = LocalReranker()

def rerank_chunks(query: str, chunks: List[Dict], top_k: int = 10) -> List[Dict]:
    """
    Función helper pública para re-rankear.
    """
    return _reranker_instance.rerank(query, chunks, top_k)
