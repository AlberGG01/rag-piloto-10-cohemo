"""
Normalización segura con logging detallado
"""

import os
import sys
import logging
import re
from pathlib import Path

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # D:\Dev\projects\defense_contracts_system
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import necessary modules
try:
    import pdfplumber
    from src.utils.normalizer import DocumentNormalizer
    from src.config import OPENAI_API_KEY
except ImportError as e:
    print(f"🚨 CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

# Configurar logging
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'normalization_detailed.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def read_pdf_text_plumber(pdf_path):
    """Reads PDF text using pdfplumber (proven to work for CIFs)"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path}: {e}")
        return None
    return text

def normalize_all_with_validation(only_pending=True):
    """Normaliza todos los PDFs con validación"""
    
    pdf_dir = os.path.join(project_root, "data", "contracts")
    output_dir = os.path.join(project_root, "data", "normalized")
    
    if only_pending:
        # Obtener lista de pendientes
        normalized_existing = [
            f.replace('_normalized.md', '.pdf') 
            for f in os.listdir(output_dir) if f.endswith('.md')
        ]
        
        pdfs = [
            f for f in os.listdir(pdf_dir) 
            if f.endswith('.pdf') and f not in normalized_existing
        ]
        
        logger.info(f"🎯 Modo: Solo contratos PENDIENTES ({len(pdfs)} archivos)")
    else:
        # Limpiar directorio de salida
        logger.info("🧹 Limpiando directorio normalized/...")
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.endswith('.md'):
                    os.remove(os.path.join(output_dir, file))
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # Obtener todos los PDFs
        pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        logger.info(f"📚 Modo: Normalización COMPLETA ({len(pdfs)} archivos)")
    
    logger.info(f"📚 Encontrados {len(pdfs)} PDFs para normalizar\n")
    
    results = {
        'success': [],
        'failed': [],
        'warnings': []
    }
    
    # Initialize Normalizer
    if not OPENAI_API_KEY:
        logger.error("❌ ERROR: No se ha encontrado OPENAI_API_KEY")
        return results

    try:
        normalizer = DocumentNormalizer()
    except Exception as e:
        logger.error(f"❌ ERROR initializing DocumentNormalizer: {e}")
        return results

    for i, pdf_file in enumerate(pdfs, 1):
        logger.info(f"{'='*60}")
        logger.info(f"Procesando [{i}/{len(pdfs)}]: {pdf_file}")
        logger.info(f"{'='*60}")
        
        pdf_path = os.path.join(pdf_dir, pdf_file)
        
        try:
            # 1. Read PDF
            raw_text = read_pdf_text_plumber(pdf_path)
            if not raw_text:
                logger.error(f"❌ Error leyendo PDF (texto vacío o error)")
                results['failed'].append(pdf_file)
                continue

            # 2. Normalize
            md_content = normalizer.normalize(raw_text)
            
            if md_content:
                # 3. Save
                output_path = os.path.join(
                    output_dir, 
                    pdf_file.replace('.pdf', '_normalized.md')
                )
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                # 4. Validation
                word_count = len(md_content.split())
                logger.info(f"✅ Normalizado: {word_count} palabras")
                
                warnings = []
                
                # Check 1: CIF/NIF
                cifs = re.findall(r'[A-Z]-?\d{8}', md_content)
                if not cifs:
                    if "CON_2024_004" in pdf_file:
                         warnings.append("⚠️ CRITICAL: Missing CIF in CON_2024_004 (Expected B-55667788)")
                    elif "CONTRATO" in pdf_file.upper():
                         warnings.append("⚠️ No se detectó CIF en documento contractual")
                
                # Check 2: Importes
                importes = re.findall(r'\d+[.,]\d+[.,]?\d*\s*(?:€|EUR)', md_content)
                if not importes and 'CONTRATO' in pdf_file.upper():
                    warnings.append("⚠️ No se detectaron importes")
                
                # Check 3: Fechas
                fechas = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', md_content)
                if not fechas:
                    warnings.append("⚠️ No se detectaron fechas")
                
                if warnings:
                    results['warnings'].append({
                        'file': pdf_file,
                        'issues': warnings
                    })
                    for w in warnings:
                        logger.warning(w)
                else:
                    results['success'].append(pdf_file)
                    logger.info("✅ Validación OK")
            
            else:
                logger.error(f"❌ Normalización retornó vacío")
                results['failed'].append(pdf_file)
        
        except Exception as e:
            logger.error(f"❌ ERROR: {e}")
            results['failed'].append(pdf_file)
        
        logger.info("")  # Línea en blanco
    
    # Resumen final
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMEN DE NORMALIZACIÓN")
    logger.info("="*60)
    logger.info(f"✅ Exitosos: {len(results['success'])}")
    logger.info(f"⚠️  Con advertencias: {len(results['warnings'])}")
    logger.info(f"❌ Fallidos: {len(results['failed'])}")
    
    if results['warnings']:
        logger.warning("\n⚠️  ARCHIVOS CON ADVERTENCIAS:")
        for item in results['warnings']:
            logger.warning(f"  - {item['file']}")
            for issue in item['issues']:
                logger.warning(f"    {issue}")
    
    if results['failed']:
        logger.error("\n❌ ARCHIVOS FALLIDOS:")
        for file in results['failed']:
            logger.error(f"  - {file}")
    
    return results

if __name__ == "__main__":
    results = normalize_all_with_validation()
    
    # Guardar resultados
    import json
    try:
        with open(os.path.join(log_dir, 'normalization_results.json'), 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        logger.info(f"\n📄 Resultados guardados en logs/normalization_results.json")
    except Exception as e:
        logger.error(f"Error saving results json: {e}")
