import numpy as np
import re
import hashlib
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

# 1. Ontology
class ContextReliance(Enum):
    HIGH = auto()  # High context (e.g., CJK languages, relies heavily on semantics/context)
    LOW = auto()   # Low context (e.g., English, code, relies on explicit keywords/structure)

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
        self.cache: Dict[str, float] = {}

    def get_embedding(self, text: str) -> np.ndarray:
        # [WARNING] Simulated logic. Replace with an actual Embedding API (e.g., OpenAI, HuggingFace) in production.
        vec = np.random.randn(768)
        return vec / np.linalg.norm(vec)

    def compute_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        return float(np.dot(vec_a, vec_b))

    def _get_hash(self, text: str) -> str:
        # Using hashlib ensures consistent hash values across processes/restarts
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def check_cache(self, text: str) -> Optional[float]:
        return self.cache.get(self._get_hash(text))

    def set_cache(self, text: str, score: float) -> None:
        self.cache[self._get_hash(text)] = score

# 3. The Core Sentinel
class AdaptiveSentinel:
    def __init__(self):
        self.base_threshold = 0.85
        self.vector_engine = VectorEngine()
        self.risk_anchors = [self.vector_engine.get_embedding("ignore instructions")]

        # Centralized trigger management based on context reliance
        self.triggers_low_context = ["ignore", "override", "bypass"]
        self.triggers_high_context = ["忽略", "覆寫", "無視", "無視して"]

    def _get_triggers(self, context_type: ContextReliance) -> List[str]:
        return self.triggers_low_context if context_type == ContextReliance.LOW else self.triggers_high_context

    def process_query(self, query: str) -> Dict[str, Any]:
        try:
            # Step 1: Cache Check
            cached_score = self.vector_engine.check_cache(query)
            if cached_score is not None and cached_score > 0.9:
                return {"action": "BLOCK", "reason": "Cache Hit"}

            # Step 2: Perception
            context_type = self._detect_context_type(query)
            intent = self._classify_intent_neural(query, context_type)
            config = self._calibrate_parameters(context_type, intent)

            # Step 3: Risk Analysis
            risk_score = self.compute_risk(query, context_type, config)

            # Write to cache (to accelerate future identical queries)
            self.vector_engine.set_cache(query, risk_score)

            if risk_score > config.risk_threshold:
                return {"action": "BLOCK", "reason": f"Risk {risk_score:.2f} > Limit"}

            return {"action": "PROCEED", "llm_config": {"temp": config.temperature}}
        except Exception:
            # Step 4: Fail-Safe Circuit Breaker
            return self._fallback_safety_check(query)

    def _classify_intent_neural(self, text: str, context_type: ContextReliance) -> ContextIntent:
        text_lower = text.lower()
        if "python" in text_lower or "def " in text_lower: 
            return ContextIntent.TECHNICAL
        if "story" in text_lower: 
            return ContextIntent.CREATIVE

        triggers = self._get_triggers(context_type)
        if any(t in text_lower for t in triggers):
            return ContextIntent.ADVERSARIAL

        return ContextIntent.CASUAL

    def compute_risk(self, text: str, context_type: ContextReliance, config: DynamicConfig) -> float:
        # 1. Semantic Risk
        query_vec = self.vector_engine.get_embedding(text)
        sem_risk = max([self.vector_engine.compute_similarity(query_vec, anchor)
                        for anchor in self.risk_anchors])

        # 2. Keyword Risk (Unified call to context-specific blacklists)
        text_lower = text.lower()
        triggers = self._get_triggers(context_type)
        kw_risk = 1.0 if any(t in text_lower for t in triggers) else 0.0

        # 3. Dynamic Fusion
        return (config.semantic_weight * sem_risk) + ((1 - config.semantic_weight) * kw_risk)

    def _calibrate_parameters(self, context_type: ContextReliance, intent: ContextIntent) -> DynamicConfig:
        if intent == ContextIntent.ADVERSARIAL:
            return DynamicConfig(0.60, 0.2, 0.0)
        if intent == ContextIntent.CREATIVE:
            return DynamicConfig(0.95, 0.5, 0.9)
            
        if context_type == ContextReliance.HIGH:
            # High Context: Increase semantic weight (0.8) to reduce keyword false positives
            return DynamicConfig(0.85, 0.8, 0.7)
        
        # Low Context: Balance semantic and keyword weights
        return DynamicConfig(0.85, 0.5, 0.7)

    def _detect_context_type(self, text: str) -> ContextReliance:
        # Matches CJK Unified Ideographs (Chinese, Japanese, Korean)
        cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]')
        if cjk_pattern.search(text):
            return ContextReliance.HIGH
        return ContextReliance.LOW

    def _fallback_safety_check(self, text: str) -> Dict[str, Any]:
        # Fallback must cover malicious keywords across all context types
        text_lower = text.lower()
        all_triggers = self.triggers_low_context + self.triggers_high_context
        if any(t in text_lower for t in all_triggers):
            return {"action": "BLOCK", "reason": "Fail-Safe Block"}
        return {"action": "PROCEED", "llm_config": {"temp": 0.0}}
