# -*- coding: utf-8 -*-
"""
🛡️ INTEGRITY GUARD - Auditor de Integridad de Datos
==================================================
Security Guard que valida el flujo de normalización PDF → Markdown
antes de reconstruir la base de datos vectorial.

MISIÓN:
- Extraer cifras críticas de PDFs originales
- Comparar con Markdowns normalizados
- Detectar alucinaciones, truncamientos o pérdidas de datos
- Veredicto: APROBAR o RECHAZAR ingesta a vectorstore
"""

import sys
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.pdf_processor import read_pdf, get_all_contracts
from src.utils.data_safety import extract_numeric_footprint
from src.config import BASE_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CriticalData:
    """Datos críticos extraídos de un documento."""
    importes: List[str]  # Importes en millones/miles
    fechas: List[str]    # Fechas de vencimiento
    avales: List[str]    # Importes de avales
    numeros_contrato: List[str]  # Números de expediente/contrato
    entidades: List[str]  # Bancos, empresas avalistas


class DataExtractor:
    """Extractor de datos críticos de texto."""
    
    # Patrones regex para datos críticos
    IMPORTE_PATTERN = r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s*(?:€|EUR|euros)'
    FECHA_PATTERN = r'\d{1,2}[/-]\d{1,2}[/-]\d{4}'
    NUMERO_CONTRATO_PATTERN = r'(?:CON|LIC|SER|SUM|EXP)[_\s-]?\d{4}[_\s-]?\d{3}'
    AVAL_PATTERN = r'(?:aval|garantía|caución)[^\d]*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:€|EUR)'
    BANCO_PATTERN = r'(?:Banco|BBVA|Santander|CaixaBank|Bankia|Sabadell)\s+\w+'
    
    @staticmethod
    def extract_critical_data(text: str) -> CriticalData:
        """
        Extrae todos los datos críticos de un texto.
        
        Args:
            text: Texto del documento (PDF o Markdown)
            
        Returns:
            CriticalData con todos los datos encontrados
        """
        # Normalizar texto para búsqueda
        text_normalized = text.replace('\n', ' ').replace('\r', ' ')
        
        # Extraer importes
        importes = re.findall(DataExtractor.IMPORTE_PATTERN, text_normalized, re.IGNORECASE)
        importes = [imp.strip() for imp in importes]
        
        # Extraer fechas
        fechas = re.findall(DataExtractor.FECHA_PATTERN, text_normalized)
        fechas = list(set(fechas))  # Deduplicar
        
        # Extraer números de contrato
        numeros_contrato = re.findall(
            DataExtractor.NUMERO_CONTRATO_PATTERN, 
            text_normalized, 
            re.IGNORECASE
        )
        numeros_contrato = [n.strip().replace(' ', '_') for n in numeros_contrato]
        
        # Extraer avales (importes específicos de aval)
        avales = re.findall(DataExtractor.AVAL_PATTERN, text_normalized, re.IGNORECASE)
        
        # Extraer bancos
        entidades = re.findall(DataExtractor.BANCO_PATTERN, text_normalized, re.IGNORECASE)
        entidades = list(set([e.strip() for e in entidades]))
        
        return CriticalData(
            importes=importes,
            fechas=fechas,
            avales=avales,
            numeros_contrato=numeros_contrato,
            entidades=entidades
        )


@dataclass
class ValidationResult:
    """Resultado de validación de un documento."""
    filename: str
    passed: bool
    errors: List[str]
    warnings: List[str]
    pdf_data: CriticalData
    md_data: CriticalData
    
    def __str__(self):
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        return f"{status} - {self.filename}"


class IntegrityGuard:
    """
    Guardián de Integridad de Datos.
    Valida que la normalización no haya perdido o alterado datos críticos.
    """
    
    def __init__(self):
        self.contracts_dir = BASE_DIR / "data" / "contracts"
        self.normalized_dir = BASE_DIR / "data" / "normalized"
        self.extractor = DataExtractor()
        
    def validate_single_document(
        self, 
        pdf_path: Path
    ) -> ValidationResult:
        """
        Valida un solo documento comparando PDF original con Markdown normalizado.
        
        Args:
            pdf_path: Ruta al PDF original
            
        Returns:
            ValidationResult con el veredicto
        """
        filename = pdf_path.stem
        errors = []
        warnings = []
        
        # Leer PDF original
        logger.info(f"📄 Procesando: {pdf_path.name}")
        pdf_text = read_pdf(pdf_path)
        
        if not pdf_text:
            errors.append("No se pudo leer el PDF original")
            return ValidationResult(
                filename=filename,
                passed=False,
                errors=errors,
                warnings=warnings,
                pdf_data=CriticalData([], [], [], [], []),
                md_data=CriticalData([], [], [], [], [])
            )
        
        # Buscar Markdown normalizado correspondiente
        md_path = self.normalized_dir / f"{filename}_normalized.md"
        
        if not md_path.exists():
            errors.append(f"No existe el Markdown normalizado: {md_path.name}")
            return ValidationResult(
                filename=filename,
                passed=False,
                errors=errors,
                warnings=warnings,
                pdf_data=CriticalData([], [], [], [], []),
                md_data=CriticalData([], [], [], [], [])
            )
        
        # Leer Markdown normalizado
        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        # Extraer datos críticos de ambos
        pdf_data = self.extractor.extract_critical_data(pdf_text)
        md_data = self.extractor.extract_critical_data(md_text)
        
        # VALIDACIONES CRÍTICAS
        
        # 1. Validar huella numérica (todos los números deben estar presentes)
        pdf_numbers = extract_numeric_footprint(pdf_text)
        md_numbers = extract_numeric_footprint(md_text)
        
        # Filtrar números muy pequeños (probablemente de formato, páginas, etc)
        pdf_numbers_critical = [n for n in pdf_numbers if len(n.replace('.', '').replace(',', '')) >= 3]
        md_numbers_critical = [n for n in md_numbers if len(n.replace('.', '').replace(',', '')) >= 3]
        
        # Verificar que todos los números críticos del PDF estén en el MD
        for pdf_num in pdf_numbers_critical:
            # Normalizar para comparación (eliminar diferencias de formato)
            pdf_normalized = pdf_num.replace('.', '').replace(',', '')
            
            found = False
            for md_num in md_numbers_critical:
                md_normalized = md_num.replace('.', '').replace(',', '')
                if pdf_normalized == md_normalized:
                    found = True
                    break
            
            if not found:
                errors.append(f"Número PERDIDO en normalización: {pdf_num}")
        
        # 2. Validar importes (magnitudes millonarias críticas)
        if len(pdf_data.importes) > len(md_data.importes):
            missing_count = len(pdf_data.importes) - len(md_data.importes)
            errors.append(f"IMPORTES FALTANTES: {missing_count} importes no aparecen en el Markdown")
        
        # 3. Validar fechas de vencimiento
        if len(pdf_data.fechas) > len(md_data.fechas):
            missing_dates = set(pdf_data.fechas) - set(md_data.fechas)
            if missing_dates:
                errors.append(f"FECHAS PERDIDAS: {missing_dates}")
        
        # 4. Validar números de contrato
        if len(pdf_data.numeros_contrato) > len(md_data.numeros_contrato):
            warnings.append("Algunos números de contrato podrían estar ausentes")
        
        # 5. Validar entidades (bancos avalistas)
        if len(pdf_data.entidades) > len(md_data.entidades):
            missing_entities = set(pdf_data.entidades) - set(md_data.entidades)
            if missing_entities:
                warnings.append(f"Entidades no explícitas en MD: {missing_entities}")
        
        # 6. Truncamiento detector - verificar longitud
        if len(md_text) < len(pdf_text) * 0.5:
            warnings.append(
                f"Markdown es sospechosamente corto ({len(md_text)} chars vs {len(pdf_text)} chars PDF)"
            )
        
        # Veredicto final
        passed = len(errors) == 0
        
        return ValidationResult(
            filename=filename,
            passed=passed,
            errors=errors,
            warnings=warnings,
            pdf_data=pdf_data,
            md_data=md_data
        )
    
    def audit_all_documents(self) -> Tuple[List[ValidationResult], bool]:
        """
        Audita todos los documentos del sistema.
        
        Returns:
            (Lista de resultados, Veredicto global)
        """
        pdf_files = get_all_contracts()
        
        if not pdf_files:
            logger.error("❌ No se encontraron PDFs para auditar")
            return [], False
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🛡️  INTEGRITY GUARD - AUDITORÍA DE INTEGRIDAD DE DATOS")
        logger.info(f"{'='*70}")
        logger.info(f"📋 Documentos a validar: {len(pdf_files)}\n")
        
        results = []
        
        for pdf_path in pdf_files:
            result = self.validate_single_document(pdf_path)
            results.append(result)
            
            # Mostrar resultado inmediato
            print(f"\n{result}")
            
            if result.errors:
                for error in result.errors:
                    print(f"  ❌ ERROR: {error}")
            
            if result.warnings:
                for warning in result.warnings:
                    print(f"  ⚠️  WARNING: {warning}")
        
        # Resumen final
        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count
        
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 RESUMEN DE AUDITORÍA")
        logger.info(f"{'='*70}")
        logger.info(f"✅ APROBADOS: {passed_count}/{len(results)}")
        logger.info(f"❌ FALLIDOS:  {failed_count}/{len(results)}")
        
        # Veredicto global
        all_passed = failed_count == 0
        
        logger.info(f"\n{'='*70}")
        if all_passed:
            logger.info("🎉 VEREDICTO: ESTRUCTURA VALIDADA")
            logger.info("✅ PROCEDER A RECONSTRUCCIÓN DE BASE VECTORIAL")
        else:
            logger.error("🚨 VEREDICTO: VALIDACIÓN FALLIDA")
            logger.error("❌ NO PROCEDER - Corregir discrepancias antes de indexar")
            logger.error("\n📋 Documentos con errores:")
            for r in results:
                if not r.passed:
                    logger.error(f"  - {r.filename}")
        logger.info(f"{'='*70}\n")
        
        return results, all_passed
    
    def generate_report(self, results: List[ValidationResult], output_path: Optional[Path] = None):
        """
        Genera un reporte detallado en JSON.
        
        Args:
            results: Resultados de validación
            output_path: Ruta donde guardar el reporte (opcional)
        """
        report = {
            "total_documents": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "details": []
        }
        
        for result in results:
            report["details"].append({
                "filename": result.filename,
                "passed": result.passed,
                "errors": result.errors,
                "warnings": result.warnings,
                "pdf_critical_data": {
                    "importes_count": len(result.pdf_data.importes),
                    "fechas_count": len(result.pdf_data.fechas),
                    "avales_count": len(result.pdf_data.avales),
                    "numeros_contrato": result.pdf_data.numeros_contrato,
                    "entidades": result.pdf_data.entidades
                },
                "md_critical_data": {
                    "importes_count": len(result.md_data.importes),
                    "fechas_count": len(result.md_data.fechas),
                    "avales_count": len(result.md_data.avales),
                    "numeros_contrato": result.md_data.numeros_contrato,
                    "entidades": result.md_data.entidades
                }
            })
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Reporte guardado en: {output_path}")
        
        return report


def main():
    """Ejecuta la auditoría completa."""
    guard = IntegrityGuard()
    results, passed = guard.audit_all_documents()
    
    # Generar reporte JSON
    report_path = BASE_DIR / "data" / "integrity_audit_report.json"
    guard.generate_report(results, report_path)
    
    # Códigos de salida
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
