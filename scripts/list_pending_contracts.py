"""
Identifica qué contratos faltan por normalizar
"""

import os

def list_pending():
    pdf_dir = "data/contracts"
    normalized_dir = "data/normalized"
    
    # Create directories if they don't exist
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(normalized_dir, exist_ok=True)
    
    # PDFs disponibles
    pdfs = [f.replace('.pdf', '') for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    # Normalizados existentes
    normalized = [f.replace('_normalized.md', '') for f in os.listdir(normalized_dir) if f.endswith('.md')]
    
    # Pendientes
    pending = [p for p in pdfs if p not in normalized]
    
    print("="*60)
    print("📊 ESTADO DE NORMALIZACIÓN")
    print("="*60)
    print(f"Total contratos: {len(pdfs)}")
    print(f"Normalizados: {len(normalized)}")
    print(f"Pendientes: {len(pending)}")
    
    if pending:
        print(f"\n📋 CONTRATOS PENDIENTES:")
        for i, contract in enumerate(pending, 1):
            print(f"  {i}. {contract}")
    
    return pending

if __name__ == "__main__":
    list_pending()
