# -*- coding: utf-8 -*-
"""
Script para normalizar masivamente todos los contratos.
"""
import sys
import logging
from pathlib import Path

# Configurar path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.pdf_processor import read_pdf, get_all_contracts
from src.utils.normalizer import DocumentNormalizer, save_normalized_doc
from src.config import OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    if not OPENAI_API_KEY:
        print("\n❌ ERROR: No se ha encontrado OPENAI_API_KEY")
        return

    pdf_files = get_all_contracts()
    if not pdf_files:
        print("❌ No se encontraron contratos en la carpeta data/contracts")
        return

    print(f"\n🚀 Iniciando normalización de {len(pdf_files)} documentos...\n")
    normalizer = DocumentNormalizer()
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Procesando: {pdf_path.name}")
        
        text = read_pdf(pdf_path)
        if not text:
            print(f"  ⚠️ Saltando {pdf_path.name}: Error de lectura.")
            continue
            
        normalized_text = normalizer.normalize(text)
        if normalized_text:
            output_path = save_normalized_doc(normalized_text, pdf_path)
            print(f"  ✅ Guardado en: {output_path.name}")
        else:
            print(f"  ❌ Error normalizando {pdf_path.name}")

    print("\n✨ ¡Proceso completado! Todos los documentos han sido normalizados.\n")

if __name__ == "__main__":
    main()
