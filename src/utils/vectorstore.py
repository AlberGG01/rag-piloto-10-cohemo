# -*- coding: utf-8 -*-
"""
Gestión de la base vectorial con ChromaDB.
Usa embeddings de OpenAI text-embedding-3-large.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional

import chromadb
from chromadb.config import Settings
from openai import OpenAI

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import VECTORSTORE_PATH, OPENAI_API_KEY, MODEL_EMBEDDINGS

import threading

logger = logging.getLogger(__name__)


# Variables globales para cache
_openai_client: Optional[OpenAI] = None
_chroma_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection] = None
_client_lock = threading.RLock()  # RLock para permitir llamadas anidadas (get_collection -> get_chroma_client)

COLLECTION_NAME = "contratos_defensa"


def get_openai_client() -> OpenAI:
    """
    Obtiene cliente OpenAI (con caché).
    """
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("Cliente OpenAI inicializado para embeddings")
    return _openai_client


def get_embeddings(texts: List[str], show_progress: bool = True) -> List[List[float]]:
    """Genera embeddings usand OpenAI."""
    client = get_openai_client()
    # Simplified call for re-insertion
    resp = client.embeddings.create(input=texts, model=MODEL_EMBEDDINGS)
    return [d.embedding for d in resp.data]


# ... get_embeddings ok ...


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Obtiene el cliente de ChromaDB (con caché y thread-safe).
    """
    global _chroma_client
    
    if _chroma_client is None:
        with _client_lock:
            # Doble check dentro del lock
            if _chroma_client is None:
                vectorstore_path = Path(VECTORSTORE_PATH)
                vectorstore_path.mkdir(parents=True, exist_ok=True)
                
                logger.info(f"Inicializando ChromaDB en: {vectorstore_path}")
                _chroma_client = chromadb.PersistentClient(
                    path=str(vectorstore_path),
                    settings=Settings(anonymized_telemetry=False)
                )
                logger.info("ChromaDB inicializado")
    
    return _chroma_client


def get_collection() -> chromadb.Collection:
    """
    Obtiene o crea la colección de ChromaDB (thread-safe).
    """
    global _collection
    
    if _collection is None:
        with _client_lock:
            # Doble check dentro del lock
            if _collection is None:
                client = get_chroma_client()
                _collection = client.get_or_create_collection(
                    name=COLLECTION_NAME,
                    metadata={"description": "Chunks de contratos de defensa con embeddings OpenAI 3072-dim"}
                )
                logger.info(f"Colección '{COLLECTION_NAME}' lista con {_collection.count()} documentos")
    
    return _collection


def add_documents(chunks: List[Dict]) -> int:
    """
    Añade chunks a la base vectorial.
    
    Args:
        chunks: Lista de chunks con 'contenido' y 'metadata'.
    
    Returns:
        int: Número de documentos añadidos.
    """
    if not chunks:
        logger.warning("No hay chunks para añadir")
        return 0
    
    import time
    start_time = time.time()
    
    collection = get_collection()
    
    # Preparar datos para ChromaDB
    ids = []
    documents = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"chunk_{i}_{chunk['metadata'].get('archivo', 'unknown')}"
        ids.append(chunk_id)
        documents.append(chunk["contenido"])
        
        # Convertir metadata preservando tipos de datos
        clean_metadata = {}
        for key, value in chunk["metadata"].items():
            if value is not None:
                # Preservar booleanos, números, y strings
                if isinstance(value, (bool, int, float, str)):
                    clean_metadata[key] = value
                elif isinstance(value, list):
                    # Listas se convierten a JSON string para ChromaDB
                    clean_metadata[key] = str(value)
                else:
                    clean_metadata[key] = str(value)
        metadatas.append(clean_metadata)
    
    # Generar embeddings en batches con tracking
    print(f"\n📊 Generando embeddings para {len(documents)} chunks...")
    print(f"   Modelo: {MODEL_EMBEDDINGS} (3072 dimensiones)")
    print(f"   Tiempo estimado: ~{len(documents) // 100 * 2} segundos\n")
    
    embeddings = get_embeddings(documents, show_progress=True)
    
    # Añadir a ChromaDB
    print(f"\n💾 Guardando en ChromaDB...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )
    
    elapsed = time.time() - start_time
    logger.info(f"✅ Añadidos {len(chunks)} chunks en {elapsed:.1f}s ({len(chunks)/elapsed:.1f} chunks/s)")
    print(f"   ✅ Completado en {elapsed:.1f}s\n")
    
    return len(chunks)



def search(query: str, k: int = 5, where: Optional[Dict] = None) -> List[Dict]:
    """
    Busca chunks similares a la query, con opción de filtrado.
    
    Args:
        query: Pregunta o texto de búsqueda.
        k: Número de resultados a retornar.
        where: Filtro de metadatos de ChromaDB (ej: {"num_contrato": "CON_001"}).
    
    Returns:
        List[Dict]: Lista de chunks con contenido y metadata.
    """
    collection = get_collection()
    
    # Generar embedding de la query
    query_embedding = get_embeddings([query])[0]
    
    # Buscar en ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where,  # Filtro opcional
        include=["documents", "metadatas", "distances"]
    )
    
    # Formatear resultados
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "contenido": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distancia": results["distances"][0][i]
        })
    
    logger.info(f"Búsqueda completada: {len(chunks)} resultados para '{query[:50]}...'")
    return chunks


def clear_collection() -> bool:
    """
    Elimina todos los documentos de la colección.
    
    Returns:
        bool: True si se limpió correctamente.
    """
    global _collection
    
    try:
        client = get_chroma_client()
        
        # Eliminar y recrear colección
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # La colección puede no existir
        
        _collection = None
        _collection = get_collection()
        
        logger.info("Colección limpiada y recreada")
        return True
        
    except Exception as e:
        logger.error(f"Error limpiando colección: {e}")
        return False


def get_document_count() -> int:
    """
    Obtiene el número de documentos en la colección.
    
    Returns:
        int: Número de documentos.
    """
    try:
        collection = get_collection()
        return collection.count()
    except Exception:
        return 0


def is_vectorstore_initialized() -> bool:
    """
    Verifica si la base vectorial tiene documentos.
    
    Returns:
        bool: True si hay documentos cargados.
    """
    return get_document_count() > 0
