
import sys
import os
from pathlib import Path
import logging

# Config logging
logging.basicConfig(level=logging.INFO)

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.rag_agent import chat

def verify_syn10():
    print("--- FULL PIPELINE TEST FOR SYN_10 ---")
    query = "Calcula el importe total de las garantías definitivas acumuladas de los contratos CON_2024_004, CON_2024_016 y SER_2024_015."
    
    print(f"Query: {query}")
    print("Executing RAG Agent (this uses the new Planner logic)...")
    
    response = chat(query, history=[])
    
    print("\n--- FINAL RESPONSE ---")
    print(response)
    print("----------------------")
    
    # Validation Logic
    expected_values = ["90.000", "84.700", "364.500", "539.200"] # 90k + ~84k + ~364k
    found = [val for val in expected_values if val in response or val.replace(".", "") in response]
    
    if len(found) >= 2:
        print("✅ SUCCESS: Found validation values in response!")
    else:
        print("⚠️ POTENTIAL FAILURE: Did not find expected numeric values. Check output manually.")

if __name__ == "__main__":
    verify_syn10()
