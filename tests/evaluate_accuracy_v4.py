# -*- coding: utf-8 -*-
"""
Evaluador de Accuracy "Juez" (LLM-as-a-Judge).
Ejecuta el Golden Dataset V4 (40 preguntas) y usa GPT-4o para calificar las respuestas.
"""
import json
import logging
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Any

# Ajustar path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.rag_agent import chat, route_query
from src.config import CLIENT as openai_client
from src.utils.llm_config import generate_response

# Configuración
DATASET_PATH = Path("tests/golden_dataset_v4.json")
REPORT_PATH = Path("data/accuracy_report_v4.json")
LOG_PATH = Path("data/evaluation.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("EVALUATOR")

def evaluate_response(question: str, rag_response: str, ground_truth: str) -> Dict[str, Any]:
    """
    Usa GPT-4o como Juez para evaluar la calidad de la respuesta.
    """
    prompt = f"""
    Actúa como JUEZ IMPARCIAL y EXPERTO en auditoría de datos.
    Tu tarea es evaluar la precisión de una respuesta generada por IA frente a la verdad absoluta.

    PREGUNTA: "{question}"
    
    RESPUESTA RAG (IA): "{rag_response}"
    
    VERDAD ABSOLUTA (Dataset): "{ground_truth}"

    EVALUACIÓN (JSON):
    Analiza la respuesta en dos dimensiones:
    1. PRECISION NUMÉRICA (0-5): ¿Los números (importes, fechas, códigos) son exactos? 
       - 5: Perfecto, exacto al céntimo/día.
       - 1: Dato incorrecto. 
       - 0: No responde o alucina inventando.
       
    2. AUSENCIA DE ALUCINACIONES (0-5): ¿Añade información falsa no presente en la verdad?
       - 5: Solo hechos verificados.
       - 1: Inventa bastante.

    Si la respuesta es "No consta" y la verdad es "No consta" (o trampa), es un 5/5.

    Devuelve SOLO un JSON con este formato:
    {{
        "precision_score": int,
        "hallucination_score": int,
        "reasoning": "Breve explicación del fallo o acierto (max 1 linea)",
        "verdict": "PASS" o "FAIL" (PASS si precision >= 4)
    }}
    """
    
    try:
        # Usar modelo potente para juzgar
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        content = completion.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error en Juez: {e}")
        return {
            "precision_score": 0, 
            "hallucination_score": 0, 
            "reasoning": "Judge Error", 
            "verdict": "FAIL"
        }

def run_evaluation(target_ids: List[str] = None):
    logger.info("🚀 INICIANDO EVALUACIÓN MASIVA V4 (GLOBAL & STRESS)")
    logger.info(f"Dataset: {DATASET_PATH}")
    
    if not DATASET_PATH.exists():
        logger.error("Dataset no encontrado.")
        return

    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        full_dataset = json.load(f)
    
    # Filtrar por IDs específicos si se proporcionan
    if target_ids:
        dataset = [q for q in full_dataset if q["id"] in target_ids]
        logger.info(f"\n🎯 EVALUACIÓN PARCIAL: {len(dataset)}/{len(full_dataset)} tests")
        logger.info(f"   IDs: {', '.join(target_ids)}\n")
    else:
        dataset = full_dataset
    
    results = []
    total_score = 0
    passed_count = 0
    
    start_time_global = time.time()
    
    for i, item in enumerate(dataset, 1):
        q_id = item["id"]
        question = item["pregunta"]
        ground_truth = item["respuesta_correcta"]
        
        logger.info(f"\n🔹 [{i}/{len(dataset)}] Evaluando {q_id}...")
        
        # 1. Ejecutar RAG
        t0 = time.time()
        try:
            rag_response = chat(question)
        except Exception as e:
            rag_response = f"ERROR DE EJECUCIÓN: {e}"
        t1 = time.time()
        latency = t1 - t0
        
        # 2. Juzgar
        logger.info("   ⚖️  Juzgando...")
        eval_result = evaluate_response(question, rag_response, ground_truth)
        
        # Métricas
        is_pass = eval_result["verdict"] == "PASS"
        if is_pass: passed_count += 1
        total_score += eval_result["precision_score"]
        
        logger.info(f"   ⏱️  Latencia: {latency:.2f}s")
        logger.info(f"   📝  Score: {eval_result['precision_score']}/5 | {eval_result['verdict']}")
        logger.info(f"   💡  Razón: {eval_result['reasoning']}")
        
        results.append({
            "id": q_id,
            "question": question,
            "rag_response": rag_response,
            "ground_truth": ground_truth,
            "latency_seconds": latency,
            "evaluation": eval_result
        })

    total_time = time.time() - start_time_global
    accuracy = (passed_count / len(dataset)) * 100
    avg_latency = total_time / len(dataset)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_questions": len(dataset),
        "passed": passed_count,
        "accuracy_percent": accuracy,
        "average_latency": avg_latency,
        "details": results
    }
    
    # Guardar reporte
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    logger.info("\n" + "="*60)
    logger.info(f"📊 RESULTADOS FINALES V4")
    logger.info(f"   Accuracy Global: {accuracy:.2f}% ({passed_count}/{len(dataset)})")
    logger.info(f"   Latencia Media: {avg_latency:.2f}s")
    logger.info(f"   Reporte guardado en: {REPORT_PATH}")
    logger.info("="*60)

if __name__ == "__main__":
    run_evaluation()
