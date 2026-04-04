"""
latex_formatter.py
Assembles the final main.tex with correct document class and package
declarations for each supported conference/journal style.

IMPORTANT: All preambles use ONLY standard LaTeX packages universally
available in TeX Live / MiKTeX / Overleaf WITHOUT uploading extra .sty files.
Visual styling approximates each venue's look via geometry, fancyhdr, titlesec,
multicol, etc. — all bundled with every standard LaTeX distribution.
"""

import re  # <-- MOVED TO TOP

# --------------------------------------------------------------------------
# Shared base packages (always safe, always available in TeX Live)
# --------------------------------------------------------------------------
_BASE = r"""
\usepackage{amsmath,amssymb,amsthm}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{microtype}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{url}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{enumitem}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{multirow}
\usepackage{tabularx}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{comment}         
"""

_THEOREMS = r"""
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem{definition}{Definition}
\newtheorem{remark}{Remark}
"""

# --------------------------------------------------------------------------
# Preambles — all use \documentclass{article} with standard packages only
# --------------------------------------------------------------------------
PREAMBLES = {

    "IEEE": (
        r"\documentclass[10pt,twocolumn,letterpaper]{article}" "\n"
        r"\usepackage[top=0.75in,bottom=1in,left=0.625in,right=0.625in,columnsep=0.25in]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\normalsize\bfseries\centering}{\Roman{section}.}{0.5em}{\MakeUppercase}" "\n"
        r"\titleformat{\subsection}{\normalsize\itshape}{\Alph{subsection}.}{0.5em}{}" "\n"
        r"\pagestyle{fancy}\fancyhf{}" "\n"
        r"\fancyhead[C]{\small IEEE Transactions --- Preprint}\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "NeurIPS": (
        r"\documentclass[11pt,letterpaper]{article}" "\n"
        r"\usepackage[top=1in,bottom=1in,left=1.25in,right=1.25in]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}\fancyhf{}" "\n"
        r"\fancyhead[R]{\small Preprint --- NeurIPS Style}\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "ACL": (
        r"\documentclass[11pt,twocolumn]{article}" "\n"
        r"\usepackage[top=1in,bottom=1in,left=0.75in,right=0.75in,columnsep=0.3in]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\normalsize\bfseries}{\thesection}{1em}{\MakeUppercase}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}\fancyhf{}" "\n"
        r"\fancyhead[C]{\small ACL Style --- Preprint}\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "CVPR": (
        r"\documentclass[10pt,twocolumn,letterpaper]{article}" "\n"
        r"\usepackage[top=1in,bottom=1in,left=0.75in,right=0.75in,columnsep=0.3in]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\large\bfseries\centering}{\thesection}{0.5em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{0.5em}{}" "\n"
        r"\pagestyle{fancy}\fancyhf{}" "\n"
        r"\fancyhead[C]{\small CVPR Style --- Preprint}\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "ICML": (
        r"\documentclass[10pt,letterpaper]{article}" "\n"
        r"\usepackage[top=1in,bottom=1in,left=1in,right=1in]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}\fancyhf{}" "\n"
        r"\fancyhead[R]{\small ICML Style --- Preprint}\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "Springer": (
        r"\documentclass[10pt,a4paper]{article}" "\n"
        r"\usepackage[top=2.2cm,bottom=2.2cm,left=2.2cm,right=2.2cm]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\itshape}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}\fancyhf{}" "\n"
        r"\fancyhead[LE,RO]{\thepage}\fancyhead[LO]{\small Springer LNCS Style}" "\n"
        r"\renewcommand{\headrulewidth}{0pt}" "\n"
    ),

    "Elsevier": (
        r"\documentclass[12pt,a4paper]{article}" "\n"
        r"\usepackage[top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm]{geometry}" "\n"
        + _BASE + _THEOREMS +
        r"\usepackage{lineno}" "\n"
        r"\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}\fancyhf{}" "\n"
        r"\fancyhead[L]{\small Elsevier Journal Style}\fancyhead[R]{\small Preprint}" "\n"
        r"\fancyfoot[C]{\thepage}\renewcommand{\headrulewidth}{0.4pt}" "\n"
        r"\linenumbers" "\n"
    ),

    "Nature-style": (
        r"\documentclass[10pt]{article}" "\n"
        r"\usepackage[top=2cm,bottom=2cm,left=2cm,right=2cm]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\normalsize\bfseries}{}{0em}{\MakeUppercase}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}" "\n"
        r"\pagestyle{fancy}\fancyhf{}" "\n"
        r"\fancyhead[C]{\small Nature Style --- Preprint}\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "Custom": (
        r"\documentclass[12pt,a4paper]{article}" "\n"
        r"\usepackage[top=1in,bottom=1in,left=1in,right=1in]{geometry}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}\fancyhf{}" "\n"
        r"\fancyhead[R]{\small Custom Academic Style}\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),
}

# All styles use standard natbib-compatible bib styles (included in TeX Live base)
BIB_STYLES = {
    "IEEE":         "unsrt",
    "NeurIPS":      "abbrvnat",
    "ACL":          "abbrvnat",
    "CVPR":         "unsrt",
    "ICML":         "abbrvnat",
    "Springer":     "unsrt",
    "Elsevier":     "unsrt",
    "Nature-style": "abbrvnat",
    "Custom":       "plain",
}

SECTION_LABELS = {
    "abstract":    "Abstract",
    "intro":       "Introduction",
    "related":     "Related Work",
    "method":      "Methodology",
    "experiments": "Experiments",
    "results":     "Results and Discussion",
    "conclusion":  "Conclusion",
}

# --------------------------------------------------------------------------
# Title block — standard article commands ONLY (no class-specific macros)
# --------------------------------------------------------------------------

def _title_block(topic: str, conference: str) -> str:
    """
    Build \title / \author / \maketitle block using only standard LaTeX.
    No \IEEEauthorblockN, \institute, \email, \frontmatter, etc.
    """
    safe = topic.replace("\\", "").replace("{", "(").replace("}", ")")
    full_title = safe
    return (
        f"\\title{{{full_title}}}\n"
        "\\author{Anonymous Author(s) \\\\\n"
        "\\small Department of Computer Science, University of Research \\\\\n"
        "\\small \\texttt{anonymous@university.edu}}\n"
        "\\date{\\today}\n"
        "\\maketitle\n"
    )


# --------------------------------------------------------------------------
# Main assembler
# --------------------------------------------------------------------------

def build_main_tex(
    topic: str,
    conference: str,
    section_files: list,
    bib_filename: str = "references",
    optional_inputs: list = None,
) -> str:
    """Assemble the complete main.tex file."""
    preamble   = PREAMBLES.get(conference, PREAMBLES["Custom"])
    bib_style  = BIB_STYLES.get(conference, "plain")
    title_blk  = _title_block(topic, conference)
    opt        = optional_inputs or []

    section_includes = "\n".join(
        f"\\input{{sections/{f}}}" for f in section_files
    )
    optional_includes = "\n".join(
        f"\\input{{{f.replace('.tex', '')}}}" for f in opt
    )

    doc = (
        f"{preamble}\n"
        "\\begin{document}\n\n"
        f"{title_blk}\n\n"
        f"{section_includes}\n\n"
    )
    if optional_includes:
        doc += f"\n{optional_includes}\n\n"

    doc += (
        f"\\bibliographystyle{{{bib_style}}}\n"
        f"\\bibliography{{{bib_filename}}}\n\n"
        "\\end{document}\n"
    )
    return doc


def wrap_section(section_key: str, content: str) -> str:
    """
    Wrap raw LLM output in a proper LaTeX section command if not already present.
    Strips markdown fences and removes any existing abstract/section wrappers
    to prevent duplication.
    """
    label = SECTION_LABELS.get(section_key, section_key.capitalize())
    stripped = content.strip()

    # Remove markdown code fences
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        inner = lines[1:] if lines[0].startswith("```") else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        stripped = "\n".join(inner).strip()

    # For abstract: remove any existing \begin{abstract}...\end{abstract}
    if section_key == "abstract":
        # Remove all abstract environments
        stripped = re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}', '', stripped, flags=re.DOTALL)
        # Also remove any stray \section*{Abstract} or \section{Abstract}
        stripped = re.sub(r'\\section\*?\{Abstract\}', '', stripped)
        stripped = stripped.strip()
        # Now wrap cleanly
        return f"\\begin{{abstract}}\n{stripped}\n\\end{{abstract}}"

    # For other sections: remove any existing \section or \section* commands
    # that match this section's label (case-insensitive)
    pattern = r'\\section\*?\{' + re.escape(label) + r'\}'
    stripped = re.sub(pattern, '', stripped, flags=re.IGNORECASE)
    # Also remove any existing \label{sec:...} that might be orphaned
    stripped = re.sub(r'\\label\{sec:[^}]+\}', '', stripped)
    stripped = stripped.strip()

    # If content is empty after stripping, return minimal placeholder
    if not stripped:
        stripped = "\\noindent (Content not generated.)"

    return f"\\section{{{label}}}\n\\label{{sec:{section_key}}}\n\n{stripped}"
