"""
Tests del sistema de Confidence Scoring
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.confidence_scorer import calculate_confidence

class MockChunk:
    """Mock de Document para testing"""
    def __init__(self, text):
        self.page_content = text
        self.metadata = {}  # Add metadata attribute

def test_high_confidence_answer():
    """Test: Respuesta con alta confianza"""
    
    print("\nTest 1: Alta Confianza...")
    answer = "El importe total es 1.234.567,89 EUR [Fuente: CON_2024_012, Pág. 8]"
    query = "¿Cuál es el importe del contrato?"
    
    # Simular chunks con scores altos
    chunks_with_scores = [
        (MockChunk("Importe total: 1.234.567,89 EUR"), 0.95),
        (MockChunk("Presupuesto de 1.234.567,89 euros"), 0.88),
        (MockChunk("Garantía de 123.456 EUR"), 0.75)
    ]
    
    # Simular validación exitosa
    validation = {
        "numerical": {"valid": True},
        "logical": {"valid": True},
        "citation": {"valid": True}
    }
    
    confidence = calculate_confidence(answer, query, chunks_with_scores, validation)
    
    print(f"✅ High confidence: {confidence['confidence']}%")
    print(f"   Recomendación: {confidence['recommendation']}")
    
    assert confidence["confidence"] >= 80, f"Esperaba >80%, obtuvo {confidence['confidence']}%"
    assert "ALTA" in confidence["recommendation"] or "BUENA" in confidence["recommendation"]

def test_low_confidence_answer():
    """Test: Respuesta con baja confianza"""
    
    print("\nTest 2: Baja Confianza...")
    answer = "No se encontró información específica."
    query = "¿Cuál es el importe?"
    
    # Chunks con scores bajos
    chunks_with_scores = [
        (MockChunk("Cláusulas administrativas generales..."), 0.45),
        (MockChunk("Normativa aplicable..."), 0.42)
    ]
    
    # Validación fallida
    validation = {
        "numerical": {"valid": False},
        "logical": {"valid": False},
        "citation": {"valid": False}
    }
    
    confidence = calculate_confidence(answer, query, chunks_with_scores, validation)
    
    print(f"✅ Low confidence: {confidence['confidence']}%")
    print(f"   Recomendación: {confidence['recommendation']}")
    
    assert confidence["confidence"] < 60, f"Esperaba <60%, obtuvo {confidence['confidence']}%"
    assert "BAJA" in confidence["recommendation"] or "MEDIA" in confidence["recommendation"]


if __name__ == "__main__":
    try:
        test_high_confidence_answer()
        test_low_confidence_answer()
        print("\n🎉 Todos los tests de Confidence Scorer pasaron")
    except Exception as e:
        print(f"\n❌ Fallo en tests: {e}")
        sys.exit(1)
