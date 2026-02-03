import sys
import os
import asyncio
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.query_router import QueryRouter
from src.agents.query_analyzer import QueryAnalyzer

logging.basicConfig(level=logging.INFO)

async def test_fixes():
    print("🚀 DEBUGGING FIXES")
    
    # 1. Test Router Fix (NUM_08)
    router = QueryRouter()
    q_num_08 = "Proporciona el CIF de la empresa adjudicataria del contrato de Ciberseguridad (CON_2024_004)."
    print(f"\n🔍 Testing Router with: '{q_num_08}'")
    complexity = router.classify(q_num_08)
    print(f"   👉 Classification: {complexity}")
    
    # Check regex
    import re
    p = r'\bCIF\b'
    match = re.search(p, q_num_08, re.I)
    print(f"   👉 Regex '{p}' match: {match}")
    print(f"   👉 Length: {len(q_num_08.split())}")

    # 2. Test Analyzer Fix (INF_02)
    # We need to mock OpenAI or just check if the logic works if we can instantiate it.
    # QueryAnalyzer uses OpenAI.
    # If I run it, it will make a call. That's fine.
    
    analyzer = QueryAnalyzer()
    q_inf_02 = "Compara el importe total del contrato de Ciberseguridad con el de Visión Nocturna. ¿Cuál es mayor y por cuánto?"
    print(f"\n🔍 Testing Analyzer with: '{q_inf_02}'")
    try:
        analysis = analyzer.analyze(q_inf_02)
        print(f"   👉 Analysis Type: {analysis.get('query_type')}")
        print(f"   👉 Filters: {analysis.get('filters')}")
    except Exception as e:
        print(f"   ❌ Analyzer Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_fixes())
