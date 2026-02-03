# -*- coding: utf-8 -*-
"""
Script para re-normalizar SOLO los documentos que fallaron la auditoría de integridad.
Usa el nuevo prompt blindado de Alta Fidelidad.
"""
import sys
import logging
from pathlib import Path

# Configurar path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.pdf_processor import read_pdf
from src.utils.normalizer import DocumentNormalizer, save_normalized_doc
from src.config import CONTRACTS_PATH, BASE_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Lista de documentos que fallaron según el Integrity Guard
FAILED_DOCUMENTS = [
    "CON_2024_002_Mantenimiento_Armamento.pdf",
    "CON_2024_004_Ciberseguridad_Infraestructuras.pdf",
    "CON_2024_007_Obras_Acuartelamiento_Zaragoza.pdf",
    "CON_2024_009_Comunicaciones_Tacticas.pdf",
    "CON_2024_010_Vigilancia_Instalaciones_Militares.pdf",
    "CON_2024_012_Centro_Mando_Retamares.pdf",
    "LIC_2024_017_Camiones_Logisticos_IVECO.pdf",
    "SER_2024_015_Mantenimiento_Flota_C295.pdf",
    "SER_2024_019_SATCOM_Operaciones.pdf",
    "SUM_2024_014_Material_Sanitario_Militar.pdf"
]

def main():
    print("\n" + "="*80)
    print("🔧 RE-NORMALIZACIÓN DE DOCUMENTOS FALLIDOS")
    print("   Usando Prompt Blindado de Alta Fidelidad")
    print("="*80 + "\n")
    
    normalizer = DocumentNormalizer()
    
    total = len(FAILED_DOCUMENTS)
    success_count = 0
    fail_count = 0
    
    for i, pdf_filename in enumerate(FAILED_DOCUMENTS, 1):
        print(f"\n[{i}/{total}] 🔄 Re-procesando: {pdf_filename}")
        
        pdf_path = CONTRACTS_PATH / pdf_filename
        
        if not pdf_path.exists():
            print(f"  ⚠️  SKIP: No se encontró el PDF {pdf_filename}")
            fail_count += 1
            continue
        
        # Leer PDF original
        text = read_pdf(pdf_path)
        if not text:
            print(f"  ❌ ERROR: No se pudo leer {pdf_filename}")
            fail_count += 1
            continue
        
        print(f"  📄 PDF leído: {len(text)} caracteres")
        
        # Re-normalizar con el nuevo prompt blindado
        print(f"  🤖 Normalizando con GPT-4o (Prompt Blindado)...")
        normalized_text = normalizer.normalize(text)
        
        if normalized_text:
            # Sobrescribir el archivo markdown antiguo
            output_path = save_normalized_doc(normalized_text, pdf_path)
            print(f"  ✅ EXITOSO: Guardado en {output_path.name}")
            print(f"     Tamaño: {len(normalized_text)} caracteres")
            success_count += 1
        else:
            print(f"  ❌ ERROR: Fallo en normalización de {pdf_filename}")
            fail_count += 1
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE RE-NORMALIZACIÓN")
    print("="*80)
    print(f"✅ Exitosos:  {success_count}/{total}")
    print(f"❌ Fallidos:  {fail_count}/{total}")
    
    if success_count == total:
        print("\n🎉 ¡PROCESO COMPLETADO CON ÉXITO!")
        print("📋 SIGUIENTE PASO: Ejecutar 'python scripts/integrity_guard.py' para re-validar")
    else:
        print(f"\n⚠️  Algunos documentos fallaron. Revisar logs.")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
