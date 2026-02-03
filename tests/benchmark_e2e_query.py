# -*- coding: utf-8 -*-
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.rag_agent import chat

# Query compleja del Golden Dataset
query = "¿Cuál es el importe total del contrato de Retamares y cuántos días de ejecución tiene?"

print("="*60)
print("🔄 BENCHMARK END-TO-END: Query Compleja")
print("="*60)
print(f"Query: {query}\n")

# Medir tiempo total
start_total = time.time()

try:
    response = chat(query)
    end_total = time.time()
    
    latency_total = end_total - start_total
    
    print(f"⏱️  LATENCIA TOTAL: {latency_total:.2f}s")
    print(f"\n📄 Respuesta generada (extracto):")
    print(response[:300] + "..." if len(response) > 300 else response)
    
    # Evaluación
    print("\n" + "="*60)
    if latency_total < 10:
        print("✅ EXCELENTE: Sistema optimizado correctamente")
    elif latency_total < 60:
        print("⚠️  PARCIAL: Hay mejora (Fast path o Streaming?), pero re-ranking pesa")
    else:
        print("❌ SIN MEJORA: Latencia similar a baseline CPU (~210s)")
    
except Exception as e:
    print(f"❌ ERROR en ejecución: {e}")

print("="*60)
