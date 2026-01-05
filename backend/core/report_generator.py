from fpdf import FPDF
import os
import qrcode
import tempfile
from datetime import datetime
from .config import settings

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        self.show_footer = kwargs.pop('show_footer', True)
        super().__init__(*args, **kwargs)

    def footer(self):
        if not self.show_footer:
            return
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
        # Live Verification Link (Points to our public verify endpoint)
        scan_id = scan_data.get("id", 0)
        base_url = settings.APP_URL
        verification_url = f"{base_url}/verify/{scan_id}"
        
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
        insight_bg = (248, 250, 252) # Slate 50

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
        ai_c = scan_data.get("ai_count", 0)
        para_c = scan_data.get("para_count", 0)
        mix_c = scan_data.get("mix_count", 0)
        human_c = scan_data.get("human_count", 0)
        cit_c = scan_data.get("citation_count", 0)
        skip_c = scan_data.get("skipped_count", 0)
        
        total_s = max(1, ai_c + para_c + mix_c + human_c + cit_c + skip_c)
        
        p_cit = (cit_c / total_s) * 100
        p_skip = (skip_c / total_s) * 100
        p_ai = (ai_c / total_s) * 100
        p_para = (para_c / total_s) * 100
        p_mix = (mix_c / total_s) * 100
        p_human = (human_c / total_s) * 100
        
        # Draw Polish Bar
        pdf.set_fill_color(226, 232, 240)
        pdf.rect(10, 187, 190, 8, 'F')
        
        cur_x = 10
        colors = [
            (59, 130, 246), # Blue-500 (Kutipan)
            (100, 116, 139), # Slate-500 (Lainnya)
            (239, 68, 68),  # Red-500 (AI)
            (249, 115, 22),  # Orange-500 (Parafrasa)
            (245, 158, 11),  # Amber-500 (Campuran)
            (16, 185, 129)   # Emerald-500 (Manusia)
        ]
        percents = [p_cit, p_skip, p_ai, p_para, p_mix, p_human]
        for color, p in zip(colors, percents):
            if p > 0:
                pdf.set_fill_color(*color)
                pdf.rect(cur_x, 187, (p/100)*190, 8, 'F')
                cur_x += (p/100)*190
        
        # Legend (2 columns)
        pdf.set_xy(10, 198)
        legend_labels = ["Kutipan", "Lainnya", "AI Identik", "Parafrasa", "Campuran", "Manusia"]
        
        col_width = 63
        for i, (color, lab, p) in enumerate(zip(colors, legend_labels, percents)):
            if i > 0 and i % 3 == 0:
                pdf.set_xy(10, pdf.get_y() + 6)
            
            pdf.set_fill_color(*color)
            pdf.rect(pdf.get_x(), pdf.get_y()+1, 3, 3, 'F')
            pdf.set_x(pdf.get_x()+4)
            pdf.set_font("Arial", '', 9)
            pdf.cell(col_width - 4, 5, f"{p:.0f}% {lab}")
            
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
                is_cite = s.get("is_citation", False)
                score = s.get("score", 0)
                
                if is_cite:
                    pdf.set_fill_color(219, 234, 254) # Blue-100 (Kutipan)
                elif score > 75: 
                    pdf.set_fill_color(254, 226, 226) # Red-100
                elif score > 50: 
                    pdf.set_fill_color(255, 247, 237) # Orange-50
                elif score > 25: 
                    pdf.set_fill_color(255, 251, 235) # Amber-50
                else: 
                    pdf.set_fill_color(255, 255, 255)
                
                sanitized_text = self._sanitize_text(s.get("text", ""))
                pdf.multi_cell(0, 8, sanitized_text, border=0, fill=True)
                pdf.ln(1)
                
                if pdf.get_y() > 260: pdf.add_page()
        
        return bytes(pdf.output())

    def generate_authenticity_certificate(self, cert_data: dict) -> bytes:
        """
        Generate a formal landscape-oriented Certificate of Authenticity.
        """
        # A4 Landscape: 297 x 210 mm | Disable auto-footer
        pdf = PDF(orientation='L', unit='mm', format='A4', show_footer=False)
        pdf.set_auto_page_break(False) # Prevent unexpected page jumps
        pdf.add_page()
        
        # --- NEW MODERN MOTIF BORDER ---
        pdf.set_fill_color(248, 250, 252) # Slate 50 background
        pdf.rect(0, 0, 297, 210, 'F')
        
        # Corner Geometric Patterns (Modern Motif)
        pdf.set_fill_color(124, 58, 237) # Purple
        # Top Left
        pdf.polygon([(0, 0), (40, 0), (0, 40)], 'F')
        pdf.set_fill_color(79, 70, 229) # Blueish Purple
        pdf.polygon([(0, 0), (25, 0), (0, 25)], 'F')
        
        # Bottom Right
        pdf.set_fill_color(124, 58, 237)
        pdf.polygon([(297, 210), (257, 210), (297, 170)], 'F')
        pdf.set_fill_color(79, 70, 229)
        pdf.polygon([(297, 210), (282, 210), (297, 195)], 'F')
        
        # Thin Side Lines
        pdf.set_draw_color(124, 58, 237)
        pdf.set_line_width(0.5)
        pdf.line(10, 10, 287, 10) # Top
        pdf.line(10, 200, 287, 200) # Bottom
        pdf.line(10, 10, 10, 200) # Left
        pdf.line(287, 10, 287, 200) # Right
        
        # --- HEADER ---
        if os.path.exists(self.logo_path):
            pdf.image(self.logo_path, 136, 18, 25)
            
        pdf.set_xy(10, 48)
        pdf.set_font("Arial", 'B', 36)
        pdf.set_text_color(15, 23, 42) # Slate 900
        pdf.cell(0, 20, "CERTIFICATE OF AUTHENTICITY", ln=True, align='C')
        
        pdf.set_font("Arial", 'I', 12)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 5, "SahihAksara Digital Integrity Verification System", ln=True, align='C')
        
        # --- BODY ---
        pdf.ln(15)
        pdf.set_font("Arial", '', 14)
        pdf.set_text_color(71, 85, 105) # Slate 600
        pdf.cell(0, 10, "Sertifikat ini diberikan secara resmi kepada:", ln=True, align='C')
        
        pdf.set_font("Arial", 'B', 28)
        pdf.set_text_color(124, 58, 237)
        pdf.cell(0, 25, self._sanitize_text(cert_data.get("full_name", "Verified User")).upper(), ln=True, align='C')
        
        pdf.set_font("Arial", '', 13)
        pdf.set_text_color(71, 85, 105)
        message = (
            f"Atas karya tulisannya yang telah melalui analisis deteksi AI SahihAksara "
            f"dengan skor probabilitas AI sebesar {cert_data.get('ai_probability')}%.\n"
            f"Dokumen ini dinyatakan sebagai 'Karya Orisinal' dengan kontribusi manusia yang dominan."
        )
        pdf.multi_cell(0, 8, self._sanitize_text(message), align='C')
        
        # --- FOOTER / VERIFICATION AREA ---
        # Verification QR (Right)
        scan_id = cert_data.get("id", 0)
        base_url = settings.APP_URL
        verification_url = f"{base_url}/verify/{scan_id}"
        qr_path = self._generate_qr(verification_url)
        pdf.image(qr_path, 248, 155, 32, 32)
        os.unlink(qr_path)
        
        # "Gold Seal" Placeholder (Left)
        # Ribbon simulation
        pdf.set_fill_color(245, 158, 11) # Amber 500
        pdf.polygon([(25, 175), (35, 175), (30, 192)], 'F') # Ribbon 1
        pdf.polygon([(45, 175), (55, 175), (50, 192)], 'F') # Ribbon 2
        
        pdf.set_fill_color(251, 191, 36) # Amber 400
        pdf.circle(41, 172, 14, 'F') # Main Seal
        pdf.set_font("Arial", 'B', 8)
        pdf.set_text_color(146, 64, 14)
        pdf.set_xy(31, 170)
        pdf.cell(20, 5, "AUTHENTIC", align='C')
        
        # Details (Center)
        pdf.set_xy(70, 160)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(100, 5, f"SERIAL: SA-CERT-{datetime.now().strftime('%Y%m%d')}-000{scan_id}", ln=True, align='L')
        
        pdf.set_xy(70, 166)
        pdf.set_font("Arial", '', 10)
        pdf.cell(100, 5, f"Verified on: {cert_data.get('created_at')}", ln=True, align='L')
        
        # Fingerprint Footer (Very Bottom - Compact)
        pdf.set_xy(10, 195)
        pdf.set_font("Courier", '', 7)
        pdf.set_text_color(148, 163, 184)
        pdf.cell(0, 5, f"SHA-256 FINGERPRINT: {cert_data.get('sha256_hash')}", align='C')
        
        return bytes(pdf.output())
