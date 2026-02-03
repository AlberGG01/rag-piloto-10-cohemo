"""
Limpia archivos innecesarios antes de subir a GitHub
"""

import os
import shutil

def clean_project():
    """Elimina archivos temporales, logs, caché"""
    
    print("="*60)
    print("🧹 LIMPIANDO PROYECTO PARA GITHUB")
    print("="*60)
    
    items_to_remove = [
        # Caché Python
        '__pycache__',
        '*.pyc',
        '.pytest_cache',
        
        # Logs y reportes temporales
        'logs/*.log',
        'logs/*.txt',
        'evaluation_report_*.md',
        'walkthrough.md',
        
        # Backups (guardar en otro lado si son importantes)
        'backups/',
        
        # VectorDB (se regenera con init_vectorstore.py)
        'chroma_db/',
        
        # Archivos de IDE
        '.vscode/',
        '.idea/',
        '*.swp',
        '*.swo',
        
        # Variables de entorno (NUNCA subir .env con API keys)
        '.env',  # Solo .env.example debe ir
        
        # Archivos de sistema
        '.DS_Store',
        'Thumbs.db'
    ]
    
    removed = []
    kept_important = []
    
    for pattern in items_to_remove:
        if '*' in pattern:
            # Es un patrón glob
            import glob
            for file in glob.glob(pattern, recursive=True):
                try:
                    os.remove(file)
                    removed.append(file)
                except:
                    pass
        else:
            # Es un directorio o archivo específico
            if os.path.exists(pattern):
                if pattern in ['data/contracts/', 'data/normalized/']:
                    kept_important.append(f"Manteniendo: {pattern}")
                    continue
                
                try:
                    if os.path.isdir(pattern):
                        shutil.rmtree(pattern)
                    else:
                        os.remove(pattern)
                    removed.append(pattern)
                except Exception as e:
                    print(f"⚠️  No se pudo eliminar {pattern}: {e}")
    
    # Crear directorios vacíos necesarios
    os.makedirs('logs', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    
    # Crear .gitkeep para mantener estructura
    for dir in ['logs', 'backups']:
        with open(f'{dir}/.gitkeep', 'w') as f:
            f.write('')
    
    print(f"\n✅ Eliminados {len(removed)} archivos/carpetas:")
    for item in removed[:10]:  # Mostrar primeros 10
        print(f"   - {item}")
    
    if len(removed) > 10:
        print(f"   ... y {len(removed) - 10} más")
    
    print(f"\n📦 Mantenidos archivos importantes:")
    print(f"   - data/contracts/ (PDFs originales)")
    print(f"   - data/normalized/ (Markdown procesados)")
    print(f"   - src/ (código fuente)")
    print(f"   - tests/ (Golden Dataset)")
    
    print("\n" + "="*60)
    print("✅ Limpieza completada. Proyecto listo para GitHub.")
    print("="*60)

if __name__ == "__main__":
    # Confirmar antes de ejecutar
    response = input("⚠️  Esto eliminará archivos. ¿Continuar? (s/n): ")
    if response.lower() == 's':
        clean_project()
    else:
        print("❌ Cancelado")
