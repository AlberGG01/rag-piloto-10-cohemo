"""
Test del sistema de validación
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.answer_validator import validate_answer

def test_numerical_integrity():
    """Test: Detecta números que no existen en fuente"""
    
    print("Test 1: Integridad Numérica...")
    answer = "El importe es 999.999,99 EUR"  # Número inventado
    source_chunks = [
        "El presupuesto base es de 1.234.567,89 EUR",
        "La garantía asciende a 123.456,78 EUR"
    ]
    
    validation = validate_answer(answer, "¿Cuál es el importe?", source_chunks)
    
    if not validation["numerical"]["valid"]:
        print("✅ PASS: Detectó número inexistente correctament.")
    else:
        print("❌ FAIL: No detectó número inexistente.")
        print(validation)
    
    assert not validation["numerical"]["valid"], "Debería detectar número inexistente"
    assert len(validation["numerical"]["violations"]) > 0

def test_valid_answer():
    """Test: Acepta respuesta correcta"""
    
    print("\nTest 2: Respuesta Válida...")
    answer = "El importe total del contrato es de 1.234.567,89 EUR según el documento."
    source_chunks = [
        "Presupuesto: El importe total del contrato es de 1.234.567,89 EUR"
    ]
    
    validation = validate_answer(answer, "¿Cuál es el importe?", source_chunks)
    
    if validation["numerical"]["valid"]:
        print("✅ PASS: Aceptó número correcto.")
    else:
        print("❌ FAIL: Rechazó número correcto.")
        print(validation)
        
    assert validation["numerical"]["valid"], "Debería aceptar número correcto"

if __name__ == "__main__":
    try:
        test_numerical_integrity()
        test_valid_answer()
        print("\n🎉 Todos los tests pasaron")
    except Exception as e:
        print(f"\n❌ Error en tests: {e}")
        sys.exit(1)
