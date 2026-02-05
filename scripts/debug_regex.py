
import re
import os

file_path = "d:/Dev/projects/defense_contracts_system/data/normalized/CON_2024_020_Fusiles_Asalto_HK416_normalized.md"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Content length: {len(content)}")

patterns = [
    r"\|\s*Garantía definitiva\s*\|.*?\|\s*([\d\.]+,\d{2})\s*(?:EUR|€|euros)\s*\|",
    r"Garantía definitiva:?\*\*?\s*([\d\.]+,\d{2})\s*(?:EUR|€|euros)",
    r"\*\*Garantía definitiva:?\*\*?\s*([\d\.]+,\d{2})\s*(?:EUR|€|euros)",
    r"garantía definitiva.*?asciende.*?a\s+([\d\.]+,\d{2})\s*(?:€|euros|EUR)",
    r"importe.*?garantía definitiva.*?([\d\.]+,\d{2})\s*(?:€|euros|EUR)",
    r"Garantía definitiva.{1,100}?\s+([\d\.]+,\d{2})\s*(?:EUR|€|euros)"
]

print(f"Testing {len(patterns)} patterns on CON_2024_020...")

for i, p in enumerate(patterns):
    match = re.search(p, content, re.IGNORECASE)
    if match:
        print(f"MATCH Pattern {i}: {match.group(1)}")
    else:
        print(f"NO MATCH Pattern {i}")
        
# Also check if text exists
idx = content.find("224.000,00")
print(f"224.000,00 found at index: {idx}")

