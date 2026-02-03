# -*- coding: utf-8 -*-
"""
Benchmark de Latencia: GPU/Hardware Detection + Streaming.
"""
import sys
import time
import torch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.reranker import rerank_chunks
from src.utils.llm_config import generate_response_stream

def benchmark_hardware():
    print("\n🔬 1. DETECCIÓN DE HARDWARE (RERANKER)")
    print("-" * 50)
    
    if torch.cuda.is_available():
        device = "CUDA (NVIDIA GPU)"
        optimization = "✅ ENABLED"
    elif torch.backends.mps.is_available():
        device = "MPS (Apple Silicon)"
        optimization = "✅ ENABLED"
    else:
        device = "CPU (Slow fallback)"
        optimization = "⚠️ DISABLED (High Latency)"
        
    print(f"Device detectado: {device}")
    print(f"Estado de optimización: {optimization}")
    
    # Simular carga de tensores
    t0 = time.time()
    try:
        x = torch.rand(1000, 1000)
        if device.startswith("CUDA"):
            x = x.to("cuda")
        elif device.startswith("MPS"):
            x = x.to("mps")
        print(f"Tensor allocation test: OK ({time.time()-t0:.4f}s)")
    except Exception as e:
        print(f"Tensor allocation failed: {e}")

def benchmark_streaming():
    print("\n🌊 2. TEST DE STREAMING (Perceived Latency)")
    print("-" * 50)
    
    prompt = "Explica brevemente qué es la latencia en 50 palabras."
    print(f"Prompt: '{prompt}'")
    print("Generando respuesta (Streaming)...")
    
    start_time = time.time()
    first_token_time = None
    
    full_response = ""
    stream = generate_response_stream(prompt, max_tokens=100)
    
    try:
        for chunk in stream:
            if first_token_time is None:
                first_token_time = time.time()
                print(f"  ⚡ PRIMER TOKEN (TTFT): {first_token_time - start_time:.4f}s")
            full_response += chunk
            # Simular UI printing
            sys.stdout.write(chunk)
            sys.stdout.flush()
            
        total_time = time.time() - start_time
        print(f"\n\n✅ Streaming completado.")
        print(f"  ⏱️ Tiempo Total: {total_time:.4f}s")
        print(f"  🚀 Perceived Latency Gain: {(total_time - (first_token_time - start_time)):.4f}s (Usuario ve texto antes)")
        
    except Exception as e:
        print(f"\n❌ Error en streaming: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO BENCHMARK DE LATENCIA Y HARDWARE")
    benchmark_hardware()
    benchmark_streaming()
