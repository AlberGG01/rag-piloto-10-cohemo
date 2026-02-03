
"""
Benchmark de latencia del sistema actual (v1.4)
"""
import time
import sys
import os

# Ensure src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.rag_agent import retrieve_and_generate

queries = [
    "¿Cuál es el importe total del contrato de Retamares?",
    "¿Qué normativa ISO específica se exige en CON_2024_010?",
    "Compara los importes de Ciberseguridad vs Visión Nocturna",
    "¿Qué contratos incluyen penalización de 50.000 EUR diarios?",
    "Identifica el contrato de menor cuantía económica"
]

print("="*60)
print("⏱️  BENCHMARK DE LATENCIA v1.4")
print("="*60)

latencies = []

for i, query in enumerate(queries, 1):
    print(f"\n[{i}/5] {query[:50]}...")
    
    start = time.time()
    try:
        # Use citations=True as requested for v1.4 validation
        result = retrieve_and_generate(query, use_citations=True)
        latency = time.time() - start
        
        latencies.append(latency)
        
        print(f"  Tiempo: {latency:.2f}s")
        # Handle potential missing keys if error occurred
        conf = result.get('confidence', {}).get('confidence', 0)
        print(f"  Confidence: {conf:.1f}%")
        
        valid = result.get('validation', {}).get('overall_valid', False)
        print(f"  Validación: {'✅ PASS' if valid else '❌ FAIL'}")
        
    except Exception as e:
        print(f"  ❌ Error en query: {e}")
        latencies.append(0) # Penalty

# Resumen
if latencies:
    valid_latencies = [l for l in latencies if l > 0]
    if not valid_latencies:
        print("\n❌ No successful queries.")
        sys.exit(1)
        
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    print(f"Queries ejecutadas: {len(valid_latencies)}")
    print(f"Latencia promedio: {sum(valid_latencies)/len(valid_latencies):.2f}s")
    print(f"Latencia mínima: {min(valid_latencies):.2f}s")
    print(f"Latencia máxima: {max(valid_latencies):.2f}s")

    BASELINE_AVG = 14.27
    current_avg = sum(valid_latencies)/len(valid_latencies)

    if current_avg < BASELINE_AVG * 1.2:
        print(f"\n✅ LATENCIA ACEPTABLE (baseline: {BASELINE_AVG:.2f}s)")
    else:
        print(f"\n⚠️  LATENCIA AUMENTÓ: {current_avg:.2f}s vs baseline {BASELINE_AVG:.2f}s")
else:
    print("\n❌ No latencies recorded.")
