"""
Exporta configuración completa del sistema
"""
import sys
import os

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.config import MODEL_EMBEDDINGS, MODEL_CHATBOT, COLLECTION_NAME
except ImportError as e:
    print(f"Error importing config: {e}")
    sys.exit(1)

config = {
    "embedding_model": MODEL_EMBEDDINGS,
    "llm_model": MODEL_CHATBOT,
    "vectordb_collection": COLLECTION_NAME,
    "python_version": sys.version,
    "working_directory": os.getcwd()
}

print("="*60)
print("⚙️  CONFIGURACIÓN DEL SISTEMA")
print("="*60)
for key, value in config.items():
    print(f"{key}: {value}")
