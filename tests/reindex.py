# -*- coding: utf-8 -*-
"""
Re-indexación rápida con metadata corregida
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.vectorstore import clear_collection, add_documents
from src.utils.chunking import create_all_chunks

print("\nLimpiando vectorstore...")
clear_collection()

print("Creando chunks con metadata enriquecida...")
chunks = create_all_chunks()

print(f"Indexando {len(chunks)} chunks...")
add_documents(chunks)

print("\n✅ Re-indexación completada\n")
