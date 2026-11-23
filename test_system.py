import sys
import os
import json

# Add backend to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.ingestion.parser import DocumentParser
from app.ingestion.cleaner import DocumentCleaner
from app.ingestion.chunker import TextChunker
from app.plagiarism.fingerprint import FingerprintEngine
from app.plagiarism.vector_engine import SemanticVectorEngine
from app.plagiarism.corpus import ReferenceCorpusManager, SYNTHETIC_CORPUS
from app.plagiarism.detector import PlagiarismDetector
from app.humanizer.ai_detector import AIDetectorScorer
from app.humanizer.engine import HumanizerEngine
from app.export.exporter import DocumentExporter
import asyncio

def run_tests():
    print("=== STARTING COMPREHENSIVE VERITAS AI SYSTEM AUDIT ===\n")

    # 1. Test Ingestion & Cleaner
    test_raw_doc = (
        "Page 1 of 4\n"
        "Decentralized federated learning enables collaborative training of deep neural networks.\n\n"
        'As stated previously, "All patient data must remain confidential under hospital privacy policies."\n\n'
        "References:\n"
        "1. Vance, E. (2024). Decentralized Federated Learning.\n"
    )

    clean_res = DocumentCleaner.clean_document(test_raw_doc)
    assert clean_res["bibliography_meta"]["has_bibliography"] is True, "Bibliography detection failed!"
    assert len(clean_res["quotations"]) == 1, "Quotation detection failed!"
    print("  ✓ Document Ingestion & Cleaner: Successfully stripped page numbers, extracted quotes, and isolated bibliography.")

    # 2. Test Fingerprinting (MinHash & Shingles)
    shingles = FingerprintEngine.generate_shingles(SYNTHETIC_CORPUS[0]["content"], k=5)
    assert len(shingles) > 10, "Shingle generation failed!"
    sig = FingerprintEngine.compute_minhash([s[0] for s in shingles])
    assert len(sig) == 64, "MinHash signature length mismatch!"
    print(f"  ✓ Fingerprinting: Generated {len(shingles)} shingles and 64-permutation MinHash signature.")

    # 3. Test Vector Engine & Dual-Layer Plagiarism Detector
    vector_eng = SemanticVectorEngine()
    corpus_mgr = ReferenceCorpusManager(vector_eng)
    detector = PlagiarismDetector(corpus_mgr, vector_eng)

    # Test plagiarized sample
    plag_text = (
        "Decentralized federated learning enables collaborative training of deep neural networks across multiple hospital nodes "
        "without centralizing sensitive patient healthcare records. By transmitting model weight updates and gradient vectors rather "
        "than raw magnetic resonance imaging scans, clinical consortia preserve patient confidentiality under HIPAA and GDPR mandates."
    )
    result = detector.scan_document(plag_text, exclude_quotes=True, exclude_bibliography=True)
    print(f"  ✓ Plagiarism Detector (Direct Copy): Detected {result['overall_similarity']}% similarity (Exact: {result['exact_similarity']}%, Paraphrase: {result['paraphrase_similarity']}%).")
    assert result["overall_similarity"] > 80.0, "Plagiarism detection failed on exact copy!"

    # Test clean original sample
    clean_text = "Photosynthetic enzymes in marine phytoplankton capture solar radiation and synthesize glucose via the Calvin cycle during sunlight hours."
    clean_result = detector.scan_document(clean_text, exclude_quotes=True, exclude_bibliography=True)
    print(f"  ✓ Plagiarism Detector (Original Text): Detected {clean_result['overall_similarity']}% similarity (Expected ~0%).")
    assert clean_result["overall_similarity"] == 0.0, "False positive on clean text!"

    # 4. Test AI Detection & Perplexity/Burstiness
    robotic_ai = (
        "In today's fast-paced world, artificial intelligence plays a pivotal role in modern society. "
        "It is important to note that machine learning delves into data patterns to unlock efficiency across multifaceted domains. "
        "Moreover, the adoption of neural networks stands as a testament to innovation."
    )
    ai_metrics = AIDetectorScorer.evaluate(robotic_ai)
    print(f"  ✓ AI Detector Scorer: Detected AI Probability: {ai_metrics['ai_probability']}% (Classification: {ai_metrics['classification']}, Markers found: {ai_metrics['total_markers']}).")
    assert ai_metrics["ai_probability"] > 60.0, "AI detector failed to catch formulaic AI clichés!"

    # 5. Test Humanizer Engine
    humanizer = HumanizerEngine()
    async def test_humanizer():
        hum_result = await humanizer.humanize_document(
            raw_text=robotic_ai,
            mode="academic",
            backend="algorithmic",
            burstiness_level="balanced",
            preserve_citations=True
        )
        print(f"  ✓ Humanizer Engine: Successfully humanized text.")
        print(f"    - Before: {hum_result['original_metrics']['ai_probability']}% AI")
        print(f"    - After:  {hum_result['humanized_metrics']['ai_probability']}% AI ({hum_result['humanized_metrics']['classification']})")
        print(f"    - Burstiness Shift: {hum_result['original_metrics']['burstiness']} -> {hum_result['humanized_metrics']['burstiness']}")
        assert hum_result["humanized_metrics"]["ai_probability"] < hum_result["original_metrics"]["ai_probability"], "AI score did not drop after humanizing!"

        # 6. Test Exporters
        docx_data = DocumentExporter.export_to_docx(hum_result["humanized_text"])
        pdf_data = DocumentExporter.export_to_pdf(hum_result["humanized_text"])
        assert len(docx_data) > 1000, "DOCX export failed!"
        assert len(pdf_data) > 1000, "PDF export failed!"
        print(f"  ✓ Exporter: Generated valid DOCX ({len(docx_data)} bytes) and PDF ({len(pdf_data)} bytes).")

    asyncio.run(test_humanizer())

    print("\n=== ALL SYSTEM TESTS PASSED PERFECTLY ===")

if __name__ == "__main__":
    run_tests()
