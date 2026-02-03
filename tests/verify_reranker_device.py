# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import torch

# Ajustar path al root del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.reranker import _reranker_instance

print("="*50)
print("🔍 VERIFICACIÓN DE DEVICE - RE-RANKER")
print("="*50)

# Obtener modelo (singleton)
model = _reranker_instance._get_model()

if model:
    try:
        # CrossEncoder de sentence_transformers guarda el modelo interno en .model
        # y el device en .device
        print(f"✅ Device del re-ranker (wrapper): {model.device}")
        
        # Verificar donde está el primer parámetro del modelo real
        if hasattr(model, 'model'):
             param_device = next(model.model.parameters()).device
             print(f"📍 Modelo cargado en (tensors): {param_device}")
        
    except Exception as e:
        print(f"⚠️ Error inspeccionando device: {e}")
else:
    print("❌ No se pudo cargar el modelo")

print(f"🎮 CUDA disponible: {torch.cuda.is_available()}")
print(f"🍎 MPS disponible: {torch.backends.mps.is_available()}")

print("="*50)
