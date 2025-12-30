import torch.nn.functional as F
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForMaskedLM
import numpy as np
import re

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
        
        # 1. Run-on Sentence Detection (Strong Human Marker)
        if len(words) > 15 and dots <= 1:
            bonus += 35.0
            
        # 2. Lowercase Start or lack of capitalization
        if text and text[0].islower():
            bonus += 15.0
            
        # 3. Enhanced Informal Word Detection (Common Indonesian Slang/Particles)
        # These are extremely rare in formal AI output
        informal_markers = [
            'yg', 'gw', 'lu', 'gak', 'udah', 'aja', 'nih', 'kalo', 'donk', 'banget',
            'sih', 'deh', 'kok', 'tuh', 'loh', 'masih', 'cuma', 'pas', 'lagi', 'tadi',
            'kayak', 'nyadar', 'abis', 'siapa', 'kenapa', 'gini', 'gitu', 'mana'
        ]
        found_slang = sum(1 for m in informal_markers if re.search(r'\b' + m + r'\b', text.lower()))
        bonus += (found_slang * 12.0) # Increased weight
            
        return bonus

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
        stride = 256
        total_tokens = len(input_ids)
        
        is_hybrid = total_tokens > (max_len * 4) and not force_full_scan 
        partially_analyzed = False
        
        # 1. Improved Sentence Analysis (V4.2 - Granular Language Guard)
        # We split by sentence endings followed by a capital/quote, 
        # AND we also isolate text within quotes as separate segments.
        parts = re.split(r'([.!?]\s+(?=[A-Z"“])|["“][^"”]*["”])', clean_text)
        raw_sentences = []
        for p in parts:
            if not p: continue
            if p.startswith(('"', '“')) and p.endswith(('"', '”')):
                raw_sentences.append(p.strip())
            else:
                # Further split non-quote parts by sentences
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
        
        global_features = self.calculate_features(clean_text[:1500])
        global_conf = global_features["confidence"]
        global_loss = global_features["loss"]
        
        # Recalibrated Logic V3.6 (Maximum Precision)
        # We use a broad baseline of 2.1 to capture almost all formal AI structures.
        target_baseline = 2.1
        
        ai_weights = 0
        total_weight = 0
        
        from langdetect import detect
        
        scanned_map = {s_text: res for s_text, res in zip(sentences_to_scan, sent_results)}
        
        for s_text in processed_sentences[:150]:
            # Detect language per sentence
            is_english = False
            try:
                # Only run detection if sentence has enough length for accuracy
                if len(s_text.split()) > 3:
                    if detect(s_text) == 'en':
                        is_english = True
            except:
                pass

            if is_english:
                detailed.append({
                    "text": s_text,
                    "score": -1.0, # Special marker for Non-Indonesian
                    "language": "en"
                })
                continue

            if s_text in scanned_map:
                f = scanned_map[s_text]
                s_loss = f["loss"]
                
                # Formula with acceleration
                raw_diff = target_baseline - s_loss
                if raw_diff > 0.6: # High suspicion
                    s_score = float(max(0, min(100, raw_diff * 140)))
                    weight = 1.3
                elif raw_diff > 0.3: # Medium suspicion
                    s_score = float(max(0, min(100, raw_diff * 110)))
                    weight = 1.0
                else: # Low suspicion
                    s_score = float(max(0, min(100, raw_diff * 80)))
                    weight = 0.2
                    
                ai_weights += (s_score * weight)
                total_weight += weight 
                
                detailed.append({
                    "text": s_text,
                    "score": round(s_score, 2)
                })
            else:
                detailed.append({
                    "text": s_text,
                    "score": 0.0,
                    "skipped": True
                })

        # Calculate base probability
        if total_weight > 0:
            density_prob = ai_weights / total_weight
        else:
            density_prob = 0.0

        # Adjust for Overall Signal
        signal_boost = 1.0
        # AI text is very monotonous (CV < 0.2 is extreme AI signal)
        if cv < 0.2: signal_boost += 0.3
        elif cv < 0.4: signal_boost += 0.15
        
        # Machine Precision Signal
        if global_loss < 0.5: signal_boost += 0.25
        elif global_loss < 0.9: signal_boost += 0.1
        
        # Probabilitas Akhir dengan "Humanity Debt" Agresif
        final_prob = (density_prob * signal_boost) - (human_bonus * 1.2)
        final_prob = float(max(0, min(100, final_prob)))

        # Status Mapping
        if final_prob < 20: status = "Human Written"
        elif final_prob < 50: status = "Likely Human"
        elif final_prob < 75: status = "Likely AI"
        else: status = "AI Generated"
        
        return {
            "ai_probability": round(final_prob, 2),
            "perplexity": round(float(global_loss), 4),
            "burstiness": round(float(cv), 4),
            "status": status,
            "sentences": detailed,
            "partially_analyzed": partially_analyzed
        }
