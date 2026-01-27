import sys
import os
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.rag_agent import retrieve_and_generate

# Configure logging to see our retrieval logs
logging.basicConfig(level=logging.INFO)

def test_q3():
    query = "¿Cuál es el importe de la base imponible EXACTA (con céntimos) del contrato SER_2024_015?"
    print(f"Testing Q3: {query}")
    print("-" * 50)
    
    result = retrieve_and_generate(query)
    
    print("\nResponse:")
    print(result['response'])
    
    print("\nSources:")
    for s in result['sources']:
        print(f"- {s.get('archivo')} (Section: {s.get('metadata', {}).get('tipo_seccion', 'N/A')})")
        # Check if the text snippet contains the target value
        if "15.041.322,31" in s.get("page_content", "") or "15.041.322,31" in s.get("page_content", "").replace(".", ""):
            print("  *** TARGET VALUE FOUND IN CHUNK ***")

if __name__ == "__main__":
    test_q3()
