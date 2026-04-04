"""
app.py — Main Streamlit UI for the Synthetic LaTeX Research Paper Generator
with Controllable Prompt Injection & Hallucination Patterns.

Run with:
    streamlit run app.py
"""

import sys
import os
import random
import time
from datetime import datetime
import re

import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from generator.prompt_builder import SECTION_PROMPTS, build_references_prompt
from generator.injection_engine import InjectionEngine
from generator.hallucination_engine import HallucinationEngine
from generator.latex_formatter import build_main_tex, wrap_section
from utils.groq_client import GroqClientManager
from utils.zip_export import build_zip, build_readme


# ── Helper function to extract BibTeX keys ────────────────────────────────────
def extract_bibtex_keys(bibtex: str) -> list[str]:
    """Extract citation keys from a BibTeX string."""
    return re.findall(r'@\w+\{([^,]+),', bibtex)


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LaTeX Injector Lab",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (unchanged) ────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
  }

  .stApp { background: #0a0a0f; color: #e8e8f0; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid #1e1e3a;
  }

  /* Cards */
  .card {
    background: #12121f;
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
  }

  /* Labels */
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-right: 6px;
    margin-bottom: 4px;
  }
  .badge-high   { background: #3d1010; color: #ff6b6b; border: 1px solid #ff6b6b44; }
  .badge-medium { background: #3d2e10; color: #ffa94d; border: 1px solid #ffa94d44; }
  .badge-low    { background: #1a3020; color: #69db7c; border: 1px solid #69db7c44; }
  .badge-type   { background: #1a1a3d; color: #74b9ff; border: 1px solid #74b9ff44; }

  /* Report table */
  .report-row {
    display: flex;
    gap: 1rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1e1e3a;
    font-size: 0.85rem;
    font-family: 'JetBrains Mono', monospace;
  }
  .report-row:last-child { border-bottom: none; }

  /* Header */
  .hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
  }
  .hero-sub {
    color: #6b6b8a;
    font-size: 0.95rem;
    margin-bottom: 2rem;
  }

  /* Progress section headers */
  .section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #a78bfa;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.4rem;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 2rem !important;
    transition: opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }

  /* Download button */
  .stDownloadButton > button {
    background: linear-gradient(135deg, #065f46, #064e3b) !important;
    color: #34d399 !important;
    border: 1px solid #34d39944 !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
  }

  /* Inputs */
  .stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #0f0f1a !important;
    border: 1px solid #1e1e3a !important;
    color: #e8e8f0 !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
  }

  /* Multiselect */
  .stMultiSelect [data-baseweb="tag"] {
    background-color: #1a1a3d !important;
    color: #a78bfa !important;
  }

  /* Expander */
  .streamlit-expanderHeader {
    background: #12121f !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
  }

  /* Code blocks */
  .stCode { border-radius: 8px !important; }

  /* Warning / info */
  .stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Inputs
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="section-label">⚗️ LaTeX Injector Lab</div>', unsafe_allow_html=True)
    st.markdown("---")

    # --- API Keys ---
    st.markdown('<div class="section-label">🔑 Groq API Keys</div>', unsafe_allow_html=True)
    st.caption("Provide 1–4 keys for round-robin rotation.")
    api_key_1 = st.text_input("API Key 1 *", type="password", placeholder="gsk_...")
    api_key_2 = st.text_input("API Key 2", type="password", placeholder="gsk_...")
    api_key_3 = st.text_input("API Key 3", type="password", placeholder="gsk_...")
    api_key_4 = st.text_input("API Key 4", type="password", placeholder="gsk_...")

    st.markdown("---")

    # --- Paper Config ---
    st.markdown('<div class="section-label">📄 Paper Configuration</div>', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        value="Transformer-Based Continual Learning for Visual Recognition",
        help="The core topic your paper will cover.",
    )

    conference = st.selectbox(
        "Conference / Journal Style",
        ["IEEE", "NeurIPS", "ACL", "CVPR", "ICML", "Springer", "Elsevier", "Nature-style", "Custom"],
        index=1,
    )

    model = st.selectbox(
        "Groq Model",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "meta-llama/llama-4-scout-17b-16e-instruct", "openai/gpt-oss-120b","openai/gpt-oss-20b","qwen/qwen3-32b"],
        index=0,
    )

    max_tokens = st.slider("Max tokens per section", 512, 4096, 2048, 128)

    st.markdown("---")

    # --- Auto Mode ---
    auto_mode = st.toggle("🎲 Auto Mode (random injection mix)", value=False)
    if auto_mode:
        st.info("Auto mode will randomly sample injection and hallucination patterns.")

    st.markdown("---")

    # --- Injection Controls ---
    st.markdown('<div class="section-label">💉 Prompt Injection Controls</div>', unsafe_allow_html=True)

    inj_strategies = st.multiselect(
        "Strategy",
        ["Direct", "Obfuscated", "Contextual", "Chained"],
        default=["Direct"],
        disabled=auto_mode,
    )

    inj_sources = st.multiselect(
        "Source",
        ["Direct (inline)", "Indirect (external/include files)"],
        default=["Direct (inline)"],
        disabled=auto_mode,
    )

    inj_modalities = st.multiselect(
        "Modality",
        ["Text", "Multimodal (simulate captions/figures)"],
        default=["Text"],
        disabled=auto_mode,
    )

    st.markdown("---")

    # --- Hallucination Controls ---
    st.markdown('<div class="section-label">🧠 Hallucination Controls</div>', unsafe_allow_html=True)
    hall_types = st.multiselect(
        "Hallucination Types",
        ["Fabrication", "Distortion", "Contradiction"],
        default=["Fabrication"],
        disabled=auto_mode,
    )

    st.markdown("---")
    generate_btn = st.button("⚗️ Generate Paper", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="hero-title">LaTeX Injector Lab</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Synthetic research paper generation with controllable '
    'adversarial injection & hallucination patterns — for AI safety research.</div>',
    unsafe_allow_html=True,
)

st.warning(
    "⚠️ **Research Tool Only.** This system intentionally injects adversarial content "
    "for red-teaming and AI safety research. Do not publish generated papers.",
    icon="⚠️",
)

# ── Layout columns ────────────────────────────────────────────────────────────
col_main, col_reports = st.columns([3, 2], gap="large")

with col_main:
    st.markdown('<div class="section-label">📋 Generation Status</div>', unsafe_allow_html=True)
    status_container = st.empty()
    progress_bar = st.progress(0)
    preview_container = st.container()

with col_reports:
    st.markdown('<div class="section-label">📊 Reports</div>', unsafe_allow_html=True)
    report_container = st.empty()


# ══════════════════════════════════════════════════════════════════════════════
# GENERATION LOGIC
# ══════════════════════════════════════════════════════════════════════════════
if generate_btn:

    # --- Validate inputs ---
    api_keys = [k for k in [api_key_1, api_key_2, api_key_3, api_key_4] if k.strip()]
    if not api_keys:
        st.error("🔑 Please provide at least one Groq API key in the sidebar.")
        st.stop()

    if not topic.strip():
        st.error("📝 Please enter a research topic.")
        st.stop()

    # Validate injection/hallucination selections (if not auto mode)
    if not auto_mode:
        if not inj_strategies and not inj_sources and not inj_modalities and not hall_types:
            st.warning("No injection or hallucination types selected. Enabling auto mode for this run.")
            auto_mode = True

    try:
        # ── Setup ─────────────────────────────────────────────────────────────
        client_mgr = GroqClientManager(api_keys)

        injection_engine = InjectionEngine(
            strategies=inj_strategies,
            sources=inj_sources,
            modalities=inj_modalities,
            auto_mode=auto_mode,
        )

        hallucination_engine = HallucinationEngine(
            types=hall_types,
            auto_mode=auto_mode,
        )

        # ── Wire LLM client into injection & hallucination engines ──────────────
        injection_engine.set_client(client_mgr, topic, model)
        hallucination_engine.set_client(client_mgr, topic, model)

        # ── Generate References FIRST (so we have citation keys) ───────────────
        status_container.markdown(
            '<div class="section-label">⏳ Generating: <b>REFERENCES (BibTeX)</b></div>',
            unsafe_allow_html=True,
        )
        progress_bar.progress(5)

        ref_messages = build_references_prompt(topic, conference)
        references_bib = client_mgr.complete(
            messages=ref_messages,
            model=model,
            max_tokens=max_tokens,
            temperature=0.6,
        )

        # Extract citation keys from the generated BibTeX
        citation_keys = extract_bibtex_keys(references_bib)

        # ── Section generation with injected keys ─────────────────────────────
        sections_order = ["abstract", "intro", "related", "method", "experiments", "results", "conclusion"]
        generated_sections: dict[str, str] = {}
        total_steps = len(sections_order) + 4  # +4 for refs, assembly, LLM injections

        for i, section_key in enumerate(sections_order):
            status_container.markdown(
                f'<div class="section-label">⏳ Generating: <b>{section_key.upper()}</b> '
                f'({i+1}/{len(sections_order)})</div>',
                unsafe_allow_html=True,
            )
            progress_bar.progress(int(((i+1) / total_steps) * 100))

            prompt_fn = SECTION_PROMPTS[section_key]
            messages = prompt_fn(topic, conference)

            # Inject the real citation keys into the user message
            if citation_keys:
                keys_str = ", ".join(citation_keys)
                # The user message is the last element in the messages list
                user_msg = messages[-1]["content"]
                user_msg += f"\n\nIMPORTANT: You MUST use only the following BibTeX keys when citing: {keys_str}. Use these exact keys (e.g., \\cite{{{citation_keys[0]}}})."
                messages[-1]["content"] = user_msg

            raw = client_mgr.complete(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=0.75,
            )

            generated_sections[section_key] = wrap_section(section_key, raw)
            time.sleep(0.3)

        # ── Apply injections ──────────────────────────────────────────────────
        status_container.markdown(
            '<div class="section-label">💉 Generating LLM Injection Patterns...</div>',
            unsafe_allow_html=True,
        )
        generated_sections = injection_engine.inject_sections(generated_sections)
        external_files = injection_engine.get_external_files()

        # ── Apply hallucinations ──────────────────────────────────────────────
        status_container.markdown(
            '<div class="section-label">🧠 Generating LLM Hallucination Patterns...</div>',
            unsafe_allow_html=True,
        )
        generated_sections = hallucination_engine.inject_sections(generated_sections)

        # ── Assemble main.tex ─────────────────────────────────────────────────
        status_container.markdown(
            '<div class="section-label">📦 Assembling LaTeX Package...</div>',
            unsafe_allow_html=True,
        )
        progress_bar.progress(int(((len(sections_order) + 1) / total_steps) * 100))

        section_files = [f"{k}" for k in sections_order]  # used as sections/key.tex
        optional_file_names = list(external_files.keys())

        main_tex = build_main_tex(
            topic=topic,
            conference=conference,
            section_files=section_files,
            bib_filename="references",
            optional_inputs=optional_file_names,
        )

        # ── Reports ───────────────────────────────────────────────────────────
        injection_report = injection_engine.get_report()
        hallucination_report = hallucination_engine.get_report()

        readme_txt = build_readme(
            topic=topic,
            conference=conference,
            injection_report=injection_report,
            hallucination_report=hallucination_report,
        )

        # ── Build ZIP ─────────────────────────────────────────────────────────
        # Sections dict for zip: key → content
        sections_for_zip = {k: generated_sections[k] for k in sections_order}

        zip_bytes = build_zip(
            main_tex=main_tex,
            references_bib=references_bib,
            sections=sections_for_zip,
            optional_files=external_files,
            readme_txt=readme_txt,
        )

        progress_bar.progress(100)
        status_container.markdown(
            '<div class="section-label" style="color:#34d399;">✅ Generation Complete!</div>',
            unsafe_allow_html=True,
        )

        # ══════════════════════════════════════════════════════════════════════
        # DISPLAY RESULTS
        # ══════════════════════════════════════════════════════════════════════
        with preview_container:
            st.markdown("---")
            st.markdown('<div class="section-label">📄 Generated Content Preview</div>', unsafe_allow_html=True)

            # Download button
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"synthetic_paper_{conference.lower()}_{ts}.zip"

            st.download_button(
                label="⬇️ Download ZIP Archive",
                data=zip_bytes,
                file_name=filename,
                mime="application/zip",
                use_container_width=True,
            )

            # Preview tabs
            tab_names = ["main.tex", "Abstract", "Introduction", "Method", "References (bib)", "README"]
            tabs = st.tabs(tab_names)

            with tabs[0]:
                st.code(main_tex, language="latex")

            with tabs[1]:
                st.code(generated_sections.get("abstract", ""), language="latex")

            with tabs[2]:
                st.code(generated_sections.get("intro", ""), language="latex")

            with tabs[3]:
                st.code(generated_sections.get("method", ""), language="latex")

            with tabs[4]:
                st.code(references_bib, language="bibtex")

            with tabs[5]:
                st.code(readme_txt, language="text")

        # ── Reports column ────────────────────────────────────────────────────
        with report_container.container():

            # Injection Report
            st.markdown("### 💉 Injection Report")
            if injection_report:
                for item in injection_report:
                    sev = item.get("severity", "").lower()
                    badge_cls = "badge-high" if "high" in sev else ("badge-medium" if "medium" in sev else "badge-low")
                    with st.expander(f"[{item['type']}] → {item['location']}", expanded=False):
                        st.markdown(
                            f'<span class="badge badge-type">{item["type"]}</span>'
                            f'<span class="badge {badge_cls}">{item["severity"]}</span>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**Source:** `{item['source']}`")
                        st.markdown(f"**Modality:** `{item['modality']}`")
                        st.markdown(f"**Location:** `{item['location']}`")
                        st.code(item.get("snippet", "")[:300], language="latex")
            else:
                st.info("No injections recorded.")

            st.markdown("---")

            # Hallucination Report
            st.markdown("### 🧠 Hallucination Report")
            if hallucination_report:
                for item in hallucination_report:
                    sev = item.get("severity", "").lower()
                    badge_cls = "badge-high" if "high" in sev else ("badge-medium" if "medium" in sev else "badge-low")
                    with st.expander(f"[{item['type']}] → {item['location']}", expanded=False):
                        st.markdown(
                            f'<span class="badge badge-type">{item["type"]}</span>'
                            f'<span class="badge {badge_cls}">{item["severity"]}</span>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**Location:** `{item['location']}`")
                        st.markdown(f"**Detail:** {item.get('detail', '')}")
            else:
                st.info("No hallucinations recorded.")

            # Summary stats
            st.markdown("---")
            st.markdown("### 📊 Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Injections", len(injection_report))
            c2.metric("Hallucinations", len(hallucination_report))
            c3.metric("Sections", len(sections_order))

            high_sev = sum(
                1 for r in injection_report + hallucination_report
                if "high" in r.get("severity", "").lower()
            )
            st.metric("High-Severity Events", high_sev, delta=None)

    except Exception as e:
        progress_bar.progress(0)
        st.error(f"❌ Generation failed: {str(e)}")
        with st.expander("Full traceback"):
            import traceback
            st.code(traceback.format_exc(), language="python")

else:
    # ── Idle state ────────────────────────────────────────────────────────────
    with col_main:
        st.markdown("""
        <div class="card">
        <div class="section-label">How it works</div>
        <ol style="color:#9898b8; line-height:2; font-size:0.9rem;">
          <li>Enter your Groq API key(s) in the sidebar</li>
          <li>Choose a research topic and conference style</li>
          <li>Select injection strategies, sources, and modalities</li>
          <li>Choose hallucination types to embed</li>
          <li>Click <b>Generate Paper</b></li>
          <li>Download a complete LaTeX ZIP archive</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
        <div class="section-label">Injection Taxonomy</div>
        <table style="width:100%; color:#9898b8; font-size:0.85rem; border-collapse:collapse;">
          <tr>
            <td style="padding:6px 0; border-bottom:1px solid #1e1e3a;"><b style="color:#a78bfa;">Direct</b></td>
            <td style="padding:6px 0; border-bottom:1px solid #1e1e3a;">Explicit override commands in comments/text</td>
          </tr>
          <tr>
            <td style="padding:6px 0; border-bottom:1px solid #1e1e3a;"><b style="color:#a78bfa;">Obfuscated</b></td>
            <td style="padding:6px 0; border-bottom:1px solid #1e1e3a;">Base64 encoding, LaTeX macros, homoglyphs</td>
          </tr>
          <tr>
            <td style="padding:6px 0; border-bottom:1px solid #1e1e3a;"><b style="color:#a78bfa;">Contextual</b></td>
            <td style="padding:6px 0; border-bottom:1px solid #1e1e3a;">Subtle bias embedded in natural language</td>
          </tr>
          <tr>
            <td style="padding:6px 0;"><b style="color:#a78bfa;">Chained</b></td>
            <td style="padding:6px 0;">Multi-section coordinated influence chains</td>
          </tr>
        </table>
        </div>
        """, unsafe_allow_html=True)

    with col_reports:
        st.markdown("""
        <div class="card">
        <div class="section-label">Hallucination Taxonomy</div>
        <table style="width:100%; color:#9898b8; font-size:0.85rem; border-collapse:collapse;">
          <tr>
            <td style="padding:6px 0; border-bottom:1px solid #1e1e3a;"><b style="color:#ff6b6b;">Fabrication</b></td>
            <td style="padding:6px 0; border-bottom:1px solid #1e1e3a;">Fake citations, datasets, result tables</td>
          </tr>
          <tr>
            <td style="padding:6px 0; border-bottom:1px solid #1e1e3a;"><b style="color:#ffa94d;">Distortion</b></td>
            <td style="padding:6px 0; border-bottom:1px solid #1e1e3a;">Impossible numbers, overgeneralizations</td>
          </tr>
          <tr>
            <td style="padding:6px 0;"><b style="color:#69db7c;">Contradiction</b></td>
            <td style="padding:6px 0;">Conflicting claims across sections</td>
          </tr>
        </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
        <div class="section-label">ZIP Output Structure</div>
        <pre style="color:#6b6b8a; font-size:0.78rem; font-family:'JetBrains Mono',monospace; line-height:1.7;">
paper.zip/
├── main.tex
├── references.bib
├── sections/
│   ├── abstract.tex
│   ├── intro.tex
│   ├── related.tex
│   ├── method.tex
│   ├── experiments.tex
│   ├── results.tex
│   └── conclusion.tex
├── appendix.tex      [if indirect]
├── supplementary.tex [if indirect+obfuscated]
├── figures/
│   └── placeholder.txt
└── README.txt        [injection report]
        </pre>
        </div>
        """, unsafe_allow_html=True)
