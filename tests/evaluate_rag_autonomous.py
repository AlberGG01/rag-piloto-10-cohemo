# -*- coding: utf-8 -*-
"""
Evaluación Autónoma del Sistema RAG V3
Ejecuta evaluación end-to-end sin necesidad de servidor web
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Configurar path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.rag_agent import chat

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def evaluate_rag(dataset_path: Path):
    """Evalúa el RAG contra el golden dataset"""
    
    print("\n" + "="*80)
    print("🧪 EVALUACIÓN AUTÓNOMA DEL SISTEMA RAG V3")
    print("="*80 + "\n")
    
    # Cargar golden dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    print(f"📋 Dataset cargado: {len(dataset)} preguntas\n")
    
    # Evaluar cada pregunta
    results = []
    correct = 0
    
    for item in dataset:
        q_id = item['id']
        pregunta = item['pregunta']
        respuesta_correcta = item['respuesta_correcta']
        
        print(f"[Q{q_id}] {pregunta}")
        
        try:
            # Obtener respuesta del RAG usando función chat
            respuesta = chat(pregunta)
            
            # Mostrar respuesta
            print(f"✅ Respuesta obtenida: {respuesta[:200]}..." if len(respuesta) > 200 else f"✅ Respuesta: {respuesta}")
            
            # Evaluación simple: verificar si la respuesta correcta está en la respuesta del RAG
            # (Esto es una aproximación; idealmente usaríamos LLM para evaluar)
            is_correct = any(keyword.lower() in respuesta.lower() for keyword in respuesta_correcta.split() if len(keyword) > 3)
            
            if is_correct:
                correct += 1
                print("✅ CORRECTO")
            else:
                print(f"❌ INCORRECTO - Esperado: {respuesta_correcta}")
            
            results.append({
                "id": q_id,
                "pregunta": pregunta,
                "respuesta_rag": respuesta,
                "respuesta_correcta": respuesta_correcta,
                "correcto": is_correct
            })
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "id": q_id,
                "pregunta": pregunta,
                "respuesta_rag": f"ERROR: {str(e)}",
                "respuesta_correcta": respuesta_correcta,
                "correcto": False
            })
        
        print()
    
    # Calcular accuracy
    accuracy = (correct / len(dataset)) * 100
    
    # Guardar resultados
    results_path = Path(__file__).parent / "evaluation_results_v3.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(dataset),
            "correct_answers": correct,
            "accuracy_percentage": accuracy,
            "details": results
        }, f, indent=2, ensure_ascii=False)
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESULTADOS DE EVALUACIÓN")
    print("="*80)
    print(f"Total Preguntas:    {len(dataset)}")
    print(f"Respuestas Correctas: {correct}")
    print(f"Accuracy:           {accuracy:.1f}%")
    print(f"\n📄 Resultados guardados en: {results_path}")
    print("="*80 + "\n")
    
    return accuracy, results

def main():
    dataset_path = Path(__file__).parent / "golden_dataset_v3.json"
    
    if not dataset_path.exists():
        print(f"❌ ERROR: No se encontró {dataset_path}")
        return
    
    accuracy, results = evaluate_rag(dataset_path)
    
    # Reporte comparativo
    print("\n" + "="*80)
    print("📈 COMPARATIVA CON VERSIÓN ANTERIOR")
    print("="*80)
    print(f"Accuracy Anterior:  46.7%")
    print(f"Accuracy Actual:    {accuracy:.1f}%")
    print(f"Mejora:             {accuracy - 46.7:+.1f} puntos porcentuales")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
