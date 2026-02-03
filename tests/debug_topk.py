
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.hybrid_search import hybrid_search

question = "¿Qué contratos ISO Y STANAG?"

# Con top_k=30
print(f"=== ANÁLISIS TOP-K: '{question}' ===")
print(f"\n--- Con top_k=30 (BASELINE) ---")
chunks_30 = hybrid_search(question, top_k=30)

iso_count = 0
stanag_count = 0
both_count = 0

for i, c in enumerate(chunks_30):
    text = c['contenido']
    has_iso = "ISO" in text
    has_stanag = "STANAG" in text
    has_both = has_iso and has_stanag
    
    label = ""
    if has_both:
        label = "✅ AMBOS"
        both_count += 1
    elif has_iso:
        label = "⚠️ SOLO ISO"
        iso_count += 1
    elif has_stanag:
        label = "⚠️ SOLO STANAG"
        stanag_count += 1
        
    if label:
        print(f"  Chunk #{i}: {label} ({c['metadata'].get('archivo', 'N/A')})")

print(f"TOTAL RELEVANTE (Top 30): ISO={iso_count}, STANAG={stanag_count}, AMBOS={both_count}")


# Con top_k=10
print(f"\n--- Con top_k=10 (STREAMING) ---")
chunks_10 = hybrid_search(question, top_k=10)

iso_count_10 = 0
stanag_count_10 = 0
both_count_10 = 0

for i, c in enumerate(chunks_10):
    text = c['contenido']
    has_iso = "ISO" in text
    has_stanag = "STANAG" in text
    has_both = has_iso and has_stanag
    
    label = ""
    if has_both:
        label = "✅ AMBOS"
        both_count_10 += 1
    elif has_iso:
        label = "⚠️ SOLO ISO"
        iso_count_10 += 1
    elif has_stanag:
        label = "⚠️ SOLO STANAG"
        stanag_count_10 += 1
        
    if label:
        print(f"  Chunk #{i}: {label} ({c['metadata'].get('archivo', 'N/A')})")

print(f"TOTAL RELEVANTE (Top 10): ISO={iso_count_10}, STANAG={stanag_count_10}, AMBOS={both_count_10}")

if both_count > 0 and both_count_10 == 0:
    print("\n❌ CRITICAL: Top-K 10 perdió los chunks de intersección!")
elif both_count_10 > 0:
    print("\n✅ Top-K 10 mantiene la intersección.")
else:
    print("\n⚠️ Ninguna configuración encontró intersección clara.")
