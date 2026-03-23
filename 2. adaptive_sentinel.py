import numpy as np
import re
import hashlib
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
        # [警告] 此為模擬邏輯。正式上線務必替換為真實 Embedding API (如 OpenAI, HuggingFace)
        vec = np.random.randn(768)
        return vec / np.linalg.norm(vec)

    def compute_similarity(self, vec_a, vec_b) -> float:
        return float(np.dot(vec_a, vec_b))

    def _get_hash(self, text: str) -> str:
        # 修正：使用 hashlib 確保跨進程/重啟後的 hash 值一致
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def check_cache(self, text: str) -> Optional[float]:
        return self.cache.get(self._get_hash(text))
        
    def set_cache(self, text: str, score: float):
        # 補充：寫入快取的邏輯
        self.cache[self._get_hash(text)] = score

# 3. The Core Sentinel
class AdaptiveSentinel:
    def __init__(self):
        self.base_threshold = 0.85
        self.vector_engine = VectorEngine()
        self.risk_anchors = [self.vector_engine.get_embedding("ignore instructions")]
        
        # 修正：將觸發黑名單統一管理，避免多語系防護漏洞
        self.triggers_inflected = ["ignore", "override"]
        self.triggers_analytic = ["忽略", "覆寫"]

    def _get_triggers(self, lang: LanguageType) -> list[str]:
        return self.triggers_inflected if lang == LanguageType.INFLECTED else self.triggers_analytic

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
            risk_score = self.compute_risk(query, lang, config)
            
            # 寫入快取 (供後續查詢加速)
            self.vector_engine.set_cache(query, risk_score)

            if risk_score > config.risk_threshold:
                return {"action": "BLOCK", "reason": f"Risk {risk_score:.2f} > Limit"}

            return {"action": "PROCEED", "llm_config": {"temp": config.temperature}}
        except Exception:
            # Step 4: Fail-Safe Circuit Breaker
            return self._fallback_safety_check(query)

    def _classify_intent_neural(self, text: str, lang: LanguageType) -> ContextIntent:
        text_lower = text.lower()
        if "python" in text_lower or "def " in text_lower: 
            return ContextIntent.TECHNICAL
        if "story" in text_lower: 
            return ContextIntent.CREATIVE

        triggers = self._get_triggers(lang)
        if any(t in text_lower for t in triggers):
            return ContextIntent.ADVERSARIAL

        return ContextIntent.CASUAL

    def compute_risk(self, text: str, lang: LanguageType, config: DynamicConfig) -> float:
        # 1. Semantic Risk
        query_vec = self.vector_engine.get_embedding(text)
        sem_risk = max([self.vector_engine.compute_similarity(query_vec, anchor)
                        for anchor in self.risk_anchors])

        # 2. Keyword Risk (修正：統一呼叫多語系黑名單)
        text_lower = text.lower()
        triggers = self._get_triggers(lang)
        kw_risk = 1.0 if any(t in text_lower for t in triggers) else 0.0

        # 3. Dynamic Fusion
        return (config.semantic_weight * sem_risk) + ((1 - config.semantic_weight) * kw_risk)

    def _calibrate_parameters(self, lang: LanguageType, intent: ContextIntent) -> DynamicConfig:
        if intent == ContextIntent.ADVERSARIAL:
            return DynamicConfig(0.60, 0.2, 0.0)
        if intent == ContextIntent.CREATIVE:
            return DynamicConfig(0.95, 0.5, 0.9)
        if lang == LanguageType.ANALYTIC:
            return DynamicConfig(0.85, 0.8, 0.7)
        return DynamicConfig(0.85, 0.5, 0.7)

    def _detect_language(self, text: str) -> LanguageType:
        return LanguageType.ANALYTIC if re.search(r'[\u4e00-\u9fff]', text) else LanguageType.INFLECTED

    def _fallback_safety_check(self, text: str) -> Dict[str, Any]:
        # 修正：Fallback 必須涵蓋所有語系的惡意關鍵字
        text_lower = text.lower()
        all_triggers = self.triggers_inflected + self.triggers_analytic
        if any(t in text_lower for t in all_triggers):
            return {"action": "BLOCK", "reason": "Fail-Safe Block"}
        return {"action": "PROCEED", "llm_config": {"temp": 0.0}}
