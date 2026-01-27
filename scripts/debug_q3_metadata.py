import chromadb
from chromadb.config import Settings
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.config import VECTORSTORE_PATH, COLLECTION_NAME

def inspect_metadata():
    print(f"Connecting to ChromaDB at {VECTORSTORE_PATH}...")
    client = chromadb.PersistentClient(path=VECTORSTORE_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    
    # Target contract
    target_contract = "SER_2024_015"
    
    print(f"\nSearching for chunks belonging to contract containing: {target_contract}")
    
    # Get all chunks for this contract
    # We'll search by checking if 'archivo' or 'num_contrato' metadata contains the string
    # Since we can't do partial match easily in 'where' without specific knowledge, 
    # let's try to fetch a few and filter in python or use a broad query if possible.
    # But wait, we can just peek or use an empty query with a where clause if we know the exact field.
    # Let's assume 'num_contrato' is the field we want to check or 'archivo'.
    
    # Try fetching by filename (partial match not supported in standard where usually, but let's try to list all distinct 'archivo' first to be sure)
    
    # Peek to see structure
    peek = collection.peek(1)
    print("\nSample Metadata Structure:")
    print(peek['metadatas'][0])

    # Let's just get all items and filter python side to find our contract, 
    # efficient enough for 280 docs.
    all_data = collection.get(include=['metadatas'])
    
    found_chunks = []
    for meta in all_data['metadatas']:
        if target_contract in meta.get('archivo', '') or target_contract in meta.get('num_contrato', ''):
            found_chunks.append(meta)
    
    print(f"\nFound {len(found_chunks)} chunks for {target_contract}.")
    
    if found_chunks:
        print("\n--- Inspecting First 3 Chunks ---")
        for i, meta in enumerate(found_chunks[:3]):
            print(f"\nChunk {i+1}:")
            print(f"  Archivo: {meta.get('archivo')}")
            print(f"  Num Contrato: {meta.get('num_contrato')}")
            print(f"  Adjudicatario (Field exists?): {'adjudicatario' in meta}")
            print(f"  Adjudicatario Value: {meta.get('adjudicatario', 'N/A')}")
            print(f"  Tipo Seccion: {meta.get('tipo_seccion', 'N/A')}")

if __name__ == "__main__":
    inspect_metadata()
