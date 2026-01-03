import os
import uuid
import pickle
# Import LangChain secara langsung ke komponen inti
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from docling.document_converter import DocumentConverter

# --- SETUP DIREKTORI ---
DATADIR = "./data"
STORAGE = "./storage"
CHROMA_PATH = os.path.join(STORAGE, "chroma_db")
PKL_PATH = os.path.join(STORAGE, "docstore.pkl")

os.makedirs(STORAGE, exist_ok=True)

# 1. Inisialisasi Model Embedding
print("🔄 Inisialisasi model embedding...")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 2. Inisialisasi Database Vektor (ChromaDB)
vectorstore = Chroma(
    collection_name="skripsi_multimodal",
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH
)

# 3. Inisialisasi Pengubah Dokumen (Docling)
converter = DocumentConverter()

def mulai_indexing():
    if not os.path.exists(DATADIR) or not os.listdir(DATADIR):
        print("⚠️ Folder 'data' kosong! Masukkan file PDF/Gambar dulu.")
        return

    all_data_asli = []
    print(f"\n=== Memulai Indexing dari folder {DATADIR} ===")

    for file_name in os.listdir(DATADIR):
        if file_name.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.xlsx', '.csv', '.docx')):
            file_path = os.path.join(DATADIR, file_name)
            print(f"⏳ Memproses: {file_name}")
            
            try:
                # Parsing Multimodal dengan Docling
                result = converter.convert(file_path)
                md_text = result.document.export_to_markdown()
                
                # Buat ID unik untuk sinkronisasi
                doc_id = str(uuid.uuid4())
                
                # Simpan Summary ke ChromaDB
                summary = md_text[:1000] # Ambil 1000 karakter pertama
                vectorstore.add_texts(
                    texts=[summary],
                    metadatas=[{"doc_id": doc_id, "source": file_name}]
                )
                
                # Simpan Data Asli ke list untuk di-pickle (BaseStore)
                all_data_asli.append({
                    "doc_id": doc_id,
                    "content": md_text,
                    "source": file_name
                })
                print(f" ✅ {file_name} berhasil di-indeks.")
                
            except Exception as e:
                print(f" ❌ Gagal memproses {file_name}: {e}")

    # Simpan BaseStore secara permanen
    with open(PKL_PATH, "wb") as f:
        pickle.dump(all_data_asli, f)
    
    print(f"\n=== SELESAI! {len(all_data_asli)} dokumen tersimpan di {STORAGE} ===")

if __name__ == "__main__":
    mulai_indexing()