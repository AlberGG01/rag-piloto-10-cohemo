
import sys
import os

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print("Attempting to import src.utils.vectorstore...")

import src.utils.vectorstore
print("✅ Import successful!")
