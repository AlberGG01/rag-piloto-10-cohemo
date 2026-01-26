import sys
import logging
from pathlib import Path

# Añadir src al path
sys.path.append(str(Path(__file__).resolve().parent))

from src.agents.rag_agent import build_metadata_context, classify_query, format_conversation_history
from src.config import RAG_SYSTEM_PROMPT
from src.utils.llm_config import generate_response

# Configura logging para ver qué pasa
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_test():
    print("🤖 INICIANDO TEST DE DEBUG DEL CHATBOT...\n")
    
    # 1. Verificar Contexto de Metadata
    print("📊 1. Generando contexto de metadata...")
    context = build_metadata_context()
    print("-" * 40)
    print(context)
    print("-" * 40)
    
    # Verificar si el contrato de 12.5M aparece y si está ordenado
    if "12.500.000,00€" in context:
        print("✅ El contrato de 12.5M (CON_2024_009) está en el contexto")
    else:
        print("❌ ALERTA: El contrato de 12.5M NO aparece en el contexto")

    # 2. Probar preguntas clave
    questions = [
        "¿Cuál es el contrato de mayor importe?",
        "¿Qué contrato vence antes?",
        "¿Cuál es el contrato de suministros de mayor valor?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n❓ PREGUNTA {i}: {question}")
        
        # Clasificación
        q_type = classify_query(question)
        print(f"   Tipo detectado: {q_type}")
        
        # Generar Prompt
        historial = ""
        prompt = RAG_SYSTEM_PROMPT.format(
            contexto=context if q_type == 'QUANTITATIVE' else "CONTEXTO_DUMMY",
            historial=historial,
            pregunta=question
        )
        
        print("   🧠 Generando respuesta con LLM...")
        response = generate_response(prompt, max_tokens=200, temperature=0.0)
        
        print(f"   🤖 RESPUESTA: {response}\n")

if __name__ == "__main__":
    run_test()
