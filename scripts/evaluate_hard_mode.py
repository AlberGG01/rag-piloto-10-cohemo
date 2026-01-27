
import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict
import re

# Configurar path para importar módulos de src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.agents.rag_agent import retrieve_and_generate
from src.utils.llm_config import generate_response

# Configurar logging simple
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Evaluator")

def load_dataset(path: str) -> List[Dict]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_recall_at_k(retrieved_docs: List[str], expected_docs: List[str]) -> float:
    """
    Calcula Recall@K: Proporción de documentos esperados que fueron recuperados.
    """
    if not expected_docs:
        return 1.0
    
    # Normalizar nombres de archivo (minusculas, sin rutas)
    retrieved_norm = {Path(d).name.lower() for d in retrieved_docs}
    expected_norm = {Path(d).name.lower() for d in expected_docs}
    
    # Intersección
    intersection = retrieved_norm.intersection(expected_norm)
    recall = len(intersection) / len(expected_norm)
    return recall

def llm_judge(query: str, expected_snippet: str, generated_answer: str) -> Dict:
    """
    Usa gpt-4o-mini como juez para puntuar la respuesta (1-5).
    """
    prompt = f"""Actúa como Juez Imparcial de un examen técnico.
    
    PREGUNTA: "{query}"
    
    RESPUESTA MODÉLICA (VERDAD): "{expected_snippet}"
    
    RESPUESTA DEL ALUMNO (AI): "{generated_answer}"
    
    TAREA:
    Evalúa la respuesta del alumno del 1 al 5.
    
    CRITERIOS:
    5 - PERFECTO: Contiene el dato exacto o la explicación completa correctos.
    4 - MUY BIEN: Correcto pero con palabrería extra o formato mejorable.
    3 - ACEPTABLE: Respuesta vaga pero apunta en la dirección correcta.
    2 - POBRE: Contiene errores menores o es demasiado ambigua.
    1 - FALLO: Información incorrecta, alucinación o "No sé".
    
    FORMATO JSON:
    {{
        "score": (int 1-5),
        "reason": "breve explicación"
    }}
    Responde SOLO con el JSON.
    """
    
    try:
        response = generate_response(prompt, max_tokens=150, temperature=0.0, model="gpt-4o-mini")
        # Limpiar markdown
        clean_resp = response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_resp)
    except Exception as e:
        logger.error(f"Error en LLM Judge: {e}")
        return {"score": 1, "reason": "Error en juez"}

def main():
    dataset_path = BASE_DIR / "tests" / "golden_dataset_hard.json"
    report_path = BASE_DIR / "evaluation_report.md"
    
    logger.info(f"Cargando dataset desde {dataset_path}...")
    dataset = load_dataset(dataset_path)
    
    results = []
    total_recall = 0.0
    total_score = 0.0
    total_latency = 0.0
    
    logger.info(f"Iniciando evaluación de {len(dataset)} preguntas...")
    
    print("-" * 60)
    
    for i, item in enumerate(dataset, 1):
        query = item['query']
        expected_docs = item['expected_docs']
        expected_snippet = item['expected_answer_snippet']
        
        print(f"[{i}/{len(dataset)}] Evaluando: {query[:60]}...")
        
        start_time = time.time()
        
        # Ejecutar RAG
        rag_result = retrieve_and_generate(query)
        
        latency = time.time() - start_time
        generated_answer = rag_result.get("response", "Error generating response")
        retrieved_sources = [s.get('archivo', '') for s in rag_result.get("sources", [])]
        
        # Métricas
        recall = calculate_recall_at_k(retrieved_sources, expected_docs)
        judge_result = llm_judge(query, expected_snippet, generated_answer)
        score = judge_result.get("score", 1)
        reason = judge_result.get("reason", "N/A")
        
        # Acumuladores
        total_recall += recall
        total_score += score
        total_latency += latency
        
        result_entry = {
            "id": item.get("id"),
            "query": query,
            "latency": latency,
            "recall": recall,
            "score": score,
            "reason": reason,
            "generated": generated_answer,
            "expected_snippet": expected_snippet,
            "retrieved_docs": retrieved_sources,
            "expected_docs": expected_docs
        }
        results.append(result_entry)
        
        status_icon = "✅" if score >= 4 else "⚠️" if score >= 3 else "❌"
        print(f"   {status_icon} Score: {score}/5 | Recall: {recall:.2f} | Time: {latency:.2f}s")
        
        # MEMORY MANAGEMENT: Limpieza cada 5 preguntas
        if i % 5 == 0:
            print(f"   [Sistema] Pausa para enfriamiento y GC... (Procesadas: {i})")
            import gc
            gc.collect() # Forzar recolección de basura
            time.sleep(5) # Enfriar CPU/GPU si aplica
    
    # Calcular promedios
    avg_recall = total_recall / len(dataset)
    avg_score = total_score / len(dataset)
    avg_latency = total_latency / len(dataset)
    accuracy = len([r for r in results if r['score'] >= 4]) / len(dataset) * 100
    
    # Generar Reporte Markdown
    logger.info("Generando reporte final...")
    
    markdown_report = f"""# 🛡️ Informe de Evaluación: Golden Dataset (Hard Mode)

**Fecha:** {time.strftime("%d/%m/%Y %H:%M")}
**Dataset:** {dataset_path}
**Modelo Evaluador:** gpt-4o-mini

## 📊 Resumen Ejecutivo

| Métrica | Resultado | Objetivo |
|---------|-----------|----------|
| **Accuracy (Score >= 4)** | **{accuracy:.1f}%** | > 85% |
| **Score Promedio (1-5)** | **{avg_score:.2f}** | > 4.5 |
| **Recall@K Promedio** | **{avg_recall:.2f}** | > 0.90 |
| **Latencia Promedio** | **{avg_latency:.2f}s** | < 15s |

---

## 🛑 Análisis de Fallos (Score <= 2)

"""
    failures = [r for r in results if r['score'] <= 2]
    if not failures:
        markdown_report += "¡Increíble! No hubo fallos críticos.\n"
    else:
        for f in failures:
            markdown_report += f"### ❌ [{f['id']}] {f['query']}\n"
            markdown_report += f"- **Esperado:** {f['expected_snippet']}\n"
            markdown_report += f"- **Generado:** {f['generated']}\n"
            markdown_report += f"- **Docs Recuperados:** {f['retrieved_docs']}\n"
            markdown_report += f"- **Docs Esperados:** {f['expected_docs']}\n"
            markdown_report += f"- **Razón Juez:** {f['reason']}\n\n"

    markdown_report += "\n## 📝 Detalle Completo\n\n| ID | Query | Score | Recall | Latency |\n|----|-------|-------|--------|---------|\n"
    for r in results:
        icon = "✅" if r['score'] >= 4 else "⚠️" if r['score'] == 3 else "❌"
        markdown_report += f"| {r['id']} | {r['query']} | {icon} {r['score']} | {r['recall']:.2f} | {r['latency']:.2f}s |\n"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
        
    logger.info(f"Reporte guardado en: {report_path}")

if __name__ == "__main__":
    main()
