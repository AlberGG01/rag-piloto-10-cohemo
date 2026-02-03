"""
Busca el CIF B-55667788 directamente en los archivos .md normalizados
"""

import os
import sys

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def search_cif_in_normalized_docs():
    """Busca CIF en todos los .md normalizados"""
    
    normalized_dir = os.path.join(project_root, "data", "normalized")
    target_cif = "B-55667788"
    
    print("="*60)
    print(f"🔍 BUSCANDO CIF: {target_cif}")
    print(f"   Directorio: {normalized_dir}")
    print("="*60)
    
    if not os.path.exists(normalized_dir):
        print(f"🚨 ERROR: No existe el directorio {normalized_dir}")
        return []

    found_files = []
    
    # Buscar en todos los .md
    for root, dirs, files in os.walk(normalized_dir):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Buscar el CIF exacto
                        if target_cif in content:
                            print(f"\n✅ ENCONTRADO en: {file}")
                            
                            # Mostrar contexto (líneas alrededor)
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if target_cif in line:
                                    print(f"\n  Contexto (líneas {max(0, i-2)} a {i+2}):")
                                    for j in range(max(0, i-2), min(len(lines), i+3)):
                                        prefix = ">>>" if j == i else "   "
                                        print(f"  {prefix} {lines[j]}")
                            
                            found_files.append(file)
                except Exception as e:
                    print(f"⚠️ Error leyendo {file}: {e}")
    
    print("\n" + "="*60)
    if found_files:
        print(f"📊 RESUMEN: CIF encontrado en {len(found_files)} archivo(s)")
    else:
        print(f"🚨 CRÍTICO: CIF '{target_cif}' NO EXISTE en ningún .md normalizado")
        print(f"   Posibles causas:")
        print(f"   1. El normalizador omitió el CIF durante la conversión PDF→MD")
        print(f"   2. El archivo CON_2024_004 no se normalizó correctamente")
        print(f"   3. El CIF tiene formato diferente en el documento original")
    
    return found_files

if __name__ == "__main__":
    search_cif_in_normalized_docs()
