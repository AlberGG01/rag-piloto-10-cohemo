
import sys
import logging
import textwrap
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Quiet logs
logging.basicConfig(level=logging.ERROR)

from src.agents.supervisor import IntegritySupervisor
from src.agents.repair import RepairAgent

def test_repair_loop():
    print("\n==========================================")
    print("🔧 TEST: SELF-HEALING REPAIR LOOP (v4.1)")
    print("==========================================")
    
    supervisor = IntegritySupervisor()
    repair = RepairAgent()
    
    # 1. Defective Input (Broken Table & OCR Garbage)
    print("\n🔹 PASO 1: Diagnóstico Inicial (Supervisor)")
    broken_md = textwrap.dedent("""
    # ID_Contrato: SER_2024_REPAIR_TEST
    
    ## Detalles Económicos
    
    Tabla de precios desalineada:
    | Concepto | Precio Unitario | Total |
    |---|---|---|
    | Mantenimiento Fase 1 | 100.000 € |
    | Mantenimiento Fase 2 | 200.000 € | 200.000 € |
    | Repuestos | | 50.000 € |
    
    Total Contrato: 350.000 €
    
    Texto sucio OCR: x00 x99 ... error
    """).strip()
    
    audit_1 = supervisor.audit_markdown(broken_md, "broken_doc.md")
    print(f"   📊 Status Original: {audit_1['status']} (Score: {audit_1['integrity_score']})")
    
    if audit_1['status'] == "FAIL":
        print("   ✅ CORRECTO: El documento está roto.")
    else:
        print("   ❌ ERROR: El supervisor debió fallar.")
        return

    # 2. Repair Action
    print("\n🔹 PASO 2: Reparación Estructural (RepairAgent)")
    repaired_md = repair.repair_markdown(broken_md, "broken_doc.md")
    print("   📝 Texto Reparado (Preview):")
    print(textwrap.indent(repaired_md[:300], "      ") + "...")

    # 3. Validation
    print("\n🔹 PASO 3: Re-Validación (Supervisor)")
    audit_2 = supervisor.audit_markdown(repaired_md, "repaired_doc.md")
    print(f"   📊 Status Final:    {audit_2['status']} (Score: {audit_2['integrity_score']})")
    print(f"   ℹ️ Metadata:       {audit_2['metadata']}")
    
    if audit_2['status'] == "PASS":
        print("   ✅ SUCCESS: El documento ha sido reparado y validado.")
    else:
        print("   ❌ FAILURE: La reparación no fue suficiente.")
        print(f"   ❌ Errores detectados: {audit_2['detected_errors']}")

if __name__ == "__main__":
    test_repair_loop()
