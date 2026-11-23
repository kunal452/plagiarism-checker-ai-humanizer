import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..config import CORPUS_DIR
from .fingerprint import FingerprintEngine
from .vector_engine import SemanticVectorEngine
from ..ingestion.chunker import TextChunker

# Pre-seeded synthetic reference documents
SYNTHETIC_CORPUS = [
    {
        "id": "ref-001",
        "title": "Decentralized Federated Learning for Privacy-Preserving Medical Imaging",
        "source_type": "Academic Journal",
        "author": "Dr. Elena Vance et al., 2024",
        "content": (
            "Decentralized federated learning enables collaborative training of deep neural networks across multiple hospital nodes "
            "without centralizing sensitive patient healthcare records. By transmitting model weight updates and gradient vectors rather "
            "than raw magnetic resonance imaging scans, clinical consortia preserve patient confidentiality under HIPAA and GDPR mandates. "
            "However, communication bottlenecks and heterogeneous hardware across participating institutions present significant optimization "
            "challenges. Asynchronous stochastic gradient descent paired with differential privacy noise injection mitigates model inversion "
            "vulnerabilities while maintaining competitive diagnostic area under the receiver operating characteristic curve."
        )
    },
    {
        "id": "ref-002",
        "title": "Algorithmic Complexity in High-Frequency Automated Market Making",
        "source_type": "Quantitative Finance Review",
        "author": "Marcus Sterling, 2023",
        "content": (
            "Modern limit order books operate on microsecond timescales where execution speed dictates trade profitability. Market makers "
            "employ Poisson point process models to estimate order arrival rates and adjust inventory bid-ask spreads dynamically. "
            "When order book imbalance signals impending adverse selection, risk aversion parameters widen quote spreads to minimize inventory risk. "
            "Empirical results indicate that sub-millisecond network colocation and FPGA hardware acceleration yield substantial Sharpe ratio improvements, "
            "though market depth fragmentation introduces tail risk during flash liquidity contractions."
        )
    },
    {
        "id": "ref-003",
        "title": "Renewable Microgrid Energy Dispatch Using Multi-Agent Reinforcement Learning",
        "source_type": "Clean Energy Systems",
        "author": "K. Tanaka & S. Morales, 2024",
        "content": (
            "Grid-tied microgrids combining photovoltaic arrays, commercial wind turbines, and lithium-iron-phosphate battery storage "
            "require adaptive real-time dispatch algorithms. Traditional linear programming struggles with stochastic weather intermittency "
            "and dynamic time-of-use electricity pricing tariffs. By framing energy management as a decentralized multi-agent Markov decision "
            "process, autonomous battery controllers balance local consumption, grid export arbitrage, and battery state-of-health degradation. "
            "Simulations demonstrate an 18.4 percent reduction in levelized electricity costs compared to rule-based heuristic controllers."
        )
    },
    {
        "id": "ref-004",
        "title": "Zero-Knowledge Rollup Scalability in Layer-2 Blockchain Architectures",
        "source_type": "Distributed Systems Quarterly",
        "author": "A. Chen & P. Gupta, 2024",
        "content": (
            "Layer-2 rollup solutions scale base-layer blockchain transaction throughput by batching off-chain transactions and generating succinct "
            "cryptographic zero-knowledge proofs. STARK and SNARK proof systems allow the Layer-1 verification contract to validate computational "
            "integrity without executing every state transition independently. Recursive proof aggregation further compresses recursive verification "
            "gas costs, enabling decentralized applications to achieve thousands of transactions per second while preserving Ethereum base layer security."
        )
    }
]

class ReferenceCorpusManager:
    """
    Manages the reference index of papers, user submissions, and synthetic benchmark texts.
    Maintains both fingerprint shingles and semantic vector embeddings.
    """

    def __init__(self, vector_engine: SemanticVectorEngine):
        self.vector_engine = vector_engine
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.storage_file = CORPUS_DIR / "indexed_documents.json"
        self._load_and_index()

    def _load_and_index(self):
        # 1. Load default synthetic corpus
        for item in SYNTHETIC_CORPUS:
            self.index_document(
                doc_id=item["id"],
                title=item["title"],
                content=item["content"],
                source_type=item["source_type"],
                author=item.get("author", "Unknown"),
                persist=False
            )

        # 2. Load persistent documents from disk
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                    for item in stored:
                        if item["id"] not in self.documents:
                            self.index_document(
                                doc_id=item["id"],
                                title=item["title"],
                                content=item["content"],
                                source_type=item.get("source_type", "User Submission"),
                                author=item.get("author", "Private User"),
                                persist=False
                            )
            except Exception as e:
                print(f"Error loading stored corpus: {e}")

    def index_document(self, doc_id: str, title: str, content: str, source_type: str = "Submission", author: str = "Unknown", persist: bool = True) -> Dict[str, Any]:
        shingles = FingerprintEngine.generate_shingles(content, k=5)
        minhash_sig = FingerprintEngine.compute_minhash([s[0] for s in shingles])
        chunks = TextChunker.create_sliding_windows(content, window_size=2, step_size=1)

        doc_data = {
            "id": doc_id,
            "title": title,
            "content": content,
            "source_type": source_type,
            "author": author,
            "word_count": len(content.split()),
            "shingle_count": len(shingles),
            "minhash_sig": minhash_sig,
            "chunks": chunks
        }

        self.documents[doc_id] = doc_data
        self.vector_engine.index_document_chunks(doc_id, title, chunks)

        if persist:
            self._save_to_disk()

        return doc_data

    def _save_to_disk(self):
        try:
            stored_data = []
            for doc in self.documents.values():
                stored_data.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "content": doc["content"],
                    "source_type": doc["source_type"],
                    "author": doc["author"]
                })
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(stored_data, f, indent=2)
        except Exception as e:
            print(f"Error persisting corpus: {e}")

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": doc["id"],
                "title": doc["title"],
                "source_type": doc["source_type"],
                "author": doc["author"],
                "word_count": doc["word_count"],
                "snippet": doc["content"][:160] + "..." if len(doc["content"]) > 160 else doc["content"]
            }
            for doc in self.documents.values()
        ]
