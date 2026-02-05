
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.confidence_scorer import calculate_confidence

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_confidence():
    print("--- TESTING CONFIDENCE SCORER ---")
    
    # Mock data
    answer = "Respuesta de prueba con suma total 5000 EUR."
    query = "Calcula la suma total de contratos."
    
    # Caso 1: Normal Aggregative
    chunks = [
        ({"metadata": {"source": "doc1.pdf"}, "contenido": "texto 1"}, 0.8),
        ({"metadata": {"source": "doc2.pdf"}, "contenido": "texto 2"}, 0.7)
    ]
    validation = {"overall_valid": True, "numerical": {"valid": True}}
    
    try:
        print("\nTest 1: Normal Aggregative")
        res = calculate_confidence(answer, query, chunks, validation)
        print("Result:", res)
    except Exception as e:
        print("CRASH Test 1:", e)
        import traceback
        traceback.print_exc()

    # Caso 2: Empty Chunks
    try:
        print("\nTest 2: Empty Chunks")
        res = calculate_confidence(answer, query, [], validation)
        print("Result:", res)
    except Exception as e:
        print("CRASH Test 2:", chunks, e)
        traceback.print_exc()

    # Caso 3: None Chunks
    try:
        print("\nTest 3: None Chunks")
        res = calculate_confidence(answer, query, None, validation)
        print("Result:", res)
    except Exception as e:
        print("CRASH Test 3:", e)
        import traceback
        traceback.print_exc()

    # Caso 4: Malformed Chunks (no tuple)
    try:
        print("\nTest 4: Malformed Chunks")
        res = calculate_confidence(answer, query, [{"bad": "format"}], validation)
        print("Result:", res)
    except Exception as e:
        print("CRASH Test 4:", e)
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    test_confidence()
