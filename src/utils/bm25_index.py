# -*- coding: utf-8 -*-
"""
Índice BM25 para búsqueda léxica.
"""

import pickle
import logging
from pathlib import Path
from typing import List, Dict
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


class BM25Index:
    """Índice BM25 para búsqueda por keywords."""
    
    def __init__(self, index_path: str = "data/bm25_index.pkl"):
        self.index_path = Path(index_path)
        self.bm25 = None
        self.documents = []
        self.metadatas = []
    
    def build(self, chunks: List[Dict]) -> None:
        """
        Construye el índice BM25 desde chunks.
        
        Args:
            chunks: Lista de chunks con 'contenido' y 'metadata'
        """
        logger.info(f"Construyendo índice BM25 con {len(chunks)} documentos...")
        
        # Tokenizar documentos (simple split por espacios)
        tokenized_docs = [
            doc['contenido'].lower().split()
            for doc in chunks
        ]
        
        self.documents = [doc['contenido'] for doc in chunks]
        self.metadatas = [doc['metadata'] for doc in chunks]
        
        # Crear índice BM25
        self.bm25 = BM25Okapi(tokenized_docs)
        
        logger.info("Índice BM25 construido exitosamente")
        
        # Guardar
        self.save()
    
    def search(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Busca documentos relevantes usando BM25.
        
        Args:
            query: Query de búsqueda
            top_k: Número de resultados a retornar
        
        Returns:
            Lista de chunks con scores BM25
        """
        if self.bm25 is None:
            raise ValueError("Índice BM25 no está cargado. Usa load() primero.")
        
        # Tokenizar query
        tokenized_query = query.lower().split()
        
        # Obtener scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Top-K índices
        top_indices = scores.argsort()[-top_k:][::-1]
        
        # Retornar resultados
        results = []
        for i in top_indices:
            if scores[i] > 0:  # Solo documentos con score positivo
                results.append({
                    'contenido': self.documents[i],
                    'metadata': self.metadatas[i],
                    'score_bm25': float(scores[i])
                })
        
        return results
    
    def save(self) -> None:
        """Guarda el índice en disco."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'bm25': self.bm25,
            'documents': self.documents,
            'metadatas': self.metadatas
        }
        
        with open(self.index_path, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"Índice BM25 guardado en: {self.index_path}")
    
    def load(self) -> None:
        """Carga el índice desde disco."""
        if not self.index_path.exists():
            raise FileNotFoundError(f"Índice BM25 no encontrado en: {self.index_path}")
        
        with open(self.index_path, 'rb') as f:
            data = pickle.load(f)
        
        self.bm25 = data['bm25']
        self.documents = data['documents']
        self.metadatas = data['metadatas']
        
        logger.info(f"Índice BM25 cargado: {len(self.documents)} documentos")
    
    def is_built(self) -> bool:
        """Verifica si el índice existe."""
        return self.index_path.exists()
