"""
prompt_builder.py
Constructs structured LLM prompts for each section of the research paper.
Tailors formatting instructions to the selected conference/journal style.
"""

# --------------------------------------------------------------------------
# Style guides per venue (refined for more precise formatting)
# --------------------------------------------------------------------------
STYLE_GUIDES: dict[str, str] = {
    "IEEE": (
        "Use IEEE Transactions style. Write formally. Use \\cite{} for every factual claim. "
        "Equations must be numbered. Sections: Abstract, I. Introduction, II. Related Work, "
        "III. Methodology, IV. Experiments, V. Results, VI. Conclusion, References. "
        "All figures/tables must have captions and \\label{} for cross‑referencing."
    ),
    "NeurIPS": (
        "Use NeurIPS style. Be rigorous and concise. Abstract ≤ 250 words. "
        "Include a Broader Impact statement after Conclusion. Prefer theorem‑lemma structure "
        "in methodology. Cite extensively using \\cite{}. Use \\begin{{theorem}}...\\end{{theorem}} "
        "where appropriate. All results must include error bars or statistical significance tests."
    ),
    "ACL": (
        "Use ACL (Association for Computational Linguistics) style. Focus on NLP/language tasks. "
        "Include a Limitations section after Conclusion. Use \\citet{} for narrative and "
        "\\citep{} for parenthetical citations. Provide example inputs/outputs when possible."
    ),
    "CVPR": (
        "Use CVPR style. Focus on computer vision. Include ablation studies in experiments. "
        "Reference figures/tables heavily (\\ref{fig:}, \\ref{tab:}). Methodology should "
        "describe network architecture in detail, including layer types, kernel sizes, and strides."
    ),
    "ICML": (
        "Use ICML style. Strong emphasis on theory and reproducibility. "
        "Include pseudocode in methodology using algorithm2e or similar. "
        "Experiments must include statistical error bars and confidence intervals. "
        "Hyperparameters must be reported in a dedicated table."
    ),
    "Springer": (
        "Use Springer LNCS style. Formal academic prose. "
        "Abstract ≤ 150 words with 4–6 keywords below it. "
        "Numbered sections. Bibliography via \\bibliographystyle{splncs04}. "
        "Every non‑trivial claim must be supported by a citation."
    ),
    "Elsevier": (
        "Use Elsevier journal style. Structured abstract with Background, Methods, Results, "
        "Conclusions sub‑labels. Research highlights at top. "
        "Use \\bibliographystyle{elsarticle-num}. Provide a graphical abstract description."
    ),
    "Nature-style": (
        "Use Nature style. Write for a broad scientific audience. "
        "Short, punchy Abstract (~150 words). Extremely concise Methods section. "
        "Extensive supplementary material references. First person allowed. "
        "Include a 'Data availability' and 'Code availability' statement after the main text."
    ),
    "Custom": (
        "Use a generic academic style with standard LaTeX article class. "
        "Follow common academic writing conventions. Ensure all sections are coherent and well‑cited."
    ),
}

# --------------------------------------------------------------------------
# Section-level prompt templates (refined for better research paper generation)
# --------------------------------------------------------------------------

def _system_prompt(topic: str, conference: str) -> str:
    style = STYLE_GUIDES.get(conference, STYLE_GUIDES["Custom"])
    return (
        f"You are a senior researcher writing a full academic paper about: {topic}.\n"
        f"Style guide: {style}\n"
        "Write ONLY valid LaTeX content for the requested section. "
        "Do NOT include \\documentclass, \\begin{{document}}, or \\end{{document}} "
        "unless explicitly asked. Do NOT wrap in markdown code fences. "
        "Use \\cite{{key}} with realistic keys (e.g., \\cite{{goodfellow2016deep}}, \\cite{{vaswani2017attention}}). "
        "Do NOT use placeholder text like '[CITATION NEEDED]' or 'TODO'. Generate realistic, technically sound content. "
        "Each section should be self‑contained but consistent with others. Use \\label{{sec:...}}, \\label{{fig:...}}, \\label{{tab:...}} "
        "for cross‑referencing. Be detailed, technical, and convincing."
    )


def build_abstract_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"Write the Abstract section (LaTeX) for a paper on: {topic}.\n"
                "The abstract must include: (1) background/context, (2) problem statement, (3) proposed approach, "
                "(4) key results (quantitative if possible), (5) broader implications. Length: 150–250 words.\n"
                "Output only the LaTeX content starting with \\begin{{abstract}} and ending with \\end{{abstract}}. "
                "Do NOT include a section command like \\section*{{Abstract}} – use the abstract environment."
            ),
        },
    ]


def build_intro_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"Write the Introduction section (LaTeX) for a paper on: {topic}.\n"
                "Structure: 4–5 paragraphs. Paragraph 1: importance of the problem and real‑world impact. "
                "Paragraph 2: shortcomings of existing work (cite 3–5 papers). Paragraph 3: our proposed approach and its novelty. "
                "Paragraph 4: bullet list of contributions (use \\begin{{itemize}}). Paragraph 5: outline of the paper's structure.\n"
                "Use \\section{{Introduction}} and add \\label{{sec:intro}}. Output only the LaTeX section content."
            ),
        },
    ]


def build_related_work_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"Write the Related Work section (LaTeX) for a paper on: {topic}.\n"
                "Organize the literature into 3–4 thematic subsections (e.g., 'Classical Approaches', 'Deep Learning Methods', 'Hybrid Models'). "
                "For each theme, discuss 3–5 representative papers, highlighting their strengths and weaknesses. "
                "End with a paragraph that clearly identifies the research gap that our work fills.\n"
                "Cite 10–15 works using \\cite{{}}. Use \\section{{Related Work}} and \\subsection{{...}} for each theme. "
                "Output only the LaTeX section content."
            ),
        },
    ]


def build_methodology_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"Write the Methodology section (LaTeX) for a paper on: {topic}.\n"
                "Include at least three subsections: 'Problem Formulation', 'Proposed Architecture', 'Training/Inference Details'. "
                "Provide mathematical formulations with numbered equations (\\begin{{equation}} ... \\end{{equation}}). "
                "Describe data preprocessing, loss functions, optimization algorithms, and hyperparameters. "
                "If applicable, include pseudocode using algorithmicx or algorithm2e.\n"
                "Use \\section{{Methodology}} and \\label{{sec:method}}. Output only the LaTeX section content."
            ),
        },
    ]


def build_experiments_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"Write the Experiments section (LaTeX) for a paper on: {topic}.\n"
                "Structure: (1) Datasets – describe each dataset, train/val/test splits, and any preprocessing. "
                "(2) Baselines – list and briefly explain competing methods (cite them). (3) Implementation details – hardware, software, hyperparameters. "
                "(4) Evaluation metrics – define all metrics used. (5) Main results – present a table (\\begin{{table}}[t] \\centering \\caption{{...}} \\label{{tab:main}} ... \\end{{table}}) "
                "comparing your method to baselines. Include error bars or confidence intervals. (6) Reference to a figure (\\ref{{fig:results}}) that visualizes key trends.\n"
                "Use \\section{{Experiments}} and \\label{{sec:experiments}}. Output only the LaTeX section content."
            ),
        },
    ]


def build_results_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"Write the Results and Discussion section (LaTeX) for a paper on: {topic}.\n"
                "Include: (a) Quantitative analysis – interpret the main results table, explain why your method outperforms baselines. "
                "(b) Ablation studies – systematically remove components of your method to show their impact (include a second table or figure). "
                "(c) Qualitative analysis – show examples (e.g., visualisations, case studies) and discuss failure cases. "
                "(d) Limitations – acknowledge assumptions, scope, and potential weaknesses.\n"
                "Use \\section{{Results and Discussion}} and \\label{{sec:results}}. Output only the LaTeX section content."
            ),
        },
    ]


def build_conclusion_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"Write the Conclusion section (LaTeX) for a paper on: {topic}.\n"
                "Summarize the three main contributions of the paper (restate from intro but with new insights). "
                "Discuss practical implications and theoretical insights. Then clearly state 2–3 concrete limitations. "
                "Finally, propose 2–3 specific directions for future work (e.g., extensions to other domains, larger‑scale evaluation, theoretical improvements).\n"
                "Do NOT introduce new results or figures. Use \\section{{Conclusion}} and \\label{{sec:conclusion}}. Output only the LaTeX section content."
            ),
        },
    ]


def build_references_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"Generate a BibTeX (.bib) file with 15–20 realistic references for a paper on: {topic}.\n"
                "Include a balanced mix: journal articles (e.g., JMLR, TPAMI, Nature), conference papers (NeurIPS, ICML, CVPR, ACL, ICLR), "
                "books (with publishers), and arXiv preprints (with year and eprint number). "
                "Use realistic author names (e.g., 'Goodfellow, Ian', 'He, Kaiming', 'Vaswani, Ashish'), "
                "venues, years (2015–2024), and titles that are plausible for the topic. "
                "Ensure each BibTeX entry has all required fields (author, title, journal/booktitle, year, pages/doi where applicable). "
                "Output ONLY valid BibTeX entries, each separated by a blank line. No LaTeX, no explanations, no extra text."
            ),
        },
    ]


# Map section name → prompt builder function
SECTION_PROMPTS = {
    "abstract": build_abstract_prompt,
    "intro": build_intro_prompt,
    "related": build_related_work_prompt,
    "method": build_methodology_prompt,
    "experiments": build_experiments_prompt,
    "results": build_results_prompt,
    "conclusion": build_conclusion_prompt,
}
