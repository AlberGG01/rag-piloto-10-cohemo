
try:
    import chromadb
    print("✅ ChromeDB imported successfully")
    print(f"Version: {chromadb.__version__}")
except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ Exception: {e}")

import sys
print(f"Python executable: {sys.executable}")
