# -*- coding: utf-8 -*-
"""
Script de ejecución para Golden Dataset V4.
Simula preguntas enviadas al chat y valida respuestas usando LLM Judge.
Genera tabla de resultados con Estado, Respuesta, Tiempo.
"""
import sys
import logging
import json
import time
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.rag_agent import chat, route_query
from src.utils.llm_config import generate_response

# Logging setup - Silence internal logs to keep output clean
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def evaluate_answer(question: str, generated: str, expected: str) -> bool:
    """
    Usa GPT-4o-mini como Juez para determinar si la respuesta es correcta.
    """
    prompt = f"""Actúa como Juez imparcial. Compara la RESPUESTA GENERADA con la RESPUESTA ESPERADA (VERDAD ABSOLUTA).
PREGUNTA: {question}

RESPUESTA ESPERADA:
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

def main():
    print("🚀 INICIANDO EJECUCIÓN DEL GOLDEN DATASET V4 (30 PREGUNTAS)")
    print("="*120)
    print(f"| {'ID':<6} | {'Estado':<8} | {'Pregunta':<60} | {'Esperado':<30} | {'Respuesta Obtenida':<30} | {'Tiempo':<8} |")
    print(f"|{'-'*8}|{'-'*10}|{'-'*62}|{'-'*32}|{'-'*32}|{'-'*10}|")
    
    dataset_path = Path("tests/golden_dataset_v4.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    results = []
    
    for item in dataset:
        q_id = item["id"]
        question = item["pregunta"]
        expected = item["respuesta_correcta"]
        
        start_time = time.time()
        try:
            # Execute Chat
            chat_result = chat(question)
            response = chat_result.get("response", "Error")
            duration = time.time() - start_time
            
            # Evaluate
            is_correct = evaluate_answer(question, response, expected)
            status = "✅ PASS" if is_correct else "❌ FAIL"
            
            # Format output strings
            q_short = (question[:57] + "...") if len(question) > 57 else question
            exp_short = (expected[:27] + "...") if len(expected) > 27 else expected
            resp_clean = response.replace("\n", " ")[:27] + "..." if len(response) > 27 else response.replace("\n", " ")
            
            print(f"| {q_id:<6} | {status:<8} | {q_short:<60} | {exp_short:<30} | {resp_clean:<30} | {duration:<8.2f}s |")
            
            # Also print detailed failures for debugging if needed (stderr or just plain print after table)
            
        except Exception as e:
            duration = time.time() - start_time
            status = "❌ FAIL"
            error_msg = f"EXCEPTION: {str(e)}"
            q_short = (question[:57] + "...") if len(question) > 57 else question
            exp_short = (expected[:27] + "...") if len(expected) > 27 else expected
            err_short = (error_msg[:27] + "...") if len(error_msg) > 27 else error_msg
            
            print(f"| {q_id:<6} | {status:<8} | {q_short:<60} | {exp_short:<30} | {err_short:<30} | {duration:<8.2f}s |")

if __name__ == "__main__":
    main()
