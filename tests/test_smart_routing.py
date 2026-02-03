
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.query_router import QueryRouter
from src.agents.rag_agent import retrieve_and_generate

def test_router_classification():
    """Valida que el clasificador funciona correctamente."""
    router = QueryRouter()
    
    test_cases = [
        ("¿CIF de Retamares?", "SIMPLE"),
        ("¿Fecha de firma CON_2024_001?", "SIMPLE"),
        ("¿Compara contratos ISO vs STANAG?", "COMPLEX"), # Has 2 terms -> COMPLEX
        ("¿Cuántos contratos hay en total?", "COMPLEX"),
        ("¿Lista todos los contratos ISO?", "COMPLEX"),
        ("¿Qué contratos ISO Y STANAG?", "COMPLEX"),
        ("Hola", "MEDIUM"), # Default fallback
    ]
    
    print("=== TEST: Clasificador de Complejidad ===\n")
    
    passed = 0
    for query, expected in test_cases:
        result = router.classify(query)
        status = "✅" if result == expected else "❌"
        print(f"{status} {query}")
        print(f"   Esperado: {expected} | Obtenido: {result}\n")
        if result == expected:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(test_cases)} correctos")
    return passed == len(test_cases)

def test_adaptive_query():
    """Valida que el routing adaptativo funciona (check logs for 'Smart Routing')."""
    
    test_cases = [
        ("¿CIF de Retamares?", "SIMPLE", 15),  # max 15s (SIMPLE should be fast)
        ("¿Cuántos contratos ISO?", "COMPLEX", 180),  # max 180s (COMPLEX uses reranker)
    ]
    
    print("\n=== TEST: Query Adaptativo ===\n")
    
    for query, expected_complexity, max_latency in test_cases:
        print(f"Query: {query}")
        print(f"Complejidad esperada: {expected_complexity}")
        
        start = time.time()
        # Usamos retrieve_and_generate que ahora usa el router internamente
        result = retrieve_and_generate(query)
        answer = result.get("response", "")
        elapsed = time.time() - start
        
        print(f"Latencia: {elapsed:.1f}s (max: {max_latency}s)")
        print(f"Respuesta: {answer[:100]}...")
        
        status = "✅" if elapsed < max_latency else "⚠️"
        print(f"{status} Dentro de límite\n")

if __name__ == "__main__":
    # Test 1: Clasificador
    if test_router_classification():
        print("\n✅ Clasificador validado")
        
        # Test 2: Adaptive query
        test_adaptive_query()
    else:
        print("\n❌ Clasificador falló, revisar lógica")
