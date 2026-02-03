
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agents.rag_agent import retrieve_and_generate, query_stream

TEST_CASES = [
    ("¿Cuántos contratos ISO?", "agregación"),
    ("CIF del proveedor Retamares", "simple"),
    ("¿Qué contratos ISO Y STANAG?", "multi-criterio"),  # EDGE_08
]

# Test sin streaming (baseline)
print("=== SIN STREAMING (top_k=30, con reranking) ===")
for q, tipo in TEST_CASES:
    try:
        print(f"\n{tipo.upper()}: {q}")
        result = retrieve_and_generate(q)
        answer = result.get("response", "")
        print(f"Respuesta: {answer[:150]}...")
    except Exception as e:
        print(f"Error: {e}")

# Test con streaming (nuevo)
print("\n\n=== CON STREAMING (top_k=10, sin reranking) ===")
for q, tipo in TEST_CASES:
    try:
        print(f"\n{tipo.upper()}: {q}")
        answer_parts = []
        for token in query_stream(q):
            answer_parts.append(token)
        answer = "".join(answer_parts)
        print(f"Respuesta: {answer[:150]}...")
    except Exception as e:
        print(f"Error: {e}")
