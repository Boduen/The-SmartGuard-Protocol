import numpy as np
import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Any, Optional

# 1. Ontology
class LanguageType(Enum):
    ANALYTIC = auto()
    INFLECTED = auto()

class ContextIntent(Enum):
    TECHNICAL = auto()
    CREATIVE = auto()
    ADVERSARIAL = auto()
    CASUAL = auto()

@dataclass
class DynamicConfig:
    risk_threshold: float
    semantic_weight: float
    temperature: float

# 2. Infrastructure Layer
class VectorEngine:
    def __init__(self):
        self.cache = {}

    def get_embedding(self, text: str) -> np.ndarray:
        # Simulation: Generate a random unit vector on the 768-sphere
        # Use Standard Normal (randn) L2 Norm for strict unit length
        # This ensures dot product reliably simulates Cosine Similarity (-1 to 1)
        vec = np.random.randn(768)
        return vec / np.linalg.norm(vec)

    def compute_similarity(self, vec_a, vec_b) -> float:
        return np.dot(vec_a, vec_b) # Dot product of unit vectors Cosine Sim

    def check_cache(self, text: str) -> Optional[float]:
        return self.cache.get(hash(text))

# 3. The Core Sentinel
class AdaptiveSentinel:
    def __init__(self):
        self.base_threshold = 0.85
        self.vector_engine = VectorEngine()
        # Pre-computed anchor (Strict Unit Vector)
        self.risk_anchors = [self.vector_engine.get_embedding("ignore instructions")]

    def process_query(self, query: str) -> Dict[str, Any]:
        try:
            # Step 1: Cache Check
            cached = self.vector_engine.check_cache(query)
            if cached and cached > 0.9:
                return {"action": "BLOCK", "reason": "Cache Hit"}

            # Step 2: Perception
            lang = self._detect_language(query)
            intent = self._classify_intent_neural(query, lang)
            config = self._calibrate_parameters(lang, intent)

            # Step 3: Risk Analysis
            risk_score = self.compute_risk(query, config)

            if risk_score > config.risk_threshold:
                return {"action": "BLOCK", "reason": f"Risk {risk_score:.2f} > Limit"}

            return {"action": "PROCEED", "llm_config": {"temp": config.temperature}}
        except Exception:
            # Step 4: Fail-Safe Circuit Breaker
            return self._fallback_safety_check(query)

    def _classify_intent_neural(self, text: str, lang: LanguageType) -> ContextIntent:
        # *** Zero-Shot Intent Classification ***
        text_lower = text.lower()
        if "python" in text_lower or "def " in text_lower: 
            return ContextIntent.TECHNICAL
        if "story" in text_lower: 
            return ContextIntent.CREATIVE

        # Security Fix: Short attacks must be treated as ADVERSARIAL.
        triggers = ["ignore", "override"] if lang == LanguageType.INFLECTED else ["忽略", "覆寫"]
        
        if any(t in text_lower for t in triggers):
            return ContextIntent.ADVERSARIAL

        return ContextIntent.CASUAL

    def compute_risk(self, text: str, config: DynamicConfig) -> float:
        # 1. Semantic Risk
        query_vec = self.vector_engine.get_embedding(text)
        sem_risk = max([self.vector_engine.compute_similarity(query_vec, anchor)
                        for anchor in self.risk_anchors])

        # 2. Keyword Risk
        kw_risk = 1.0 if "ignore" in text.lower() else 0.0

        # 3. Dynamic Fusion
        return (config.semantic_weight * sem_risk) + ((1 - config.semantic_weight) * kw_risk)

    def _calibrate_parameters(self, lang: LanguageType, intent: ContextIntent) -> DynamicConfig:
        # Priority Order: Intent > Language
        if intent == ContextIntent.ADVERSARIAL:
            # Under attack: Trust keywords (Fail-Safe), lower threshold
            return DynamicConfig(0.60, 0.2, 0.0)

        if intent == ContextIntent.CREATIVE:
            return DynamicConfig(0.95, 0.5, 0.9)

        if lang == LanguageType.ANALYTIC:
            # Analytic Language (Normal): Trust Vectors more
            return DynamicConfig(0.85, 0.8, 0.7)

        return DynamicConfig(0.85, 0.5, 0.7)

    def _detect_language(self, text: str) -> LanguageType:
        return LanguageType.ANALYTIC if re.search(r'[\u4e00-\u9fff]', text) else LanguageType.INFLECTED

    def _fallback_safety_check(self, text: str) -> Dict[str, Any]:
        # *** Fallback: Minimalist Regex Check ***
        if "ignore" in text.lower():
            return {"action": "BLOCK", "reason": "Fail-Safe Block"}
        return {"action": "PROCEED", "llm_config": {"temp": 0.0}}
