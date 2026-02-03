import pdfplumber
import re
from pathlib import Path

DATA_DIR = Path("data/contracts")

def forensic_search():
    files = list(DATA_DIR.glob("*.pdf"))
    
    print("🕵️ BUSQUEDA FORENSE DETALLADA")
    
    for f in files:
        text = ""
        try:
            with pdfplumber.open(f) as pdf:
                for p in pdf.pages:
                    text += p.extract_text() + "\n"
        except:
            continue
            
        findings = []
        
        # Check UTE
        if "UTE" in text:
            match = re.search(r"(UTE\s+[A-Z][\w\s]+)", text)
            if match:
                findings.append(f"UTE: {match.group(1)[:50]}")
                
        # Check Limpieza
        if "limpieza" in text.lower():
            # Look for context
            ctx = re.search(r"limpieza.{0,50}(\d+[\.,]\d+)", text.lower())
            if ctx:
                findings.append(f"Precio Limpieza?: {ctx.group(1)}")

        # Check Penalidad > 10000
        if "penalida" in text.lower():
             # Look for big numbers near penalidad
             matches = re.findall(r"penali[^\.]*?(\d{1,3}(?:\.\d{3})*)", text.lower())
             for m in matches:
                 try:
                    val = float(m.replace(".",""))
                    if val >= 10000:
                        findings.append(f"Penalidad HIGH: {m}")
                 except: pass

        # Check ISO 9001
        if "9001" in text:
            findings.append("ISO 9001 Found")
            
        # Check Responsable
        if "responsable" in text.lower():
            match = re.search(r"responsable (?:técnico|del contrato).{0,30}?([A-Z][a-z]+ [A-Z][a-z]+)", text)
            if match:
                 findings.append(f"Responsable: {match.group(1)}")
                 
        if findings:
            print(f"📄 {f.name}: {findings}")

if __name__ == "__main__":
    forensic_search()
