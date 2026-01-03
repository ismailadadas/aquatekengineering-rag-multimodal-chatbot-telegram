import os
import database
import phoenix as px
from flashrank import Ranker, RerankRequest
from langchain_ollama import ChatOllama
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

# --- 1. SETUP MONITORING PHOENIX (OTEL VERSION) ---

# Meluncurkan server Phoenix secara otomatis jika belum aktif
if not px.active_session():
    session = px.launch_app()
    print(f"🚀 Phoenix Dashboard aktif di: {session.url}")
else:
    print("✅ Phoenix session sudah berjalan.")

# Registrasi Tracer ke Project "default" sesuai instruksi dashboard
tracer_provider = register(
    project_name="default",
    endpoint="http://localhost:6006/v1/traces",
    auto_instrument=True
)

# Mengaktifkan instrumen LangChain agar tercatat di dashboard
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
print("✅ Tracing Phoenix Berhasil Dikonfigurasi.")

# --- 2. CLASS RAG ENGINE ---

class RAGEngine:
    def __init__(self):
        print("🔄 Menginisialisasi RAG Engine...")
        
        # Memuat database dari database.py
        self.vectorstore = database.load_vectorstore()
        self.docstore = database.load_docstore()
        
        # Inisialisasi LLM: Llama 3.2 3B (GPU GTX 1660 Super)
        self.llm = ChatOllama(
            model="llama3.2:3b", 
            num_gpu=1, 
            temperature=0
        )
        
        # Inisialisasi Re-ranker (Sesuai Diagram Skripsi)
        self.ranker = Ranker(
            model_name="ms-marco-MiniLM-L-12-v2", 
            cache_dir="./storage/flashrank"
        )

    def generate_response(self, query):
        """
        Alur: Retrieval -> Re-ranking -> Generation
        Seluruh proses ini akan otomatis muncul di menu 'Traces' di Phoenix
        """
        
        # 1. RETRIEVAL: Mencari 10 dokumen kandidat
        docs = self.vectorstore.similarity_search_with_score(query, k=10)
        
        # 2. DATA PREPARATION: Mengambil teks asli
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

        # 3. RE-RANKING: Mendapatkan Top 3 Contexts (Sesuai Diagram)
        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)
        top_3 = results[:3]

        # 4. PROMPT TEMPLATE
        context_text = "\n\n".join([
            f"Sumber: {r['meta']['source']}\nIsi: {r['text']}" 
            for r in top_3
        ])
        
        prompt = f"""
        Anda adalah asisten ahli PT. Aquatek Engineering. 
        Jawablah pertanyaan hanya berdasarkan KONTEKS yang diberikan.
        Jika informasi tidak ada, katakan Anda tidak tahu.
        
        KONTEKS:
        {context_text}
        
        PERTANYAAN: {query}
        
        JAWABAN:
        """

        # 5. GENERATION: Mendapatkan jawaban dari model Llama
        response = self.llm.invoke(prompt)
        
        # Mengambil daftar sumber unik
        sources = list(set([r['meta']['source'] for r in top_3]))
        
        return response.content, sources

if __name__ == "__main__":
    engine = RAGEngine()
    print("Engine siap digunakan.")