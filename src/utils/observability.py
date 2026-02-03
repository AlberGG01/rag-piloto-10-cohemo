"""
Sistema de observabilidad para monitorear el RAG
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Configurar logger
logger = logging.getLogger(__name__)

class RAGObserver:
    """Monitorea y loguea métricas del RAG"""
    
    def __init__(self, log_file: str = "logs/queries.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_query(
        self,
        query: str,
        answer: str,
        metadata: Dict[str, Any]
    ):
        """
        Loguea query completa con métricas
        
        Args:
            query: Pregunta del usuario
            answer: Respuesta generada
            metadata: Dict con métricas {
                "latency_total": float,
                "latency_retrieval": float,
                "latency_generation": float,
                "latency_validation": float,
                "chunks_retrieved": int,
                "confidence": float,
                "validation_passed": bool,
                "model_used": str,
                "cost_usd": float
            }
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "answer_preview": answer[:200] + "..." if len(answer) > 200 else answer,
            "answer_length": len(answer.split()),
            **metadata
        }
        
        # Append a archivo JSONL
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        logger.info(f"📊 Query logged: {query[:50]}... | Latency: {metadata.get('latency_total', 0):.2f}s | Cost: ${metadata.get('cost_usd', 0):.4f}")
    
    def get_metrics_summary(self, last_n: int = 100) -> Dict[str, Any]:
        """
        Calcula métricas agregadas de las últimas N queries
        
        Returns:
            {
                "total_queries": int,
                "avg_latency": float,
                "p50_latency": float,
                "p95_latency": float,
                "total_cost": float,
                "avg_confidence": float,
                "validation_pass_rate": float
            }
        """
        if not self.log_file.exists():
            return {}
        
        # Leer últimas N líneas
        with open(self.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        recent_logs = [json.loads(line) for line in lines[-last_n:]]
        
        if not recent_logs:
            return {}
        
        # Calcular métricas
        latencies = [log.get("latency_total", 0) for log in recent_logs]
        costs = [log.get("cost_usd", 0) for log in recent_logs]
        confidences = [log.get("confidence", 0) for log in recent_logs]
        validations = [log.get("validation_passed", False) for log in recent_logs]
        
        latencies.sort()
        
        return {
            "total_queries": len(recent_logs),
            "avg_latency": sum(latencies) / len(latencies),
            "p50_latency": latencies[len(latencies) // 2],
            "p95_latency": latencies[int(len(latencies) * 0.95)],
            "max_latency": max(latencies),
            "total_cost": sum(costs),
            "avg_cost_per_query": sum(costs) / len(costs),
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "validation_pass_rate": sum(validations) / len(validations) * 100 if validations else 0
        }


# Singleton global
_observer = None

def get_observer() -> RAGObserver:
    """Obtiene instancia global del observer"""
    global _observer
    if _observer is None:
        _observer = RAGObserver()
    return _observer
