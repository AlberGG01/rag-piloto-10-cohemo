# -*- coding: utf-8 -*-
"""
Script de inicialización de la base vectorial.
Ejecutar UNA VEZ antes de lanzar la aplicación.

Uso:
    python init_vectorstore.py
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Configurar path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import CONTRACTS_PATH, NORMALIZED_PATH, LOGS_PATH, LOGS_FILE
from src.utils.pdf_processor import get_contracts_count
from src.utils.chunking import create_all_chunks
from src.utils.vectorstore import (
    clear_collection,
    add_documents,
    get_document_count,
    is_vectorstore_initialized
)
from src.utils.llm_config import is_model_available, get_model_info

# Configurar logging
LOGS_PATH.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(LOGS_FILE)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_header():
    """Imprime el encabezado del script."""
    print("\n" + "=" * 60)
    print("🛡️  SISTEMA DE CONTROL DE CONTRATOS DE DEFENSA")
    print("    Inicialización de Base Vectorial")
    print("=" * 60 + "\n")


def check_prerequisites():
    """Verifica los requisitos previos."""
    print("📋 Verificando requisitos...\n")
    
    all_ok = True
    
    # Verificar carpeta de normalizados
    if not NORMALIZED_PATH.exists() or not list(NORMALIZED_PATH.glob("*.md")):
        print(f"   ⚠️  No se han encontrado documentos normalizados en: {NORMALIZED_PATH}")
        print(f"      Ejecuta primero 'python normalize_all.py'")
        all_ok = False
    else:
        norm_count = len(list(NORMALIZED_PATH.glob("*.md")))
        print(f"   ✅ Documentos normalizados encontrados: {norm_count}")
    
    print()
    return all_ok


def initialize_vectorstore():
    """Inicializa o reinicializa la base vectorial desde documentos normalizados."""
    print("🗄️  Inicializando base vectorial...\n")
    
    # Verificar si ya hay documentos
    current_count = get_document_count()
    if current_count > 0:
        print(f"   ℹ️  Base vectorial existente con {current_count} documentos")
        response = input("   ¿Deseas borrar y reinicializar? (s/n): ").strip().lower()
        if response != 's':
            print("   Operación cancelada.")
            return False
        
        print("   Limpiando base vectorial...")
        clear_collection()
    
    # Contar documentos normalizados
    md_files = list(NORMALIZED_PATH.glob("*.md"))
    if not md_files:
        print("\n   ❌ No hay documentos normalizados para procesar.")
        print(f"      Ejecuta primero: python normalize_all.py")
        return False
    
    print(f"\n   📄 Procesando {len(md_files)} documentos normalizados...")
    
    # Crear chunks desde los archivos normalizados
    print("   🔄 Creando chunks semánticos desde Markdown...")
    chunks = create_all_chunks()
    
    if not chunks:
        print("   ❌ No se pudieron crear chunks.")
        return False
    
    print(f"   ✅ Creados {len(chunks)} chunks")
    
    # Añadir a ChromaDB
    print("   🔄 Generando embeddings y guardando en ChromaDB...")
    added = add_documents(chunks)
    
    print(f"   ✅ Añadidos {added} documentos a la base vectorial")
    
    # Construir índice BM25 (Léxico)
    print("   📚 Construyendo índice BM25 (Léxico)...")
    try:
        from src.utils.bm25_index import BM25Index
        bm25 = BM25Index()
        bm25.build(chunks)
        print(f"   ✅ Índice BM25 construido para {len(chunks)} chunks")
    except Exception as e:
        print(f"   ❌ Error construyendo BM25: {e}")
        return False
    
    return True


def print_summary():
    """Imprime el resumen final."""
    print("\n" + "-" * 60)
    print("📊 RESUMEN")
    print("-" * 60)
    
    # Contar archivos normalizados
    normalized_count = len(list(NORMALIZED_PATH.glob("*.md"))) if NORMALIZED_PATH.exists() else 0
    
    print(f"   Documentos normalizados: {normalized_count}")
    print(f"   Chunks en vectorstore: {get_document_count()}")
    print(f"   Base vectorial lista: {'✅ Sí' if is_vectorstore_initialized() else '❌ No'}")
    print(f"   Modelo disponible: {'✅ Sí' if is_model_available() else '❌ No'}")
    print(f"   Modo: OpenAI (text-embedding-3-large)")
    
    print("\n" + "=" * 60)
    print("✅ Inicialización completada")
    print("\nPara ejecutar la aplicación:")
    print("   streamlit run app.py")
    print("=" * 60 + "\n")


def main():
    """Función principal."""
    print_header()
    
    logger.info("Iniciando script de inicialización de vectorstore")
    
    # Verificar requisitos
    has_docs = check_prerequisites()
    
    if has_docs:
        # Inicializar vectorstore
        success = initialize_vectorstore()
        
        if success:
            logger.info("Vectorstore inicializado correctamente")
        else:
            logger.warning("Vectorstore no inicializado")
    else:
        print("ℹ️  No hay documentos normalizados disponibles.")
        print("   Ejecuta primero 'python normalize_all.py' para procesar los PDFs.\n")
    
    # Mostrar resumen
    print_summary()


if __name__ == "__main__":
    main()
