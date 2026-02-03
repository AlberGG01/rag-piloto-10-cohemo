"""
Tests del sistema de observability
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.observability import RAGObserver
import json
import time

def test_logging():
    """Test: Logging de queries"""
    print("\nTest 1: Logging...")
    
    # Observer de prueba
    log_path = "logs/test_queries.jsonl"
    if os.path.exists(log_path):
        os.remove(log_path)
        
    observer = RAGObserver(log_file=log_path)
    
    # Log query
    observer.log_query(
        query="Test query",
        answer="Test answer",
        metadata={
            "latency_total": 5.5,
            "confidence": 85.0,
            "cost_usd": 0.015
        }
    )
    
    # Verificar que se guardó
    assert observer.log_file.exists(), "El archivo de log no se creó"
    
    with open(observer.log_file, "r") as f:
        log = json.loads(f.readline())
    
    print(f"Log leido: {log}")
    
    assert log["query"] == "Test query"
    assert log["latency_total"] == 5.5
    
    print("✅ Test logging PASS")

def test_metrics():
    """Test: Cálculo de métricas"""
    print("\nTest 2: Metricas Aggregated...")
    
    log_path = "logs/test_queries_metrics.jsonl"
    if os.path.exists(log_path):
        os.remove(log_path)
        
    observer = RAGObserver(log_file=log_path)
    
    # Añadir varias queries
    for i in range(10):
        observer.log_query(
            query=f"Query {i}",
            answer="Answer",
            metadata={
                "latency_total": 5.0 + i, # 5,6,7...
                "confidence": 80.0,
                "validation_passed": i % 2 == 0, # True, False, True...
                "cost_usd": 0.01
            }
        )
    
    # Calcular métricas
    metrics = observer.get_metrics_summary(last_n=10)
    print(f"Métricas calculadas: {metrics}")
    
    assert metrics["total_queries"] == 10
    assert metrics["avg_latency"] > 0
    assert metrics["validation_pass_rate"] == 50.0  # 5/10
    assert abs(metrics["total_cost"] - 0.10) < 0.0001, f"Coste incorrecto: {metrics['total_cost']}"
    
    print("✅ Test metrics PASS")

if __name__ == "__main__":
    try:
        test_logging()
        test_metrics()
        print("\n🎉 Todos los tests de Observability pasaron")
    except Exception as e:
        print(f"\n❌ Fallo en tests: {e}")
        sys.exit(1)
