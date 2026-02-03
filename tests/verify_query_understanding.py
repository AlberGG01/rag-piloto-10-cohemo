import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.agents.query_analyzer import QueryAnalyzer

def test_query_analyzer():
    analyzer = QueryAnalyzer()
    
    test_cases = [
        {
            "query": "Lista los contratos que citan la norma ISO 9001 de forma genérica.",
            "expected_type": ["LIST", "EXHAUSTIVE_SCAN"],
            "expected_entities": ["ISO 9001"]
        },
        {
            "query": "¿Cuál es el importe total del contrato de Retamares?",
            "expected_type": ["FACTUAL"],
            "expected_entities": ["Retamares"]
        },
        {
            "query": "¿Qué contrato tiene mayor densidad de fechas?",
            "expected_type": ["AGGREGATION", "COMPARISON", "FACTUAL"],
            "expected_entities": []
        }
    ]
    
    print("=== TEST DE QUERY UNDERSTANDING LAYER ===\n")
    
    for case in test_cases:
        print(f"🔎 Query: {case['query']}")
        try:
            plan = analyzer.analyze(case['query'])
            print(f"   Type: {plan.get('query_type')}")
            print(f"   Intent: {plan.get('intent')}")
            print(f"   Entities: {plan.get('entities')}")
            print(f"   Strategy: {plan.get('search_strategy')}")
            
            # Basic validation
            matched = False
            if plan.get('query_type') in case['expected_type']: matched = True
            if plan.get('search_strategy') in case['expected_type']: matched = True
            
            if matched:
                 print("   ✅ Type Match")
            else:
                 print(f"   ⚠️ Type Mismatch (Expected: {case['expected_type']})")
                 
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"   ❌ Error: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_query_analyzer()
