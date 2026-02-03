
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agents.rag_agent import retrieve_and_generate

queries = [
    "¿Cuántos contratos ISO?", 
    "¿CIF del proveedor Retamares?",
    "Identifica los contratos con una penalización exacta de 10.000 EUR (ni más ni menos)."  # EDGE_05
]

print("=== DEBUG: RESPUESTAS SIN VERIFIER (BASELINE) ===")
for q in queries:
    print(f"\nQUERY: {q}")
    try:
        result = retrieve_and_generate(q)
        print(f"RESPONSE: {result['response']}")
    except Exception as e:
        print(f"ERROR: {e}")
