# -*- coding: utf-8 -*-
"""
Test del Evaluation Agent (Día 4).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph.workflow import run_agentic_rag


def test_evaluation_agent():
    """Test del flujo completo hasta evaluación."""
    
    print("\n" + "="*80)
    print("TEST: Evaluation Agent - Día 4")
    print("="*80)
    
    # Query compleja que debería tener info suficiente o parcial
    query = "¿Cuál es la suma total de todos los avales bancarios en el sistema?"
    
    print(f"\nQuery: {query}")
    print("Ejecutando workflow (Orchestrator -> Planner -> Retrieval -> Evaluator)...")
    
    result = run_agentic_rag(query)
    
    metadata = result.get('metadata', {})
    eval_report = metadata.get('evaluation_report', {})
    
    print(f"\n=== RESULTADOS DE EVALUACIÓN ===")
    print(f"Status: {eval_report.get('status', 'N/A')}")
    print(f"Score: {eval_report.get('score', 0)}")
    print(f"\nReasoning:")
    print(f"{eval_report.get('reasoning', 'N/A')}")
    
    print(f"\nMissing Info:")
    missing = eval_report.get('missing_info', [])
    if missing:
        for item in missing:
            print(f"  - {item}")
    else:
        print("  (Ninguna)")
    
    if eval_report.get('status') in ["SUFFICIENT", "PARTIAL"]:
        print("\n✅ Evaluation Agent funcionando correctamente")
    else:
        print("\n⚠️ Resultado INSUFFICIENT (Revisar si es esperado por falta de docs)")


if __name__ == "__main__":
    test_evaluation_agent()
