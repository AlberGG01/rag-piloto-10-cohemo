
import os
import shutil
import logging
from pathlib import Path
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LOCAL_MODEL_PATH = MODELS_DIR / "all-MiniLM-L6-v2"

def download_embedding_model():
    """Descarga el modelo de embeddings para uso offline."""
    print("\n🚀 DESCAGANDO MODELOS PARA USO OFFLINE")
    print("======================================\n")
    
    # Crear directorio models si no existe
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"📂 Directorio de modelos: {MODELS_DIR}")
    print(f"⬇️  Descargando: {EMBEDDING_MODEL_NAME}...")
    
    try:
        # Usamos snapshot_download para bajar todos los archivos del modelo
        # Esto asegura que SentenceTransformer(local_path) funcione sin internet
        snapshot_download(
            repo_id=EMBEDDING_MODEL_NAME,
            local_dir=str(LOCAL_MODEL_PATH),
            local_dir_use_symlinks=False  # Importante para Windows
        )
        
        print(f"\n✅ Modelo descargado correctamente en: {LOCAL_MODEL_PATH}")
        print("   Ahora el sistema funcionará 100% offline.")
        
        # Prueba de carga inmediata
        print("\n🧪 Verificando carga del modelo local...")
        model = SentenceTransformer(str(LOCAL_MODEL_PATH))
        print("✅ Carga exitosa. El sistema está listo.")
        
    except Exception as e:
        print(f"\n❌ Error durante la descarga: {e}")
        print("   Verifica tu conexión a internet para esta operación inicial.")

if __name__ == "__main__":
    download_embedding_model()
