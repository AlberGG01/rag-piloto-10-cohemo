# -*- coding: utf-8 -*-
"""
Script para re-normalizar SOLO los 5 documentos que AÚN fallan tras múltiples iteraciones.
Usa el prompt quirúrgico ultra-específico.
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

# Lista de los 5 documentos que TODAVÍA fallan (75% → objetivo 100%)
FINAL_FAILED_DOCUMENTS = [
    "CON_2024_004_Ciberseguridad_Infraestructuras.pdf",
    "CON_2024_010_Vigilancia_Instalaciones_Militares.pdf",
    "LIC_2024_017_Camiones_Logisticos_IVECO.pdf",
    "SER_2024_015_Mantenimiento_Flota_C295.pdf",
    "SER_2024_019_SATCOM_Operaciones.pdf"
]

def main():
    print("\n" + "="*80)
    print("🔬 REPARACIÓN QUIRÚRGICA - ITERACIÓN FINAL")
    print("   5 documentos rebeldes con protocolo anti-resumen")
    print("="*80 + "\n")
    
    normalizer = DocumentNormalizer()
    
    total = len(FINAL_FAILED_DOCUMENTS)
    success_count = 0
    fail_count = 0
    
    for i, pdf_filename in enumerate(FINAL_FAILED_DOCUMENTS, 1):
        print(f"\n[{i}/{total}] 🎯 REPARACIÓN QUIRÚRGICA: {pdf_filename}")
        
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
        
        # Mostrar hint específico según el documento
        if "CON_2024_010" in pdf_filename:
            print(f"  🎯 Objetivo: Capturar número de aval '28011231'")
        elif "CON_2024_004" in pdf_filename:
            print(f"  🎯 Objetivo: Preservar TODOS los '2017' en normativas")
        elif "LIC_2024_017" in pdf_filename:
            print(f"  🎯 Objetivo: Capturar códigos bancarios largos")
        
        # Re-normalizar con el prompt quirúrgico
        print(f"  🔬 Normalizando con GPT-4o (Protocolo Quirúrgico)...")
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
        
        # Pequeña pausa para evitar rate limit
        if i < total:
            import time
            time.sleep(1)
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE REPARACIÓN QUIRÚRGICA")
    print("="*80)
    print(f"✅ Exitosos:  {success_count}/{total}")
    print(f"❌ Fallidos:  {fail_count}/{total}")
    
    if success_count == total:
        print("\n🎉 ¡REPARACIÓN COMPLETADA CON ÉXITO!")
        print("📋 PASO FINAL: Ejecutar 'python scripts/integrity_guard.py' para validación")
        print("   Objetivo: 20/20 documentos aprobados (100%)")
    else:
        print(f"\n⚠️  Algunos documentos fallaron. Revisar logs.")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
