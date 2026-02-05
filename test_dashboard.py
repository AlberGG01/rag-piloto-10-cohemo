
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph.reporting import run_quick_analysis

# Setup logging to console
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def test_dashboard():
    print("--- TESTING DASHBOARD ANALYSIS ---")
    try:
        result = run_quick_analysis()
        if result.get("success"):
            print("[SUCCESS]")
            s = result.get("alerts_summary")
            print(f"Contracts: {s.get('contracts_count')}")
            print(f"Alerts Total: {s.get('alerts_total')}")
            print(f"High: {s.get('high')}")
            print(f"Medium: {s.get('medium')}")
            print(f"Low/Normal: {s.get('low')}")
        else:
            print("[FAILED]")
            print("Error:", result.get("error"))
    except Exception as e:
        print("[CRASH]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard()
