"""
prompt_builder.py
Constructs structured LLM prompts for each section of the research paper.
Tailors formatting instructions to the selected conference/journal style.
"""

# --------------------------------------------------------------------------
# Style guides per venue
# --------------------------------------------------------------------------
STYLE_GUIDES: dict[str, str] = {
    "IEEE": (
        "Use IEEE Transactions style. Write formally. Use \\cite{} for every factual claim. "
        "Equations must be numbered. Sections: Abstract, I. Introduction, II. Related Work, "
        "III. Methodology, IV. Experiments, V. Results, VI. Conclusion, References."
    ),
    "NeurIPS": (
        "Use NeurIPS style. Be rigorous and concise. Abstract ≤ 250 words. "
        "Include a Broader Impact statement after Conclusion. Prefer theorem-lemma structure "
        "in methodology. Cite extensively using \\cite{}."
    ),
    "ACL": (
        "Use ACL (Association for Computational Linguistics) style. Focus on NLP/language tasks. "
        "Include a Limitations section after Conclusion. Use \\citet{} for narrative and "
        "\\citep{} for parenthetical citations."
    ),
    "CVPR": (
        "Use CVPR style. Focus on computer vision. Include ablation studies in experiments. "
        "Reference figures/tables heavily (\\ref{fig:}, \\ref{tab:}). Methodology should "
        "describe network architecture in detail."
    ),
    "ICML": (
        "Use ICML style. Strong emphasis on theory and reproducibility. "
        "Include pseudocode in methodology using algorithm2e or similar. "
        "Experiments must include statistical error bars."
    ),
    "Springer": (
        "Use Springer LNCS style. Formal academic prose. "
        "Abstract ≤ 150 words with 4–6 keywords below it. "
        "Numbered sections. Bibliography via \\bibliographystyle{splncs04}."
    ),
    "Elsevier": (
        "Use Elsevier journal style. Structured abstract with Background, Methods, Results, "
        "Conclusions sub-labels. Research highlights at top. "
        "Use \\bibliographystyle{elsarticle-num}."
    ),
    "Nature-style": (
        "Use Nature style. Write for a broad scientific audience. "
        "Short, punchy Abstract (~150 words). Extremely concise Methods section. "
        "Extensive supplementary material references. First person allowed."
    ),
    "Custom": (
        "Use a generic academic style with standard LaTeX article class. "
        "Follow common academic writing conventions."
    ),
}

# --------------------------------------------------------------------------
# Section-level prompt templates
# --------------------------------------------------------------------------

def _system_prompt(topic: str, conference: str) -> str:
    style = STYLE_GUIDES.get(conference, STYLE_GUIDES["Custom"])
    return (
        f"You are a senior researcher writing a full academic paper about: {topic}.\n"
        f"Style guide: {style}\n"
        "Write ONLY valid LaTeX content for the requested section. "
        "Do NOT include \\documentclass, \\begin{{document}}, or \\end{{document}} "
        "unless explicitly asked. Do NOT wrap in markdown code fences. "
        "Include \\cite{{key}} references throughout. Be detailed, technical, and convincing."
    )


def build_abstract_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"Write the Abstract section (LaTeX) for a paper on: {topic}.\n"
                "Output only the LaTeX content starting with \\begin{abstract} or \\section*{Abstract}."
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
                "Include motivation, problem statement, contributions (itemized), and paper outline. "
                "Output only the LaTeX section content."
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
                "Group related work into 3–4 sub-themes. Cite 10–15 works using \\cite{{}}. "
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
                "Include system architecture, mathematical formulations with equations, "
                "and algorithmic details. Use subsections. "
                "Include at least one \\begin{{equation}} block. "
                "Output only the LaTeX section content."
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
                "Describe experimental setup, datasets, baselines, metrics, and a results table "
                "using \\begin{{table}}...\\end{{table}}. "
                "Include a figure reference like \\ref{{fig:results}}. "
                "Output only the LaTeX section content."
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
                "Discuss quantitative and qualitative findings, ablation studies, and limitations. "
                "Output only the LaTeX section content."
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
                "Summarize contributions, limitations, and future work. "
                "Output only the LaTeX section content."
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
                "Include journal articles, conference papers, books, and arXiv preprints. "
                "Use realistic author names, venues (NeurIPS, ICML, CVPR, ACL, Nature, JMLR, etc.), "
                "years (2015–2024), and titles. "
                "Output ONLY valid BibTeX entries. No LaTeX, no explanations."
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
