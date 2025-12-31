import torch.nn.functional as F
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForMaskedLM
import numpy as np
import re
from .citation_handler import CitationHandler

class AIDetector:
    def __init__(self, model_name="indolem/indobert-base-uncased"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        base_model = AutoModelForMaskedLM.from_pretrained(model_name)
        
        if self.device.type == "cpu":
            # Optimization for VPS (CPU only)
            # 1. Dynamic Quantization: Reduces model size and speeds up CPU inference
            self.model = torch.quantization.quantize_dynamic(
                base_model, {torch.nn.Linear}, dtype=torch.qint8
            )
            # 2. Thread Optimization: Use available cores efficiently
            torch.set_num_threads(min(4, torch.get_num_threads())) 
        else:
            self.model = base_model.to(self.device)
            
        self.model.eval()
        self.citation_handler = CitationHandler()

    def calculate_features_batch(self, texts: list[str], batch_size: int = 8):
        """
        Calculate features for a list of texts in batches for speed.
        """
        results = []
        if not texts:
            return results

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            encodings = self.tokenizer(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**encodings, labels=encodings["input_ids"])
                logits = outputs.logits
                
                # Manual cross entropy for per-item loss
                shift_logits = logits.contiguous()
                shift_labels = encodings["input_ids"].contiguous()
                
                loss_fct = torch.nn.CrossEntropyLoss(reduction='none')
                loss = loss_fct(shift_logits.reshape(-1, shift_logits.size(-1)), shift_labels.reshape(-1))
                loss = loss.reshape(shift_labels.size(0), -1)
                
                # Apply mask to loss calculation
                mask = encodings["attention_mask"]
                loss = (loss * mask).sum(dim=1) / mask.sum(dim=1)
                
                # Confidence
                probs = F.softmax(logits, dim=-1)
                token_probs = torch.gather(probs, 2, encodings["input_ids"].unsqueeze(-1)).squeeze(-1)
                
                # Average confidence per item (ignoring padding)
                avg_confidence = (token_probs * mask).sum(dim=1) / mask.sum(dim=1)
                
            for l, c in zip(loss.tolist(), avg_confidence.tolist()):
                results.append({"loss": l, "confidence": c})
        return results

    def calculate_features(self, text: str):
        if not text.strip() or len(text.split()) < 5:
            return {"loss": 0.0, "confidence": 0.0}
        return self.calculate_features_batch([text])[0]

    def calculate_burstiness(self, text: str) -> float:
        """
        Calculate the Coefficient of Variation (CV) of sentence lengths.
        """
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if len(s.strip()) > 10]
        if len(sentences) <= 1:
            return 1.0
            
        lengths = [len(s.split()) for s in sentences]
        mean_len = np.mean(lengths)
        if mean_len == 0: return 0.0
        
        std_dev = np.std(lengths)
        cv = std_dev / mean_len
        return float(cv)



    def calculate_naturalness(self, text: str) -> float:
        """
        Detects 'Linguistic Chaos' - the hallmark of human writing.
        """
        words = text.split()
        if not words: return 0.0
        
        bonus = 0.0
        dots = text.count('.')
        commas = text.count(',')
        
        # 1. Run-on Sentence Detection (Moderate Marker)
        if len(words) > 20 and dots <= 1:
            bonus += 15.0 # Reduced from 35.0
            
        # 2. Lowercase Start (Minor Marker)
        if text and text[0].islower():
            bonus += 8.0 # Reduced from 15.0
            
        # 3. Human Markers (Slang & Non-Standard Consistency)
        # These are rare in formal AI output
        human_markers = [
            'yg', 'gw', 'lu', 'gak', 'udah', 'aja', 'nih', 'kalo', 'donk', 'banget',
            'sih', 'deh', 'kok', 'tuh', 'loh', 'masih', 'cuma', 'pas', 'lagi', 'tadi',
            'kayak', 'nyadar', 'abis', 'siapa', 'kenapa', 'gini', 'gitu', 'mana',
            # Non-standard common typos (AI usually writes perfectly)
            'analisa', 'praktek', 'risiko', 'obyek', 'subyek', 'efektifitas', 
            'aktifitas', 'hirarki', 'kwalitas', 'prosentase', 'sekedar', 'merubah'
        ]
        
        # 4. AI Hallmarks (Formal Transition words & Jargon)
        # AI (GPT) LOVES these connectors. Presence should SUBTRACT from human bonus.
        ai_hallmarks = [
            'perlu digarisbawahi', 'oleh karena itu', 'namun demikian', 'kendati demikian',
            'di sisi lain', 'dalam hal ini', 'sehubungan dengan', 'merujuk pada',
            'selaras dengan', 'berkenaan dengan', 'lebih lanjut', 'tak kalah pentingnya',
            'paradigma', 'diskursus', 'manifestasi', 'konstruksi', 'fundamen', 
            'substansi', 'implementasi', 'signifikansi', 'komprehensif', 'empiris',
            'teoretis', 'metodologis', 'interpretasi', 'perspektif'
        ]
        
        found_human = sum(1 for m in human_markers if re.search(r'\b' + m + r'\b', text.lower()))
        found_ai = sum(1 for m in ai_hallmarks if re.search(r'\b' + m + r'\b', text.lower()))
        
        bonus += (found_human * 6.0)
        bonus -= (found_ai * 3.0) # AI connectors reduce the manual human bonus
            
        # 5. Length Normalization
        length_factor = min(1.0, 250 / (len(words) + 1))
        return max(0, bonus * length_factor)

    def normalize_text(self, text: str) -> str:
        """
        Cleans extraction artifacts like physical line breaks from layout.
        Reconstructs sentences and paragraphs.
        """
        # 1. Normalize line breaks: double \n is paragraph, single \n is space
        temp = text.replace("\r\n", "\n").replace("\n\n", "||PARA||")
        temp = temp.replace("\n", " ").replace("\t", " ")
        temp = temp.replace("||PARA||", "\n\n")
        
        # 2. Normalize whitespace
        temp = re.sub(r' +', ' ', temp)
        
        return temp.strip()

    def analyze(self, text: str, force_full_scan: bool = False):
        clean_text = self.normalize_text(text)
        
        tokens = self.tokenizer(clean_text, return_tensors="pt", add_special_tokens=False).to(self.device)
        input_ids = tokens["input_ids"][0]
        
        cv = self.calculate_burstiness(clean_text)
        human_bonus = self.calculate_naturalness(clean_text)
        
        # --- PERFORMANCE OPTIMIZATION: Hybrid Sampling ---
        max_len = 512
        total_tokens = len(input_ids)
        
        is_hybrid = total_tokens > (max_len * 4) and not force_full_scan 
        partially_analyzed = False
        
        # 1. Improved Sentence Analysis
        parts = re.split(r'([.!?]\s+(?=[A-Z"“])|["“][^"”]*["”])', clean_text)
        raw_sentences = []
        for p in parts:
            if not p: continue
            if p.startswith(('"', '“')) and p.endswith(('"', '”')):
                raw_sentences.append(p.strip())
            else:
                sub_parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"“])', p)
                raw_sentences.extend([s.strip() for s in sub_parts if s.strip()])
        
        processed_sentences = [s for s in raw_sentences if len(s) > 5]
        if not processed_sentences: processed_sentences = [clean_text]
        
        # Determine which sentences to scan
        if not is_hybrid:
            sentences_to_scan = processed_sentences[:100]
        else:
            partially_analyzed = True
            idx_s = processed_sentences[:20]
            mid = len(processed_sentences) // 2
            idx_m = processed_sentences[mid-10:mid+10]
            idx_e = processed_sentences[-20:]
            sentences_to_scan = idx_s + idx_m + idx_e

        sent_results = self.calculate_features_batch(sentences_to_scan, batch_size=24)
        detailed = []
        
        # --- CITATION FILTERING ---
        citation_count = 0
        
        # --- ENSEMBLE OPINION 1: SEMANTIC (IndoBERT) ---
        target_baseline = 1.94 # Target: High-Confidence Academic Detection
        ai_weights = 0
        total_weight = 0
        
        # Track word counts for length-weighted scoring
        total_relevant_words = 0
        weighted_s_score = 0
        
        from langdetect import detect
        scanned_map = {s_text: res for s_text, res in zip(sentences_to_scan, sent_results)}
        
        for s_text in processed_sentences[:150]:
            is_english = False
            try:
                if len(s_text.split()) > 3:
                    if detect(s_text) == 'en': is_english = True
            except: pass

            if is_english:
                detailed.append({"text": s_text, "score": -1.0, "language": "en"})
                continue
                
            # Check for citation
            is_cite = self.citation_handler.is_citation(s_text)
            if is_cite:
                citation_count += 1

            if s_text in scanned_map:
                f = scanned_map[s_text]
                s_loss = f["loss"]
                # FILTERING: Ignore noise (headers/footers/citations/numerics)
                # Skip sentences < 5 words or containing too many numbers/symbols
                s_words = s_text.split()
                if len(s_words) < 5 or (sum(c.isdigit() or not c.isalnum() for c in s_text) / (len(s_text) + 1)) > 0.4:
                    continue

                raw_diff = target_baseline - s_loss
                
                # Semantic Scoring Logic (Bullseye for Docs)
                if raw_diff > 0.6: s_score, weight = float(max(0, min(100, raw_diff * 140))), 1.5
                elif raw_diff > 0.3: s_score, weight = float(max(0, min(100, raw_diff * 105))), 1.2
                else: s_score, weight = float(max(0, min(100, raw_diff * 72))), 0.4
                    
                # Length-Weighted Addition
                l_weight = len(s_words) / 15.0 # Normalizing around 15 words
                
                # --- CITATION LOGIC: Exclude from global weight if citation ---
                if is_cite:
                    detailed.append({"text": s_text, "score": round(s_score, 2), "is_citation": True})
                else:
                    ai_weights += (s_score * weight * l_weight)
                    total_weight += (weight * l_weight)
                    detailed.append({"text": s_text, "score": round(s_score, 2), "is_citation": False})
            else:
                detailed.append({"text": s_text, "score": 0.0, "skipped": True, "is_citation": is_cite})
                
        citation_percentage = round((citation_count / len(processed_sentences)) * 100, 1) if processed_sentences else 0.0

        opinion_semantic = (ai_weights / total_weight) if total_weight > 0 else 0.0

        # --- ENSEMBLE OPINION 2: STATISTICAL (Perplexity) ---
        global_features = self.calculate_features(clean_text[:1500])
        global_loss = global_features["loss"]
        # Convert Loss to 0-100 scale. Lower loss = Higher AI Probability.
        # Loss around 0.5 is very high AI, loss > 2.0 is likely human.
        opinion_perplexity = max(0, min(100, (1.94 - global_loss) * 75))

        # --- ENSEMBLE OPINION 3: STRUCTURAL (Burstiness) ---
        # CV < 0.2 (Flat/AI), CV > 0.8 (Very Bursty/Human)
        opinion_burstiness = max(0, min(100, (0.75 - cv) * 110))

        # Weighted Musyawarah (Academic Precision): 55% Semantic, 35% Perplexity, 10% Burstiness
        ensemble_score = (opinion_semantic * 0.55) + (opinion_perplexity * 0.35) + (opinion_burstiness * 0.10)
        
        # Apply Humanity Bonuses (Reduces the final AI score)
        # Multiplier: 1.1 (Slightly lowered for stricter alignment)
        calculated_bonus = human_bonus * 1.1
        
        # CAP: If AI signal is very high, 20% max bonus
        if ensemble_score > 80:
            calculated_bonus = min(calculated_bonus, 20.0)
            
        final_prob = ensemble_score - calculated_bonus
        final_prob = float(max(0, min(100, final_prob)))

        # Console Debug for Admin to see the "Musyawarah"
        print(f"--- ENSEMBLE DEBATE (FINAL ALIGNMENT) ---")
        print(f"1. Semantic Opinion: {opinion_semantic:.2f}")
        print(f"2. Perplexity Opinion: {opinion_perplexity:.2f}")
        print(f"3. Burstiness Opinion: {opinion_burstiness:.2f}")
        print(f"4. Humanity Bonus: -{calculated_bonus:.2f}")
        print(f"=> FINAL ENSEMBLE SCORE: {final_prob:.2f}% AI Probability")
        print(f"-----------------------")

        # Status Mapping
        if final_prob < 20: status = "Human Written"
        elif final_prob < 50: status = "Likely Human"
        elif final_prob < 75: status = "Likely AI"
        else: status = "AI Generated"
        
        # Calculate granular counts for the return dict
        # This replaces the logic that was partially moved to main.py
        ai_count = sum(1 for s in detailed if s.get("score", 0) > 75)
        para_count = sum(1 for s in detailed if 50 < s.get("score", 0) <= 75)
        mix_count = sum(1 for s in detailed if 25 < s.get("score", 0) <= 50)
        human_count = sum(1 for s in detailed if 0 <= s.get("score", 0) <= 25)

        return {
            "ai_probability": round(final_prob, 2),
            "perplexity": round(float(global_loss), 4),
            "burstiness": round(float(cv), 4),
            "status": status,
            "sentences": detailed,
            "ai_count": ai_count,
            "para_count": para_count,
            "mix_count": mix_count,
            "human_count": human_count,
            "citation_percentage": citation_percentage,
            "partially_analyzed": partially_analyzed,
            "opinion_semantic": round(opinion_semantic, 2),
            "opinion_perplexity": round(opinion_perplexity, 2),
            "opinion_burstiness": round(opinion_burstiness, 2),
            "opinion_humanity": round(calculated_bonus, 2)
        }
