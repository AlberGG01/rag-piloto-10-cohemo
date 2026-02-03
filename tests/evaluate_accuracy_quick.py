# -*- coding: utf-8 -*-
"""
Evaluador RÁPIDO para tests específicos (evaluación incremental).
Solo ejecuta los IDs especificados para iterar más rápido.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# IDs de tests que fallaron en Iter1 (73.33%)
FAILED_IDS_ITER1 = [
    "INF_04",   # Fecha final ejecución (incorrecto)
    "INF_05",   # Normativa alimentaria (info extra)
    "EDGE_01",  # ISO genérico (no detecta)
    "EDGE_04",  # Densidad hitos (cuenta incorrecta)
    "EDGE_05",  # Penalización 10k (nuevo fallo - regresión)
    "EDGE_06",  # Subcontratación prohibida (frase exacta)
    "EDGE_07",  # Hito compartido (fecha)
    "EDGE_08"   # ISO+STANAG (multi-criterio)
]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="+", default=FAILED_IDS_ITER1, 
                       help="Test IDs to evaluate")
    args = parser.parse_args()
    
    # Importar el evaluador principal
    from evaluate_accuracy_v4 import run_evaluation
    
    print(f"\n🎯 EVALUACIÓN RÁPIDA: {len(args.ids)} tests")
    print(f"   IDs: {', '.join(args.ids)}\n")
    
    # Ejecutar solo los IDs especificados
    run_evaluation(target_ids=args.ids)
