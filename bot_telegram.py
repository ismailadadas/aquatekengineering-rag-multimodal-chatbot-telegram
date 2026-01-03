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
TOKEN_TELEGRAM = "TELEGRAM_BOT_TOKEN"
DATA_FOLDER = "./data"

try:
    engine = RAGEngine()
    print("✅ RAG Engine Ready!")
except Exception as e:
    print(f"❌ Gagal memuat Engine: {e}")

def clean_for_html(text):
    """Membersihkan tag ilegal agar Telegram tidak error"""
    # Menghapus tag komentar Docling seperti text = re.sub(r"", "", text)
    # Menghapus karakter < dan > yang bukan tag HTML resmi agar tidak error parse
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    # Mengembalikan tag yang kita butuhkan untuk tabel (pre dan b)
    text = text.replace("&lt;pre&gt;", "<pre>").replace("&lt;/pre&gt;", "</pre>")
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    return text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    query_lower = user_query.lower()
    
    await update.message.reply_text("🔎 Sedang menganalisis dokumen...")

    try:
        # 1. Ambil Jawaban dari AI
        answer, sources = engine.generate_response(user_query)
        
        # 2. Format Jawaban untuk Tabel
        if "|" in answer:
            formatted_answer = f"<b>Jawaban:</b>\n<pre>{answer}</pre>"
        else:
            formatted_answer = f"<b>Jawaban:</b>\n{answer}"
            
        # 3. Bersihkan hasil akhir sebelum dikirim
        final_text = clean_for_html(f"{formatted_answer}\n\n<b>📚 Sumber:</b> {', '.join(sources)}")
        
        # Kirim teks ke Telegram
        await update.message.reply_text(final_text, parse_mode=ParseMode.HTML)

        # 4. LOGIKA KIRIM GAMBAR 
        found_image = False
        # Strategi A: Cari berdasarkan nama file di folder data yang mirip dengan query
        all_files = os.listdir(DATA_FOLDER)
        
        # Jika user tanya piktogram atau korosif, cari file yang mengandung kata itu
        if any(word in query_lower for word in ["piktogram", "gambar", "foto", "korosif"]):
            for file_name in all_files:
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # Mencocokkan nama file (contoh: GHS-Piktogram-Korosif.png)
                    if "piktogram" in file_name.lower() or "korosif" in file_name.lower():
                        file_path = os.path.join(DATA_FOLDER, file_name)
                        with open(file_path, 'rb') as photo:
                            await update.message.reply_photo(photo=photo, caption=f"🖼️ Lampiran: {file_name}")
                        found_image = True
                        break

    except Exception as e:
        logging.error(f"Error: {e}")
        # Jika HTML gagal, kirim teks polos sebagai cadangan
        await update.message.reply_text(f"Terjadi kendala format, ini jawabannya:\n\n{answer[:3000]}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()