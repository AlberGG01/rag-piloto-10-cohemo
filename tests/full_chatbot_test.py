import sys
import logging
from pathlib import Path
import time

# Añadir src al path
sys.path.append(str(Path(__file__).resolve().parent))

from src.agents.rag_agent import retrieve_and_generate, classify_query

# Configurar logging limpio
logging.basicConfig(level=logging.ERROR) # Solo errores del sistema, yo imprimiré lo importante
logger = logging.getLogger(__name__)

TEST_CASES = {
    "💰 SOBRE IMPORTES Y AVALES": [
        "¿Cuál es el contrato de mayor importe?",
        "¿Qué entidades bancarias aparecen como avalistas?",
        "Dame los detalles económicos del contrato CON_2024_009"
    ],
    "📅 SOBRE FECHAS Y PLAZOS": [
        "¿Qué contratos vencen en los próximos 30 días?",
        "¿Qué avales vencen pronto?",
        "¿Cuándo vence el contrato de ciberseguridad?"
    ],
    "🔒 SOBRE SEGURIDAD": [
        "¿Qué contratos tienen clasificación SECRETO?",
        "¿El contrato de munición tiene cláusula de confidencialidad?"
    ],
    "📜 SOBRE NORMAS": [
        "¿Qué contratos deben cumplir normas STANAG?",
        "¿Qué certificaciones ISO se requieren?"
    ],
    "🚨 SOBRE PENALIZACIONES": [
        "¿Qué penalizaciones tiene el contrato de obras?",
        "¿Cuánto es la penalización por indisponibilidad del SOC?"
    ]
}

def run_full_test():
    print("\n" + "="*60)
    print("🤖 INICIANDO BATERÍA DE PRUEBAS DEL CHATBOT")
    print("="*60 + "\n")
    
    for category, questions in TEST_CASES.items():
        print(f"\n>>> CATEGORÍA: {category}")
        print("-" * 40)
        
        for q in questions:
            print(f"\n❓ PREGUNTA: {q}")
            
            # 1. Clasificación
            q_type = classify_query(q)
            print(f"   [Tipo detectado: {q_type}]")
            
            # 2. Ejecución (SIN HISTORIAL PREVIO para aislar pruebas)
            start_time = time.time()
            result = retrieve_and_generate(q, history=[])
            elapsed = time.time() - start_time
            
            response = result.get("response", "ERROR EN RESPUESTA")
            
            # 3. Resultado
            print(f"   🤖 RESPUESTA ({elapsed:.1f}s):")
            print(f"   {response}")
            
            # Validar si hay warnings
            if result.get("warnings"):
                print(f"   ⚠️ WARNINGS: {result['warnings']}")
                
            print("\n" + "." * 60)

if __name__ == "__main__":
    run_full_test()
