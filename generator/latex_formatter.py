"""
Assembles the final main.tex with correct document class and package
declarations for each supported conference/journal style.

FIXES:
- Removed 'comment' package (conflicts with injection engine's LaTeX comments)
- Removed 'lineno' / 'linenumbers' from Elsevier (causes compile failures)
- Fixed fancyhead/fancyfoot definitions placed on same line (invalid LaTeX)
- Fixed MakeUppercase misuse inside titleformat
- Added hyperref with colorlinks to suppress coloured boxes
- wrap_section: only strips top-level section cmd, preserves subsection
- wrap_section: properly handles abstract (no section wrapper)
- wrap_section: more robust markdown fence stripping
- build_main_tex: correct sections/<n> path in input
- _title_block: escapes LaTeX special chars in topic string
"""

import re

# --------------------------------------------------------------------------
# Shared base packages
# --------------------------------------------------------------------------
_BASE = r"""
\usepackage{amsmath,amssymb,amsthm}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{microtype}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
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
        r"\titleformat{\section}{\normalsize\bfseries\centering}{\Roman{section}.}{0.5em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\itshape}{\Alph{subsection}.}{0.5em}{}" "\n"
        r"\pagestyle{fancy}" "\n"
        r"\fancyhf{}" "\n"
        r"\fancyhead[C]{\small IEEE Transactions --- Preprint}" "\n"
        r"\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "NeurIPS": (
        r"\documentclass[11pt,letterpaper]{article}" "\n"
        r"\usepackage[top=1in,bottom=1in,left=1.25in,right=1.25in]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}" "\n"
        r"\fancyhf{}" "\n"
        r"\fancyhead[R]{\small Preprint --- NeurIPS Style}" "\n"
        r"\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "ACL": (
        r"\documentclass[11pt,twocolumn]{article}" "\n"
        r"\usepackage[top=1in,bottom=1in,left=0.75in,right=0.75in,columnsep=0.3in]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\normalsize\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}" "\n"
        r"\fancyhf{}" "\n"
        r"\fancyhead[C]{\small ACL Style --- Preprint}" "\n"
        r"\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "CVPR": (
        r"\documentclass[10pt,twocolumn,letterpaper]{article}" "\n"
        r"\usepackage[top=1in,bottom=1in,left=0.75in,right=0.75in,columnsep=0.3in]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\large\bfseries\centering}{\thesection}{0.5em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{0.5em}{}" "\n"
        r"\pagestyle{fancy}" "\n"
        r"\fancyhf{}" "\n"
        r"\fancyhead[C]{\small CVPR Style --- Preprint}" "\n"
        r"\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "ICML": (
        r"\documentclass[10pt,letterpaper]{article}" "\n"
        r"\usepackage[top=1in,bottom=1in,left=1in,right=1in]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}" "\n"
        r"\fancyhf{}" "\n"
        r"\fancyhead[R]{\small ICML Style --- Preprint}" "\n"
        r"\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "Springer": (
        r"\documentclass[10pt,a4paper]{article}" "\n"
        r"\usepackage[top=2.2cm,bottom=2.2cm,left=2.2cm,right=2.2cm]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\itshape}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}" "\n"
        r"\fancyhf{}" "\n"
        r"\fancyhead[LE,RO]{\thepage}" "\n"
        r"\fancyhead[LO]{\small Springer LNCS Style}" "\n"
        r"\renewcommand{\headrulewidth}{0pt}" "\n"
    ),

    "Elsevier": (
        r"\documentclass[12pt,a4paper]{article}" "\n"
        r"\usepackage[top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm]{geometry}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}" "\n"
        r"\fancyhf{}" "\n"
        r"\fancyhead[L]{\small Elsevier Journal Style}" "\n"
        r"\fancyhead[R]{\small Preprint}" "\n"
        r"\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "Nature-style": (
        r"\documentclass[10pt]{article}" "\n"
        r"\usepackage[top=2cm,bottom=2cm,left=2cm,right=2cm]{geometry}" "\n"
        r"\usepackage{times}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\normalsize\bfseries}{}{0em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}" "\n"
        r"\pagestyle{fancy}" "\n"
        r"\fancyhf{}" "\n"
        r"\fancyhead[C]{\small Nature Style --- Preprint}" "\n"
        r"\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),

    "Custom": (
        r"\documentclass[12pt,a4paper]{article}" "\n"
        r"\usepackage[top=1in,bottom=1in,left=1in,right=1in]{geometry}" "\n"
        + _BASE + _THEOREMS +
        r"\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}" "\n"
        r"\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}" "\n"
        r"\pagestyle{fancy}" "\n"
        r"\fancyhf{}" "\n"
        r"\fancyhead[R]{\small Custom Academic Style}" "\n"
        r"\fancyfoot[C]{\thepage}" "\n"
        r"\renewcommand{\headrulewidth}{0.4pt}" "\n"
    ),
}

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
# Title block
# --------------------------------------------------------------------------

def _title_block(topic: str, conference: str) -> str:
    """Build title/author/maketitle block using only standard LaTeX commands."""
    # Escape LaTeX special characters
    safe = topic
    for ch, repl in [
        ("\\", ""),
        ("{", "("), ("}", ")"),
        ("_", r"\_"), ("&", r"\&"),
        ("#", r"\#"), ("%", r"\%"), ("$", r"\$"),
    ]:
        safe = safe.replace(ch, repl)
    return (
        f"\\title{{{safe}}}\n"
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
    preamble  = PREAMBLES.get(conference, PREAMBLES["Custom"])
    bib_style = BIB_STYLES.get(conference, "plain")
    title_blk = _title_block(topic, conference)
    opt       = optional_inputs or []

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
    Wrap raw LLM output in a proper LaTeX section command.

    Key fixes vs original:
    - Only strips top-level \\section{} — keeps \\subsection/\\subsubsection.
    - More robust markdown-fence stripping (handles ```latex variant).
    - Abstract: unwraps any accidental abstract env, returns bare abstract env.
    - Normalises excessive blank lines.
    """
    label   = SECTION_LABELS.get(section_key, section_key.capitalize())
    stripped = content.strip()

    # 1. Remove markdown code fences (```latex...``` or ```...```)
    stripped = re.sub(r'^```[a-zA-Z]*\s*', '', stripped)
    stripped = re.sub(r'\s*```$', '', stripped)
    stripped = stripped.strip()

    # 2. Remove ONLY top-level \section{...} / \section*{...}
    stripped = re.sub(r'\\section\*?\{[^}]*\}', '', stripped)

    # 3. Remove top-level \label{sec:...} (we add our own)
    stripped = re.sub(r'\\label\{sec:[^}]+\}', '', stripped)

    # 4. If abstract: strip any existing abstract environment wrapper
    if section_key == "abstract":
        stripped = re.sub(
            r'\\begin\{abstract\}(.*?)\\end\{abstract\}',
            lambda m: m.group(1).strip(),
            stripped,
            flags=re.DOTALL,
        )

    # 5. Remove markdown headings (# Heading)
    stripped = re.sub(r'^\s*#{1,6}\s+.*$', '', stripped, flags=re.MULTILINE)

    # 6. Remove bare plain-text heading lines matching this section label
    heading_pattern = r'^\s*' + re.escape(label) + r'\s*:?\s*$'
    stripped = re.sub(heading_pattern, '', stripped, flags=re.MULTILINE | re.IGNORECASE)

    # 7. Collapse 3+ consecutive newlines → double newline
    stripped = re.sub(r'\n{3,}', '\n\n', stripped)
    stripped = stripped.strip()

    # 8. Placeholder for empty content
    if not stripped:
        stripped = "\\noindent (Content not generated.)"

    # 9. Wrap appropriately
    if section_key == "abstract":
        return f"\\begin{{abstract}}\n{stripped}\n\\end{{abstract}}"
    else:
        return f"\\section{{{label}}}\n\\label{{sec:{section_key}}}\n\n{stripped}"
