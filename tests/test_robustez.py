# -*- coding: utf-8 -*-
"""
Test de Robustez: Verificando generalización con otros bancos.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.utils.llm_config import set_llm_provider
from src.agents.rag_agent import chat

# Forzamos modo OpenAI para asegurar la capacidad de razonamiento
set_llm_provider("openai")

def run_checks():
    print("="*60)
    print("TEST DE ROBUSTEZ: PREGUNTAS NO GUIONIZADAS")
    print("="*60)
    
    # Pregunta 1: Liberbank (lo que el usuario preguntó)
    q1 = "¿Qué contratos tiene avalados Liberbank y por qué importe?"
    print(f"\nQ: {q1}")
    print("-" * 60)
    print(chat(q1))
    
    # Pregunta 2: BBVA (otro banco para asegurar)
    q2 = "Listame los avales del BBVA y sus vencimientos."
    print(f"\nQ: {q2}")
    print("-" * 60)
    print(chat(q2))

if __name__ == "__main__":
    run_checks()
