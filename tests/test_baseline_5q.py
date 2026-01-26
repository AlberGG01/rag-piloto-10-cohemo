# -*- coding: utf-8 -*-
"""
Test Baseline RAG - 5 Preguntas Representativas
Mide capacidades actuales antes de optimización
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.agents.rag_agent import chat

# 5 preguntas representativas (una por categoría básica)
BASELINE_QUESTIONS = [
    {
        "id": "AGG001",
        "category": "Agregación",
        "question": "¿Cuál es el importe total acumulado de todos los avales bancarios en el sistema?",
        "expected_keywords": ["570.000", "364.000", "316.000", "246.000"],  # Principales avales
        "difficulty": "Media"
    },
    {
        "id": "CMP001", 
        "category": "Comparación",
        "question": "Lista los 3 contratos con mayor importe total, ordenados de mayor a menor con sus importes exactos",
        "expected_keywords": ["28.500.000", "18.200.000", "15.800.000"],  # Top 3 importes
        "difficulty": "Media"
    },
    {
        "id": "TMP002",
        "category": "Temporal",
        "question": "De los avales que vencen en 2027, ¿cuál vence más pronto?",
        "expected_keywords": ["26/03/2027", "CON_2024_018", "Hangares", "Morón"],
        "difficulty": "Media"
    },
    {
        "id": "FLT001",
        "category": "Filtrado",
        "question": "¿Qué contratos tienen clasificación de seguridad SECRETO Y un importe superior a 20 millones de euros?",
        "expected_keywords": ["CON_2024_012", "28.500.000", "Retamares"],
        "difficulty": "Alta"
    },
    {
        "id": "NEG001",
        "category": "Negación",
        "question": "¿Qué contratos prohíben completamente la subcontratación?",
        "expected_keywords": ["SER_2024_013", "prohibida", "F-110"],
        "difficulty": "Alta"
    }
]

def evaluate_answer(answer: str, expected_keywords: list) -> tuple:
    """
    Evalúa si la respuesta contiene las keywords esperadas.
    
    Returns:
        (is_correct, found_keywords, missing_keywords)
    """
    answer_lower = answer.lower()
    found = []
    missing = []
    
    for keyword in expected_keywords:
        if keyword.lower() in answer_lower:
            found.append(keyword)
        else:
            missing.append(keyword)
    
    # Correcta si encuentra al menos 50% de keywords
    is_correct = len(found) >= len(expected_keywords) * 0.5
    
    return is_correct, found, missing

def run_baseline_test():
    """Ejecuta el test baseline de 5 preguntas."""
    
    print("\n" + "="*80)
    print("TEST BASELINE RAG - 5 PREGUNTAS REPRESENTATIVAS")
    print("="*80)
    print("\nObjetivo: Medir capacidades actuales antes de optimizacion\n")
    
    results = []
    total_time = 0
    
    for i, q in enumerate(BASELINE_QUESTIONS, 1):
        print(f"\n[{i}/5] {q['id']} ({q['category']}) - Dificultad: {q['difficulty']}")
        print(f"Pregunta: {q['question']}")
        
        # Medir tiempo
        start_time = time.time()
        try:
            answer = chat(q['question'], history=[])
        except Exception as e:
            answer = f"ERROR: {e}"
        elapsed = time.time() - start_time
        total_time += elapsed
        
        # Evaluar
        is_correct, found, missing = evaluate_answer(answer, q['expected_keywords'])
        
        # Mostrar resultado
        status = "✅ CORRECTA" if is_correct else "❌ INCORRECTA"
        print(f"\n💬 Respuesta ({elapsed:.2f}s):")
        print(answer[:300] + "..." if len(answer) > 300 else answer)
        print(f"\n{status}")
        print(f"   Keywords encontradas: {len(found)}/{len(q['expected_keywords'])}")
        if missing:
            print(f"   Faltantes: {missing}")
        
        results.append({
            "id": q['id'],
            "category": q['category'],
            "correct": is_correct,
            "latency": elapsed,
            "found": found,
            "missing": missing
        })
    
    # Resumen
    print("\n" + "="*80)
    print("RESULTADOS BASELINE")
    print("="*80)
    
    correct_count = sum(1 for r in results if r['correct'])
    avg_latency = total_time / len(results)
    max_latency = max(r['latency'] for r in results)
    
    print(f"Correctas: {correct_count}/5 ({correct_count*20}%)")
    print(f"Latencia promedio: {avg_latency:.2f}s")
    print(f"Latencia maxima: {max_latency:.2f}s")
    
    # Desglose por categoria
    print("\nDetalle por categoria:")
    for r in results:
        status = "[OK]" if r['correct'] else "[X]"
        print(f"  {status} {r['category']:15s} ({r['latency']:.2f}s)")
    
    # Analisis de gaps
    print("\n" + "="*80)
    print("ANALISIS DE GAPS")
    print("="*80)
    
    failed = [r for r in results if not r['correct']]
    if failed:
        print("\nCategorias con problemas:")
        for r in failed:
            print(f"\n[X] {r['category']} ({r['id']})")
            print(f"   Keywords faltantes: {r['missing']}")
            
            # Diagnostico probable
            if len(r['found']) == 0:
                print("   -> Problema: RETRIEVAL (no encontro chunks correctos)")
            elif len(r['found']) < len(r['missing']):
                print("   -> Problema: LLM EXTRACCION (chunks OK, pero respuesta incompleta)")
    else:
        print("\n[OK] Sin problemas detectados! Sistema funcionando bien en baseline.")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    results = run_baseline_test()
