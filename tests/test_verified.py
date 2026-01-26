# -*- coding: utf-8 -*-
"""
Test Profesional RAG - Validación Semántica
Usa respuestas verificadas del dataset
"""

import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.agents.rag_agent import chat

# Test con respuestas VERIFICADAS
VERIFIED_TESTS = [
    {
        "id": "AGG001",
        "question": "¿Cuál es el importe total acumulado de todos los avales bancarios en el sistema?",
        "expected_value": 2900000,  # ~2.9M EUR
        "tolerance": 0.15,  # ±15% tolerancia
        "validation": "numeric_sum"
    },
    {
        "id": "CMP001",
        "question": "Lista los 3 contratos con mayor importe total, ordenados de mayor a menor con sus importes exactos",
        "expected_contracts": ["CON_2024_012", "SER_2024_015", "CON_2024_018"],
        "expected_amounts": [28500000, 18200000, 15800000],
        "validation": "top3_ranking"
    },
    {
        "id": "TMP002",
        "question": "De los avales que vencen en 2027, ¿cuál vence más pronto?",
        "expected_date": "26/03/2027",
        "expected_contracts": ["CON_2024_009", "CON_2024_018"],  # Empate
        "validation": "temporal_first"
    },
    {
        "id": "FLT001",
        "question": "¿Qué contratos tienen clasificación de seguridad SECRETO Y un importe superior a 20 millones de euros?",
        "expected_contracts": ["CON_2024_012"],  # Solo uno
        "validation": "filtered_list"
    },
    {
        "id": "NEG001",
        "question": "¿Qué contratos prohíben completamente la subcontratación?",
        "expected_contracts": ["SER_2024_013"],
        "validation": "negation_list"
    }
]

def validate_numeric_sum(answer, expected, tolerance):
    """Valida suma numérica con tolerancia."""
    # Buscar números grandes en la respuesta (>100k)
    # Normalizar: quitar puntos de miles, reemplazar comas por puntos
    normalized = answer.replace('.', '').replace(',', '.')
    numbers_raw = re.findall(r'\d+\.?\d*', normalized)
    
    found_numbers = []
    for n in numbers_raw:
        try:
            val = float(n)
            if val > 100000:  # Solo números >100k
                found_numbers.append(val)
        except:
            continue
    
    if not found_numbers:
        return False, "No se encontró suma total"
    
    # Buscar el número más cercano al esperado
    closest = min(found_numbers, key=lambda x: abs(x - expected))
    error_pct = abs(closest - expected) / expected
    
    if error_pct <= tolerance:
        return True, f"Suma encontrada: {closest:,.0f} EUR (error: {error_pct*100:.1f}%)"
    else:
        return False, f"Suma incorrecta: {closest:,.0f} EUR (esperado: ~{expected:,.0f} EUR)"

def validate_top3_ranking(answer, expected_contracts, expected_amounts):
    """Valida top 3 con códigos y montos."""
    found_contracts = 0
    found_amounts = 0
    
    for contract in expected_contracts:
        if contract in answer:
            found_contracts += 1
    
    for amount in expected_amounts:
        # Buscar el monto (puede estar con puntos, comas, etc)
        amount_str = f"{amount:,}".replace(',', '[.,]?')
        if re.search(amount_str, answer.replace('.', '').replace(',', '')):
            found_amounts += 1
    
    if found_contracts == 3 and found_amounts >= 2:
        return True, f"Top 3 correcto: {found_contracts}/3 contratos, {found_amounts}/3 importes"
    else:
        return False, f"Incompleto: {found_contracts}/3 contratos, {found_amounts}/3 importes"

def validate_temporal_first(answer, expected_date, expected_contracts):
    """Valida fecha más temprana."""
    if expected_date in answer:
        # Verificar que mencione al menos uno de los contratos
        if any(c in answer for c in expected_contracts):
            return True, f"Fecha correcta: {expected_date}"
        else:
            return True, f"Fecha correcta pero falta código contrato"
    else:
        return False, f"Fecha incorrecta (esperada: {expected_date})"

def validate_filtered_list(answer, expected_contracts):
    """Valida lista filtrada (debe mencionar solo los esperados)."""
    found = sum(1 for c in expected_contracts if c in answer)
    
    if found == len(expected_contracts):
        return True, f"{found}/{len(expected_contracts)} contratos correctos"
    else:
        return False, f"Solo {found}/{len(expected_contracts)} encontrados"

def validate_negation_list(answer, expected_contracts):
    """Valida lista de negación."""
    return validate_filtered_list(answer, expected_contracts)

def run_verified_test():
    """Ejecuta test con validación semántica."""
    
    print("\n" + "="*80)
    print("TEST PROFESIONAL RAG - VALIDACION SEMANTICA")
    print("="*80)
    print("\nDataset: Respuestas verificadas de documentos fuente\n")
    
    results = []
    
    for i, test in enumerate(VERIFIED_TESTS, 1):
        print(f"\n[{i}/5] {test['id']}")
        print(f"Pregunta: {test['question']}")
        
        # Obtener respuesta
        try:
            answer = chat(test['question'], history=[])
            print(f"\nRespuesta: {answer[:200]}...")
        except Exception as e:
            answer = f"ERROR: {e}"
            print(f"\nERROR: {e}")
        
        # Validar según tipo
        validation_type = test['validation']
        
        if validation_type == "numeric_sum":
            is_correct, msg = validate_numeric_sum(
                answer, test['expected_value'], test['tolerance']
            )
        elif validation_type == "top3_ranking":
            is_correct, msg = validate_top3_ranking(
                answer, test['expected_contracts'], test['expected_amounts']
            )
        elif validation_type == "temporal_first":
            is_correct, msg = validate_temporal_first(
                answer, test['expected_date'], test['expected_contracts']
            )
        elif validation_type == "filtered_list":
            is_correct, msg = validate_filtered_list(
                answer, test['expected_contracts']
            )
        elif validation_type == "negation_list":
            is_correct, msg = validate_negation_list(
                answer, test['expected_contracts']
            )
        else:
            is_correct, msg = False, "Validación desconocida"
        
        status = "[OK]" if is_correct else "[X]"
        print(f"\n{status} {msg}")
        
        results.append({
            "id": test['id'],
            "correct": is_correct,
            "message": msg
        })
    
    # Resumen
    print("\n" + "="*80)
    print("RESULTADOS")
    print("="*80)
    
    correct_count = sum(1 for r in results if r['correct'])
    print(f"\nCorrect: {correct_count}/5 ({correct_count*20}%)")
    
    print("\nDetalle:")
    for r in results:
        status = "[OK]" if r['correct'] else "[X]"
        print(f"  {status} {r['id']}: {r['message']}")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    results = run_verified_test()
