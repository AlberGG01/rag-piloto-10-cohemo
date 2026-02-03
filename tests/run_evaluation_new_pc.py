# -*- coding: utf-8 -*-
"""
Script de ejecución para Golden Dataset V4 - NEW PC EVALUATION.
Ejecuta el test de 30 preguntas, mide tiempos y genera informe en Markdown.
"""
import sys
import logging
import json
import time
import statistics
from pathlib import Path
from datetime import datetime

# Configurar path para importar src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.rag_agent import chat
from src.utils.llm_config import generate_response

# Logging setup
logging.basicConfig(level=logging.ERROR)

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

def generate_markdown_report(results, metrics, total_duration):
    report_path = Path("evaluation_report_NEW_PC.md")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_content = f"""# 📊 Informe de Evaluación del Sistema RAG - NEW PC

**Fecha:** {timestamp}
**Hardware:** GPU GTX 1060 6GB | RAM 8GB
**Dataset:** Golden Dataset V4 (30 preguntas)

## 1. Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| **Accuracy Global** | **{metrics['accuracy']:.2f}%** |
| **Preguntas Acertadas** | {metrics['correct_count']} / {metrics['total_count']} |
| **Tiempo Total Test** | {total_duration:.2f}s |
| **Tiempo Promedio/Pregunta** | {metrics['avg_time']:.2f}s |
| **Tiempo Mediana** | {metrics['median_time']:.2f}s |
| **Tiempo Mínimo** | {metrics['min_time']:.2f}s |
| **Tiempo Máximo** | {metrics['max_time']:.2f}s |

## 2. Detalles de Fallos
"""

    failures = [r for r in results if r['status'] == "❌ FAIL"]
    if not failures:
        md_content += "\n🎉 **¡Felicidades! No hubo fallos. El sistema respondió correctamente a todas las preguntas.**\n"
    else:
        for f in failures:
            md_content += f"""
### ❌ {f['id']}: {f['question']}
- **Esperado:** {f['expected']}
- **Obtenido:** {f['generated']}
- **Tiempo:** {f['duration']:.2f}s
---
"""

    md_content += """
## 3. Tabla Completa de Resultados

| ID | Estado | Pregunta (Resumen) | Tiempo |
|----|--------|-------------------|--------|
"""
    for r in results:
        q_short = (r['question'][:60] + "...") if len(r['question']) > 60 else r['question']
        md_content += f"| {r['id']} | {r['status']} | {q_short} | {r['duration']:.2f}s |\n"

    md_content += """
## 4. Distribución de Tiempos
(Gráfico omitido en versión texto, ver métricas arriba)

## 5. Conclusiones y Recomendaciones
- **Accuracy:** El sistema ha obtenido un {accuracy:.2f}% de precisión.
- **Latencia:** El tiempo promedio de respuesta es de {avg_time:.2f}s.
""".format(accuracy=metrics['accuracy'], avg_time=metrics['avg_time'])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"\n📄 Informe generado: {report_path.absolute()}")

def main():
    print("🚀 INICIANDO EJECUCIÓN DEL GOLDEN DATASET V4 (30 PREGUNTAS)")
    print("="*120)
    print(f"| {'ID':<6} | {'Estado':<8} | {'Pregunta':<60} | {'Esperado':<30} | {'Tiempo':<8} |")
    print(f"|{'-'*8}|{'-'*10}|{'-'*62}|{'-'*32}|{'-'*10}|")
    
    dataset_path = Path("tests/golden_dataset_v4.json")
    if not dataset_path.exists():
        print(f"❌ Error: No se encontró el dataset en {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    results = []
    times = []
    correct_count = 0
    
    test_start_time = time.time()
    
    for item in dataset:
        q_id = item["id"]
        question = item["pregunta"]
        expected = item["respuesta_correcta"]
        
        start_time = time.time()
        try:
            # Execute Chat
            response = chat(question)
            duration = time.time() - start_time
            
            # Evaluate
            is_correct = evaluate_answer(question, response, expected)
            status = "✅ PASS" if is_correct else "❌ FAIL"
            
            if is_correct:
                correct_count += 1
            
            times.append(duration)
            
            # Record result
            results.append({
                "id": q_id,
                "question": question,
                "expected": expected,
                "generated": response,
                "status": status,
                "duration": duration
            })
            
            # Print row
            q_short = (question[:57] + "...") if len(question) > 57 else question
            exp_short = (expected[:27] + "...") if len(expected) > 27 else expected
            
            print(f"| {q_id:<6} | {status:<8} | {q_short:<60} | {exp_short:<30} | {duration:<8.2f}s |")
            
        except Exception as e:
            duration = time.time() - start_time
            status = "❌ FAIL"
            error_msg = f"EXCEPTION: {str(e)}"
            times.append(duration)
            results.append({
                "id": q_id,
                "question": question,
                "expected": expected,
                "generated": error_msg,
                "status": status,
                "duration": duration
            })
            print(f"| {q_id:<6} | {status:<8} | ERROR: {str(e)[:50]}... | {duration:<8.2f}s |")

    total_test_time = time.time() - test_start_time
    
    # Calculate metrics
    metrics = {
        "total_count": len(dataset),
        "correct_count": correct_count,
        "accuracy": (correct_count / len(dataset)) * 100 if dataset else 0,
        "avg_time": statistics.mean(times) if times else 0,
        "median_time": statistics.median(times) if times else 0,
        "min_time": min(times) if times else 0,
        "max_time": max(times) if times else 0
    }
    
    generate_markdown_report(results, metrics, total_test_time)
    print("\n🏁 EJECUCIÓN COMPLETADA.")

if __name__ == "__main__":
    main()
