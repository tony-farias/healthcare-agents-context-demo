"""Generate the fictional workshop policy PDFs from their Markdown sources."""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parent


def build(source: Path) -> Path:
    target = source.with_suffix(".pdf")
    styles = getSampleStyleSheet()
    styles["Title"].textColor = HexColor("#FF5F46")
    story = []
    for raw in source.read_text().splitlines():
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 0.08 * inch))
        elif line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
        elif line.startswith("> "):
            story.append(Paragraph(f"<b>{line[2:].replace('**', '')}</b>", styles["BodyText"]))
        elif line.startswith("|"):
            values = [value.strip() for value in line.strip("|").split("|")]
            if values and not all(set(value) <= {"-", ":"} for value in values):
                story.append(Paragraph(" — ".join(values), styles["BodyText"]))
        else:
            story.append(Paragraph(line.replace("**", "<b>", 1).replace("**", "</b>", 1), styles["BodyText"]))
    doc = SimpleDocTemplate(
        str(target), pagesize=LETTER, rightMargin=0.7 * inch, leftMargin=0.7 * inch,
        topMargin=0.65 * inch, bottomMargin=0.65 * inch,
    )
    doc.build(story)
    return target


if __name__ == "__main__":
    for markdown in sorted(ROOT.glob("*.md")):
        print(build(markdown))
