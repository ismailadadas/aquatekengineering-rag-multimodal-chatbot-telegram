import os
import uuid
import pickle
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
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

# 4. Inisialisasi Text Splitter (Tahap Chunking)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", " ", ""]
)

def mulai_indexing():
    if not os.path.exists(DATADIR) or not os.listdir(DATADIR):
        print("⚠️ Folder 'data' kosong! Masukkan file PDF/Gambar dulu.")
        return

    all_data_asli = []
    print(f"\n=== Memulai Indexing Multimodal General dari folder {DATADIR} ===")

    # --- PROSES DATA LOADING ---
    for file_name in os.listdir(DATADIR):
        # Mendukung berbagai format file secara general
        if file_name.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.xlsx', '.csv', '.docx')):
            file_path = os.path.join(DATADIR, file_name)
            print(f"⏳ Memproses file: {file_name}")
            
            try:
                # --- TAHAP MULTIMODAL PARSING (DOCLING) ---
                result = converter.convert(file_path)
                md_text = result.document.export_to_markdown()
                
                # --- LOGIKA GENERAL: FILENAME AUGMENTATION ---
                # Menyisipkan nama file agar gambar/file apapun bisa dicari berdasarkan namanya
                full_text_with_meta = f"Nama File: {file_name}\nIsi Konten: {md_text}"
                
                # --- TAHAP CHUNKING ---
                chunks = text_splitter.split_text(full_text_with_meta)
                print(f"   🧩 Berhasil memecah menjadi {len(chunks)} chunks.")

                for chunk in chunks:
                    doc_id = str(uuid.uuid4())
                    
                    # --- TAHAP VECTORIZATION & INDEXING (CHROMADB) ---
                    vectorstore.add_texts(
                        texts=[chunk],
                        metadatas=[{"doc_id": doc_id, "source": file_name}]
                    )
                    
                    # --- SIMPAN KE DOCUMENT STORE (BASESTORE) ---
                    all_data_asli.append({
                        "doc_id": doc_id,
                        "content": chunk,
                        "source": file_name
                    })
                
                print(f" ✅ {file_name} selesai di-indeks.")
                
            except Exception as e:
                print(f" ❌ Gagal memproses {file_name}: {e}")

    # Simpan BaseStore (Pickle) secara permanen
    with open(PKL_PATH, "wb") as f:
        pickle.dump(all_data_asli, f)
    
    print(f"\n=== SELESAI! Total {len(all_data_asli)} chunks tersimpan di {STORAGE} ===")

if __name__ == "__main__":
    mulai_indexing()