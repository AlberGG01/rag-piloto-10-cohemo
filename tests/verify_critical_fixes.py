"""
Verifica que las queries que antes fallaban ahora funcionen
"""

import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.rag_agent import chat

# Estas 13 queries FALLABAN en evaluation_report_NEW_PC.md
CRITICAL_TESTS = [
    {
        "id": "NUM_06",
        "query": "¿Qué norma ISO específica se exige en el contrato de Vigilancia (CON_2024_010)?",
        "expected_contains": "ISO 18788",
        "previous_fail": "Formato incorrecto (UNE-EN ISO)"
    },
    {
        "id": "NUM_08",
        "query": "Proporciona el CIF de la empresa adjudicataria del contrato de Ciberseguridad (CON_2024_004)",
        "expected_contains": "B-55667788",
        "previous_fail": "NO CONSTA"
    },
    {
        "id": "NUM_10",
        "query": "¿Qué dos normativas de calidad y ergonomía aplican al contrato SUM_2024_014?",
        "expected_contains": ["ISO 13485", "MIL-STD-1472"],
        "previous_fail": "Orden diferente o formato UNE-EN"
    },
    {
        "id": "INF_01",
        "query": "¿Qué contratos incluyen cláusulas de penalización por retraso de 50.000 EUR diarios?",
        "expected_contains": ["SER_2024_015", "SUM_2024_011"],
        "previous_fail": "Solo encontró 1 contrato"
    },
    {
        "id": "INF_02",
        "query": "Compara el importe total del contrato de Ciberseguridad con el de Visión Nocturna. ¿Cuál es mayor y por cuánto?",
        "expected_contains": ["4.5", "4.2", "300.000"],
        "previous_fail": "NO CONSTA"
    },
    {
        "id": "INF_04",
        "query": "¿Cuál es la fecha final de ejecución material programada para el contrato de Retamares (CON_2024_012)?",
        "expected_contains": "12/10/2027",
        "previous_fail": "Fecha incorrecta (12/09/2027)"
    },
    {
        "id": "INF_05",
        "query": "¿Qué normativa de seguridad alimentaria aplica al suministro de raciones de combate?",
        "expected_contains": "ISO 22000",
        "previous_fail": "Respondió Reglamento CE"
    },
    {
        "id": "INF_08",
        "query": "Calcula la diferencia de importe entre el Mantenimiento C295 y los Hangares de Morón",
        "expected_contains": "2.400.000",
        "previous_fail": "NO CONSTA"
    },
    {
        "id": "EDGE_01",
        "query": "Lista los contratos que citan la norma ISO 9001 de forma genérica (sin especificar año)",
        "expected_contains": ["LIC_2024_003", "CON_2024_001", "CON_2024_002"],
        "previous_fail": "NO CONSTA"
    },
    {
        "id": "EDGE_04",
        "query": "¿Cuál es el contrato que contiene mayor densidad de hitos temporales identificados (cerca de 10 fechas)?",
        "expected_contains": ["CON_2024_007", "CON_2024_009"],
        "previous_fail": "Solo mencionó uno"
    },
    {
        "id": "EDGE_05",
        "query": "Identifica los contratos con una penalización exacta de 10.000 EUR (ni más ni menos)",
        "expected_contains": ["SER_2024_008", "SER_2024_019"],
        "previous_fail": "Solo encontró 1"
    },
    {
        "id": "EDGE_07",
        "query": "¿Qué contratos comparten un hito de ejecución fijado para el 16/12/2024?",
        "expected_contains": ["CON_2024_004", "CON_2024_007", "SER_2024_008", "SER_2024_019"],
        "previous_fail": "Solo encontró 2"
    },
    {
        "id": "EDGE_08",
        "query": "¿Qué contrato de suministros combina normativas ISO (civiles) y STANAG (militares) simultáneamente?",
        "expected_contains": "SUM_2024_006",
        "previous_fail": "Respondió CON_2024_001"
    }
]

def verify_fixes():
    print("="*70)
    print("🔍 VERIFICACIÓN DE QUERIES QUE ANTES FALLABAN")
    print("="*70)
    
    fixed = []
    still_failing = []
    
    for i, test in enumerate(CRITICAL_TESTS, 1):
        print(f"\n[{i}/13] {test['id']}: {test['query'][:65]}...")
        print(f"  Fallo anterior: {test['previous_fail']}")
        
        try:
            response = chat(test['query'])
            
            # Verificar si contiene lo esperado
            expected = test['expected_contains']
            if isinstance(expected, str):
                expected = [expected]
            
            # Contar cuántos elementos esperados aparecen
            found_count = sum(1 for exp in expected if exp in response)
            
            if found_count == len(expected):
                print(f"  ✅ PASS - Todos los elementos encontrados ({found_count}/{len(expected)})")
                fixed.append(test['id'])
            elif found_count > 0:
                print(f"  ⚠️  PARCIAL - Solo {found_count}/{len(expected)} elementos")
                print(f"     Respuesta: {response[:150]}...")
                still_failing.append(test['id'])
            else:
                print(f"  ❌ FAIL - No contiene elementos esperados")
                print(f"     Respuesta: {response[:150]}...")
                still_failing.append(test['id'])
        
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            still_failing.append(test['id'])
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN FINAL")
    print("="*70)
    print(f"✅ Queries arregladas: {len(fixed)}/13")
    print(f"❌ Queries que siguen fallando: {len(still_failing)}/13")
    
    accuracy_recovered = (len(fixed) / 13) * 100
    print(f"\n🎯 ACCURACY RECUPERADO: {accuracy_recovered:.1f}%")
    
    if len(fixed) == 13:
        print("🎉 ¡CONFIRMADO! 100% DE LAS QUERIES CRÍTICAS AHORA FUNCIONAN")
        return True
    else:
        print(f"\n⚠️  Queries problemáticas: {still_failing}")
        return False

if __name__ == "__main__":
    success = verify_fixes()
    exit(0 if success else 1)
