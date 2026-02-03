
import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.rag_agent import chat

query = "Identifica el contrato de menor cuantía económica"

print("Running debug query...")
try:
    result = chat(query)
    print("Success!")
except Exception:
    traceback.print_exc()
