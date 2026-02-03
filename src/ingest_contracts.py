# -*- coding: utf-8 -*-
"""
Script de Ingestión MAESTRA.
Ejecutar ESTRICTAMENTE cuando se añadan nuevos contratos.
Realiza:
1. Limpieza de VectorStore (ChromaDB).
2. Procesamiento de PDFs con PyMuPDFLoader (Tablas + Anexos).
3. Generación de Embeddings (OpenAI) y almacenamiento en ChromaDB.
4. Construcción y guardado de índice BM25.
5. Generación de Metadata Cache para contexto rápido.
"""

import json
import logging
import time
from pathlib import Path
from typing import List, Dict

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.pdf_processor import get_all_contracts
from src.utils.chunking import create_chunks_from_pdf
from src.utils.vectorstore import clear_collection, add_documents
from src.utils.bm25_index import BM25Index

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

METADATA_CACHE_PATH = Path("data/metadata_cache.txt") # Guardamos como texto listo para inyectar

def generate_metadata_context_cache(metadatas: List[Dict]) -> None:
    """
    Genera y guarda el contexto de resumen de contratos para el agente.
    Replica la lógica de 'build_metadata_context' pero offline.
    """
    logger.info("Generando caché de contexto de metadatos...")
    
    contract_data = []
    for meta in metadatas:
        # Limpiar importe para ordenar
        raw_importe = meta.get("importe", "0")
        try:
            clean_importe = raw_importe.replace("€", "").replace("EUR", "").replace(".", "").replace(",", ".").replace(" ", "").strip()
            importe_float = float(clean_importe)
        except (ValueError, AttributeError):
            importe_float = 0.0
            
        contract_data.append({
            "num": meta.get("num_contrato", "N/A"),
            "importe": meta.get("importe", "N/A"),
            "importe_val": importe_float,
            "fecha_fin": meta.get("fecha_fin", "N/A"),
            "tipo": meta.get("tipo_contrato", "N/A"),
            "aval_venc": meta.get("aval_vencimiento", "N/A"),
            "entidad_aval": meta.get("aval_entidad", "N/A"),
            "aval_importe": meta.get("aval_importe", "N/A"),
            "normas": meta.get("normas", "N/A"),
            "confidencial": "Sí" if meta.get("requiere_confidencialidad") else "No"
        })
    
    # Ordenar por Número de Contrato (para consistencia)
    contract_data.sort(key=lambda x: str(x["num"]))
    
    lines = ["LISTA DE CONTRATOS DISPONIBLES (Referencia completa):"]
    for c in contract_data:
        normas_str = f", Normas={c['normas']}" if c['normas'] else ""
        aval_str = f", AvalVence={c['aval_venc']}, AvalEntidad={c['entidad_aval']}"
        lines.append(f"{c['num']}: Importe={c['importe']}, Tipo={c['tipo']}, Vence={c['fecha_fin']}{normas_str}{aval_str}")
    
    context_text = "\n".join(lines)
    
    # Guardar en disco
    METADATA_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_CACHE_PATH, "w", encoding="utf-8") as f:
        f.write(context_text)
        
    logger.info(f"✅ Metadata Cache guardado en: {METADATA_CACHE_PATH}")


def main():
    start_global = time.time()
    print("\n🚀 INICIANDO PROCESO DE INGESTIÓN MASIVA (OFFLINE)\n")
    print("⚠️  Esto borrará la base de datos actual y la reconstruirá.")
    print("⏳  Puede tomar varios minutos dependiendo de la cantidad de PDFs.\n")
    
    # 1. Limpiar BD existente
    print("🧹 Limpiando VectorStore...")
    clear_collection()
    
    # 2. Obtener contratos
    pdf_files = get_all_contracts()
    if not pdf_files:
        logger.error("❌ No hay contratos en data/contracts. Abortando.")
        return

    all_chunks = []
    unique_metadatas = {} # Para el caché, un metadata por contrato
    
    # 3. Procesar cada PDF
    print(f"\n📄 Procesando {len(pdf_files)} documentos con PyMuPDF...")
    
    for pdf_path in pdf_files:
        try:
            chunks = create_chunks_from_pdf(pdf_path)
            if not chunks:
                logger.warning(f"⚠️ {pdf_path.name} no generó chunks.")
                continue
                
            # Añadir a la lista global para BM25
            all_chunks.extend(chunks)
            
            # Guardar metadata representativa (usamos la del primer chunk que suele tener todo)
            # Mejor aún: Combinar lo mejor de los chunks si fuera necesario, pero el chunking ya propaga global_meta
            if chunks[0]["metadata"].get("num_contrato"): 
                key = chunks[0]["metadata"]["num_contrato"]
                unique_metadatas[key] = chunks[0]["metadata"]
            else:
                unique_metadatas[pdf_path.name] = chunks[0]["metadata"]
            
            # Añadir a ChromaDB (Vectorial)
            # Lo hacemos archivo por archivo para gestión de memoria y progreso visual
            add_documents(chunks)
            
        except Exception as e:
            logger.error(f"❌ Error crítico procesando {pdf_path.name}: {e}")

    # 4. Construir índice BM25
    print(f"\n📚 Construyendo Índice Invertido BM25 con {len(all_chunks)} chunks...")
    bm25 = BM25Index()
    bm25.build(all_chunks)
    
    # 5. Generar Caché de Contexto
    print("\n💾 Generando Caché de Metadatos...")
    generate_metadata_context_cache(list(unique_metadatas.values()))
    
    total_time = time.time() - start_global
    print(f"\n✨ INGESTIÓN COMPLETADA EN {total_time:.1f} SEGUNDOS")
    print(f"📊 Total Chunks: {len(all_chunks)}")
    print(f"📂 Contratos Procesados: {len(unique_metadatas)}")
    print("✅ El sistema está listo para 'rag_agent.py' en modo FAST-PATH.")

if __name__ == "__main__":
    main()
