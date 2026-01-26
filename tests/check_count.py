import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from src.utils.vectorstore import get_document_count
print(f"--- CURRENT COUNT: {get_document_count()} ---")
