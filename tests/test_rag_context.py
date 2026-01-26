import sys
from pathlib import Path
import logging

# Añadir src al path
sys.path.append(str(Path(__file__).resolve().parent))

try:
    from src.agents.rag_agent import build_metadata_context, classify_query
    from src.utils.vectorstore import get_chroma_client
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)

def test_context():
    print("\n=== TEST DE RAG CONTEXT ===\n")
    
    # 1. Verificar clasificación
    query = "¿Cuál es el contrato de mayor importe?"
    q_type = classify_query(query)
    print(f"Query: '{query}' -> Tipo: {q_type}")
    
    if q_type != 'QUANTITATIVE':
        print("ERROR: La query debería clasificarse como QUANTITATIVE")
        return

    # 2. Generar contexto
    print("\nGenerando contexto de metadata...")
    context = build_metadata_context()
    
    print("\n--- CONTEXTO GENERADO ---\n")
    print(context)
    print("\n-------------------------\n")
    
    # 3. Verificar si hay importes
    if "Importe=" in context and "EUR" in context or "€" in context:
        print("✅ Importes detectados en el contexto")
        # Verificar si aparece 12.500.000 (el más alto)
        # Nota: El formato puede variar, pero buscamos números grandes
        import re
        importes = re.findall(r"Importe=([\d\.,\s]+)(?:€|EUR)", context)
        print(f"Importes extraídos del contexto: {importes}")
    else:
        print("❌ NO se detectaron importes correctamente en el contexto")

if __name__ == "__main__":
    test_context()
