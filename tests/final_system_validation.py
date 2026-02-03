# -*- coding: utf-8 -*-
"""
Validación Final del Sistema RAG (Fase 3).
Ejecuta el Golden Dataset V3 completo (20 preguntas).
Métricas: Accuracy, Router Decision, Latency, Estimated Cost.
"""
import sys
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any

# Configurar path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.rag_agent import chat, route_query
from src.utils.llm_config import generate_response

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Precios estimados (USD per 1M tokens input/output blend approx)
COST_GPT4O = 5.00  # Aprox blend
COST_MINI = 0.30   # Aprox blend

def evaluate_answer(question: str, generated: str, expected: str) -> bool:
    """
    Usa GPT-4o-mini como Juez para determinar si la respuesta es correcta.
    """
    prompt = f"""Actúa como Juez imparcial. Compara la RESPUESTA GENERADA con la RESPUESTA ESPERADA.
PREGUNTA: {question}

RESPUESTA ESPERADA (VERDAD ABSOLUTA):
{expected}

RESPUESTA GENERADA:
{generated}

¿La respuesta generada contiene la información clave de la esperada y es correcta?
Responde solo "SI" o "NO".
"""
    try:
        verdict = generate_response(prompt, max_tokens=5, model="gpt-4o-mini").strip().upper()
        return "SI" in verdict
    except Exception:
        return False

def estimate_cost(model: str, context_chars: int) -> float:
    # Estimación grosera: 1 token ~= 4 chars
    tokens = context_chars / 4
    price_per_m = COST_GPT4O if "gpt-4o" in model and "mini" not in model else COST_MINI
    return (tokens / 1_000_000) * price_per_m

def main():
    print("🚀 INICIANDO VALIDACIÓN FINAL DEL SISTEMA (GOLDEN DATASET V3)")
    print("="*80)
    print(f"{'ID':<4} | {'ROUTER':<10} | {'RESULT':<8} | {'TIME (s)':<8} | {'COST ($)':<10} | {'PREGUNTA'}")
    print("-" * 80)
    
    dataset_path = Path("tests/golden_dataset_v3.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    results = []
    total_cost = 0.0
    start_global = time.time()
    
    for item in dataset:
        q_id = item["id"]
        question = item["pregunta"]
        expected = item["respuesta_correcta"]
        
        # 1. Router Prediction
        complexity = route_query(question)
        model = "GPT-4o" if complexity == "COMPLEX" else "GPT-4o-mini"
        
        # 2. Execution
        t0 = time.time()
        try:
            # Capturar logs para estimar contexto? Difícil sin instrumentación profunda.
            # Asumiremos un contexto promedio de 15k chars para RAG.
            response = chat(question)
            duration = time.time() - t0
            
            # 3. Evaluation
            is_correct = evaluate_answer(question, response, expected)
            status = "✅ PASS" if is_correct else "❌ FAIL"
            
            # 4. Cost Calc
            # Si Router es SIMPLE, el contexto es el mismo pero el modelo es barato.
            # Asumimos 15,000 chars de contexto promedio (~3750 tokens) + 500 output
            estimated_tokens = 4000
            cost = (estimated_tokens / 1_000_000) * (COST_GPT4O if model == "GPT-4o" else COST_MINI)
            total_cost += cost
            
            print(f"{q_id:<4} | {model:<10} | {status:<8} | {duration:<8.2f} | ${cost:<9.5f} | {question[:40]}...")
            
            results.append({
                "id": q_id,
                "question": question,
                "expected": expected,
                "generated": response,
                "router": complexity,
                "model": model,
                "status": status,
                "time": duration,
                "cost": cost
            })
            
        except Exception as e:
            print(f"{q_id:<4} | {model:<10} | ❌ ERROR | 0.00     | $0.00000   | {e}")
    
    total_time = time.time() - start_global
    accuracy = len([r for r in results if "PASS" in r["status"]]) / len(dataset) * 100
    
    print("="*80)
    print(f"📊 RESUMEN FINAL")
    print(f"Precisión: {accuracy:.1f}%")
    print(f"Tiempo Total: {total_time:.1f}s")
    print(f"Coste Total Est: ${total_cost:.5f}")
    
    # Análisis de Fallos
    failures = [r for r in results if "FAIL" in r["status"]]
    if failures:
        print("\n❌ ANÁLISIS DE FALLOS:")
        for f in failures:
            print(f"- Q{f['id']} ({f['model']}): {f['question']}")
            print(f"  Esperado: {f['expected']}")
            print(f"  Obtenido: {f['generated'][:200]}...")

if __name__ == "__main__":
    main()
