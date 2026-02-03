"""
Tests del Citation Engine
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.citation_engine import generate_cited_answer

def test_citation_format():
    """Test: Respuesta incluye citaciones en formato correcto"""
    
    print("\nTest 1: Formato de Citación...")
    query = "¿Cuál es el importe del contrato de Retamares?"
    
    chunks = [
        {
            "text": "El presupuesto base de licitación asciende a 1.234.567,89 EUR (IVA excluido).",
            "metadata": {
                "archivo": "CON_2024_012_Centro_Mando_Retamares.md",
                "pagina": 8,
                "seccion": "Presupuesto Base"
            }
        }
    ]
    
    result = generate_cited_answer(query, chunks)
    answer = result["answer"]
    
    print(f"Respuesta generada: {answer[:200]}...")
    
    # Verificar que incluye citación
    if "[Fuente:" in answer and "CON_2024_012" in answer:
        print("✅ Citación presente y correcta.")
    else:
        print("❌ Fallo en citación.")
        
    assert "[Fuente:" in answer, "Respuesta debe incluir citación"
    assert "CON_2024_012" in answer, "Debe citar el documento correcto"
    assert "1.234.567,89" in answer, "Debe incluir el número exacto"
    
    print("✅ Test citation_format PASS")

def test_contradiction_detection():
    """Test: Detecta contradicciones entre documentos"""
    
    print("\nTest 2: Detección de Contradicciones...")
    query = "¿Cuándo inicia el contrato?"
    
    chunks = [
        {
            "text": "Fecha de inicio del plazo de ejecución: 01/03/2024",
            "metadata": {"archivo": "DOC_TECNICO.md", "pagina": 3}
        },
        {
            "text": "La firma del contrato se realizará el 15/03/2024 y el inicio será el 15/03/2024",
            "metadata": {"archivo": "DOC_ADMINISTRATIVO.md", "pagina": 45}
        }
    ]
    
    result = generate_cited_answer(query, chunks)
    answer = result["answer"]
    
    print(f"Respuesta generada (contradiction check): {answer[:200]}...")
    
    # Verificar detección de contradicción
    has_warning = "discrepancia" in result["answer"].lower() or len(result["contradictions"]) > 0
    
    if has_warning:
        print("✅ Contradicción detectada.")
    else:
        print("❌ Contradicción NO detectada.")
        
    assert has_warning, "Debe detectar contradicción en fechas"
    
    print("✅ Test contradiction_detection PASS")

if __name__ == "__main__":
    try:
        test_citation_format()
        test_contradiction_detection()
        print("\n🎉 Todos los tests de Citation Engine pasaron")
    except Exception as e:
        print(f"\n❌ Fallo en tests: {e}")
        sys.exit(1)
