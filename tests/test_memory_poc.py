
import sys
import uuid
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.graph.workflow import run_agentic_rag

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_memory():
    thread_id = str(uuid.uuid4())
    logger.info(f"🆔 Starting Verification Session (Thread ID: {thread_id})")
    
    # ---------------------------------------------------------
    # Turn 1: Initial Query
    # ---------------------------------------------------------
    q1 = "¿Quién es el adjudicatario del contrato SER_2024_015?"
    logger.info(f"🗣️ User (Turn 1): {q1}")
    
    # Run RAG
    result1 = run_agentic_rag(query=q1, thread_id=thread_id)
    answer1 = result1["answer"]
    logger.info(f"🤖 AI (Turn 1): {answer1}")
    
    # Verify State Persistence (Implicitly) by running Turn 2
    
    # ---------------------------------------------------------
    # Turn 2: Follow-up Query (Dependent)
    # ---------------------------------------------------------
    q2 = "¿Y qué importe total tiene?"
    logger.info(f"🗣️ User (Turn 2): {q2}")
    
    # Run RAG (We expect Rewriter to kick in)
    result2 = run_agentic_rag(query=q2, thread_id=thread_id)
    answer2 = result2["answer"]
    
    logger.info(f"🤖 AI (Turn 2): {answer2}")
    
    # Validation logic (Simple text check for now)
    if "Airbus" in answer1 and ("3.500.000" in answer2 or "3,5" in answer2 or "millones" in answer2):
        print("\n✅ TEST PASSED: Context retained and query rewritten correctly.")
    else:
        print("\n❌ TEST FAILED: Context might be lost.")

if __name__ == "__main__":
    test_memory()
