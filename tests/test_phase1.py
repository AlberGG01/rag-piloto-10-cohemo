# -*- coding: utf-8 -*-
"""
Script de prueba rápida del sistema RAG con 5 preguntas del Golden Dataset.
"""

import sys
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.agents.rag_agent import chat

# 5 preguntas del Golden Dataset (trivial + media)
TEST_QUESTIONS = [
    {
        "id": "G001",
        "pregunta": "¿Cuál es el importe total del contrato de suministro de vehículos blindados (CON_2024_001)?",
        "respuesta_esperada": "2.450.000,00 EUR",
        "dificultad": "Trivial"
    },
    {
        "id": "G002",
        "pregunta": "¿Qué entidad bancaria emitió el aval para el contrato de mantenimiento de armamento (CON_2024_002)?",
        "respuesta_esperada": "CaixaBank",
        "dificultad": "Trivial"
    },
    {
        "id": "G005",
        "pregunta": "¿Cuáles son los códigos NSN asociados al contrato de suministro de comunicaciones tácticas?",
        "respuesta_esperada": "NSN-5820123456789 y NSN-5820987654321",
        "dificultad": "Trivial"
    },
    {
        "id": "G004",
        "pregunta": "¿Qué penalización se aplica por retraso en el suministro de camiones logísticos IVECO?",
        "respuesta_esperada": "1.500 EUR por vehículo y día de retraso",
        "dificultad": "Media"
    },
    {
        "id": "G009",
        "pregunta": "¿Se permite la subcontratación en el contrato de formación de la fragata F-110?",
        "respuesta_esperada": "No, está expresamente prohibida",
        "dificultad": "Trivial"
    },
]

print("\n" + "=" * 80)
print("🧪 PRUEBA RÁPIDA DEL SISTEMA RAG - 5 PREGUNTAS")
print("=" * 80 + "\n")

resultados = []
correctas = 0

for i, test in enumerate(TEST_QUESTIONS, 1):
    print(f"\n[{i}/{len(TEST_QUESTIONS)}] {test['id']} ({test['dificultad']})")
    print(f"Pregunta: {test['pregunta']}")
    print(f"Respuesta esperada: {test['respuesta_esperada']}")
    
    try:
        # Ejecutar query
        respuesta = chat(test['pregunta'], history=[])
        print(f"\nRespuesta del sistema:\n{respuesta}")
        
        # Verificación manual
        correcto_input = input("\n¿Es correcta? (s/n): ").strip().lower()
        correcto = correcto_input == 's'
        
        if correcto:
            correctas += 1
            print("✅ CORRECTA")
        else:
            print("❌ INCORRECTA")
            
        resultados.append({
            "id": test['id'],
            "correcto": correcto,
            "respuesta": respuesta[:200]  # Primeros 200 chars
        })
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        resultados.append({
            "id": test['id'],
            "correcto": False,
            "error": str(e)
        })

print("\n" + "=" * 80)
print(f"📊 RESULTADOS FINALES: {correctas}/{len(TEST_QUESTIONS)} correctas ({correctas/len(TEST_QUESTIONS)*100:.0f}%)")
print("=" * 80)

# Target: >= 3/5 (60%)
if correctas >= 3:
    print("✅ TARGET ALCANZADO (>= 60% precisión)")
else:
    print("⚠️ TARGET NO ALCANZADO (target: >= 3/5)")

print("\nDetalles:")
for r in resultados:
    status = "✅" if r.get("correcto") else "❌"
    print(f"  {status} {r['id']}")
