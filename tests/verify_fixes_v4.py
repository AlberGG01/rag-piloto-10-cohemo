import sys
import os
import json
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.rag_agent import chat

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TARGET_IDS = ["NUM_08", "INF_02"]

def run_verification():
    print(f"🚀 VERIFICANDO FIXES PARA: {TARGET_IDS}")
    
    # Load dataset
    with open("tests/golden_dataset_v4.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    # Filter
    targets = [q for q in dataset if q["id"] in TARGET_IDS]
    
    if not targets:
        print("❌ No se encontraron los IDs objetivos.")
        return

    for item in targets:
        print(f"\n🔹 Evaluando {item['id']}...")
        print(f"❓ Pregunta: {item['pregunta']}")
        
        try:
            response = chat(item["pregunta"])
            print(f"🤖 Respuesta RAG:\n{response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
        print(f"📝 Verdad Absoluta: {item['respuesta_correcta']}")
        print("-" * 50)

    print("\n✅ VERIFICACIÓN COMPLETADA")

if __name__ == "__main__":
    run_verification()
