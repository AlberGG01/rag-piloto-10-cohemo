# -*- coding: utf-8 -*-
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.reranker import rerank_chunks, _reranker_instance

# Simular 15 chunks y una query
query = "¿Cuál es el importe total del contrato de Retamares?"
chunks = [
    {"contenido": "El importe total del contrato es de 1.234.567,89 EUR", "metadata": {}},
    {"contenido": "Cláusula administrativa particular sobre modificaciones", "metadata": {}},
    {"contenido": "El plazo de ejecución es de 880 días naturales", "metadata": {}},
] * 5  # Genera 15 chunks

print("="*60)
print("⏱️  BENCHMARK: RE-RANKING AISLADO (15 chunks)")
print("="*60)

# Obtener device para info
model = _reranker_instance._get_model()
device = model.device if model else "Unknown"
print(f"Device usado: {device}")

# Warm-up
_ = rerank_chunks(query, chunks[:3])

# Benchmark real
start = time.time()
scores = rerank_chunks(query, chunks) # rerank_chunks ya maneja list[dict]
end = time.time()

latency = end - start

print(f"\n✅ Latencia de re-ranking: {latency:.2f}s")
print(f"📊 Chunks procesados: {len(chunks)}")
print(f"⚡ Throughput: {len(chunks)/latency:.2f} chunks/segundo")

# Evaluación
if latency < 5:
    print("🎯 OBJETIVO CUMPLIDO: < 5s")
elif latency < 100:
    print("⚠️  MEJORABLE: Aún lejos del objetivo (Probablemente CPU)")
else:
    print("❌ CRÍTICO: Sigue en CPU (~150-200s esperado)")

print("="*60)
