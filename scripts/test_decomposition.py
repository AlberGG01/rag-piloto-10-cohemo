
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.planner import PlanningAgent
from src.graph.state import WorkflowState  # Ensure this import works or mock it

def test_planner_decomposition():
    print("--- Testing Planner Decomposition for SYN_10 ---")
    
    query = "Calcula el importe total de las garantías definitivas acumuladas de los contratos CON_2024_004, CON_2024_016 y SER_2024_015."
    print(f"Query: {query}")
    
    planner = PlanningAgent()
    
    # Mock state
    state = WorkflowState(query=query)
    
    # Run planner logic (simulated part)
    complexity = planner._classify_complexity(query)
    print(f"Detected Complexity: {complexity}")
    
    sub_queries = planner._decompose_query_structured(query, complexity)
    
    print(f"\nSub-Queries Generated ({len(sub_queries)}):")
    for sq in sub_queries:
        print(f"  - [{sq['id']}] {sq['query']} (Rationale: {sq['rationale']})")
        
    if len(sub_queries) >= 3:
        print("\n✅ SUCCESS: Planner successfully split the query!")
    else:
        print("\n❌ FAILURE: Planner did not split the query correctly.")

if __name__ == "__main__":
    test_planner_decomposition()
