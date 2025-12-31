from fpdf import FPDF
import os
import qrcode
import tempfile
from datetime import datetime

class PDF(FPDF):
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, "Laporan ini dihasilkan secara otomatis oleh SahihAksara AI Detector.", align='C', ln=True)
        self.cell(0, 5, "Universitas Kutai Kartanegara - TIM IT fahrijal", align='C', ln=True)

class ReportGenerator:
    def __init__(self, logo_path: str = "backend/assets/logo.png"):
        self.logo_path = logo_path

    def _sanitize_text(self, text: str) -> str:
        """Replace problematic Unicode characters with PDF-safe equivalents."""
        if not text: return ""
        replacements = {
            '\u2013': '-', # en-dash
            '\u2014': '-', # em-dash
            '\u2018': "'", # left single quote
            '\u2019': "'", # right single quote
            '\u201c': '"', # left double quote
            '\u201d': '"', # right double quote
            '\u2026': '...', # ellipsis
            '\u00a0': ' ',   # non-breaking space
            '\u2022': '-',   # bullet point (replaced with dash)
            '\u2212': '-',   # minus sign
            '\u202f': ' ',   # narrow no-break space
            '\u200b': '',    # zero width space
            '\u2009': ' ',   # thin space
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    def _generate_qr(self, data: str):
        """Generate a QR code image temporarily."""
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(temp_file.name)
        return temp_file.name

    def generate_scan_report(self, scan_data: dict) -> bytes:
        """
        Generate a professional "Interactive" PDF report.
        """
        pdf = PDF()
        pdf.add_page()
        
        # --- HEADER ---
        if os.path.exists(self.logo_path):
            pdf.image(self.logo_path, 10, 8, 30)
        
        pdf.set_font("Arial", 'B', 22)
        pdf.set_text_color(124, 58, 237) # Theme Purple (7c3aed)
        pdf.set_xy(10, 10)
        pdf.cell(0, 10, "SahihAksara", ln=True, align='R')
        
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 10, "Digital Integrity Verification", ln=True, align='R')
        
        pdf.ln(10)
        pdf.set_draw_color(226, 232, 240)
        pdf.line(10, 42, 200, 42)
        
        # --- VERIFICATION QR ---
        # Concept: Verify on portal
        verification_url = f"https://sahihaksara.id/verify/{datetime.now().timestamp()}"
        qr_path = self._generate_qr(verification_url)
        pdf.image(qr_path, 175, 45, 25, 25)
        os.unlink(qr_path) # Cleanup
        
        # --- REPORT TITLE ---
        pdf.set_xy(10, 45)
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 15, "OFFICIAL INTEGRITY REPORT", ln=True, align='L')
        
        # --- SUMMARY SECTION (CARD) ---
        pdf.ln(5)
        pdf.set_fill_color(250, 250, 251)
        pdf.rect(10, 62, 160, 45, 'F')
        
        pdf.set_xy(15, 67)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(50, 5, "AI SIGNATURE PERCENTAGE")
        
        prob = scan_data.get("ai_probability", 0)
        if prob > 70: pdf.set_text_color(239, 68, 68) 
        elif prob > 40: pdf.set_text_color(245, 158, 11)
        else: pdf.set_text_color(16, 185, 129)
        
        pdf.set_xy(15, 73)
        pdf.set_font("Arial", 'B', 32)
        pdf.cell(50, 15, f"{prob}%")
        
        # Verdict Badge in Header area
        verdict_text = self._sanitize_text(scan_data.get("status", "Unknown"))
        pdf.set_xy(70, 73)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(226, 232, 240)
        pdf.cell(40, 6, verdict_text, border=0, fill=True, align='C', ln=True)
        
        pdf.set_xy(15, 93)
        pdf.set_text_color(71, 85, 105)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 5, f"Scanned on: {scan_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}")
        
        # Metrics Sidebar
        pdf.set_xy(120, 67)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(148, 163, 184)
        pdf.cell(40, 5, "WORD DENSITY", ln=True)
        pdf.set_xy(120, 72)
        pdf.set_font("Courier", 'B', 12)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(40, 5, f"{scan_data.get('perplexity', 0):.4f}", ln=True)
        
        pdf.set_xy(120, 82)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(148, 163, 184)
        pdf.cell(40, 5, "STRUCTURAL FLEX", ln=True)
        pdf.set_xy(120, 87)
        pdf.set_font("Courier", 'B', 12)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(40, 5, f"{scan_data.get('burstiness', 0):.4f}", ln=True)
        
        # --- ENSEMBLE INSIGHT SECTION ---
        pdf.ln(25)
        pdf.set_xy(10, 115)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, "Analisis Musyawarah Digital (AI Insights)", ln=True)
        
        # Logic for automated insight
        s_opinion = scan_data.get("opinion_semantic") or 0
        p_opinion = scan_data.get("opinion_perplexity") or 0
        b_opinion = scan_data.get("opinion_burstiness") or 0
        final_prob = scan_data.get("ai_probability", 0)
        
        insight_text = ""
        # 1. Check for specific high signals
        if s_opinion > 70:
            insight_text += "- Model Semantik mendeteksi konstruksi kalimat yang sangat identik dengan pola generator bahasa (LLM).\n"
        if p_opinion > 70:
            insight_text += "- Tingkat densitas kata menunjukkan 'perfection bias', di mana pilihan kata terlalu optimal untuk tulisan manusia.\n"
        if b_opinion > 50:
            insight_text += "- Ritme penulisan terdeteksi terlalu konsisten (monoton), minim variasi panjang kalimat yang biasa ada pada karya manusia.\n"
        
        # 2. Fallback for High Probability but missing granular data (Legacy/Edge cases)
        if not insight_text and final_prob > 70:
            insight_text = "- Sistem mendeteksi tanda-tanda kuat otomatisasi linguistik. Struktur argumen dan frekuensi kata menunjukkan pola yang sangat mirip dengan keluaran AI generasi terbaru."
        elif not insight_text:
            insight_text = "- Sistem mendeteksi variasi linguistik yang sehat. Pola kalimat acak dan memiliki karakteristik humanis yang kuat."

        # Calculate dynamic height for insight box
        # Each line is roughly 6 units, plus padding
        line_count = insight_text.count('\n') + 1
        box_h = (line_count * 6) + 8
        
        pdf.set_fill_color(*insight_bg)
        pdf.rect(10, 125, 190, box_h, 'F')
        
        pdf.set_xy(15, 128)
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(180, 6, self._sanitize_text(insight_text.strip()))
        
        # --- TEXT COMPOSITION ---
        pdf.set_xy(10, 175)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Komposisi Teks (Text Composition)", ln=True)
        
        # Bar chart logic (re-used and polished)
        sentences = scan_data.get("sentences") or []
        ai_c = scan_data.get("ai_count", 0)
        para_c = scan_data.get("para_count", 0)
        mix_c = scan_data.get("mix_count", 0)
        human_c = scan_data.get("human_count", 0)
        total_s = max(1, ai_c + para_c + mix_c + human_c)
        
        p_ai = (ai_c / total_s) * 100
        p_para = (para_c / total_s) * 100
        p_mix = (mix_c / total_s) * 100
        p_human = (human_c / total_s) * 100
        
        # Draw Polish Bar
        pdf.set_fill_color(226, 232, 240)
        pdf.rect(10, 187, 190, 8, 'F')
        
        cur_x = 10
        colors = [(239, 68, 68), (249, 115, 22), (245, 158, 11), (16, 185, 129)]
        percents = [p_ai, p_para, p_mix, p_human]
        for color, p in zip(colors, percents):
            if p > 0:
                pdf.set_fill_color(*color)
                pdf.rect(cur_x, 187, (p/100)*190, 8, 'F')
                cur_x += (p/100)*190
        
        # Legend
        pdf.set_xy(10, 198)
        legend_labels = ["AI Identik", "Parafrasa", "Campuran", "Manusia"]
        for color, lab, p in zip(colors, legend_labels, percents):
            pdf.set_fill_color(*color)
            pdf.rect(pdf.get_x(), pdf.get_y()+1, 3, 3, 'F')
            pdf.set_x(pdf.get_x()+4)
            pdf.set_font("Arial", '', 9)
            pdf.cell(44, 5, f"{p:.0f}% {lab}")
            
        # --- SARAN PERBAIKAN (ACTIONABLE) ---
        pdf.ln(15)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Saran Perbaikan Orisinalitas", ln=True)
        
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(51, 65, 85)
        
        tips = []
        if prob > 50:
            tips.append("1. Hindari penggunaan konjungsi formal berlebih (oleh karena itu, sehubungan dengan).")
            tips.append("2. Masukkan opini pribadi atau anekdot yang spesifik pada argumen Anda.")
            tips.append("3. Ubah struktur kalimat pasif menjadi aktif untuk meningkatkan 'Human Signature'.")
        else:
            tips.append("1. Karya Anda sudah memiliki orisinalitas yang baik.")
            tips.append("2. Pertahankan gaya bahasa personal dan variasi panjang kalimat.")
            
        pdf.multi_cell(0, 6, self._sanitize_text("\n".join(tips)))

        # --- SENTENCE HEATMAP (Page 2) ---
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 15, "Sentence Heatmap Analysis", ln=True)
        
        pdf.set_font("Arial", '', 10)
        if not sentences:
            pdf.set_font("Arial", 'I', 10)
            pdf.set_text_color(150, 150, 150)
            pdf.multi_cell(0, 10, "[Detail kalimat telah dihapus atas alasan privasi digital. Gunakan aplikasi SahihAksara untuk melihat analisis real-time.]", border=1, align='C')
        else:
            for s in sentences:
                score = s.get("score", 0)
                if score > 75: pdf.set_fill_color(254, 226, 226) # Red-100
                elif score > 50: pdf.set_fill_color(255, 247, 237) # Orange-50
                elif score > 25: pdf.set_fill_color(255, 251, 235) # Amber-50
                else: pdf.set_fill_color(255, 255, 255)
                
                sanitized_text = self._sanitize_text(s.get("text", ""))
                pdf.multi_cell(0, 8, sanitized_text, border=0, fill=True)
                pdf.ln(1)
                
                if pdf.get_y() > 260: pdf.add_page()
        
        return bytes(pdf.output())
