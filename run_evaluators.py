import phoenix as px
from phoenix.evals import HallucinationEvaluator, RelevanceEvaluator
from langchain_ollama import ChatOllama
import pandas as pd
import re

def clean_text(text):
    """Membersihkan teks dari karakter JSON/metadata agar lebih mudah dibaca AI"""
    text = str(text)
    match = re.search(r"content='(.*?)'", text)
    if match:
        return match.group(1)
    return text[:1000]

def main():
    print("🔍 Menghubungkan ke Phoenix Dashboard...")
    client = px.Client(endpoint="http://127.0.0.1:6006")
    
    # Inisialisasi model penilai (Judge)
    eval_model = ChatOllama(model="llama3.2:3b", temperature=0)

    print("📂 Menarik data dari Project 'default'...")
    try:
        spans_df = client.get_spans_dataframe(project_name="default")
        df_llm = spans_df[spans_df['name'] == 'ChatOllama'].copy()
        
        if df_llm.empty:
            print("⚠️ Data ChatOllama tidak ditemukan.")
            return

        # Ambil 50 data terakhir (sesuai jumlah pengujian terbaru Anda)
        df_llm = df_llm.tail(50)
        print(f"✅ Berhasil menarik {len(df_llm)} data trace.")
    except Exception as e:
        print(f"❌ Error saat menarik data: {e}")
        return

    # Inisialisasi Phoenix Evaluator
    hallucination_evaluator = HallucinationEvaluator(eval_model)
    relevance_evaluator = RelevanceEvaluator(eval_model)

    results = []
    print("🚀 Menjalankan Evaluasi (LLM-as-a-Judge)...")

    for i, (_, row) in enumerate(df_llm.iterrows()):
        query = clean_text(row.get('attributes.input.value', ""))
        response = clean_text(row.get('attributes.output.value', ""))
        reference = clean_text(row.get('attributes.llm.input_messages', ""))

        print(f"[{i+1}/{len(df_llm)}] Sedang menilai...")
        
        # --- PENILAIAN RELEVANCE ---
        rel_score = 0
        try:
            rel_res = relevance_evaluator.evaluate(input=query, output=response)
            rel_label = str(rel_res.label).lower()
            
            # Logika pencarian kata kunci agar tidak kaku (Exact Match Fix)
            if any(word in rel_label for word in ["relevant", "yes", "benar", "nyambung"]):
                rel_score = 1
            print(f"    > Relevance: {rel_label}")
        except:
            pass

        # --- PENILAIAN FAITHFULNESS ---
        hal_score = 0
        try:
            hal_res = hallucination_evaluator.evaluate(input=query, output=response, reference=reference)
            hal_label = str(hal_res.label).lower()
            
            # Phoenix biasanya menggunakan label 'factual' atau 'passing'
            if any(word in hal_label for word in ["factual", "passing", "correct", "no hallucination"]):
                hal_score = 1
            print(f"    > Faithfulness: {hal_label}")
        except:
            pass

        results.append({
            "relevance": rel_score,
            "faithfulness": hal_score
        })

    # --- TAMPILKAN RINGKASAN AKHIR ---
    if results:
        res_df = pd.DataFrame(results)
        print("\n" + "="*35)
        print("📊 RINGKASAN SKOR AKHIR (BAB 4)")
        print("="*35)
        print(f"📌 Answer Relevance : {res_df['relevance'].mean():.2f}")
        print(f"📌 Faithfulness    : {res_df['faithfulness'].mean():.2f}")
        print("="*35)
        
        res_df.to_csv("hasil_kualitas_final.csv", index=False)
        print("✅ Hasil detil disimpan di: hasil_kualitas_final.csv")
    else:
        print("❌ Gagal mendapatkan skor. Pastikan Ollama & Phoenix menyala.")

if __name__ == "__main__":
    main()