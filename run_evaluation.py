import phoenix as px
import pandas as pd
import time
import os

def main():
    print("🔍 Menghubungkan ke Phoenix Dashboard...")
    client = px.Client(endpoint="http://127.0.0.1:6006")

    try:
        from engine import RAGEngine
        engine = RAGEngine()
    except Exception as e:
        print(f"❌ Gagal memuat engine.py: {e}")
        return

    try:
        print("📂 Mengambil dataset dari Phoenix...")
        dataset = client.get_dataset(name="50_golden_dataset")
        df_test = dataset.as_dataframe() 
        print(f"✅ Dataset dimuat: {len(df_test)} baris ditemukan.")
    except Exception as e:
        print(f"❌ Gagal mengambil dataset: {e}")
        return

    results = []
    print(f"🚀 Memulai evaluasi otomatis...")

    for i, (index, row) in enumerate(df_test.iterrows()):
        raw_input = row.get('input') or row.get('question')
        
        # --- LOGIKA EKSTRAK TEKS (PENTING) ---
        # Jika data berupa dict {'question': 'teks'}, ambil teksnya saja
        if isinstance(raw_input, dict):
            query = raw_input.get('question', "")
        else:
            query = raw_input
        
        # Filter baris kosong
        if pd.isna(query) or str(query).strip() == "" or str(query) == "{}":
            continue
        
        print(f"[{i + 1}] Memproses: {str(query)[:50]}...")
        
        start_time = time.time()
        try:
            # Mengirimkan STRING ke engine, bukan DICT
            prediction, sources = engine.generate_response(str(query))
            latency = time.time() - start_time
            
            # Ekstrak ground truth jika berupa dict
            raw_gt = row.get('output')
            gt = raw_gt.get('output', str(raw_gt)) if isinstance(raw_gt, dict) else str(raw_gt)

            results.append({
                "question": query,
                "prediction": prediction,
                "ground_truth": gt,
                "sources": ", ".join(sources) if sources else "Tidak ada",
                "latency_seconds": round(latency, 2)
            })
        except Exception as e:
            print(f"❌ Error pada baris {i + 1}: {e}")

    if results:
        df_results = pd.DataFrame(results)
        df_results.to_csv("hasil_evaluasi_otomatis.csv", index=False)
        print(f"\n✅ SELESAI! {len(results)} data berhasil diproses.")
        print(f"📄 Hasil tersimpan di: {os.path.abspath('hasil_evaluasi_otomatis.csv')}")
    else:
        print("⚠️ Tidak ada data valid yang diproses.")

if __name__ == "__main__":
    main()