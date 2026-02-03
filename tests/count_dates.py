import re
from pathlib import Path

results = []
for f in Path('data/normalized').glob('*.md'):
    content = f.read_text(encoding='utf-8')
    dates = len(re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', content))
    contract_id = f.stem.split('_')[:3]  # CON_2024_009
    contract_id = '_'.join(contract_id)
    results.append((contract_id, dates))

results.sort(key=lambda x: x[1], reverse=True)

print("\n🏆 TOP 10 CONTRATOS POR DENSIDAD DE FECHAS:")
for i, (name, count) in enumerate(results[:10], 1):
    print(f"{i:2}. {name:20} {count:3} fechas")
