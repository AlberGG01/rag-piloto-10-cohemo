
import os
import re
import json
import glob
from typing import List, Dict, Optional

# Configuration
DATA_DIR = "d:/Dev/projects/defense_contracts_system/data/normalized"
OUTPUT_FILE = "d:/Dev/projects/defense_contracts_system/guarantees_extracted.json"

def normalize_number(num_str: str) -> float:
    """Converts 1.234,56 to 1234.56"""
    clean = num_str.replace('.', '').replace(',', '.')
    return float(clean)

def extract_guarantees_from_file(filepath: str) -> Optional[Dict]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    contrato_match = re.search(r"(CON_|LIC_|SER_|SUM_)\d{4}_\d{3}", filename)
    contrato_id = contrato_match.group(0) if contrato_match else filename
    
    # Patterns to find guarantee amounts
    # Prioridad: Garantía definitiva explícita
    # Examples: 
    # "importe de la garantía definitiva: 12.345,67 euros"
    # "se constituye garantía definitiva por 12.345,67 €"
    
    patterns = [
        # Table Format: | Garantía definitiva | ... | 224.000,00 EUR |
        r"\|\s*Garantía definitiva\s*\|.*?\|\s*([\d\.]+,\d{2})\s*(?:EUR|€|euros)\s*\|",
        
        # Markdown specific list Format: - **Garantía definitiva:** 50.000,00 EUR
        r"Garantía definitiva:?\*\*?\s*([\d\.]+,\d{2})\s*(?:EUR|€|euros)",
        r"\*\*Garantía definitiva:?\*\*?\s*([\d\.]+,\d{2})\s*(?:EUR|€|euros)",
        
        # Narrative with safeguards (avoid matching across too many lines)
        # We manually use [\s\S] for dotall where needed, but prefer single line for these
        r"garantía definitiva.*?asciende.*?a\s+([\d\.]+,\d{2})\s*(?:€|euros|EUR)",
        r"importe.*?garantía definitiva.*?([\d\.]+,\d{2})\s*(?:€|euros|EUR)",
        
        # Fallback simplistic (only if close proximity)
        r"Garantía definitiva.{1,100}?\s+([\d\.]+,\d{2})\s*(?:EUR|€|euros)"
    ]
    
    amount_str = None
    
    print(f"DEBUG: Checking {filename}")
    
    # Intenta patrones PRIMERO sin DOTALL (línea a línea, más seguro y preciso)
    for p in patterns:
        match = re.search(p, content, re.IGNORECASE) 
        if match:
            extracted = match.group(1)
            print(f"  DEBUG: Matched STRICT pattern '{p}' -> {extracted}")
            amount_str = extracted
            break
            
    if not amount_str:
        # Fallback localizados (sin DOTALL masivo)
        # Buscar "Garantía definitiva" y mirar en los siguientes 100 caracteres
        idx = content.find("Garantía definitiva")
        if idx != -1:
            snippet = content[idx:idx+200] # Contexto local
            # Buscar número en ese snippet
            num_match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})\s*(?:EUR|€|euros)", snippet)
            if num_match:
                 amount_str = num_match.group(1)
                 print(f"  DEBUG: Matched SNIPPET -> {amount_str}")

    if amount_str:
        return {
            "contrato": contrato_id,
            "garantia_eur": normalize_number(amount_str),
            "garantia_texto": amount_str,
            "archivo": filename
        }
    else:
        print(f"DEBUG: No guarantee found in {filename}")
    
    return None

def main():
    md_files = glob.glob(os.path.join(DATA_DIR, "*.md"))
    results = []
    total_eur = 0.0
    
    print(f"Propcessing {len(md_files)} files...")
    
    for file in md_files:
        data = extract_guarantees_from_file(file)
        if data:
            results.append(data)
            total_eur += data["garantia_eur"]
    
    # Generate Output
    output_data = {
        "garantias": results,
        "total_contratos": len(results),
        "suma_total_eur": total_eur
    }
    
    # Write JSON
    json_path = "guarantees_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"JSON written to {json_path}")
    
    # Write Markdown Table
    md_path = "guarantees_table.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Tabla de Garantías\n\n")
        f.write("| # | Contrato | Garantía (EUR) | Archivo |\n")
        f.write("|---|----------|----------------|---------|\n")
        
        for i, item in enumerate(results, 1):
            # Format eur back to spanish
            eur_fmt = f"{item['garantia_eur']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            f.write(f"| {i} | {item['contrato']} | {eur_fmt} | {item['archivo']} |\n")
            
        total_fmt = f"{total_eur:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        f.write(f"\n**Total Acumulado:** {total_fmt} EUR\n")
    print(f"Markdown table written to {md_path}")

if __name__ == "__main__":
    main()
