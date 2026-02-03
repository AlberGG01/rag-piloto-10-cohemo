import os
from huggingface_hub import hf_hub_download
import shutil

REPO_ID = "bartowski/Llama-3.2-3B-Instruct-GGUF"
FILENAME = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
TARGET_DIR = "./models"
TARGET_FILENAME = "llama-3.2-3b-instruct.Q4_K_M.gguf"

def download_model():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    
    print(f"Downloading {FILENAME} from {REPO_ID}...")
    try:
        file_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME, local_dir=TARGET_DIR)
        
        # Rename to match .env expectation if necessary (though strictly not required on Windows, good for consistency)
        target_path = os.path.join(TARGET_DIR, TARGET_FILENAME)
        if os.path.abspath(file_path) != os.path.abspath(target_path):
            print(f"Renaming {file_path} to {target_path}...")
            if os.path.exists(target_path):
                os.remove(target_path)
            os.rename(file_path, target_path)
            
        print(f"Success! Model saved to {target_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")

if __name__ == "__main__":
    download_model()
