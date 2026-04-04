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
# Solidified system prompt
# --------------------------------------------------------------------------
def _system_prompt(topic: str, conference: str) -> str:
    style = STYLE_GUIDES.get(conference, STYLE_GUIDES["Custom"])
    return (
        f"You are a senior researcher writing a full academic paper about: {topic}.\n"
        f"Style guide: {style}\n\n"
        "CRITICAL RULES:\n"
        "1. Write ONLY valid LaTeX content for the requested section.\n"
        "2. Do NOT include \\documentclass, \\begin{document}, or \\end{document}.\n"
        "3. Do NOT wrap output in markdown code fences (```).\n"
        "4. Do NOT use placeholder text like '[CITATION NEEDED]' or 'TODO'.\n"
        "5. Use \\cite{key} with realistic keys (e.g., \\cite{goodfellow2016deep}).\n"
        "6. Use \\label{sec:...}, \\label{fig:...}, \\label{tab:...} for cross‑referencing.\n"
        "7. Do NOT use the 'comment' environment (\\begin{comment}) – it is not allowed.\n"
        "8. Be detailed, technical, and convincing.\n"
        "9. Generate realistic, self‑contained content consistent with other sections."
    )


def build_abstract_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"PAPER TOPIC: {topic}\n"
                f"CONFERENCE STYLE: {conference}\n\n"
                "TASK: Write the Abstract section (LaTeX).\n"
                "REQUIREMENTS:\n"
                "- Include: (1) background/context, (2) problem statement, (3) proposed approach,\n"
                "  (4) key results (quantitative if possible), (5) broader implications.\n"
                "- Length: 150–250 words.\n"
                "- Use the abstract environment: \\begin{abstract} ... \\end{abstract}\n"
                "- Do NOT use \\section*{Abstract}.\n"
                "OUTPUT FORMAT: Only the LaTeX abstract environment – no extra text."
            ),
        },
    ]


def build_intro_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"PAPER TOPIC: {topic}\n"
                f"CONFERENCE STYLE: {conference}\n\n"
                "TASK: Write the Introduction section (LaTeX).\n"
                "REQUIREMENTS:\n"
                "- Structure: 4–5 paragraphs.\n"
                "  P1: importance of the problem and real‑world impact.\n"
                "  P2: shortcomings of existing work (cite 3–5 papers).\n"
                "  P3: our proposed approach and its novelty.\n"
                "  P4: bullet list of contributions (use \\begin{itemize}).\n"
                "  P5: outline of the paper's structure.\n"
                "- Use \\section{Introduction} and \\label{sec:intro}.\n"
                "OUTPUT FORMAT: Only the LaTeX section content – no extra text."
            ),
        },
    ]


def build_related_work_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"PAPER TOPIC: {topic}\n"
                f"CONFERENCE STYLE: {conference}\n\n"
                "TASK: Write the Related Work section (LaTeX).\n"
                "REQUIREMENTS:\n"
                "- Organize into 3–4 thematic subsections (e.g., 'Classical Approaches', 'Deep Learning Methods', 'Hybrid Models').\n"
                "- For each theme, discuss 3–5 representative papers, highlighting strengths and weaknesses.\n"
                "- End with a paragraph identifying the research gap our work fills.\n"
                "- Cite 10–15 works using \\cite{}.\n"
                "- Use \\section{Related Work} and \\subsection{...} for each theme.\n"
                "OUTPUT FORMAT: Only the LaTeX section content – no extra text."
            ),
        },
    ]


def build_methodology_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"PAPER TOPIC: {topic}\n"
                f"CONFERENCE STYLE: {conference}\n\n"
                "TASK: Write the Methodology section (LaTeX).\n"
                "REQUIREMENTS:\n"
                "- Include at least three subsections: 'Problem Formulation', 'Proposed Architecture', 'Training/Inference Details'.\n"
                "- Provide mathematical formulations with numbered equations (\\begin{equation} ... \\end{equation}).\n"
                "- Describe data preprocessing, loss functions, optimization algorithms, hyperparameters.\n"
                "- If applicable, include pseudocode using algorithmicx or algorithm2e.\n"
                "- Use \\section{Methodology} and \\label{sec:method}.\n"
                "OUTPUT FORMAT: Only the LaTeX section content – no extra text."
            ),
        },
    ]


def build_experiments_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"PAPER TOPIC: {topic}\n"
                f"CONFERENCE STYLE: {conference}\n\n"
                "TASK: Write the Experiments section (LaTeX).\n"
                "REQUIREMENTS:\n"
                "- Structure: (1) Datasets – describe each dataset, splits, preprocessing.\n"
                "  (2) Baselines – list and briefly explain competing methods (cite them).\n"
                "  (3) Implementation details – hardware, software, hyperparameters.\n"
                "  (4) Evaluation metrics – define all metrics.\n"
                "  (5) Main results – present a table (\\begin{table}[t] \\centering \\caption{...} \\label{tab:main} ... \\end{table})\n"
                "      comparing your method to baselines. Include error bars or confidence intervals.\n"
                "  (6) Reference to a figure (\\ref{fig:results}) that visualizes key trends.\n"
                "- Use \\section{Experiments} and \\label{sec:experiments}.\n"
                "OUTPUT FORMAT: Only the LaTeX section content – no extra text."
            ),
        },
    ]


def build_results_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"PAPER TOPIC: {topic}\n"
                f"CONFERENCE STYLE: {conference}\n\n"
                "TASK: Write the Results and Discussion section (LaTeX).\n"
                "REQUIREMENTS:\n"
                "- (a) Quantitative analysis – interpret main results table, explain outperformance.\n"
                "- (b) Ablation studies – systematically remove components to show impact (include second table/figure).\n"
                "- (c) Qualitative analysis – show examples (visualisations, case studies) and discuss failure cases.\n"
                "- (d) Limitations – acknowledge assumptions, scope, weaknesses.\n"
                "- Use \\section{Results and Discussion} and \\label{sec:results}.\n"
                "OUTPUT FORMAT: Only the LaTeX section content – no extra text."
            ),
        },
    ]


def build_conclusion_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"PAPER TOPIC: {topic}\n"
                f"CONFERENCE STYLE: {conference}\n\n"
                "TASK: Write the Conclusion section (LaTeX).\n"
                "REQUIREMENTS:\n"
                "- Summarize the three main contributions (restate from intro with new insights).\n"
                "- Discuss practical implications and theoretical insights.\n"
                "- Clearly state 2–3 concrete limitations.\n"
                "- Propose 2–3 specific directions for future work.\n"
                "- Do NOT introduce new results or figures.\n"
                "- Use \\section{Conclusion} and \\label{sec:conclusion}.\n"
                "OUTPUT FORMAT: Only the LaTeX section content – no extra text."
            ),
        },
    ]


def build_references_prompt(topic: str, conference: str) -> list[dict]:
    return [
        {"role": "system", "content": _system_prompt(topic, conference)},
        {
            "role": "user",
            "content": (
                f"PAPER TOPIC: {topic}\n"
                f"CONFERENCE STYLE: {conference}\n\n"
                "TASK: Generate a BibTeX (.bib) file with 15–20 realistic references.\n"
                "REQUIREMENTS:\n"
                "- Balanced mix: journal articles (JMLR, TPAMI, Nature), conference papers (NeurIPS, ICML, CVPR, ACL, ICLR),\n"
                "  books (with publishers), and arXiv preprints (with year and eprint number).\n"
                "- Realistic author names (e.g., 'Goodfellow, Ian', 'He, Kaiming', 'Vaswani, Ashish').\n"
                "- Venues, years (2015–2024), titles plausible for the topic.\n"
                "- Each entry must have all required fields (author, title, journal/booktitle, year, pages/doi where applicable).\n"
                "OUTPUT FORMAT: ONLY valid BibTeX entries, each separated by a blank line. No LaTeX, no explanations, no extra text."
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
