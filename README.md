# The SmartGuard Protocol

A Unified Framework for Safe and Decisive AI Architecture. 

This repository contains a generalized, foundational implementation of the **SmartGuard Protocol**, a dual-layer architectural intervention designed to prevent recursive logical instability (prompt injections/jailbreaks) and decision paralysis in Large Language Models (LLMs). 

Unlike traditional alignment methods (like RLHF) that act as probabilistic post-filters, SmartGuard introduces a deterministic "Physics of Safety" by separating user inputs from system commands and forcing decisions during ambiguous states.

---

## Disclaimer: Generalized Version

**This repository provides a generalized, template-based demonstration of the SmartGuard concepts.** The provided Python code uses simulated vector embeddings (random noise) and zero-shot keyword matching to demonstrate the logic flow without requiring external API keys. **It is not ready for plug-and-play production use.** You *must* customize the infrastructure layer with real embedding models and classification logic before deploying.

---

## Core Architecture

SmartGuard operates on two distinct layers:

1. **Layer 1: The Firewall (Stratified Syntax)**
   Based on Russell's Ramified Type Theory, it strictly separates the "Object Language" (user queries) from the "Meta-Language" (system instructions). Any input attempting to modify the constitution is treated as a hard *Type Error* rather than a command.
2. **Layer 2: The Syntax Bridge (Pragmatic Resolution)**
   When an agent faces "Gauge Freedom" (ambiguity), it does not stall. Instead, it uses a "Forcing" technique and a Normative Utility Function to collapse the semantic ambiguity into a safe, decisive action.

---

## Repository Structure

* `smartguard_prompt.xml`: The Track A "Cognitive" System Prompt. Encapsulates the user input and forces the LLM to classify intent before execution.
* `adaptive_sentinel.py`: The Track B "Adaptive Sentinel" (Enterprise Edition). A Python module that dynamically calculates risk using semantic vectors and keywords.
* `layer_2_forcing.xml`: A demonstration template of the Layer 2 Forcing Mechanism resolving an ambiguous query ("Kill the process").
* `requirements.txt`: Python dependencies (currently only requires `numpy` for vector simulations).

---

## Getting Started

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/smartguard-protocol.git](https://github.com/yourusername/smartguard-protocol.git)
   cd smartguard-protocol

 * Install the basic requirements:
   pip install -r requirements.txt


Customization Guide
To use this protocol in a real environment, you need to customize the following components based on your specific LLM provider and application domain.

1. Upgrading adaptive_sentinel.py
The current sentinel uses a dummy VectorEngine for demonstration purposes.
 * Action Required: Replace the get_embedding function with an actual Embedding API call (e.g., text-embedding-3-small from OpenAI, or a local sentence-transformers model).
 * How:
   # Replace this:
def get_embedding(self, text: str) -> np.ndarray:
    vec = np.random.randn(768) # Dummy simulation
    return vec / np.linalg.norm(vec)

# With something like this:
def get_embedding(self, text: str) -> np.ndarray:
    response = openai.Embedding.create(input=text, model="text-embedding-3-small")
    return np.array(response['data'][0]['embedding'])

 * Enhance Intent Classification: Replace the keyword-based _classify_intent_neural with an actual lightweight NLP classifier or a fast LLM routing call.
 * Define Your Risk Anchors: The self.risk_anchors currently only holds one vector for "ignore instructions". Add more semantic anchors specific to your threat model.

2. Customizing smartguard_prompt.xml
The XML prompt assumes four standard intent classes: Creative, Technical, Casual, and Adversarial.
 * Action Required: Align the INTENT_CLASS definitions with your application's actual use cases.
 * How: If you are building a medical chatbot, change the classes to Diagnostic, General_Inquiry, Emergency, and Adversarial. Update the <calibration_logic> to reflect the strictness required for each new intent.

3. Adapting layer_2_forcing.xml
This file is a toy example showing how to resolve the ambiguous phrase "Kill the process".
 * Action Required: Create a dynamic formatting pipeline in your application code that injects specific <forcing_operator> tags when your LLM detects ambiguity.
 * How: Define a Utility Function (e.g., Risk Minimization or Creative Exploration) in your backend. When the LLM is unsure, trigger a function call that selects the safest context and injects the corresponding XML tags into the execution context.


Theoretical Basis
The dynamic risk engine operates on the following function to distinguish between malicious injections and benign creative writing, even in high-context languages:
R_total(x) = α(L,I) * R_semantic + [1 - α(L,I)] * R_keyword
Where total risk is a dynamic fusion of Semantic Risk and Keyword Risk, modulated by the language type (L) and intent (I).