# 🏗️ Architecture V2: Guardrails & Integrity

This document details the advanced **Ingestion Pipeline v5.0** added to the DefenseRAG system to guarantee data integrity and security.

## 🔄 The "Iron-Clad" Ingestion Pipeline

Unlike V1 (classic RAG), V2 implements a strict quality gate before any document reaches the vector store.

```mermaid
graph TD
    PDF[Raw PDF Document] --> OCR[OCR & Normalization]
    OCR --> Markdown[Markdown Text]
    
    subgraph "Integrity Supervisor (Quality Gate)"
        Markdown --> Check{Integrity Check}
        Check -->|Pass > 7/10| Classify[Security Classification]
        Check -->|Fail < 7/10| Repair[Repair Agent]
        
        Repair --> Fix[Self-Healing]
        Fix --> Safety{Data Safety Belt}
        
        Safety -- "Original == Repaired" --> ReAud[Re-Audit]
        Safety -- "Numbers Changed!" --> Quarantine[High-Prio Quarantine]
        
        ReAud --> Check
    end
    
    subgraph "Human-in-the-Loop"
        Check -->|Critical Fail| Manual[Quarantine (JSON)]
        Manual --> Panel[Streamlit Audit Panel]
        Panel -- "Human Fix" --> Indexer
    end
    
    Classify --> Indexer[Vector Store / ChromaDB]
    Indexer --> Metadata[Searchable Metadata]
```

## 🧩 New Components Breakdown

### 1. Integrity Supervisor (`src/agents/supervisor.py`)
*   **Role**: Quality Assurance.
*   **Logic**: Audits Markdown for broken tables, OCR headers, and missing metadata.
*   **Prompting**: Uses strict criteria. Score < 7 triggers review. Missing `ID_Contrato` is an automatic 0 (Critical Fail).

### 2. Repair Agent (`src/agents/repair.py`)
*   **Role**: Structural Surgeon.
*   **Logic**: Uses LLM to fix syntax errors (pipes, line breaks) without altering content.
*   **Strict Mode**: Explicitly forbidden from paraphrasing or inventing data.

### 3. Data Safety Belt (`src/utils/data_safety.py`)
*   **Role**: Fraud Prevention.
*   **Logic**: Extracts the "Numeric Footprint" (ordered sequence of all numbers) from the original and repaired versions.
*   **Constraint**: If `Matches(Original, Repaired) == False`, the document is blocked immediately. This prevents LLM hallucinations like "500.000" -> "50.000".

### 4. Security Classification
*   **Role**: Access Control Labelling.
*   **Levels**:
    *   **Level 1**: Public.
    *   **Level 2**: Internal.
    *   **Level 3**: Confidential (Default for Contracts).
    *   **Level 4**: Restricted (Strategic/Intel).
*   **Implementation**: Enriched metadata during the Audit phase.

## 📊 Updated Database Schema

The Vector Store now holds enriched chunks with the following schema:

```json
{
  "content": "Chunk text...",
  "metadata": {
    "source": "contract.pdf",
    "page": 1,
    "id_contrato": "SER_2024_001",
    "adjudicatario": "ACME Corp",
    "importe_total": 500000,
    "integrity_score": 10,
    "security_level": 3
  }
}
```

---
**DefenseRAG V2 - "Trust but Verify"**
