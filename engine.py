import os
import database
import phoenix as px
from flashrank import Ranker, RerankRequest
from langchain_ollama import ChatOllama
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

# --- 1. SETUP MONITORING PHOENIX (ANTI-BENTROK) ---

# Cek apakah sudah ada sesi Phoenix yang aktif
session = px.active_session()

if session is None:
    try:
        # Jika belum ada sesi, coba nyalakan Phoenix
        session = px.launch_app()
        print(f"🚀 Phoenix Dashboard baru aktif di: {session.url}")
    except Exception:
        # Jika gagal (misal port terkunci tapi session terdeteksi None), paksa konek ke port 6006
        print("⚠️ Port sibuk, mencoba menghubungkan ke Client yang sudah ada...")
        session = px.Client(endpoint="http://127.0.0.1:6006")
else:
    print(f"✅ Menggunakan Phoenix session yang sudah berjalan.")

# Registrasi Tracer (Gunakan try-except agar tidak double instrumentasi)
try:
    tracer_provider = register(
        project_name="default",
        endpoint="http://localhost:6006/v1/traces",
        auto_instrument=True
    )
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
    print("✅ Tracing Phoenix Berhasil Dikonfigurasi.")
except Exception:
    print("ℹ️ Tracing sudah aktif sebelumnya.")

# --- 2. CLASS RAG ENGINE ---

class RAGEngine:
    def __init__(self):
        print("🔄 Menginisialisasi RAG Engine...")
        
        # Memuat database dari database.py
        self.vectorstore = database.load_vectorstore()
        self.docstore = database.load_docstore()
        
        # Inisialisasi LLM Llama 3.2 3B
        self.llm = ChatOllama(model="llama3.2:3b", temperature=0)
        
        # Inisialisasi Re-ranker (FlashRank)
        self.ranker = Ranker()
        print("✅ RAG Engine Ready!")

    def generate_response(self, query):
        # 1. RETRIEVAL (Mencari 10 dokumen)
        docs = self.vectorstore.similarity_search_with_score(query, k=10)
        
        # 2. DATA PREPARATION
        passages = []
        for doc, score in docs:
            doc_id = doc.metadata.get("doc_id")
            info = self.docstore.get(doc_id)
            if info:
                passages.append({
                    "id": doc_id,
                    "text": info['content'],
                    "meta": {"source": info['source']}
                })

        if not passages:
            return "Maaf, saya tidak menemukan informasi terkait dalam dokumen.", []

        # 3. RE-RANKING (Menyaring menjadi 3 terbaik)
        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)
        top_3 = results[:3]

        # 4. CONSTRUCT CONTEXT & SOURCES
        context_text = "\n\n".join([
            f"Sumber: {r['meta']['source']}\nIsi: {r['text']}" 
            for r in top_3
        ])
        
        sources = list(set([r['meta']['source'] for r in top_3]))

        # 5. PROMPT TEMPLATE
        prompt = f"""
        Anda adalah asisten ahli PT. Aquatek Engineering. 
        Jawablah pertanyaan hanya berdasarkan KONTEKS yang diberikan.
        Jika informasi tidak ada dalam KONTEKS, katakan Anda tidak tahu secara sopan.
        
        KONTEKS:
        {context_text}
        
        PERTANYAAN: {query}
        
        JAWABAN:
        """

        # 6. GENERATION
        response = self.llm.invoke(prompt)
        
        return response.content, sources