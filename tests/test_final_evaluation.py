# -*- coding: utf-8 -*-
"""
Final Evaluation Script (Day 7)
Runs the full Golden Dataset (20 questions) and Adversarial Tests against the Agentic RAG system.
Generates a comprehensive report in JSON and Markdown formats.
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph.workflow import run_agentic_rag

# --- GOLDEN DATASET (20 QUESTIONS) ---
GOLDEN_DATASET = [
    {"id": "ADV001", "type": "Aggregation", "query": "¿Cuál es el importe total acumulado de todos los avales bancarios en el sistema?", "keywords": ["avales", "total"]},
    {"id": "ADV002", "type": "Ranking", "query": "Lista los 4 contratos con mayor importe total, ordenados de mayor a menor", "keywords": ["CON_2024_012", "SER_2024_015", "CON_2024_018"]},
    {"id": "ADV003", "type": "Filtrado Complejo", "query": "¿Qué contratos tienen nivel de seguridad SECRETO Y un importe superior a 5 millones de euros?", "keywords": ["CON_2024_012"]},
    {"id": "ADV004", "type": "Agregación Condicional", "query": "¿Cuántos contratos vencen entre febrero y abril de 2026?", "keywords": ["vencen", "2026"]},
    {"id": "ADV005", "type": "Comparación", "query": "Compara los plazos de ejecución entre el contrato de mayor y menor importe total", "keywords": ["plazo", "días"]},
    {"id": "ADV006", "type": "Análisis Cruzado", "query": "¿Qué entidad bancaria avala el mayor importe acumulado y cuánto es?", "keywords": ["banco", "avala"]},
    {"id": "ADV007", "type": "Temporal + Numérico", "query": "¿Cuántos días faltan para que venzan los avales cuyo importe supera los 400.000€?", "keywords": ["días", "venzan"]},
    {"id": "ADV008", "type": "Razonamiento", "query": "¿Qué contratos de OBRAS tienen penalizaciones por retraso superiores a 5.000€/día?", "keywords": ["OBRAS", "penalización"]},
    {"id": "ADV009", "type": "Identificación de Riesgos", "query": "De los contratos que vencen en los próximos 30 días, ¿cuáles son de tipo SERVICIOS?", "keywords": ["SERVICIOS"]},
    {"id": "ADV010", "type": "Agregación Porcentual", "query": "¿Qué porcentaje del importe total de todos los contratos representa el contrato de mayor valor?", "keywords": ["porcentaje"]},
    {"id": "ADV011", "type": "Multi-documento", "query": "¿Cuántos contratos diferentes mencionan normativas STANAG?", "keywords": ["STANAG"]},
    {"id": "ADV012", "type": "Comparación Temporal", "query": "¿Qué contrato tiene el plazo de ejecución más largo y cuántos días dura?", "keywords": ["plazo", "largo"]},
    {"id": "ADV013", "type": "Multicriterio", "query": "Lista los contratos con avales de Banco Santander cuyo importe de aval sea superior a 200.000€", "keywords": ["Santander", "200.000"]},
    {"id": "ADV014", "type": "Análisis de Frecuencias", "query": "¿Cuál es el código STANAG que aparece en más contratos distintos?", "keywords": ["STANAG"]},
    {"id": "ADV015", "type": "Umbral + Ranking", "query": "De los contratos con importe superior a 10 millones, ¿cuál tiene la penalización por día más alta?", "keywords": ["penalización", "alta"]},
    {"id": "ADV016", "type": "Temporal Complejo", "query": "¿Qué contratos se firmaron en el Q3 de 2024 (julio-septiembre)?", "keywords": ["2024", "firmaron"]},
    {"id": "ADV017", "type": "Cruce de Datos", "query": "¿Qué contratos clasificados como CONFIDENCIAL o SECRETO tienen subcontratación prohibida?", "keywords": ["subcontratación", "prohibida"]},
    {"id": "ADV018", "type": "Estadística", "query": "¿Cuál es el importe promedio de los contratos de tipo SUMINISTRO?", "keywords": ["promedio", "SUMINISTRO"]},
    {"id": "ADV019", "type": "Identificación Crítica", "query": "¿Qué contrato tiene el aval que vence más pronto y cuántos días faltan?", "keywords": ["aval", "vence"]},
    {"id": "ADV020", "type": "Multi-agregación", "query": "¿Cuántos contratos hay por cada nivel de clasificación de seguridad?", "keywords": ["SECRETO", "CONFIDENCIAL"]}
]

# --- ADVERSARIAL TEST ---
ADVERSARIAL_QUESTIONS = [
    {"id": "ADV_NEG_01", "type": "Negation", "query": "¿Qué contratos NO tienen cláusula de confidencialidad?", "keywords": ["no consta", "todos tienen"]},
    {"id": "ADV_HAL_01", "type": "Hallucination Check", "query": "¿Qué proveedores han fallado en las entregas?", "keywords": ["no consta", "información no disponible"]}
]

RESULTS_FILE = "final_evaluation_results.json"
REPORT_FILE = "final_evaluation_report.md"

def run_tests():
    print("="*80)
    print("🚀 STARTING FINAL EVALUATION (DAY 7)")
    print(f"Dataset Size: {len(GOLDEN_DATASET)} Questions")
    print(f"Adversarial Tests: {len(ADVERSARIAL_QUESTIONS)} Questions")
    print("="*80)

    all_results = []
    
    # 1. Run Golden Dataset
    print("\n--- PHASE 1: GOLDEN DATASET ---\n")
    for i, item in enumerate(GOLDEN_DATASET):
        print(f"[{i+1}/{len(GOLDEN_DATASET)}] Running {item['id']} ({item['type']})...")
        start_time = time.time()
        try:
            result = run_agentic_rag(item['query'])
            latency = time.time() - start_time
            
            # Extract key metrics
            answer_text = result.get('answer', '')
            sources = result.get('sources', [])
            meta = result.get('metadata', {})
            
            outcome = {
                "id": item['id'],
                "type": item['type'],
                "query": item['query'],
                "answer": answer_text,
                "sources_count": len(sources),
                "latency": round(latency, 2),
                "complexity": meta.get('complexity', 'unknown'),
                "retry_count": meta.get('retry_count', 0),
                "eval_score": meta.get('evaluation_score', 0.0),
                "keywords_found": [k for k in item['keywords'] if k.lower() in answer_text.lower()]
            }
            all_results.append(outcome)
            print(f"   ✅ Done in {outcome['latency']}s | Score: {outcome['eval_score']} | Sources: {outcome['sources_count']}")
            print("-" * 40)
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            all_results.append({
                "id": item['id'],
                "error": str(e)
            })

    # 2. Run Adversarial Tests
    print("\n--- PHASE 2: ADVERSARIAL TESTING ---\n")
    for item in ADVERSARIAL_QUESTIONS:
        print(f"Running {item['id']} ({item['type']})...")
        start_time = time.time()
        try:
            result = run_agentic_rag(item['query'])
            latency = time.time() - start_time
            
            outcome = {
                "id": item['id'],
                "type": item['type'],
                "query": item['query'],
                "answer": result.get('answer', ''),
                "latency": round(latency, 2),
                "retry_count": result.get('metadata', {}).get('retry_count', 0)
            }
            all_results.append(outcome)
            print(f"   ✅ Done in {outcome['latency']}s")
            
        except Exception as e:
             print(f"   ❌ ERROR: {e}")
             all_results.append({"id": item['id'], "error": str(str)})

    # 3. Save Results
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Results saved to {RESULTS_FILE}")
    generate_markdown_report(all_results)

def generate_markdown_report(results):
    report = "# Final Evaluation Report (Day 7)\n\n"
    report += "| ID | Type | Latency (s) | Sources | Score | Keywords Found |\n"
    report += "|---|---|---|---|---|---|\n"
    
    for r in results:
        if "error" in r:
            report += f"| {r['id']} | ERROR | - | - | - | - |\n"
        else:
            kws = ", ".join(r.get('keywords_found', []))
            if r['id'].startswith("ADV_"): # Adversarial
                 report += f"| {r['id']} | {r['type']} | {r['latency']} | N/A | N/A | N/A |\n"
            else:
                 report += f"| {r['id']} | {r['type']} | {r['latency']} | {r['sources_count']} | {r['eval_score']} | {kws} |\n"

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    run_tests()
