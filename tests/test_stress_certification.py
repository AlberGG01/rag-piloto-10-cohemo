# -*- coding: utf-8 -*-
"""
Stress Certification Script.
Ejecuta una consulta masiva para verificar:
1. Token Budgeting (Recorte de contexto)
2. Exponential Backoff (Manejo de Rate Limits)
"""

import sys
import logging
import time
from pathlib import Path

# Configurar logging para ver los mensajes de los agentes en consola
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Ajustar nivel de logs para ver los warnings de retries y trimming
logging.getLogger("agent.synthesis").setLevel(logging.INFO)
logging.getLogger("agent.base_agent").setLevel(logging.WARNING) # Para ver retries

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph.workflow import run_agentic_rag

def run_stress_test():
    print("="*80)
    print("🔥 INICIANDO TEST DE ESTRÉS: TOKEN BUDGETING & BACKOFF 🔥")
    print("="*80)
    
    query = (
        "Genera un informe ejecutivo exhaustivo que compare el objeto de todos los contratos "
        "del repositorio, sus importes totales, fechas de finalización y el estado detallado "
        "de sus avales, clasificándolos por nivel de riesgo financiero."
    )
    
    print(f"\nQuery Masiva: {query}\n")
    
    start_time = time.time()
    result = run_agentic_rag(query)
    duration = time.time() - start_time
    
    print("\n" + "="*80)
    print("RESULTADO FINAL DEL RAG:")
    print("="*80)
    print(result.get('answer', 'Sin respuesta'))
    
    print("\n" + "="*80)
    print(f"ESTADÍSTICAS DE EJECUCIÓN (Tiempo: {duration:.2f}s)")
    print("="*80)
    
    # Intentar extraer info de logs analizando metadata (si persistimos algo)
    # O simplemente confiamos en la salida de consola que hemos configurado arriba.
    
    meta = result.get('metadata', {})
    eval_report = result.get('evaluation_report', {})
    
    print(f"- Eval Score: {meta.get('evaluation_score')}")
    print(f"- Retries Grafo: {meta.get('retry_count')}")
    print(f"- Sources Used: {len(result.get('sources', []))}")
    
    print("\n✅ Test finalizado. Revisar logs superiores para confirmar 'Contexto recortado' y 'Intento LLM fallido'.")

if __name__ == "__main__":
    run_stress_test()
