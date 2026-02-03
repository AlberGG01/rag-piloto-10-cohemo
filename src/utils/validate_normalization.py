# -*- coding: utf-8 -*-
"""
Validador de Normalización PDF → Markdown
Detecta pérdida de información crítica en el proceso de normalización.

USO:
    python validate_normalization.py [pdf_path] [md_path]
    
FUNCIÓN:
    1. Extrae texto completo del PDF
    2. Lee contenido del MD normalizado
    3. Busca términos técnicos críticos en PDF
    4. Verifica si están presentes en MD
    5. Genera reporte de pérdidas

TERMS CRÍTICOS:
    - STANAG (normativa OTAN)
    - MIL-STD (normativa US)
    - ISO/IEC (normativas internacionales)
    - Números de serie, SKUs, referencias técnicas
    - Importes, fechas, CIF/NIF
"""
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
import fitz  # PyMuPDF

# Términos técnicos críticos que NO deben perderse
CRITICAL_PATTERNS = {
    "STANAG": r'STANAG\s+\d{4}',
    "MIL-STD": r'MIL-STD-\d+[A-Z]*',
    "ISO": r'ISO\s+\d+(?:/IEC\s+\d+)?',
    "NATO": r'NATO\s+AEP-\d+',
    "CIF/NIF": r'[A-Z]-\d{8}',
    "Importes": r'\d+(?:\.\d{3})*(?:,\d{2})?\s*€',
    "Fechas": r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
}


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extrae texto completo del PDF usando PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"❌ Error leyendo PDF: {e}")
        return ""


def find_patterns_in_text(text: str, patterns: Dict[str, str]) -> Dict[str, List[str]]:
    """Busca todos los patterns críticos en el texto"""
    found = {}
    for category, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Eliminar duplicados preservando orden
            found[category] = list(dict.fromkeys(matches))
    return found


def validate_normalization(pdf_path: Path, md_path: Path) -> Tuple[bool, Dict]:
    """
    Valida que la normalización no perdió información crítica.
    
    Returns:
        (is_valid, report): Tupla con validación y reporte detallado
    """
    print(f"\n🔍 Validando normalización:")
    print(f"   PDF: {pdf_path.name}")
    print(f"   MD:  {md_path.name}\n")
    
    # Leer contenido
    pdf_text = extract_text_from_pdf(pdf_path)
    if not pdf_text:
        return False, {"error": "No se pudo leer PDF"}
    
    try:
        md_text = md_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, {"error": f"No se pudo leer MD: {e}"}
    
    # Buscar términos críticos
    pdf_terms = find_patterns_in_text(pdf_text, CRITICAL_PATTERNS)
    md_terms = find_patterns_in_text(md_text, CRITICAL_PATTERNS)
    
    # Comparar
    losses = {}
    warnings = {}
    
    for category, pdf_items in pdf_terms.items():
        md_items = md_terms.get(category, [])
        
        # Términos perdidos
        lost_items = [item for item in pdf_items if item not in md_text]
        
        if lost_items:
            # Crítico si son normativas técnicas
            if category in ["STANAG", "MIL-STD", "NATO"]:
                losses[category] = lost_items
            else:
                warnings[category] = lost_items
    
    # Reporte
    report = {
        "pdf_terms": pdf_terms,
        "md_terms": md_terms,
        "losses": losses,
        "warnings": warnings,
        "is_valid": len(losses) == 0
    }
    
    return report["is_valid"], report


def print_report(report: Dict):
    """Imprime reporte de validación con formato"""
    print("\n" + "="*80)
    print("📊 REPORTE DE VALIDACIÓN")
    print("="*80)
    
    # Términos encontrados
    print("\n📌 TÉRMINOS CRÍTICOS EN PDF:")
    for category, items in report["pdf_terms"].items():
        print(f"\n  {category}:")
        for item in items[:5]:  # Máximo 5 por categoría
            print(f"    - {item}")
        if len(items) > 5:
            print(f"    ... ({len(items) - 5} más)")
    
    # Pérdidas críticas
    if report["losses"]:
        print("\n\n❌ PÉRDIDAS CRÍTICAS (Normativas técnicas):")
        for category, items in report["losses"].items():
            print(f"\n  {category}: {len(items)} términos PERDIDOS")
            for item in items:
                print(f"    ❌ {item}")
    
    # Warnings
    if report["warnings"]:
        print("\n\n⚠️ ADVERTENCIAS (Otros términos):")
        for category, items in report["warnings"].items():
            print(f"\n  {category}: {len(items)} términos con diferencias")
            for item in items[:3]:
                print(f"    ⚠️ {item}")
    
    # Veredicto
    print("\n" + "="*80)
    if report["is_valid"]:
        print("✅ VALIDACIÓN EXITOSA - No se detectaron pérdidas críticas")
    else:
        print("❌ VALIDACIÓN FALLIDA - Se detectaron pérdidas de información crítica")
        print("\n🔧 ACCIÓN REQUERIDA:")
        print("   1. Re-normalizar el documento con prompt mejorado")
        print("   2. Verificar que includes todas las normativas técnicas")
        print("   3. Re-ingestar el documento en el vectorstore")
    print("="*80 + "\n")


def main():
    if len(sys.argv) < 3:
        print("Uso: python validate_normalization.py <pdf_path> <md_path>")
        print("\nEjemplo:")
        print("  python validate_normalization.py data/contracts/SUM_2024_006.pdf data/normalized/SUM_2024_006_normalized.md")
        return
    
    pdf_path = Path(sys.argv[1])
    md_path = Path(sys.argv[2])
    
    if not pdf_path.exists():
        print(f"❌ PDF no encontrado: {pdf_path}")
        return
    
    if not md_path.exists():
        print(f"❌ MD no encontrado: {md_path}")
        return
    
    # Validar
    is_valid, report = validate_normalization(pdf_path, md_path)
    
    # Imprimir reporte
    print_report(report)
    
    # Exit code
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
