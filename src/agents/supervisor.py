# -*- coding: utf-8 -*-
"""
Supervisor Agent - Guardián de Integridad de Datos (v4.0).
Valida la calidad del Markdown y extrae metadatos críticos antes de la indexación.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent
from src.utils.llm_config import generate_response
from src.utils.data_safety import compare_numeric_footprint

logger = logging.getLogger(__name__)

class IntegritySupervisor(BaseAgent):
    """
    Agente que audita la calidad estructural y semántica de los documentos.
    Implementa lógica Human-in-the-Loop (HITL) para bloquear documentos defectuosos.
    """
    
    def __init__(self):
        super().__init__(name="integrity_supervisor")
        self.review_file = "pending_review.json"

    def run(self, state: Any) -> Any:
        """
        Método dummy para complacer a BaseAgent. 
        Este agente se usa principalmente offline via audit_markdown.
        """
        return state

    def audit_markdown(self, markdown_text: str, filename: str = "unknown", original_text: str = None) -> Dict[str, Any]:
        """
        Audita el texto Markdown usando un LLM ligero.
        
        Args:
            markdown_text: El contenido del documento normalizado.
            filename: Nombre del archivo origen para logging.
            original_text: Texto original (roto) para validación de seguridad numérica.
            
        Returns:
            Dict con status, score, errores y metadatos.
        """
        self.logger.info(f"👮 Iniciando auditoría de integridad para: {filename}")

        # 0. Safety Belt Check (Pre-LLM) - Si es una re-validación
        safety_error = None
        if original_text:
            safe, msg = compare_numeric_footprint(original_text, markdown_text)
            if not safe:
                self.logger.error(f"🚨 SECURITY VIOLATION: {msg}")
                safety_error = msg
                # Podemos retornar fallo inmediato o dejar que el LLM audite también.
                # Retornamos inmediato para bloquear.
                return {
                    "status": "FAIL",
                    "integrity_score": 0,
                    "detected_errors": [f"SECURITY VIOLATION: {msg}"],
                    "metadata": {}
                }
        
        prompt = f"""Actúa como Supervisor de Calidad de Datos para un sistema RAG de contratos de defensa.
TU TAREA:
Auditar el siguiente texto Markdown convertido desde un PDF para detectar errores de conversión y extraer metadatos clave.

TEXTO A AUDITAR (Primeros 4000 caracteres):
{markdown_text[:4000]}... (truncado para auditoría)

REGLAS DE VALIDACIÓN:
1. **Tablas**: Verifica si hay tablas rotas, pipes `|` desalineados o filas mezcladas.
2. **OCR**: Busca texto basura (ej: ``, `x00`, secuencias sin sentido).
3. **Estructura**: Busca encabezados clave (PLIEGO, OBJETO, PRECIO, ADJUDICATARIO).

EXTRACCIÓN DE METADATOS:
Busca activamente en el texto (encabezados, tablas o texto plano) los siguientes datos:
- ID_Contrato: EL MÁS IMPORTANTE. Busca códigos como 'SER_2024_015', 'CON_2025_001', 'EXP_...', 'LIC_...'. Suele estar en el título o primeras líneas. Si ves 'ID_Contrato: XXX', extrae 'XXX'.
- Adjudicatario: Empresa ganadora.
- Importe_Total: Valor económico global (numérico).
- Objeto: Propósito del contrato.

CLASIFICACIÓN DE SEGURIDAD (Niveles 1-4):
Clasifica el documento según su sensibilidad:
- Nivel 1 (Público): DATASETS PÚBLICOS, manuales de usuario genéricos, boletines oficiales (BOE), pliegos administrativos sin precios. Si es un manual de extintor o similar, es 1.
- Nivel 2 (Uso Interno): Procedimientos standard, listas de inventario no sensibles.
- Nivel 3 (Confidencial): CONTRATOS ESTÁNDAR. Presupuestos, facturas, detalles técnicos de vehículos o armas convencionales. La mayoría de contratos de suministro son Nivel 3.
- Nivel 4 (Restringido): ALERTA INTELIGENCIA. Palabras clave: "Ciberataque", "Vulnerabilidad", "Satélite Espía", "Ubicación Secreta", "Operaciones Especiales". Si habla de debilidades de la defensa nacional, es 4.

CRITERIOS DE FALLO CRÍTICO:
- Si NO encuentras el `ID_Contrato`, el documento es CRÍTICO (Score = 0).

SISTEMA DE PUNTUACIÓN (0-10):
- 10: Perfecto. Estructurado, limpio, todos los metadatos.
- 7-9: Bueno. Errores menores de formato, falta algún metadato no crítico.
- 4-6: Regular. Tablas dudosas, mucho texto sucio.
- 0-3: Crítico. Sin ID, ininteligible, o tablas rotas ilegibles.

FORMATO JSON ESPERADO (Sin bloques de código):
{{
  "status": "PASS" | "FAIL",
  "integrity_score": <int 0-10>,
  "detected_errors": ["..."],
  "metadata": {{
      "id_contrato": "VALOR_DETECTADO_O_VACIO",
      "adjudicatario": "...",
      "importe_total": "...",
      "objeto": "...",
      "security_level": <int 1-4>
  }}
}}

Responde SOLO con el JSON válido.
"""
        
        try:
            # Usamos modelo rápido y barato
            response = self.call_llm(prompt, max_tokens=4096, temperature=0.0, model="gpt-4o-mini")
            
            clean_resp = response.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_resp)
            
            # Validación Post-LLM
            score = result.get("integrity_score", 0)
            
            # Regla de Oro: Sin ID es fallo crítico automático
            meta = result.get("metadata", {})
            if not meta.get("id_contrato") or meta.get("id_contrato") == "NO_ENCONTRADO":
                self.logger.error(f"❌ FALLO CRÍTICO: ID de contrato no encontrado en {filename}")
                score = 0
                result["status"] = "FAIL"
                result["integrity_score"] = 0
                result["detected_errors"].append("CRITICAL: Missing ID_Contrato")

            # HITL Logic
            if score < 7:
                self._log_review_needed(filename, result, markdown_text[:500])
                self.logger.warning(f"⚠️ Documento {filename} marcado para REVISIÓN (Score: {score})")
            else:
                self.logger.info(f"✅ Documento {filename} APROBADO (Score: {score})")
                
            return result

        except Exception as e:
            self.logger.error(f"Error en auditoría: {e}")
            return {
                "status": "FAIL",
                "integrity_score": 0,
                "detected_errors": [f"System Error: {str(e)}"],
                "metadata": {}
            }

    def _log_review_needed(self, filename: str, audit_result: Dict, preview: str):
        """
        Registra el fallo en un archivo JSON para revisión humana.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "audit_result": audit_result,
            "preview_snippet": preview
        }
        
        try:
            data = []
            if os.path.exists(self.review_file):
                with open(self.review_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = [] # Reset if corrupt
            
            data.append(entry)
            
            with open(self.review_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"📝 Incidencia registrada en {self.review_file}")
            
        except Exception as e:
            self.logger.error(f"No se pudo escribir en log de revisión: {e}")

# Uso para pruebas directas
if __name__ == "__main__":
    supervisor = IntegritySupervisor()
    # Test rápido
    dummy_md = "# Contrato SER_2024_001\n| Tabla | Rota |\n|---|---|\n| Dato | \nTexto sucio: "
    print(supervisor.audit_markdown(dummy_md, "test_doc.md"))
