from core.ai_detector import AIDetector

def run_test():
    detector = AIDetector()
    
    # User's Problematic Text (AI Generated but getting 0%)
    target_text = """Dalam dunia pertambangan, alat berat memainkan peran yang sangat penting untuk mendukung kelancaran dan efektivitas operasional. Penggunaan alat berat yang tepat dapat meningkatkan efisiensi dan mengurangi waktu yang dibutuhkan untuk menyelesaikan berbagai tugas yang rumit di area tambang. Alat berat dalam industri pertambangan mencakup berbagai jenis, mulai dari alat penggali, pengangkut, perata tanah, hingga pengangkat, yang masing-masing memiliki fungsi spesifik sesuai dengan kebutuhan di lapangan. Setiap alat memiliki desain dan kapasitas yang disesuaikan untuk menangani pekerjaan yang berat, seperti menggali, memindahkan material, meratakan permukaan tanah, serta mengangkat beban berat. Dengan adanya alat berat, proses pertambangan dapat dilakukan dengan lebih cepat, aman, dan efisien, yang pada akhirnya meningkatkan produktivitas dan menurunkan biaya operasional. Oleh karena itu, pemahaman yang baik tentang jenis dan fungsi alat berat sangat diperlukan untuk mendukung operasional yang optimal di sektor pertambangan."""
    
    # Fragmented Version (Simulating PDF Extraction artifacts)
    fragmented_text = """Dalam dunia pertambangan, alat berat memainkan peran 
    yang sangat penting untuk mendukung kelancaran dan 
    efektivitas operasional. Penggunaan alat berat yang 
    tepat dapat meningkatkan efisiensi dan mengurangi waktu 
    yang dibutuhkan untuk menyelesaikan berbagai tugas."""

    # Control: Real Human Informal
    human_text = """Btw tadi gue abis dari tambang, gila sih panas banget cuacanya. Liat excavator segede rumah gitu baru nyadar betapa kecilnya kita ya. Beruntung bangey dapet kesempatan liat operasionalnya langsung, meskipun cuma sebentar."""

    print("\n--- Testing SahihAksara AI Detector (Recalibration V3.4) ---")
    
    for label, text in [("Target (AI)", target_text), ("Fragmented (AI)", fragmented_text), ("Human (Informal)", human_text)]:
        print(f"\n[{label} Test]")
        res = detector.analyze(text)
        print(f"Probabilitas AI: {res['ai_probability']}%")
        print(f"Status: {res['status']}")
        print(f"Perplexity (Loss): {res['perplexity']}")
        print(f"Burstiness: {res['burstiness']}")
        print(f"Normalized Count: {len(res['sentences'])} sentences")
        print("Sampel Kalimat:")
        for s in res['sentences'][:3]:
            print(f" - {s['score']}%: {s['text'][:70]}...")

if __name__ == "__main__":
    run_test()
