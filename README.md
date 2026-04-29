Arsitektur Sistem Multimodal RAG dengan Multi Vector Retrieval & Monitoring Arize Phoenix Studi Kasus PT. Aquatek Engineering

<img width="1012" height="741" alt="image" src="https://github.com/user-attachments/assets/793b4702-0a49-4b77-b3fd-fc9fa803af35" />


⚠️ Requirement 

Python 3.10.11

Ollama


🚀 Multimodal RAG Installation Guide
Ikuti langkah cepat ini untuk menjalankan proyek di PC lokal:

1. Persiapan Environment
   
Bash

# Clone repository
git clone https://github.com/ismailadadas/aquatekengineering-rag-multimodal-chatbot-telegram


# Buat virtual environment
python -m venv venv

# Aktivasi venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Library

pip install langchain langchain-community langchain-ollama langchain-chroma docling flashrank python-telegram-bot


2. Persiapan Model (Ollama)
   
Pastikan Ollama sudah terinstall dan jalankan:

Bash

ollama pull nomic-embed-text
ollama pull llama3.2:1b


3. Cara Menjalankan
Buat Folder dan Letakkan data: Masukkan file (PDF, Gambar, CSV, Docx dll) ke folder ./data.

Indexing: Jalankan python indexing.py (Gunakan Run as Administrator jika di Windows).

Konfigurasi Bot: Masukkan Token BotFather ke bot_telegram.py.

Run Bot: Jalankan python bot_telegram.py.
