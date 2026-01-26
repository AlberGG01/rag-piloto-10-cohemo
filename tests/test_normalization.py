# -*- coding: utf-8 -*-
"""
Script de prueba para la normalización inteligente.
"""
import sys
import logging
from pathlib import Path

# Configurar path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.pdf_processor import read_pdf
from src.utils.normalizer import DocumentNormalizer, save_normalized_doc
from src.config import OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    if not OPENAI_API_KEY:
        print("\n❌ ERROR: No se ha encontrado OPENAI_API_KEY en el archivo .env")
        print("Añade la clave y vuelve a intentar.\n")
        return

    # Probar con el primer contrato
    pdf_path = Path("data/contracts/CON_2024_001_Suministro_Vehiculos_Blindados.pdf")
    
    if not pdf_path.exists():
        print(f"❌ ERROR: No se encuentra el archivo {pdf_path}")
        return

    print(f"\n📄 Leyendo PDF: {pdf_path.name}...")
    text = read_pdf(pdf_path)
    
    if not text:
        print("❌ ERROR: No se pudo extraer texto del PDF.")
        return

    print("🧠 Normalizando con GPT-4o (esto puede tardar unos segundos)...")
    normalizer = DocumentNormalizer()
    normalized_text = normalizer.normalize(text)
    
    if normalized_text:
        output_path = save_normalized_doc(normalized_text, pdf_path)
        print(f"✅ ¡ÉXITO! Documento normalizado guardado en: {output_path}")
        print("\n--- PRIMERAS LÍNEAS DEL RESULTADO ---\n")
        print("\n".join(normalized_text.split("\n")[:15]))
        print("\n------------------------------------\n")
    else:
        print("❌ ERROR: La normalización falló.")

if __name__ == "__main__":
    main()
