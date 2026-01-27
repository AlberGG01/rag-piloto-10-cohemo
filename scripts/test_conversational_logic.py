
import sys
import uuid
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Quiet logs for clean output
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

from src.graph.workflow import run_agentic_rag

def run_turn(query, thread_id, turn_name):
    print(f"\n🔹 [{turn_name}] User: {query}")
    result = run_agentic_rag(query, thread_id=thread_id)
    rewritten = result['metadata'].get('rewritten_query', 'N/A')
    answer = result['answer'].split('\n')[0] # First line of answer
    print(f"   🧠 Thinking (Rewriter): '{rewritten}'")
    print(f"   🤖 AI: {answer[:80]}...")
    return result

def test_drift():
    print("\n==========================================")
    print("🚧 TEST 1: CONTEXT DRIFT & SWITCHING")
    print("==========================================")
    tid = str(uuid.uuid4())
    
    # 1. Context A
    run_turn("Quién es el adjudicatario del contrato SER_2024_015?", tid, "Turn 1 (Context A)")
    
    # 2. Reference A
    res = run_turn("¿Y qué importe tiene?", tid, "Turn 2 (Ref A)")
    if "SER_2024_015" in res['metadata']['rewritten_query']:
        print("   ✅ SUCCESS: Correctly linked to SER_2024_015")
    else:
        print("   ❌ FAILURE: Lost context of SER_2024_015")

    # 3. Switch to Context B
    run_turn("Háblame ahora del contrato CON_2024_004.", tid, "Turn 3 (Switch to B)")
    
    # 4. Reference B
    res = run_turn("¿Cuál es su plazo de ejecución?", tid, "Turn 4 (Ref B)")
    if "CON_2024_004" in res['metadata']['rewritten_query'] and "SER_2024_015" not in res['metadata']['rewritten_query']:
        print("   ✅ SUCCESS: Switched context to CON_2024_004")
    else:
        print(f"   ❌ FAILURE: Incorrect context. Got: {res['metadata']['rewritten_query']}")

def test_independence():
    print("\n==========================================")
    print("🚧 TEST 2: INDEPENDENCE QUERY")
    print("==========================================")
    tid = str(uuid.uuid4())
    run_turn("Quién ganó el contrato SER_2024_015?", tid, "Turn 1")
    
    query = "Lista todos los contratos de munición."
    res = run_turn(query, tid, "Turn 2 (Independent)")
    
    if res['metadata']['rewritten_query'] == query:
        print("   ✅ SUCCESS: Query remained unchanged.")
    else:
        print(f"   ❌ FAILURE: Query modified unnecessarily -> {res['metadata']['rewritten_query']}")

def test_window():
    print("\n==========================================")
    print("🚧 TEST 3: WINDOW LIMIT (5 Messages)")
    print("==========================================")
    tid = str(uuid.uuid4())
    
    # Turn 1: Set Context (Messages 0, 1)
    # Important: AI needs to generate a response about SER_2024_015
    run_turn("Dame detalles del contrato SER_2024_015.", tid, "T1 (Target Context)")
    
    # Turn 2: Filler (Messages 2, 3)
    run_turn("¿Cuánto es 1 + 1?", tid, "T2 (Filler)")
    
    # Turn 3: Filler (Messages 4, 5)
    run_turn("¿Cuánto es 2 + 2?", tid, "T3 (Filler)")
    
    # Turn 4: Filler (Messages 6, 7)
    run_turn("¿Cuánto es 3 + 3?", tid, "T4 (Filler)")
    
    # Current History Length = 8 messages.
    # Window [-5:] = Messages [3, 4, 5, 6, 7]
    # Message 0 (User query Target) and 1 (AI response Target) are GONE.
    
    # Turn 5: Probe
    res = run_turn("¿Cuál es su importe?", tid, "T5 (Probe - Should Forget)")
    
    # If successful, it should NOT define "SER_2024_015" because explicitly mention is gone.
    # It might fail to rewrite or try to link to "3+3".
    if "SER_2024_015" not in res['metadata']['rewritten_query']:
        print("   ✅ SUCCESS: Correctly FORGOT SER_2024_015 (Window Limit Works)")
    else:
        print("   ❌ FAILURE: Still remembers SER_2024_015 (Window Leak)")

def test_isolation():
    print("\n==========================================")
    print("🚧 TEST 4: THREAD ISOLATION")
    print("==========================================")
    tid_a = f"thread_A_{uuid.uuid4()}"
    tid_b = f"thread_B_{uuid.uuid4()}"
    
    run_turn("Dime el adjudicatario de SER_2024_015", tid_a, "Thread A - Turn 1")
    run_turn("Dime el adjudicatario de CON_2024_004", tid_b, "Thread B - Turn 1")
    
    res_a = run_turn("¿Y su importe?", tid_a, "Thread A - Turn 2")
    res_b = run_turn("¿Y su importe?", tid_b, "Thread B - Turn 2")
    
    ok_a = "SER_2024_015" in res_a['metadata']['rewritten_query']
    ok_b = "CON_2024_004" in res_b['metadata']['rewritten_query']
    
    if ok_a and ok_b:
        print("   ✅ SUCCESS: Threads are fully isolated.")
    else:
        print(f"   ❌ FAILURE: Leak detected. A: {ok_a}, B: {ok_b}")

if __name__ == "__main__":
    # test_drift()
    # test_independence()
    test_window()
    # test_isolation()
