# -*- coding: utf-8 -*-
"""
Auditoría de Consistencia Semántica (Safety Audit).
Valida que la optimización de hardware no degradó la inteligencia del sistema.
"""
import sys
from pathlib import Path
import logging

# Ajustar path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.rag_agent import chat, route_query

# Configurar logging para ver warnings del sistema si los hay
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("AUDIT")

TEST_CASES = [
    {
        "id": "Q_HARD_1 (Retamares)",
        "query": "¿Cuál es el importe total del contrato del Centro de Mando de Retamares?",
        "expected_route": "COMPLEX",
        "key_fact": "28.5" # 28.5M approx
    },
    {
        "id": "Q_HARD_2 (Aval Exacto)",
        "query": "Busca el número de aval AV-2023-1515 e indica qué entidad lo emitió.",
        "expected_route": "SIMPLE", # Puede ser simple o complex dependiendo de keywords "busca"
        # "Busca" no esta en complex_keywords, pero "indica" tampoco. 
        # Esperemos que sea SIMPLE o COMPLEX, lo importante es el dato.
        # Actually, "número" usually triggers simple unless math/compare. 
        # But wait, route_query logic: "comparar", "resumir", math...
        # "Busca el número..." -> Probably SIMPLE.
        "key_fact": "ING Bank"
    },
    {
        "id": "Q_HARD_3 (Synthesis)",
        "query": "¿Cuál es la diferencia en días de ejecución entre el contrato de Mantenimiento C295 y el de Ciberseguridad?",
        "expected_route": "COMPLEX", # "diferencia" is a complex keyword
        "key_fact": "30 días"
    }
]

def run_audit():
    print("\n🧐 INICIANDO AUDITORÍA DE CONSISTENCIA SEMÁNTICA")
    print("="*60)
    
    passed = 0
    total = len(TEST_CASES)
    
    for test in TEST_CASES:
        print(f"\n🔹 TEST: {test['id']}")
        print(f"   Query: {test['query']}")
        
        # 1. Verificar Router
        route = route_query(test['query'])
        print(f"   🤖 Router Decision: {route}")
        
        # Validación de Router (Opcional, pero informativo)
        if "expected_route" in test and test["expected_route"] and route != test["expected_route"]:
            print(f"   ⚠️  Router Divergence (Expected {test['expected_route']}). Checking answer accuracy...")
        
        # 2. Ejecutar Chat
        response = chat(test['query'])
        print(f"   📄 Respuesta:\n   {response[:200]}...") # Preview
        
        # 3. Verificar Dato Clave
        if test['key_fact'].lower() in response.lower():
            print(f"   ✅ RESULTADO: PASS (Dato '{test['key_fact']}' encontrado)")
            passed += 1
        else:
            print(f"   ❌ RESULTADO: FAIL (Dato '{test['key_fact']}' NO encontrado)")
    
    print("\n" + "="*60)
    print(f"🏁 VEREDICTO FINAL: {passed}/{total} TESTS APROBADOS")
    if passed == total:
        print("✅ CERTIFICADO DE CALIDAD: CONSISTENCIA CONFIRMADA")
    else:
        print("❌ ALERTA: DEGRADACIÓN DETECTADA")

if __name__ == "__main__":
    run_audit()
