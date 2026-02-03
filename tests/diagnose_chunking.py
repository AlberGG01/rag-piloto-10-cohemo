# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO: Inspeccionar chunks ANTES de guardar en ChromaDB
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.chunking import create_chunks_from_pdf

# Test con CON_2024_004
pdf_path = Path("data/normalized/CON_2024_004_Ciberseguridad_Infraestructuras_normalized.md")

print("="*80)
print("🔍 DIAGNÓSTICO: CHUNKING DE CON_2024_004")
print("="*80)

chunks = create_chunks_from_pdf(pdf_path)

print(f"\n📊 Total chunks generados: {len(chunks)}")

# Buscar chunk con "subcontratación prohibida"
print("\n🎯 Buscando chunks con 'subcontrat'...")
found = False
for i, chunk in enumerate(chunks, 1):
    content = chunk.get("contenido", "")
    if "subcontrat" in content.lower():
        found = True
        print(f"\n✅ CHUNK #{i} CONTIENE 'subcontrat':")
        print(f"   Longitud: {len(content)} chars")
        print(f"   Metadata: {chunk.get('metadata', {}).get('source', 'N/A')}")
        print(f"\n   CONTENIDO:")
        print(f"   {content}")
        print("\n" + "-"*80)

if not found:
    print("\n❌ NO se encontró 'subcontrat' en ningún chunk")
    print("\n🔍 Mostrando primeros 3 chunks:")
    for i, chunk in enumerate(chunks[:3], 1):
        content = chunk.get("contenido", "")
        print(f"\nChunk #{i}:")
        print(f"   Longitud: {len(content)} chars")
        print(f"   Contenido: {content[:200]}...")

# Verificar si hay chunks vacíos
empty_chunks = [i for i, c in enumerate(chunks, 1) if len(c.get("contenido", "").strip()) == 0]
if empty_chunks:
    print(f"\n⚠️ CHUNKS VACÍOS DETECTADOS: {len(empty_chunks)}/{len(chunks)}")
    print(f"   Posiciones: {empty_chunks[:10]}")
else:
    print(f"\n✅ No hay chunks vacíos")
