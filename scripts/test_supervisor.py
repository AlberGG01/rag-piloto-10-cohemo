
import sys
import logging
import json
from pathlib import Path
import textwrap

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Quiet logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.agents.supervisor import IntegritySupervisor

def test_supervisor_integrity():
    print("\n==========================================")
    print("👮 TEST: INTEGRITY SUPERVISOR (v4.0)")
    print("==========================================")
    
    supervisor = IntegritySupervisor()
    
    # CASO 1: Documento Roto (Sin ID, tabla rota)
    print("\n🔹 CASO 1: Documento Defectuoso (Humo Test)")
    broken_md = textwrap.dedent("""
    # Contrato sin identificador
    
    Esta tabla esta rota:
    | Columna 1 | Columna 2 |
    |---|---|
    | Dato A |
    | Dato B | Extra | Error |
    
    Texto con basura OCR: xe2x80x99 ... sdadjkasd
    """)
    
    result_fail = supervisor.audit_markdown(broken_md, "doc_roto_test.md")
    
    print(f"   📊 Status: {result_fail['status']}")
    print(f"   📈 Score:  {result_fail['integrity_score']}")
    print(f"   ❌ Errors: {result_fail['detected_errors']}")
    
    if result_fail['status'] == "FAIL" and result_fail['integrity_score'] < 7:
        print("   ✅ PASSED: Correctly flagged as FAIL.")
    else:
        print("   ❌ FAILED: Should have failed.")

    # Verificar si se creó el log de revisión
    if Path("pending_review.json").exists():
        print("   ✅ PASSED: 'pending_review.json' created.")
        with open("pending_review.json", "r") as f:
            log = json.load(f)
            print(f"   📝 Log entries: {len(log)}")
    else:
        print("   ❌ FAILED: Log file not found.")

    # CASO 2: Documento Bueno (Simulado con metadatos claros)
    print("\n🔹 CASO 2: Documento Correcto")
    good_md = textwrap.dedent("""
    # PLIEGO DE PRESCRIPCIONES TÉCNICAS
    ## ID_Contrato: SER_2025_TEST_01
    
    **Objeto**: Mantenimiento de vehículos blindados.
    **Adjudicatario**: General Dynamics Santa Bárbara Sistemas.
    **Importe Total**: 1.500.000,00 EUR.
    
    | Concepto | Precio |
    |---|---|
    | Mantenimiento Preventivo | 500.000 |
    | Mantenimiento Correctivo | 1.000.000 |
    """)
    
    result_pass = supervisor.audit_markdown(good_md, "doc_bueno_test.md")
    
    print(f"   📊 Status: {result_pass['status']}")
    print(f"   📈 Score:  {result_pass['integrity_score']}")
    print(f"   ℹ️ Meta:   {result_pass['metadata']}")
    
    if result_pass['status'] == "PASS":
        print("   ✅ PASSED: Correctly PASSED.")
    else:
        print("   ❌ FAILED: Should have passed.")

    if result_pass['metadata'].get('id_contrato') == 'SER_2025_TEST_01':
        print("   ✅ PASSED: Correctly extracted ID.")
    else:
        print("   ❌ FAILED: ID extraction failed.")

if __name__ == "__main__":
    test_supervisor_integrity()
