# 🐳 Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum (16GB recommended)

### 1. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your OpenAI API key
nano .env  # or vim, code, etc.
```

**Minimum required in `.env`:**
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. Build and Start
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f rag-app
```

### 3. Access Application
Open browser: http://localhost:8501

## Configuration Options

### Hardware Optimization

**Auto-detect GPU (Recommended):**
```bash
# .env
USE_GPU=auto
```

**Force CPU-only:**
```bash
# .env
USE_GPU=false
ENABLE_RERANKER=false  # Disable re-ranker to save 18s
```

**Force GPU (if available):**
```bash
# .env
USE_GPU=true
ENABLE_RERANKER=true
```

## Latency vs Accuracy Trade-offs

**Maximum Accuracy (Default):**
```bash
ENABLE_RERANKER=true       # Best ranking
ENABLE_LLM_JUDGE=true      # Extra validation
# Latency: ~26s (CPU) or ~10s (GPU)
```

**Balanced:**
```bash
ENABLE_RERANKER=true       # Keep ranking
ENABLE_LLM_JUDGE=false     # Skip LLM judge
# Latency: ~21s (CPU) or ~5s (GPU)
# Accuracy: ~93% (minimal impact)
```

**Fast Mode:**
```bash
ENABLE_RERANKER=false      # Skip re-ranking
ENABLE_LLM_JUDGE=false     # Skip LLM judge
# Latency: ~8s
# Accuracy: ~90% (acceptable for non-critical)
```

## Common Commands

### Service Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View status
docker-compose ps

# View logs
docker-compose logs -f rag-app
docker-compose logs -f vectordb
```

### Maintenance
```bash
# Rebuild after code changes
docker-compose build --no-cache rag-app
docker-compose up -d

# Access container shell
docker-compose exec rag-app bash

# Run diagnostics inside container
docker-compose exec rag-app python scripts/diagnose_vectordb.py

# View resource usage
docker stats
```

### Data Management
```bash
# Backup VectorDB
docker-compose exec rag-app tar -czf /tmp/chroma_backup.tar.gz /app/chroma_db
docker cp defense-rag-app:/tmp/chroma_backup.tar.gz ./backup_$(date +%Y%m%d).tar.gz

# Restore VectorDB
docker cp backup_20260203.tar.gz defense-rag-app:/tmp/
docker-compose exec rag-app tar -xzf /tmp/backup_20260203.tar.gz -C /app
docker-compose restart rag-app

# Clear VectorDB (re-index from scratch)
docker-compose down -v
docker-compose up -d
```

## Using Qdrant (Optional Server-mode VectorDB)
By default, the system uses ChromaDB (local, file-based). To use Qdrant server:
```bash
# Start with Qdrant profile
docker-compose --profile with-qdrant up -d

# Update .env
VECTOR_DB_TYPE=qdrant
VECTOR_DB_HOST=vectordb
VECTOR_DB_PORT=6333

# Restart RAG app
docker-compose restart rag-app
```
Qdrant UI: http://localhost:6333/dashboard

## Troubleshooting

### Port Already in Use
```bash
# Change Streamlit port
# In .env:
STREAMLIT_PORT=8502

# Rebuild
docker-compose up -d
```

### Out of Memory
```bash
# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory: 8GB+

# Or reduce resource limits in docker-compose.yml
```

### GPU Not Detected
```bash
# Verify GPU in container
docker-compose exec rag-app python -c "import torch; print(torch.cuda.is_available())"

# If False, check nvidia-docker installation
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### VectorDB Connection Failed
```bash
# Check if vectordb service is running
docker-compose ps vectordb

# View vectordb logs
docker-compose logs vectordb

# Restart vectordb
docker-compose restart vectordb
```

## Production Deployment

### Security Hardening
**Use Docker Secrets (not .env)**
```yaml
# docker-compose.prod.yml
secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt

services:
  rag-app:
    secrets:
      - openai_api_key
```

**Enable HTTPS (nginx reverse proxy)**
```bash
# Add nginx service in docker-compose
# Use Let's Encrypt for SSL certificates
```

### Monitoring
```bash
# Prometheus + Grafana (optional)
# Add monitoring services to docker-compose.yml

# Check logs at /logs on host machine
```

### Backup Strategy
```bash
# Automated daily backups (cron job on host)
0 2 * * * docker-compose exec rag-app tar -czf /backup/vectordb_$(date +\%Y\%m\%d).tar.gz /app/chroma_db
```
