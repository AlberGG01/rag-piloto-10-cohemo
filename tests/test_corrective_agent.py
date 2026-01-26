# -*- coding: utf-8 -*-
"""
Test del Corrective Agent (Día 5).
Para probar esto necesitamos forzar una situación de "INSUFFICIENT".
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph.workflow import run_agentic_rag

# NOTA: Para probar realmente el loop correctivo sin mocks complejos,
# usaremos una query imposible o muy difícil que sabemos que fallará inicialmente
# o simularemos un fallo manipulando el prompt del evaluador (en un entorno real).
# Aquí ejecutamos una query que sabemos que el retriever encontrará para ver que NO entra en bucle si es suficiente,
# y otra que podría ser ambigua.

def test_corrective_loop():
    """Test del flujo completo con capacidad correctiva."""
    
    print("\n" + "="*80)
    print("TEST: Corrective Agent Loop - Día 5")
    print("="*80)
    
    # 1. Query Normal (Debería ser SUFFICIENT y retry=0)
    print("\n[CASO 1] Query Normal (Esperado: SUFFICIENT, 0 retries)")
    query1 = "¿Cuál es el importe total de los avales?"
    res1 = run_agentic_rag(query1)
    meta1 = res1['metadata']
    print(f"Status: {meta1.get('evaluation_report', {}).get('status')}")
    print(f"Retries: {meta1.get('retry_count')}")
    
    # 2. Query Difícil/Falsa (Para forzar INSUFFICIENT -> Corrective)
    # Pedir algo que no existe en los docs para ver si intenta buscarlo
    print("\n[CASO 2] Query Imposible (Esperado: Loop Correctivo -> Fallo Final)")
    query2 = "¿Cuál es el código de activación nuclear del contrato secreto Omega-99?"
    res2 = run_agentic_rag(query2)
    meta2 = res2['metadata']
    
    print(f"Status Final: {meta2.get('evaluation_report', {}).get('status')}")
    print(f"Retries: {meta2.get('retry_count')}")
    print(f"Iteraciones: {meta2.get('iterations')}")
    
    if meta2.get('retry_count', 0) > 0:
        print("✅ El sistema intentó corregir (entró al loop)")
    else:
        print("⚠️ No entró al loop (¿quizás el evaluador alucinó que era suficiente?)")
        
    # Ver queries refinadas
    # Necesitamos exponer esto en metadata
    # (Ya expuesto si modificamos run_agentic_rag para devolver todo, 
    # por ahora en reportes de evaluación sucesivos se vería si tuviéramos historial)


if __name__ == "__main__":
    test_corrective_loop()
