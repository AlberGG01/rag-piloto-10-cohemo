# -*- coding: utf-8 -*-
"""
Script de evaluación del RAG con el Golden Dataset.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.agents.rag_agent import chat

# Golden Dataset - Preguntas de prueba
GOLDEN_QUESTIONS = [
    "¿Cuál es el importe total del contrato de suministro de vehículos blindados (CON_2024_001)?",
    "¿Qué entidad bancaria emitió el aval para el contrato de mantenimiento de armamento (CON_2024_002)?",
    "¿Cuándo vence el aval del contrato CON_2024_002 y por qué es crítico?",
    "¿Cuál es el contrato de obras con mayor importe y cuál es su objeto principal?",
    "¿Quién es el contratista del servicio de transporte estratégico y qué CIF tiene?",
]

EXPECTED_ANSWERS = [
    "2.450.000,00 EUR",
    "CaixaBank",
    "28/01/2026",
    "CON_2024_012",
    "Logística Militar Internacional S.A.",
]

def main():
    print("\n" + "="*60)
    print("EVALUACIÓN DEL RAG CON GOLDEN DATASET")
    print("="*60 + "\n")
    
    correct = 0
    total = len(GOLDEN_QUESTIONS)
    
    for i, (question, expected) in enumerate(zip(GOLDEN_QUESTIONS, EXPECTED_ANSWERS), 1):
        print(f"\n[{i}/{total}] Pregunta: {question}")
        print(f"Respuesta Esperada: {expected}")
        
        try:
            response = chat(question)
            print(f"Respuesta del Sistema:\n{response}\n")
            
            # Verificación simple: si la respuesta contiene la clave esperada
            if expected.lower() in response.lower():
                print("✅ CORRECTO")
                correct += 1
            else:
                print("❌ INCORRECTO o PARCIAL")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 60)
    
    accuracy = (correct / total) * 100
    print(f"\n{'='*60}")
    print(f"RESULTADO FINAL: {correct}/{total} correctas ({accuracy:.1f}%)")
    print(f"{'='*60}\n")
    
    if accuracy >= 80:
        print("🏆 ¡SISTEMA APROBADO! RAG 10/10")
    elif accuracy >= 60:
        print("⚠️ Sistema funcional pero necesita ajustes")
    else:
        print("❌ Sistema necesita revisión profunda")

if __name__ == "__main__":
    main()
