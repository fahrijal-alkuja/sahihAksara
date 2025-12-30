from fpdf import FPDF
import os
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

    def generate_scan_report(self, scan_data: dict) -> bytes:
        """
        Generate a professional PDF report for a scan result.
        """
        pdf = PDF()
        pdf.add_page()
        
        # --- HEADER ---
        # Add Logo
        if os.path.exists(self.logo_path):
            pdf.image(self.logo_path, 10, 8, 33)
        
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(30, 41, 59) # Slate 800
        pdf.cell(0, 10, "SahihAksara", ln=True, align='R')
        
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(100, 116, 139) # Slate 500
        pdf.cell(0, 10, "Deteksi Kejujuran Akademik & Digital", ln=True, align='R')
        
        pdf.ln(20)
        pdf.set_draw_color(226, 232, 240) # Slate 200
        pdf.line(10, 45, 200, 45)
        
        # --- REPORT TITLE ---
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(15, 23, 42) # Slate 900
        pdf.cell(0, 15, "Laporan Analisis Deteksi AI", ln=True, align='C')
        
        # --- SUMMARY SECTION ---
        pdf.ln(5)
        pdf.set_fill_color(248, 250, 252) # Slate 50
        pdf.rect(10, 65, 190, 40, 'F')
        
        pdf.set_xy(15, 70)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(50, 10, "Skor AI Signature:")
        
        # Color score based on probability
        prob = scan_data.get("ai_probability", 0)
        if prob > 70: pdf.set_text_color(239, 68, 68) # Red
        elif prob > 40: pdf.set_text_color(245, 158, 11) # Amber
        else: pdf.set_text_color(16, 185, 129) # Emerald
        
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(50, 10, f"{prob}%", ln=True)
        
        pdf.set_xy(15, 85)
        pdf.set_text_color(30, 41, 59)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 5, "Status:")
        pdf.set_font("Arial", '', 10)
        pdf.cell(50, 5, self._sanitize_text(scan_data.get("status", "Unknown")).upper(), ln=True)
        
        pdf.set_xy(15, 92)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 5, "Tanggal Analisis:")
        pdf.set_font("Arial", '', 10)
        pdf.cell(50, 5, self._sanitize_text(scan_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))), ln=True)
        
        # --- METRICS ---
        pdf.set_xy(120, 75)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(40, 5, "Word Density (Loss):", ln=True)
        pdf.set_xy(120, 80)
        pdf.set_font("Courier", 'B', 11)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(40, 5, f"{scan_data.get('perplexity', 0):.4f}", ln=True)
        
        pdf.set_xy(120, 90)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(40, 5, "Structural Flex (Burstiness):", ln=True)
        pdf.set_xy(120, 95)
        pdf.set_font("Courier", 'B', 11)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(40, 5, f"{scan_data.get('burstiness', 0):.4f}", ln=True)
        
        # --- TEXT COMPOSITION SECTION ---
        pdf.ln(20)
        pdf.set_xy(10, 110)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Komposisi Teks (Text Composition):", ln=True)
        
        sentences = scan_data.get("sentences") or []
        
        if not sentences:
            # Fallback to persistent metadata (counts) stored in DB
            counts = {
                "ai": scan_data.get("ai_count", 0),
                "para": scan_data.get("para_count", 0),
                "mix": scan_data.get("mix_count", 0),
                "human": scan_data.get("human_count", 0)
            }
            total_s = sum(counts.values()) or 1
            
            # Handle purged data UI
            pdf.set_font("Arial", 'I', 10)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 10, "[Detail analisis telah dihapus untuk melindungi privasi Anda]", ln=True, align='C')
        else:
            total_s = len(sentences) if sentences else 1
            counts = {"ai": 0, "para": 0, "mix": 0, "human": 0}
            for s in sentences:
                score = s.get("score", 0)
                if score > 70: counts["ai"] += 1
                elif score > 40: counts["para"] += 1
                elif score > 15: counts["mix"] += 1
                else: counts["human"] += 1
            
        # Percents (Always correctly calculated from counts)
        p_ai = (counts["ai"] / total_s) * 100
        p_para = (counts["para"] / total_s) * 100
        p_mix = (counts["mix"] / total_s) * 100
        p_human = (counts["human"] / total_s) * 100
        
        # Draw Bar
        start_x = 10
        y_bar = 122
        h_bar = 8
        w_total = 190
        
        pdf.set_fill_color(239, 68, 68) # Red
        pdf.rect(start_x, y_bar, (p_ai/100)*w_total, h_bar, 'F')
        start_x += (p_ai/100)*w_total
        
        pdf.set_fill_color(249, 115, 22) # Orange
        pdf.rect(start_x, y_bar, (p_para/100)*w_total, h_bar, 'F')
        start_x += (p_para/100)*w_total
        
        pdf.set_fill_color(245, 158, 11) # Amber
        pdf.rect(start_x, y_bar, (p_mix/100)*w_total, h_bar, 'F')
        start_x += (p_mix/100)*w_total
        
        pdf.set_fill_color(16, 185, 129) # Emerald
        pdf.rect(start_x, y_bar, (p_human/100)*w_total, h_bar, 'F')
        
        # Legend
        pdf.ln(10)
        pdf.set_font("Arial", '', 9)
        pdf.set_xy(10, 132)
        
        # AI Legend
        pdf.set_fill_color(239, 68, 68)
        pdf.rect(10, 133, 3, 3, 'F')
        pdf.set_xy(14, 132)
        pdf.cell(40, 5, f"{p_ai:.0f}% AI Identik")
        
        # Para Legend
        pdf.set_xy(55, 132)
        pdf.set_fill_color(249, 115, 22)
        pdf.rect(55, 133, 3, 3, 'F')
        pdf.set_xy(59, 132)
        pdf.cell(40, 5, f"{p_para:.0f}% Parafrasa")
        
        # Mix Legend
        pdf.set_xy(100, 132)
        pdf.set_fill_color(245, 158, 11)
        pdf.rect(100, 133, 3, 3, 'F')
        pdf.set_xy(104, 132)
        pdf.cell(40, 5, f"{p_mix:.0f}% Campuran")
        
        # Human Legend
        pdf.set_xy(145, 132)
        pdf.set_fill_color(16, 185, 129)
        pdf.rect(145, 133, 3, 3, 'F')
        pdf.set_xy(149, 132)
        pdf.cell(40, 5, f"{p_human:.0f}% Manusia")

        # --- NEW: INTEGRITY VERDICT SECTION ---
        pdf.ln(15)
        pdf.set_xy(10, 142)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(0, 10, "Asesmen Integritas (Integrity Assessment):", ln=True)

        # Logic for Verdict
        ai_total = p_ai + p_para
        ai_signature = scan_data.get("ai_probability", 0)
        
        verdict = ""
        verdict_color = (0, 0, 0)
        verdict_bg = (255, 255, 255)
        recommendation = ""

        if ai_total < 20 and ai_signature < 50:
            verdict = "LULUS (PASSED)"
            verdict_color = (16, 120, 80) # Dark Emerald
            verdict_bg = (209, 250, 229) # Emerald-100
            recommendation = "Karya menunjukkan orisinalitas yang kuat. Kontribusi manusia dominan dan penggunaan AI berada dalam batas toleransi wajar ( < 20% )."
        elif ai_total <= 50:
            verdict = "PERLU REVISI (REVISION REQUIRED)"
            verdict_color = (180, 83, 9) # Dark Amber
            verdict_bg = (254, 243, 199) # Amber-100
            recommendation = "Ditemukan kontaminasi AI yang signifikan (20% - 50%). Penulis disarankan untuk merumuskan ulang bagian yang terdeteksi AI dengan gaya bahasa sendiri."
        else:
            verdict = "INVESTIGASI LANJUT (INVESTIGATE / REJECTED)"
            verdict_color = (153, 27, 27) # Dark Red
            verdict_bg = (254, 226, 226) # Red-100
            recommendation = "Kadar AI melebihi ambang batas toleransi ( > 50% ). Diperlukan verifikasi lebih lanjut oleh tim editor atau dosen terkait keabsahan naskah ini."

        # Draw Verdict Box
        pdf.set_xy(10, 151)
        pdf.set_fill_color(*verdict_bg)
        pdf.rect(10, 151, 190, 25, 'F')
        
        pdf.set_xy(15, 154)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(*verdict_color)
        pdf.cell(0, 5, f"STATUS: {verdict}", ln=True)
        
        pdf.set_xy(15, 161)
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(180, 5, recommendation, align='L')

        # Heatmap Label moved down
        pdf.ln(10)
        pdf.set_xy(10, 185)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(0, 10, "Peta Panas Kalimat (Sentence Heatmap):", ln=True)
        
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(51, 65, 85)
        
        sentences = scan_data.get("sentences") or []
        if not sentences:
            pdf.set_font("Arial", 'I', 10)
            pdf.set_text_color(150, 150, 150)
            pdf.multi_cell(0, 10, "Data Peta Panas (Heatmap) sudah tidak tersedia karena kebijakan Zero-Retention. Naskah lengkap Anda tidak disimpan secara permanen di server kami demi keamanan.", border=1, align='C')
        else:
            for s in sentences:
                score = s.get("score", 0)
                # Apply light background colors for sentences
                if score > 70: pdf.set_fill_color(254, 226, 226) # Red-100
                elif score > 40: pdf.set_fill_color(255, 247, 237) # Orange-50
                elif score > 15: pdf.set_fill_color(255, 251, 235) # Amber-50
                else: pdf.set_fill_color(255, 255, 255) # White
                
                # Print sentence with multi_cell for wrapping
                sanitized_text = self._sanitize_text(s.get("text", ""))
                pdf.multi_cell(0, 6, sanitized_text, border=0, fill=True)
                pdf.ln(1)
                
                # Check if we need a new page
                if pdf.get_y() > 260:
                    pdf.add_page()
        
        return bytes(pdf.output())
