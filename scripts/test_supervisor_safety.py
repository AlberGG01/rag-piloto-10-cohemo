
import sys
import logging
import textwrap
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Quiet logs
logging.basicConfig(level=logging.ERROR)

from src.agents.supervisor import IntegritySupervisor

def test_supervisor_safety_belt():
    print("\n==========================================")
    print("👮🛡️ TEST: SUPERVISOR SAFETY INTEGRATION")
    print("==========================================")
    
    supervisor = IntegritySupervisor()
    
    original_md = textwrap.dedent("""
    | Item | Cost |
    |---|---|
    | Tank | 10.000 € |
    """).strip()
    
    fraud_md = textwrap.dedent("""
    | Item | Cost |
    |---|---|
    | Tank | 1.000 € |
    """).strip()
    
    print("\n🔹 Testing Fraud via Supervisor...")
    # Pasamos original_text para activar el Safety Belt
    result = supervisor.audit_markdown(fraud_md, "fraud_doc.md", original_text=original_md)
    
    print(f"   Status: {result['status']}")
    print(f"   Errors: {result['detected_errors']}")
    
    if result['status'] == "FAIL" and any("SECURITY VIOLATION" in e for e in result['detected_errors']):
        print("   ✅ SUCCESS: Supervisor caught the fraud!")
    else:
        print("   ❌ FAILURE: Supervisor let the fraud pass.")

if __name__ == "__main__":
    test_supervisor_safety_belt()
