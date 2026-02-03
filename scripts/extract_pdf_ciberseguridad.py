"""
Extrae texto crudo del PDF de Ciberseguridad
"""
import sys
import os
import re

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import pdfplumber
except ImportError:
    print("🚨 pdfplumber not installed. Please run: pip install pdfplumber")
    sys.exit(1)

def extract_pdf_text():
    """Extrae texto del PDF para verificar si el CIF está presente"""
    
    # Correct path found via find_by_name
    pdf_path = os.path.join(project_root, "data", "contracts", "CON_2024_004_Ciberseguridad_Infraestructuras.pdf")
    
    print("="*60)
    print(f"📄 EXTRAYENDO TEXTO DE: {pdf_path}")
    print("="*60)
    
    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            print(f"   Total páginas: {len(pdf.pages)}")
            
            target_cif_clean = "B55667788"
            target_cif_formatted = "B-55667788"
            found_any = False

            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                full_text += text
                
                # Buscar CIF en esta página
                if target_cif_formatted in text or target_cif_clean in text:
                    print(f"\n✅ CIF encontrado en PÁGINA {page_num}")
                    found_any = True
                    
                    # Mostrar contexto
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if target_cif_formatted in line or target_cif_clean in line:
                            print(f"\n  Contexto:")
                            for j in range(max(0, i-2), min(len(lines), i+3)):
                                prefix = ">>>" if j == i else "   "
                                print(f"    {prefix} {lines[j]}")
            
            if not found_any:
                 print("\n❌ CIF NO ENCONTRADO en el texto extraído del PDF.")

            # Buscar variantes
            cifs = re.findall(r'[A-Z]-?\d{8}', full_text)
            print(f"\n📊 Todos los CIFs encontrados en el PDF: {set(cifs)}")
            
    except Exception as e:
        print(f"🚨 Error procesando PDF: {e}")

if __name__ == "__main__":
    extract_pdf_text()
