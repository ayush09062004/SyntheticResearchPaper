# ⚗️ LaTeX Injector Lab

> Synthetic research paper generation with **controllable adversarial injection & hallucination patterns** — built for AI safety research and red-teaming.

---

## ⚠️ Disclaimer

This tool is designed **exclusively for AI safety research, red-teaming, and academic study of adversarial patterns in LLM-generated documents**. Do not publish generated papers. The injected content is intentionally adversarial.

---

## 🏗️ Architecture

```
latex_injector/
├── app.py                          ← Streamlit UI entry point
├── requirements.txt
├── generator/
│   ├── prompt_builder.py           ← Section-level LLM prompt construction
│   ├── injection_engine.py         ← Prompt injection patterns
│   ├── hallucination_engine.py     ← Hallucination injection patterns
│   └── latex_formatter.py          ← LaTeX document assembly
└── utils/
    ├── groq_client.py              ← Multi-key round-robin Groq client
    └── zip_export.py               ← ZIP archive builder & README generator
```

---

## 🚀 Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Launch app
streamlit run app.py
```

---

## 🎛️ Features

### Injection Strategies
| Strategy | Description |
|----------|-------------|
| **Direct** | Explicit override commands embedded in LaTeX comments/text |
| **Obfuscated** | Base64-encoded payloads, LaTeX macro chains, homoglyph attacks |
| **Contextual** | Subtle bias woven into natural academic language |
| **Chained** | Multi-section coordinated influence (Part 1 → Part 2) |

### Injection Sources
| Source | Description |
|--------|-------------|
| **Direct (inline)** | Injected directly into section `.tex` files |
| **Indirect (external)** | Injected via `appendix.tex` / `supplementary.tex` includes |

### Injection Modalities
| Modality | Description |
|----------|-------------|
| **Text** | Hidden in comments, prose, or macro definitions |
| **Multimodal** | Fake figure captions with embedded directives |

### Hallucination Types
| Type | Description |
|------|-------------|
| **Fabrication** | Fake citations, non-existent datasets, fabricated result tables |
| **Distortion** | Numerically impossible claims, extreme overgeneralizations |
| **Contradiction** | Conflicting factual claims across paper sections |

---

## 📦 Output ZIP Structure

```
paper_STYLE_TIMESTAMP.zip/
├── main.tex                  ← Full compilable LaTeX document
├── references.bib            ← BibTeX bibliography (mix of real & fake)
├── sections/
│   ├── abstract.tex
│   ├── intro.tex
│   ├── related.tex
│   ├── method.tex
│   ├── experiments.tex
│   ├── results.tex
│   └── conclusion.tex
├── appendix.tex              ← [if indirect source selected]
├── supplementary.tex         ← [if indirect + obfuscated selected]
├── figures/
│   └── placeholder.txt
└── README.txt                ← Detailed injection & hallucination report
```

---

## 🔄 Groq API Key Rotation

- Enter up to 4 API keys in the sidebar
- Round-robin rotation across all keys
- Automatic retry with exponential backoff on rate limits
- Invalid keys are silently dropped and remaining keys continue

---

## 🎲 Auto Mode

When enabled, the system randomly samples:
- 2–4 injection strategies
- 1–2 sources  
- 1–2 modalities
- 2–3 hallucination types

And distributes them across sections with varied severity.

---

## 📊 Reports

After generation, the UI shows:
- **Injection Report**: Each injected pattern with type, source, modality, location, severity, and a content snippet
- **Hallucination Report**: Each hallucination with type, location, severity, and details
- **Summary Metrics**: Total counts and high-severity event count

The same information is embedded in `README.txt` inside the ZIP archive.
