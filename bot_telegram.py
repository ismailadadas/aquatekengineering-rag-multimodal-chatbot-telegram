import os
import logging
import re
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from engine import RAGEngine

# --- 1. LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 2. KONFIGURASI ---
TOKEN_TELEGRAM = "8231767796:AAH8hH-ezfs6ubjHu6g-pDl5t7Nw8lsPVio"
DATA_FOLDER = "./data"

try:
    engine = RAGEngine()
    print("✅ RAG Engine Ready!")
except Exception as e:
    print(f"❌ Gagal memuat Engine: {e}")

def clean_for_html(text):
    """Membersihkan tag ilegal agar Telegram tidak error"""
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("&lt;pre&gt;", "<pre>").replace("&lt;/pre&gt;", "</pre>")
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    return text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    
    await update.message.reply_text("🔎 Sedang menganalisis dokumen...")

    try:
        # 1. Ambil Jawaban dan Daftar Sumber dari Engine
        answer, sources = engine.generate_response(user_query)
        
        # 2. Format Jawaban untuk Tabel (menggunakan <pre> agar rapi)
        if "|" in answer:
            formatted_answer = f"<b>Jawaban:</b>\n<pre>{answer}</pre>"
        else:
            formatted_answer = f"<b>Jawaban:</b>\n{answer}"
            
        # 3. Bersihkan hasil akhir sebelum dikirim ke Telegram
        final_text = clean_for_html(f"{formatted_answer}\n\n<b>📚 Sumber:</b> {', '.join(sources)}")
        
        # Kirim respons teks
        await update.message.reply_text(final_text, parse_mode=ParseMode.HTML)

        # --- 4. LOGIKA KIRIM GAMBAR SECARA GENERAL (FIXED) ---
        all_files = os.listdir(DATA_FOLDER)
        found_images = []

        # Mencocokkan file di folder data dengan daftar 'sources' yang diberikan Engine
        for source_path in sources:
            # Mengambil nama file saja (menghilangkan folder path jika ada)
            clean_source_name = os.path.basename(source_path).lower()
            
            for file_name in all_files:
                file_lower = file_name.lower()
                # Cek jika nama file di folder data muncul dalam referensi sumber AI
                if file_lower in clean_source_name and file_lower.endswith(('.png', '.jpg', '.jpeg')):
                    if file_name not in found_images:
                        found_images.append(file_name)

        # Mengirimkan lampiran gambar yang relevan secara otomatis
        for img_name in found_images:
            file_path = os.path.join(DATA_FOLDER, img_name)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo, 
                        caption=f"🖼️ Lampiran Referensi: {img_name}"
                    )

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"Terjadi kendala teknis saat memproses permintaan.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()