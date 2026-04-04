"""
zip_export.py
Assembles the LaTeX paper and all supporting files into a structured ZIP archive.
"""

import io
import zipfile
from datetime import datetime


def build_zip(
    main_tex: str,
    references_bib: str,
    sections: dict[str, str],          # {"intro": "...", "method": "...", ...}
    optional_files: dict[str, str],    # {"appendix.tex": "...", ...}
    readme_txt: str,
    figures_placeholder: bool = True,
) -> bytes:
    """
    Build and return ZIP archive as bytes.

    ZIP structure:
      main.tex
      references.bib
      sections/
        intro.tex
        method.tex
        results.tex
        ...
      appendix.tex  (optional)
      figures/
        placeholder.txt
      README.txt
    """
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Core files
        zf.writestr("main.tex", main_tex)
        zf.writestr("references.bib", references_bib)

        # Section files
        for name, content in sections.items():
            zf.writestr(f"sections/{name}.tex", content)

        # Optional injected files (appendix, supplementary, etc.)
        for filename, content in optional_files.items():
            zf.writestr(filename, content)

        # Figures directory placeholder
        if figures_placeholder:
            zf.writestr(
                "figures/placeholder.txt",
                "# Figures directory\n"
                "Place your figure files here (e.g., fig1.pdf, fig2.png).\n"
                "Some captions in the paper reference synthetic/hallucinated figures.\n",
            )

        # README
        zf.writestr("README.txt", readme_txt)

    buffer.seek(0)
    return buffer.read()


def build_readme(
    topic: str,
    conference: str,
    injection_report: list[dict],
    hallucination_report: list[dict],
    timestamp: str | None = None,
) -> str:
    """Generate a human-readable README describing what was injected and where."""
    ts = timestamp or datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "=" * 70,
        "  SYNTHETIC LATEX PAPER — INJECTION & HALLUCINATION REPORT",
        "=" * 70,
        f"  Generated : {ts}",
        f"  Topic     : {topic}",
        f"  Style     : {conference}",
        "=" * 70,
        "",
        "⚠️  WARNING: This paper contains INTENTIONALLY INJECTED adversarial",
        "   content for research and red-teaming purposes. DO NOT publish.",
        "",
        "─" * 70,
        "PROMPT INJECTION PATTERNS",
        "─" * 70,
    ]

    if injection_report:
        for i, item in enumerate(injection_report, 1):
            lines += [
                f"\n[Injection #{i}]",
                f"  Type     : {item.get('type', 'N/A')}",
                f"  Source   : {item.get('source', 'N/A')}",
                f"  Modality : {item.get('modality', 'N/A')}",
                f"  Location : {item.get('location', 'N/A')}",
                f"  Severity : {item.get('severity', 'N/A')}",
                f"  Snippet  : {item.get('snippet', '')[:120]}...",
            ]
    else:
        lines.append("  (none injected)")

    lines += [
        "",
        "─" * 70,
        "HALLUCINATION PATTERNS",
        "─" * 70,
    ]

    if hallucination_report:
        for i, item in enumerate(hallucination_report, 1):
            lines += [
                f"\n[Hallucination #{i}]",
                f"  Type     : {item.get('type', 'N/A')}",
                f"  Location : {item.get('location', 'N/A')}",
                f"  Severity : {item.get('severity', 'N/A')}",
                f"  Detail   : {item.get('detail', '')}",
            ]
    else:
        lines.append("  (none injected)")

    lines += [
        "",
        "=" * 70,
        "  END OF REPORT",
        "=" * 70,
    ]

    return "\n".join(lines)
