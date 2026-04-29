# 🤖 Multimodal RAG Chatbot for Industrial Safety (MSDS)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Model](https://img.shields.io/badge/Model-Llama_3.2_Vision-orange.svg)](https://ollama.com/)
[![RAG](https://img.shields.io/badge/Technique-Advanced_RAG-green.svg)](https://langchain.com/)

### 📄 Publikasi
Proyek ini merupakan bagian dari penelitian skripsi di BINUS University.

Sistem ini adalah solusi chatbot cerdas berbasis **Advanced Retrieval-Augmented Generation (RAG)** yang dirancang untuk memberikan akses informasi presisi terhadap dokumen **Material Safety Data Sheets (MSDS)** pada PT Aquatek Engineering.

<img width="1025" height="649" alt="Screenshot 2026-04-29 221105" src="https://github.com/user-attachments/assets/a7d1a2a2-322b-4fef-a951-7f39c5c92a50" />

Proyek ini berfokus pada penyelesaian masalah **"hallucination"** pada AI konvensional saat menangani data teknis kritis dalam lingkungan industri.

---

## 🌟 Fitur Utama

- **Multimodal Extraction**  
  Mengekstraksi data dari **tabel kompleks** secara akurat menggunakan **Docling** (layout-aware parsing).

- **Visual Reasoning**  
  Menggunakan **Llama 3.2 Vision** untuk memahami simbol piktogram bahaya GHS (*Global Harmonized System*).

- **Advanced Retrieval**  
  Optimasi pencarian menggunakan **FlashRank (Cross-Encoder Re-ranking)** untuk memastikan relevansi dokumen.

- **On-Premise Privacy**  
  Seluruh pemrosesan model berjalan lokal via **Ollama**, menjaga kerahasiaan data perusahaan.

- **Telegram Integration**  
  Akses informasi keselamatan kerja secara real-time bagi staf lapangan.

---

## 🛠️ Tech Stack

- **Core LLM:** Llama 3.2 3B-Vision (via Ollama)  
- **Embedding Model:** `nomic-embed-text-v1.5`  
- **Vector Database:** ChromaDB  
- **Orchestration:** LangChain / Python  
- **Reranker:** FlashRank  
- **Parsing Tool:** IBM Docling  

---

## 📊 Hasil Evaluasi

Pengujian dilakukan pada **50 Golden Datasets** dengan audit manual biner:

- **Accuracy Rate:** 82%  
- **Faithfulness (RAGAS):** 0.98 *(sangat sesuai dengan fakta dokumen)*  
- **Answer Relevance:** 0.76  
- **Performance:** Latency P50 sebesar **4.7 detik**

---

## 🚀 Panduan Instalasi & Penggunaan

### 1. Persiapan Model (Ollama)

Pastikan Ollama sudah terinstal, lalu unduh model berikut:

```bash
1. Pull 
ollama pull llama3.2-vision
ollama pull nomic-embed-text

2. Setup Project & Environment

Clone repository dan siapkan virtual environment:

git clone https://github.com/ismailadadas/aquatekengineering-rag-multimodal-chatbot-telegram.git
cd aquatekengineering-rag-multimodal-chatbot-telegram

python -m venv venv

# Mac/Linux
source venv/bin/activate  

# Windows
# venv\Scripts\activate  

pip install -r requirements.txt
3. Konfigurasi Bot

Buat file .env di root project:

TELEGRAM_BOT_TOKEN=masukkan_token_bot_anda_disini
4. Ingesti Data (Indexing)

Letakkan file PDF MSDS ke folder data/, lalu jalankan:

python indexing.py
5. Jalankan Chatbot

Setelah indexing selesai:

python bot_telegram.py<img width="1025" height="649" alt="Screenshot 2026-04-29 221105" src="https://github.com/user-attachments/assets/5e99096c-ea1c-4e81-b75a-d9310ee9470b" />
