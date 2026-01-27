# -*- coding: utf-8 -*-
"""
Repair Agent - Especialista en Reparación Estructural de Markdown (v4.1).
Corrige tablas rotas y formatos inválidos sin alterar el contenido.
"""

import logging
import textwrap
from typing import Dict, Any

from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class RepairAgent(BaseAgent):
    """
    Agente correctivo que repara la sintaxis Markdown defectuosa.
    Especializado en tablas rotas y errores de OCR estructurales.
    """
    
    def __init__(self):
        super().__init__(name="repair_agent")

    def run(self, state: Any) -> Any:
        """
        Método dummy para BaseAgent.
        """
        return state

    def repair_markdown(self, broken_text: str, filename: str = "unknown") -> str:
        """
        Repara un fragmento de Markdown usando instrucciones estrictas.
        
        Args:
            broken_text: Texto MD dañado.
            filename: Referencia para logs.
            
        Returns:
            str: Texto reparado.
        """
        self.logger.info(f"🔧 Iniciando reparación estructural para: {filename}")
        
        prompt = textwrap.dedent(f"""
        MISIÓN: REPARACIÓN ESTRUCTURAL DE MARKDOWN (STRICT MODE)

        CONTEXTO: Eres un experto en sintaxis Markdown. Se te ha entregado un fragmento de un contrato de defensa que ha sufrido errores en la conversión de PDF a texto (OCR).

        TU ÚNICA TAREA: Corregir la sintaxis estructural (principalmente tablas y saltos de línea) para que sea un Markdown válido y legible.

        TEXTO A REPARAR:
        {broken_text}

        REGLAS DE ORO (INCUMPLIMIENTO = ERROR CRÍTICO):
        1. PROHIBIDO alterar números, fechas, nombres de empresas o códigos de contrato.
        2. PROHIBIDO resumir o parafrasear. Si falta texto, deja el espacio, pero no inventes.
        3. SOLO puedes añadir caracteres de control de Markdown: pipes |, guiones -, dos puntos : y saltos de línea \\n.
        4. Si una fila de una tabla está rota (le faltan pipes), complétala basándote en la estructura de las filas adyacentes.

        FORMATO DE SALIDA: Devuelve exclusivamente el fragmento reparado, sin explicaciones ni bloques de código.
        """).strip()
        
        try:
            # Usamos GPT-4o-mini por eficiencia, o GPT-4o si se requiere máxima precisión
            response = self.call_llm(prompt, max_tokens=2000, temperature=0.0, model="gpt-4o-mini")
            
            # Limpieza básica por si el modelo devuelve markdown block
            repaired_text = response.replace("```markdown", "").replace("```", "").strip()
            
            self.logger.info(f"✅ Reparación completada para {filename}")
            return repaired_text

        except Exception as e:
            self.logger.error(f"❌ Fallo en reparación: {e}")
            return broken_text # Fallback: devolver original
