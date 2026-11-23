import re
import math
from typing import Dict, Any, List

class AIDetectorScorer:
    """
    Evaluates Perplexity, Burstiness, and Lexical AI Indicators:
    - AI detectors (e.g., Turnitin AI, GPTZero) flag text with uniform sentence lengths (low burstiness)
      and highly predictable token sequences (low perplexity).
    - Human writing exhibits high variance in sentence length, natural conversational rhythms,
      and diverse vocabulary.
    """

    AI_MARKER_WORDS = {
        "delve", "delves", "delving", "tapestry", "testament", "moreover", "furthermore",
        "in conclusion", "it is crucial to", "it is important to note", "multifaceted",
        "pivotal", "beacon", "foster", "fostering", "intertwined", "game-changer",
        "revolutionize", "underscore", "underscores", "paramount", "nuanced",
        "holistic", "realm", "harness", "harnessing", "unravel", "unraveling",
        "vital role", "beacon of", "rich tapestry", "testament to"
    }

    @classmethod
    def calculate_sentence_metrics(cls, text: str) -> Dict[str, Any]:
        raw_sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if not raw_sentences:
            return {"count": 0, "mean_len": 0, "std_dev": 0, "burstiness": 0.0}

        word_counts = [len(s.split()) for s in raw_sentences]
        mean_len = sum(word_counts) / len(word_counts)

        # Variance and standard deviation of sentence lengths
        variance = sum((w - mean_len) ** 2 for w in word_counts) / max(1, len(word_counts))
        std_dev = math.sqrt(variance)

        # Burstiness metric = std_dev / mean_len (higher is more human-like)
        burstiness = round(std_dev / max(1.0, mean_len), 3)

        return {
            "count": len(raw_sentences),
            "lengths": word_counts,
            "mean_len": round(mean_len, 1),
            "std_dev": round(std_dev, 2),
            "burstiness": burstiness
        }

    @classmethod
    def count_ai_markers(cls, text: str) -> Dict[str, Any]:
        lower_text = text.lower()
        found_markers = []
        for marker in cls.AI_MARKER_WORDS:
            occurrences = len(re.findall(r'\b' + re.escape(marker) + r'\b', lower_text))
            if occurrences > 0:
                found_markers.append({"marker": marker, "count": occurrences})

        return {
            "total_markers": sum(m["count"] for m in found_markers),
            "markers": found_markers
        }

    @classmethod
    def estimate_perplexity_score(cls, text: str) -> float:
        """
        Estimates vocabulary diversity and syntactic unpredictability on a 0-100 scale.
        """
        words = re.findall(r'[a-zA-Z]+', text.lower())
        if not words:
            return 50.0

        total_words = len(words)
        unique_words = len(set(words))
        # Type-Token Ratio (TTR)
        ttr = unique_words / total_words

        # Long word frequency (words > 7 chars)
        long_words = sum(1 for w in words if len(w) > 7) / total_words

        raw_score = (ttr * 60) + (long_words * 40)
        return min(100.0, max(10.0, round(raw_score, 1)))

    @classmethod
    def evaluate(cls, text: str) -> Dict[str, Any]:
        """
        Calculates comprehensive AI vs Human probability score.
        Low burstiness + high AI markers + low perplexity = High AI probability.
        High burstiness + zero AI markers + varied syntax = Low AI (Human) probability.
        """
        if not text.strip():
            return {
                "ai_probability": 0.0,
                "classification": "Human",
                "burstiness": 0.0,
                "perplexity": 0.0,
                "detected_markers": []
            }

        sent_metrics = cls.calculate_sentence_metrics(text)
        ai_markers = cls.count_ai_markers(text)
        perplexity = cls.estimate_perplexity_score(text)

        # Baseline AI probability
        prob = 50.0

        # Burstiness penalty/bonus:
        # Uniform length (<0.35 burstiness) strongly indicates LLM generation
        # Varied length (>0.60 burstiness) indicates human generation
        b = sent_metrics["burstiness"]
        if b < 0.25:
            prob += 30.0
        elif b < 0.40:
            prob += 15.0
        elif b > 0.65:
            prob -= 30.0
        elif b > 0.50:
            prob -= 15.0

        # AI marker penalty
        marker_impact = min(35.0, ai_markers["total_markers"] * 7.5)
        prob += marker_impact

        # Perplexity adjustment
        if perplexity < 35.0:
            prob += 15.0
        elif perplexity > 55.0:
            prob -= 15.0

        final_ai_prob = min(99.0, max(2.0, round(prob, 1)))

        if final_ai_prob >= 70.0:
            classification = "Likely AI-Generated"
        elif final_ai_prob >= 40.0:
            classification = "Mixed / Moderately AI"
        else:
            classification = "Likely Human-Written"

        return {
            "ai_probability": final_ai_prob,
            "classification": classification,
            "burstiness": sent_metrics["burstiness"],
            "sentence_std_dev": sent_metrics["std_dev"],
            "mean_sentence_length": sent_metrics["mean_len"],
            "perplexity_estimate": perplexity,
            "detected_markers": ai_markers["markers"],
            "total_markers": ai_markers["total_markers"]
        }
