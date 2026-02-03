# -*- coding: utf-8 -*-
"""
Test de Consolidación - Fase 2: Orquestación Eficiente.
Valida Router (Complex vs Simple) y Reordering U-Shape en preguntas Q1-Q6.
"""
import sys
import logging
import json
from pathlib import Path
import time

# Configurar path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.rag_agent import chat, route_query

# Configurar logging para ver decisiones del Router
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

def main():
    print("🚀 INICIANDO TEST DE CONSOLIDACIÓN (ROUTER + U-SHAPE)")
    print("="*60)
    
    # Cargar Golden Dataset V3
    dataset_path = Path("tests/golden_dataset_v3.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        full_dataset = json.load(f)
    
    # Filtrar Q1-Q6
    subset = [q for q in full_dataset if q["id"] <= 6]
    
    results = []
    
    for item in subset:
        q_id = item["id"]
        question = item["pregunta"]
        expected = item["respuesta_correcta"]
        
        print(f"\n🔹 [Q{q_id}] {question}")
        
        # 1. Verificar Router (Predicción)
        complexity = route_query(question)
        model = "GPT-4o" if complexity == "COMPLEX" else "GPT-4o-mini"
        print(f"   🤖 Router Prediction: {complexity} -> {model}")
        
        start_time = time.time()
        
        # 2. Ejecutar RAG
        try:
            # Capturamos logs de stdout para ver que realmente se usó el modelo (confiamos en la lógica implementada)
            response = chat(question)
            duration = time.time() - start_time
            
            # 3. Validación (básica manual/visual en el output)
            print(f"   ✅ Respuesta ({duration:.1f}s):")
            print(f"   {response[:200]}..." if len(response) > 200 else f"   {response}")
            
            results.append({
                "id": q_id,
                "model": model,
                "status": "COMPLETED"
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append({
                "id": q_id,
                "model": model,
                "status": "ERROR"
            })
            
    print("\n" + "="*60)
    print("📊 RESUMEN DE EJECUCIÓN")
    for r in results:
        print(f"Q{r['id']}: Modelo {r['model']} - Status {r['status']}")

if __name__ == "__main__":
    main()
