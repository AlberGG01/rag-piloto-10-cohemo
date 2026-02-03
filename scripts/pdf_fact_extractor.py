# -*- coding: utf-8 -*-
"""
Extraer Hechos "Forense" de PDFs para Ground Truth V4.
Usa pdfplumber para leer texto crudo e identificar datos clave.
"""
import pdfplumber
import re
import os
from pathlib import Path
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("FACT_EXTRACTOR")

DATA_DIR = Path("data/contracts")

def extract_facts_from_pdf(pdf_path):
    facts = {
        "filename": pdf_path.name,
        "contrato_id": "N/A",
        "importe_total": "N/A",
        "fecha_fin": "N/A",
        "empresa": "N/A",
        "avales": [],
        "normas": [],
        "penalizaciones": []
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            
            # 1. ID Contrato (CON_..., SER_..., SUM_..., LIC_...)
            match_id = re.search(r'((?:CON|SER|SUM|LIC)_\d{4}_\d{3})', text)
            if match_id:
                facts["contrato_id"] = match_id.group(1)
            
            # 2. Importe Total
            # Buscar patrones con EUR o €
            matches_eur = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*(?:EUR|€)', text)
            if matches_eur:
                # Asumimos que el mayor importe suele ser el total, o buscamos "Importe total"
                # Simple heuristica: coger el mayor numéricamente
                try:
                    vals = []
                    for m in matches_eur:
                        clean = m.replace(".", "").replace(",", ".")
                        vals.append((float(clean), m))
                    vals.sort(key=lambda x: x[0], reverse=True)
                    facts["importe_total"] = f"{vals[0][1]} EUR"
                except:
                    facts["importe_total"] = str(matches_eur)
            
            # 3. Fecha Fin / Plazo
            # Buscamos "Plazo de ejecución:", "hasta el", text dates
            dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', text)
            if dates:
                # Heuristica debil: la ultima fecha suele ser fin, pero mejor buscar contexto
                facts["fecha_fin"] = f"Fechas encontradas: {dates}"
                
            # 4. Avales
            if "aval" in text.lower() or "garantía" in text.lower():
                # Extract context around "aval"
                avales_ctx = []
                iter = re.finditer(r"(aval|garantía)[^.]*?(\d[\d\.,]*\s*(?:EUR|€))", text, re.IGNORECASE)
                for m in iter:
                    avales_ctx.append(m.group(0).strip())
                facts["avales"] = avales_ctx
            
            # 5. Normas (ISO, MIL, STANAG, PECAL)
            normas = re.findall(r'(ISO\s?\d+|MIL-[A-Z]+-\d+|STANAG\s?\d+|PECAL\s?\d+)', text)
            facts["normas"] = list(set(normas))

            # 6. Banco ING check
            if "ING Bank" in text:
                facts["banco_ing"] = True
            else:
                facts["banco_ing"] = False
                
    except Exception as e:
        logger.error(f"Error leyendo {pdf_path.name}: {e}")
        
    return facts

def main():
    print("🔎 EXTRAYENDO HECHOS DE PDFs...")
    files = list(DATA_DIR.glob("*.pdf"))
    all_facts = []
    
    for f in files:
        facts = extract_facts_from_pdf(f)
        all_facts.append(facts)
        
    # Imprimir Reporte Forense
    print("-" * 60)
    for f in all_facts:
        print(f"📄 {f['filename']} ({f['contrato_id']})")
        print(f"   💰 Importe: {f['importe_total']}")
        print(f"   📅 Fechas: {f['fecha_fin']}")
        print(f"   🛡️ Avales: {f['avales']}")
        print(f"   📜 Normas: {f['normas']}")
        print(f"   🏦 ING: {'SÍ' if f.get('banco_ing') else 'No'}")
        print("-" * 60)

if __name__ == "__main__":
    main()
