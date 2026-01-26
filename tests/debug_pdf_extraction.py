# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import re
from PyPDF2 import PdfReader

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def debug_extraction(filename):
    pdf_path = Path("data/contracts") / filename
    print(f"Propcessing: {pdf_path}")
    
    if not pdf_path.exists():
        print("File not found")
        return

    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
        
    print("\n--- RAW TEXT EXTRACTED ---")
    print(text[:2000]) # First 2000 chars
    print("--------------------------\n")
    
    # Metadata init
    metadata = {}
    
    # Test Entidad Avalista patterns
    print("Testing Avalista Patterns:")
    aval_entidad_patterns = [
        r"Entidad avalista:\s*(.+?)(?:\n|$)",
        r"Entidad avalista\s*:\s*(.+?)(?:\n|$)",
        r"Banco avalista:\s*(.+?)(?:\n|$)",
        r"Avalista:\s*(.+?)(?:\n|$)",
        r"Emitido por:\s*(.+?)(?:\n|$)",
        r"Entidad\s+avalista\s*:\s*(.+?)(?:\n|$)",
         # New guesses
        r"aval bancario\s*Entidad avalista\s*(.+?)(?:\n|$)",
    ]
    
    for pattern in aval_entidad_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        print(f"Pattern '{pattern}': {'MATCH: ' + match.group(1) if match else 'NO MATCH'}")

    # Test Security Level
    print("\nTesting Security Patterns:")
    seguridad_patterns = [
        r"Clasificacion de seguridad:\s*(.+?)(?:\n|$)",
        r"Clasificación de seguridad:\s*(.+?)(?:\n|$)",
        r"Nivel de seguridad:\s*(.+?)(?:\n|$)",
        r"Grado de seguridad:\s*(.+?)(?:\n|$)",
    ]
    for pattern in seguridad_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        print(f"Pattern '{pattern}': {'MATCH: ' + match.group(1) if match else 'NO MATCH'}")

if __name__ == "__main__":
    # Test with one of the new PDFs
    debug_extraction("CON_2024_012_Centro_Mando_Retamares.pdf")
