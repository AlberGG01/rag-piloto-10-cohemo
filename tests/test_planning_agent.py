# -*- coding: utf-8 -*-
"""
Test del Planning Agent con diferentes tipos de queries.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph.workflow import run_agentic_rag


def test_planning_agent():
    """Test del planner con queries de diferentes complejidades."""
    
    print("\n" + "="*80)
    print("TEST: Planning Agent - Día 2")
    print("="*80)
    
    # Definir queries de test
    test_queries = [
        {
            "query": "¿Cuál es el importe del contrato CON_2024_012?",
            "expected_complexity": "simple"
        },
        {
            "query": "¿Qué contratos tienen clasificación SECRETO Y importe superior a 20 millones?",
            "expected_complexity": "multi-hop"
        },
        {
            "query": "¿Cuál es la suma total de todos los avales bancarios en el sistema?",
            "expected_complexity": "aggregation"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/3")
        print(f"{'='*80}")
        print(f"Query: {test['query']}")
        print(f"Complejidad esperada: {test['expected_complexity']}")
        
        result = run_agentic_rag(test['query'])
        
        metadata = result.get('metadata', {})
        complexity = metadata.get('complexity', 'N/A')
        
        print(f"\nComplejidad detectada: {complexity}")
        
        if complexity == test['expected_complexity']:
            print("✅ Clasificación CORRECTA")
        else:
            print(f"❌ Clasificación incorrecta (esperado: {test['expected_complexity']})")
        
        # Mostrar plan si existe
        if 'execution_plan' in metadata:
            print(f"\nPlan de ejecución:")
            print(metadata['execution_plan'])
    
    print("\n" + "="*80)
    print("✅ Planning Agent - Tests completados")
    print("="*80)


if __name__ == "__main__":
    test_planning_agent()
