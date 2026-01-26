# -*- coding: utf-8 -*-
"""
Test automático de Fase 1 - 5 preguntas del Golden Dataset.
Evalúa automáticamente si las respuestas contienen los datos esperados.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.agents.rag_agent import chat

# 5 preguntas del Golden Dataset
TEST_QUESTIONS = [
    {
        "id": "G001",
        "pregunta": "¿Cuál es el importe total del contrato de suministro de vehículos blindados (CON_2024_001)?",
        "keywords_esperados": ["2.450.000", "2450000", "CON_2024_001"],
        "dificultad": "Trivial"
    },
    {
        "id": "G002",
        "pregunta": "¿Qué entidad bancaria emitió el aval para el contrato de mantenimiento de armamento (CON_2024_002)?",
        "keywords_esperados": ["CaixaBank", "Caixa"],
        "dificultad": "Trivial"
    },
    {
        "id": "G005",
        "pregunta": "¿Cuáles son los códigos NSN asociados al contrato de suministro de comunicaciones tácticas?",
        "keywords_esperados": ["NSN-5820123456789", "NSN-5820987654321", "5820"],
        "dificultad": "Trivial"
    },
    {
        "id": "G004",
        "pregunta": "¿Qué penalización se aplica por retraso en el suministro de camiones logísticos IVECO?",
        "keywords_esperados": ["1.500", "1500", "EUR", "vehículo", "día"],
        "dificultad": "Media"
    },
    {
        "id": "G009",
        "pregunta": "¿Se permite la subcontratación en el contrato de formación de la fragata F-110?",
        "keywords_esperados": ["no", "prohib", "SER_2024_013"],
        "dificultad": "Trivial"
    },
]

def evaluate_answer(respuesta: str, keywords: list) -> bool:
    """Evalúa si la respuesta contiene al menos 2 de los keywords esperados."""
    respuesta_lower = respuesta.lower()
    matches = sum(1 for kw in keywords if kw.lower() in respuesta_lower)
    return matches >= 2

print("\n" + "=" * 80)
print("🧪 TEST AUTOMÁTICO FASE 1 - 5 PREGUNTAS DEL GOLDEN DATASET")
print("=" * 80 + "\n")

resultados = []
correctas = 0
tiempos = []

for i, test in enumerate(TEST_QUESTIONS, 1):
    print(f"\n[{i}/5] {test['id']} ({test['dificultad']})")
    print(f"❓ {test['pregunta']}")
    
    try:
        start = time.time()
        respuesta = chat(test['pregunta'], history=[])
        elapsed = time.time() - start
        tiempos.append(elapsed)
        
        print(f"\n💬 Respuesta ({elapsed:.2f}s):")
        print(respuesta[:300] + "..." if len(respuesta) > 300 else respuesta)
        
        # Evaluación automática
        correcto = evaluate_answer(respuesta, test['keywords_esperados'])
        
        if correcto:
            correctas += 1
            print("✅ CORRECTA (contiene datos esperados)")
        else:
            print(f"❌ INCORRECTA (esperaba: {', '.join(test['keywords_esperados'])})")
            
        resultados.append({
            "id": test['id'],
            "correcto": correcto,
            "latencia": elapsed
        })
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        resultados.append({
            "id": test['id'],
            "correcto": False,
            "error": str(e)
        })

print("\n" + "=" * 80)
print(f"📊 RESULTADOS FINALES")
print("=" * 80)
print(f"✅ Correctas: {correctas}/5 ({correctas/5*100:.0f}%)")
print(f"⏱️  Latencia promedio: {sum(tiempos)/len(tiempos):.2f}s")
print(f"⏱️  Latencia máxima: {max(tiempos):.2f}s")
print()

# Target: >= 3/5 (60%)
if correctas >= 3:
    print("🎉 ✅ TARGET ALCANZADO (>= 60% precisión)")
    print("    Fase 1 completada exitosamente")
else:
    print("⚠️  TARGET NO ALCANZADO (esperado: >= 3/5)")

print("\nDetalle por pregunta:")
for r in resultados:
    status = "✅" if r.get("correcto") else "❌"
    latencia = f" ({r.get('latencia', 0):.2f}s)" if 'latencia' in r else ""
    print(f"  {status} {r['id']}{latencia}")

print("\n" + "=" * 80)
