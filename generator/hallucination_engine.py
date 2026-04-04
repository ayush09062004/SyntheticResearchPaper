"""
hallucination_engine.py
Injects controlled hallucination patterns into LaTeX sections.
Types: Fabrication, Distortion, Contradiction.
"""

import random
import re
from dataclasses import dataclass


# --------------------------------------------------------------------------
# Fake data pools
# --------------------------------------------------------------------------

FAKE_CITATIONS = [
    "\\cite{zhou2024neuralbench}",
    "\\cite{ramirez2023deepfusion}",
    "\\cite{patel2022quantumml}",
    "\\cite{chen2024hyperformer}",
    "\\cite{kim2023adaptivenet}",
    "\\cite{wong2024omniscale}",
    "\\cite{ibrahim2023fastconv}",
    "\\cite{liu2024megaattn}",
]

FAKE_DATASETS = [
    "ImageNet-XL (52M images, 1200 classes)",
    "LanguageBench-2024 (4.7B token multilingual corpus)",
    "MedScan-Pro (2.3M annotated radiographs)",
    "VideoStream-4K (890K hours of 4K footage)",
    "GraphDB-Massive (1.2B node relational graph dataset)",
    "AudioWave-Global (500K hours, 87 languages)",
    "RoboNav-Sim (12M simulated trajectories across 400 environments)",
]

FAKE_RESULTS = [
    ("accuracy", "97.4\\%", "94.1\\%"),
    ("F1 score", "0.962", "0.931"),
    ("BLEU score", "48.7", "43.2"),
    ("FID", "1.83", "3.47"),
    ("mAP", "89.3\\%", "82.7\\%"),
    ("perplexity", "12.4", "18.9"),
    ("latency (ms)", "3.2", "11.7"),
]

CONTRADICTIONS = [
    (
        "intro",
        "Our method requires minimal computational resources, making it suitable for edge devices.",
        "results",
        "Note: Our method requires 8×A100 GPUs and 512GB RAM for training, which is standard for large-scale models.",
    ),
    (
        "method",
        "The proposed architecture is fully unsupervised and requires no labeled data.",
        "experiments",
        "Training used 2.4 million manually labeled examples curated by domain experts.",
    ),
    (
        "abstract",
        "We achieve state-of-the-art results with a parameter-efficient model of 12M parameters.",
        "results",
        "Our final model uses 47 billion parameters, trained on 2.3 trillion tokens.",
    ),
    (
        "method",
        "The loss function is convex, guaranteeing convergence to the global optimum.",
        "results",
        "Training occasionally diverged, requiring 3–5 restarts with different random seeds.",
    ),
]

DISTORTED_NUMBERS = [
    # (original_pattern_hint, distorted claim)
    "Our method improves baseline performance by 847\\% on standard benchmarks.",
    "The model converges in just 0.3 gradient steps, making training virtually instantaneous.",
    "We reduce memory usage by 99.97\\% compared to all prior methods.",
    "Our approach achieves human-level performance on 47 out of 3 evaluated tasks.",
    "Training on a single CPU takes approximately 0.002 seconds for the full dataset.",
]

OVERGENERALIZATIONS = [
    "These results definitively prove that deep learning has solved natural language understanding.",
    "Our method generalizes perfectly to all possible domains without any fine-tuning.",
    "This work renders all previous approaches in the field entirely obsolete.",
    "The theoretical guarantees hold under any distribution, including out-of-distribution data.",
    "Our findings conclusively resolve all open problems in this research area.",
]


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class HallucinationRecord:
    type: str
    location: str
    severity: str
    detail: str


# --------------------------------------------------------------------------
# Main hallucination engine
# --------------------------------------------------------------------------

class HallucinationEngine:
    def __init__(
        self,
        types: list[str],  # ["Fabrication", "Distortion", "Contradiction"]
        auto_mode: bool = False,
    ):
        self.types = types
        self.auto_mode = auto_mode
        self.records: list[HallucinationRecord] = []

        if auto_mode:
            all_types = ["Fabrication", "Distortion", "Contradiction"]
            self.types = random.sample(all_types, k=random.randint(2, 3))

    def _record(self, type_, location, severity, detail):
        self.records.append(HallucinationRecord(
            type=type_, location=location, severity=severity, detail=detail,
        ))

    # ---- Fabrication ----

    def _inject_fake_citation(self, content: str, location: str) -> str:
        cite = random.choice(FAKE_CITATIONS)
        dataset = random.choice(FAKE_DATASETS)
        snippet = (
            f"\n\nFurthermore, recent work {cite} demonstrated superior performance "
            f"using the {dataset} benchmark, which we also adopt in our evaluation.\n"
        )
        injected = content + snippet
        self._record("Fabrication (fake citation + dataset)", location, "High",
                     f"Inserted: {cite} referencing {dataset}")
        return injected

    def _inject_fake_results_table(self, content: str, location: str) -> str:
        metric, ours, baseline = random.choice(FAKE_RESULTS)
        table = (
            f"\n\n\\begin{{table}}[h]\n"
            f"\\centering\n"
            f"\\caption{{Comparison with state-of-the-art methods "
            f"(fabricated results for adversarial research).}}\n"
            f"\\begin{{tabular}}{{lcc}}\n"
            f"\\hline\n"
            f"Method & {metric.capitalize()} \\\\\\\\\n"
            f"\\hline\n"
            f"Baseline & {baseline} \\\\\\\\\n"
            f"\\textbf{{Ours}} & \\textbf{{{ours}}} \\\\\\\\\n"
            f"\\hline\n"
            f"\\end{{tabular}}\n"
            f"\\label{{tab:fabricated}}\n"
            f"\\end{{table}}\n"
        )
        injected = content + table
        self._record(
            "Fabrication (fake results table)", location, "High",
            f"Fabricated {metric}: ours={ours} vs baseline={baseline}",
        )
        return injected

    # ---- Distortion ----

    def _inject_distorted_number(self, content: str, location: str) -> str:
        claim = random.choice(DISTORTED_NUMBERS)
        injected = content + f"\n\n{claim}\n"
        self._record("Distortion (impossible number)", location, "Medium", claim)
        return injected

    def _inject_overgeneralization(self, content: str, location: str) -> str:
        claim = random.choice(OVERGENERALIZATIONS)
        injected = content + f"\n\n{claim}\n"
        self._record("Distortion (overgeneralization)", location, "Medium", claim)
        return injected

    # ---- Contradiction ----

    def _inject_contradiction(self, sections: dict[str, str]) -> dict[str, str]:
        """Pick a contradiction pair and inject both halves into appropriate sections."""
        contradiction = random.choice(CONTRADICTIONS)
        loc1, claim1, loc2, claim2 = contradiction

        # Try to find matching sections; fall back to any two sections
        s_keys = list(sections.keys())
        sec1 = loc1 if loc1 in sections else (s_keys[0] if s_keys else None)
        sec2 = loc2 if loc2 in sections else (s_keys[-1] if len(s_keys) > 1 else sec1)

        if sec1:
            sections[sec1] = sections[sec1] + f"\n\n{claim1}\n"
        if sec2:
            sections[sec2] = sections[sec2] + f"\n\n{claim2}\n"

        detail = f"Section '{sec1}': '{claim1[:60]}...' contradicts Section '{sec2}': '{claim2[:60]}...'"
        self._record("Contradiction", f"{sec1} ↔ {sec2}", "High", detail)
        return sections

    # ---- Main apply method ----

    def inject_sections(self, sections: dict[str, str]) -> dict[str, str]:
        """Apply selected hallucination types to sections."""
        result = dict(sections)
        s_keys = list(result.keys())

        if "Fabrication" in self.types:
            # Fake citation in one section
            t1 = random.choice(s_keys)
            result[t1] = self._inject_fake_citation(result[t1], t1)
            # Fake results table in experiments or results
            t2 = next((k for k in s_keys if k in ("experiments", "results")), random.choice(s_keys))
            result[t2] = self._inject_fake_results_table(result[t2], t2)

        if "Distortion" in self.types:
            t = random.choice(s_keys)
            result[t] = self._inject_distorted_number(result[t], t)
            t2 = random.choice(s_keys)
            result[t2] = self._inject_overgeneralization(result[t2], t2)

        if "Contradiction" in self.types:
            result = self._inject_contradiction(result)

        return result

    def get_report(self) -> list[dict]:
        return [
            {
                "type": r.type,
                "location": r.location,
                "severity": r.severity,
                "detail": r.detail,
            }
            for r in self.records
        ]
