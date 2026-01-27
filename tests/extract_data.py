# -*- coding: utf-8 -*-
"""
Extrae datos verificados de todos los documentos normalizados
"""

import os
import re
from pathlib import Path

docs_dir = Path(__file__).parent.parent / "data" / "normalized"

avales = []
importes = []
fechas_vencimiento = []
clasificaciones = []

for doc_file in sorted(docs_dir.glob("*.md")):
    with open(doc_file, 'r', encoding='utf-8') as f:
        content = f.read()
        doc_name = doc_file.stem[:16]  # Primeros 16 chars del nombre
        
        # Extraer aval
        aval_match = re.search(r'Garantía definitiva:\s*([0-9.,]+)\s*EUR', content)
        if aval_match:
            aval_str = aval_match.group(1).replace('.', '').replace(',', '.')
            aval_val = float(aval_str)
            
            # Extraer entidad avalista
            entidad_match = re.search(r'Entidad avalista:\s*(.+)', content)
            entidad = entidad_match.group(1).strip() if entidad_match else "N/A"
            
            avales.append((doc_name, aval_val, entidad))
        
        # Extraer importe total
        importe_match = re.search(r'Importe total \(IVA incluido\):\s*([0-9.,]+)\s*EUR', content)
        if importe_match:
            importe_str = importe_match.group(1).replace('.', '').replace(',', '.')
            importe_val = float(importe_str)
            importes.append((doc_name, importe_val))
        
        # Extraer fecha vencimiento aval
        venc_match = re.search(r'Fecha de vencimiento del aval:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})', content)
        if venc_match:
            fecha_venc = venc_match.group(1)
            fechas_vencimiento.append((doc_name, fecha_venc))
        
        # Extraer clasificación
        clas_match = re.search(r'Clasificación de seguridad:\s*(\w+)', content)
        if clas_match:
            clasificacion = clas_match.group(1)
            clasificaciones.append((doc_name, clasificacion))

# RESULTADOS
print("="*80)
print("EXTRACCION COMPLETA DE DATOS")
print("="*80)

print("\n### AGG001: AVALES BANCARIOS")
print("-" * 80)
total_avales = 0
for doc, aval, entidad in sorted(avales):
    print(f"{doc}: {aval:,.2f} EUR - {entidad}")
    total_avales += aval
print(f"\n**TOTAL AVALES: {total_avales:,.2f} EUR**\n")

print("\n### CMP001: TOP 5 CONTRATOS POR IMPORTE")
print("-" * 80)
importes_sorted = sorted(importes, key=lambda x: x[1], reverse=True)
for i, (doc, importe) in enumerate(importes_sorted[:5], 1):
    print(f"{i}. {doc}: {importe:,.2f} EUR")

print("\n### TMP002: AVALES QUE VENCEN EN 2027")
print("-" * 80)
avales_2027 = [(doc, fecha) for doc, fecha in fechas_vencimiento if '/2027' in fecha]
avales_2027_sorted = sorted(avales_2027, key=lambda x: x[1].split('/')[1] + x[1].split('/')[0])
for doc, fecha in avales_2027_sorted:
    print(f"{doc}: {fecha}")
if avales_2027_sorted:
    print(f"\n**MÁS PRONTO: {avales_2027_sorted[0][0]} - {avales_2027_sorted[0][1]}**")

print("\n### FLT001: SECRETO Y > 20M EUR")
print("-" * 80)
for doc, clasificacion in clasificaciones:
    if clasificacion == "SECRETO":
        # Buscar importe de este doc
        doc_importe = next((imp for d, imp in importes if d == doc), None)
        if doc_importe and doc_importe > 20000000:
            print(f"✓ {doc}: {clasificacion} + {doc_importe:,.2f} EUR")

print("\n" + "="*80)
