
import sys
import logging
import textwrap
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Quiet logs
logging.basicConfig(level=logging.ERROR)

from src.agents.supervisor import IntegritySupervisor

def test_security_classification():
    print("\n==========================================")
    print("🔐 TEST: SECURITY CLASSIFICATION (v5.1)")
    print("==========================================")
    
    supervisor = IntegritySupervisor()
    
    # CASO 1: Nivel 3 (Contrato Estándar / Financiero)
    print("\n🔹 CASO 1: Contrato Financiero (Esperado: Nivel 3)")
    financial_doc = textwrap.dedent("""
    # ID_Contrato: SER_2024_FINANCE_01
    **Objeto**: Adquisición de repuestos para vehículos.
    **Importe**: 2.500.000 €
    
    ## Presupuesto Detallado
    Se detalla el coste de mantenimiento correctivo y preventivo...
    """).strip()
    
    res_1 = supervisor.audit_markdown(financial_doc, "finance.md")
    sec_1 = res_1['metadata'].get('security_level')
    print(f"   📊 Nivel Asignado: {sec_1}")
    
    if sec_1 == 3:
        print("   ✅ CORRECTO: Clasificado como Confidencial (3).")
    else:
        print(f"   ⚠️ DIFERENTE: Se esperaba 3, obtuvo {sec_1}.")

    # CASO 2: Nivel 4 (Estratégico / Militar)
    print("\n🔹 CASO 2: Documento Estratégico (Esperado: Nivel 4)")
    strategic_doc = textwrap.dedent("""
    # ID_Contrato: STRAT_2024_INTEL_01
    **Objeto**: Despliegue de red de satélites espía.
    
    ## INFORME DE INTELIGENCIA
    Se han detectado vulnerabilidades críticas en el flanco este.
    La ubicación secreta de la base de operaciones especiales ha sido comprometida.
    Se requiere ciberataque ofensivo inmediato.
    """).strip()
    
    res_2 = supervisor.audit_markdown(strategic_doc, "intel.md")
    sec_2 = res_2['metadata'].get('security_level')
    print(f"   📊 Nivel Asignado: {sec_2}")
    
    if sec_2 == 4:
        print("   ✅ CORRECTO: Clasificado como Restringido (4).")
    else:
        print(f"   ⚠️ DIFERENTE: Se esperaba 4, obtuvo {sec_2}.")
    
    # CASO 3: Nivel 1 (Público)
    print("\n🔹 CASO 3: Manual Público (Esperado: Nivel 1 o 2)")
    public_doc = textwrap.dedent("""
    # ID_Contrato: PUB_2024_MANUAL_01
    # Manual de Usuario: Extintor Polvo ABC
    
    Este manual es de dominio público.
    Instrucciones:
    1. Quite la anilla.
    2. Apunte a la base del fuego.
    Este documento no contiene información clasificada ni precios.
    """).strip()
    
    res_3 = supervisor.audit_markdown(public_doc, "manual.md")
    sec_3 = res_3['metadata'].get('security_level')
    print(f"   📊 Nivel Asignado: {sec_3}")
    
    if sec_3 in [1, 2]:
        print(f"   ✅ CORRECTO: Clasificado como Bajo Riesgo ({sec_3}).")
    else:
        print(f"   ⚠️ DIFERENTE: Se esperaba 1 o 2, obtuvo {sec_3}.")

if __name__ == "__main__":
    test_security_classification()
