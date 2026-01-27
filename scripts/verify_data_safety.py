
import sys
import logging
import textwrap
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Quiet logs
logging.basicConfig(level=logging.ERROR)

from src.utils.data_safety import compare_numeric_footprint

def test_fraud_attempt():
    print("\n==========================================")
    print("🛡️ TEST: NUMERIC SAFETY BELT (v4.2)")
    print("==========================================")
    
    # Textos base
    original_md = textwrap.dedent("""
    | Concepto | Precio |
    |---|---|
    | Mantenimiento | 500.000 € |
    | Piezas | 25.000,50 € |
    """).strip()
    
    # 1. Caso Reparación Legítima (Solo estructura)
    legit_repair = textwrap.dedent("""
    | Concepto | Precio |
    |---|---|
    | Mantenimiento | 500.000 € |
    | Piezas | 25.000,50 € |
    """).strip()
    
    print("\n🔹 Caso 1: Reparación Legítima")
    ok, msg = compare_numeric_footprint(original_md, legit_repair)
    print(f"   Resultado: {'✅ PASS' if ok else '❌ FAIL'}")
    print(f"   Mensaje:   {msg}")
    
    if ok:
        print("   ✅ SUCCESS: Cambio estructural seguro aprobado.")
    else:
        print("   ❌ FAILURE: Falso positivo.")

    # 2. Caso Intento de Fraude (Cambio sutil de cifra)
    fraud_repair = textwrap.dedent("""
    | Concepto | Precio |
    |---|---|
    | Mantenimiento | 50.000 € |
    | Piezas | 25.000,50 € |
    """).strip()
    # Notar 500.000 -> 50.000
    
    print("\n🔹 Caso 2: Intento de Fraude (500k -> 50k)")
    ok_fraud, msg_fraud = compare_numeric_footprint(original_md, fraud_repair)
    print(f"   Resultado: {'✅ PASS' if ok_fraud else '❌ DETECTED'}")
    print(f"   Mensaje:   {msg_fraud}")
    
    if not ok_fraud:
        print("   ✅ SUCCESS: Fraude detectado y bloqueado.")
    else:
        print("   ❌ FAILURE: El fraude pasó desapercibido.")

if __name__ == "__main__":
    test_fraud_attempt()
