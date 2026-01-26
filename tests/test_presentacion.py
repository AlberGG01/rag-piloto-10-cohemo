# -*- coding: utf-8 -*-
"""Test con OpenAI (gpt-4o-mini) para preguntas complejas de presentación."""
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.utils.llm_config import set_llm_provider
from src.agents.rag_agent import chat

# FORZAR OPENAI
set_llm_provider("openai")

PREGUNTAS = [
    # Las 3 de la guía
    "Haz una comparativa de los avales que vencen en el año 2027: Indica código de contrato, importe del aval, entidad avalista y el nivel de seguridad del contrato.",
    "¿Para qué contratos el Banco Santander nos ha dado un aval y qué importe total suman?",
    "Identifica qué contratos tienen una penalización por retraso superior al 0.5% e indica el objeto del contrato.",
    # 2 con historial
    "Del contrato que mencionaste con mayor penalización, ¿cuál es su nivel de seguridad y quién es el contratista?",
    "¿Y ese contratista tiene otros contratos con nosotros? Si es así, ¿cuáles son?",
]

def run_tests():
    print("=" * 70)
    print("TEST OPENAI (gpt-4o-mini) - PREGUNTAS PRESENTACIÓN")
    print("=" * 70)
    
    history = []
    total_time = 0
    
    for i, pregunta in enumerate(PREGUNTAS, 1):
        print(f"\n{'='*70}")
        print(f"Q{i}: {pregunta}")
        print("-" * 70)
        
        start = time.time()
        respuesta = chat(pregunta, history=history)
        elapsed = time.time() - start
        total_time += elapsed
        
        history.append({"role": "user", "content": pregunta})
        history.append({"role": "assistant", "content": respuesta})
        
        print(f"\n⏱️ TIEMPO: {elapsed:.2f}s")
        print(f"\n📝 RESPUESTA:\n{respuesta}")
        
        if elapsed > 10:
            print("\n⚠️ LENTO (>10s)")
        else:
            print("\n✅ TIEMPO OK")
    
    print(f"\n{'='*70}")
    print(f"TOTAL: {total_time:.2f}s para {len(PREGUNTAS)} preguntas")
    print(f"PROMEDIO: {total_time/len(PREGUNTAS):.2f}s/pregunta")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
