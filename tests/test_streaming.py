
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agents.rag_agent import query_stream

print("Testeando streaming...")
start = time.time()

first_token_time = None
query = "¿CIF de Retamares?"

print(f"Query: {query}")
try:
    token_count = 0
    for i, token in enumerate(query_stream(query)):
        if i == 0:
            first_token_time = time.time() - start
            print(f"\n⏱️ TTFT: {first_token_time:.2f}s")
        print(token, end="", flush=True)
        token_count += 1

    total_time = time.time() - start
    print(f"\n\n⏱️ Total: {total_time:.2f}s")
    
    if first_token_time is None:
        print("\n❌ NO TOKENS RECEIVED")
    elif first_token_time < 2.0:
        print(f"\n✅ TTFT SUCCESS ({first_token_time:.2f}s < 2s)")
    else:
        print(f"\n❌ TTFT FAIL ({first_token_time:.2f}s >= 2s)")

except Exception as e:
    print(f"\nERROR: {e}")
