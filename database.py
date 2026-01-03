import pickle
import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# Lokasi penyimpanan database
CHROMA_PATH = "./storage/chroma_db"
PKL_PATH = "./storage/docstore.pkl"

def load_vectorstore():
    """Memuat database vektor untuk pencarian kemiripan teks"""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(
        collection_name="skripsi_multimodal", 
        embedding_function=embeddings, 
        persist_directory=CHROMA_PATH
    )

def load_docstore():
    """Memuat database dokumen asli dari file Pickle (.pkl)"""
    if not os.path.exists(PKL_PATH):
        return {}
    with open(PKL_PATH, "rb") as f:
        data = pickle.load(f)
        # Mengubah list menjadi dictionary {doc_id: {content, source}} agar pencarian cepat
        return {d['doc_id']: {'content': d['content'], 'source': d['source']} for d in data}