
import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add src to path
# sys.path.append(os.path.join(os.path.dirname(__file__), 'src')) 

from src.agents.rag_agent import chat
from src.utils.llm_config import set_llm_provider

def run_regression_test():
    """Calcula métricas de todas las preguntas de la guía."""
    
    print("\n🚀 INICIANDO TEST DE REGRESIÓN: GUÍA DE PREGUNTAS CHATBOT")
    print("=========================================================\n")

    # Force OpenAI mode for complex reasoning
    set_llm_provider("openai")
    
    # Test Cases: (Question, Expected Keywords/Logic)
    test_cases = [
        {
            "id": 1,
            "question": "Haz una comparativa de los avales que vencen en el año 2027: Indica código de contrato, importe del aval, entidad avalista y el nivel de seguridad del contrato.",
            "expected_keywords": ["2027", "aval", "seguridad"],
            "description": "Comparativa Avales 2027"
        },
        {
            "id": 2,
            "question": "¿Para qué contratos el Banco Santander nos ha dado un aval y qué importe total suman?",
            "expected_keywords": ["Santander", "total"],
            "description": "Santander Agregado"
        },
        {
            "id": 3,
            "question": "Identifica qué contratos tienen una penalización por retraso superior al 0.5% e indica el objeto del contrato.",
            "expected_keywords": ["penalización", "objeto"],
            "description": "Filtro Penalizaciones > 0.5%"
        },
        {
            "id": 4,
            "question": "¿Qué entidad avala mayor importe total acumulado?",
            "expected_keywords": ["mayor", "total", "€"],
            "description": "Entidad Mayor Aval Acumulado"
        },
        {
            "id": 5,
            "question": "¿Cuál es el contrato con mayor duración en días?",
            "expected_keywords": ["días", "duración"],
            "description": "Contrato Más Largo (Días)"
        },
        {
            "id": 6,
            "question": "Lista los contratos con nivel 'Secreto' por valor superior a 1.000.000€",
            "expected_keywords": ["Secreto", "€"],
            "description": "Filtro Multicriterio (Secreto + Importe)"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for case in test_cases:
        print(f"🧪 Probando {case['id']}: {case['description']}...")
        start_time = time.time()
        
        try:
            response = chat(case['question'])
            elapsed = time.time() - start_time
            
            # Basic Validation
            missing_keywords = [kw for kw in case['expected_keywords'] if kw.lower() not in response.lower()]
            
            if not missing_keywords and len(response) > 50:
                print(f"✅ PASSED ({elapsed:.2f}s)")
                passed += 1
            else:
                print(f"❌ FAILED ({elapsed:.2f}s)")
                print(f"   Missing Keywords: {missing_keywords}")
                print(f"   Response Preview: {response[:100]}...")
                
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
        
        print("-" * 50)

    print(f"\n📊 RESULTADOS FINALES: {passed}/{total} PASARON")
    
    if passed == total:
        print("✅ EL SISTEMA ESTÁ LISTO PARA LA DEMO.")
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON. REVISAR LOGS.")

if __name__ == "__main__":
    run_regression_test()
