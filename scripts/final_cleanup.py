import os
import shutil
import glob

def safe_move(pattern, dest_dir):
    for file in glob.glob(pattern):
        if os.path.basename(file) == 'requirements.txt':
            continue
        try:
            shutil.move(file, dest_dir)
            print(f"Moved: {file}")
        except Exception as e:
            print(f"Error moving {file}: {e}")

if not os.path.exists('_legacy'):
    os.makedirs('_legacy')

patterns = [
    'init_vectorstore.py',
    'normalize_all.py',
    'debug_chroma.py',
    'download_models.py',
    '*.txt',
    '*.bak',
    'pending_review.json',
    'evaluation_report.md',
    'final_diagnosis.txt'
]

for p in patterns:
    safe_move(p, '_legacy')

# Clear logs folder safely
if os.path.exists('logs'):
    shutil.rmtree('logs')
os.makedirs('logs')
with open('logs/.gitkeep', 'w') as f:
    f.write('')
print("Logs folder reset.")
