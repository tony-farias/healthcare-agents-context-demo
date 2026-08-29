"""Build the companion deck for the accuracy + PHI-safety combined lab."""

from pathlib import Path
import sys

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from build_combined_lab_deck import BG, CORAL, GREEN, MUTED, PANEL, SOFT, WARM, add_text, blank, bullets, card, footer, heading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "notebooks"))

from healthcare_reliability_utils import ReliabilityConfig, run_reliability_agent, scorecard  # noqa: E402

OUTPUT = Path(__file__).with_name("Accurate_and_PHI_Safe_Healthcare_Agents.pptx")


def build():
    configs = [
        ReliabilityConfig.broken(),
        ReliabilityConfig.over_redacted(),
        ReliabilityConfig.accurate_unsafe(),
        ReliabilityConfig.governed(),
    ]
    results = [run_reliability_agent(config) for config in configs]
    rows = scorecard(results)
    governed = results[-1]

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide = blank(prs)
    add_text(slide, "FICTIONAL BUSINESS CONTEXT", 0.72, 0.55, 5.5, 0.3, 11, CORAL, True)
    logo = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.35), Inches(1.35), Inches(1.35))
    logo.fill.solid(); logo.fill.fore_color.rgb = CORAL; logo.line.color.rgb = CORAL
    vertical = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.32), Inches(1.61), Inches(0.22), Inches(0.82))
    horizontal = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.05), Inches(1.91), Inches(0.76), Inches(0.22))
    for mark in (vertical, horizontal):
        mark.fill.solid(); mark.fill.fore_color.rgb = WARM; mark.line.color.rgb = WARM
    add_text(slide, "LumaCare", 2.35, 1.35, 5.5, 0.60, 31, WARM, True)
    add_text(slide, "CLINICAL INTELLIGENCE", 2.39, 2.05, 5.5, 0.30, 11, CORAL, True)
    add_text(slide, "LumaCare provides clinical decision support that helps care teams determine appropriate follow-up after hospital discharge.", 0.78, 3.20, 11.7, 1.05, 24, WARM, True)
    add_text(slide, "Its healthcare agent must use current clinical policy and the minimum necessary patient context—producing an accurate, cited recommendation without exposing PHI in prompts, tools, traces, or memory.", 0.82, 4.55, 11.6, 1.05, 17, SOFT)
    add_text(slide, "The company, logo, policies, patients, and identifiers in this lab are entirely fictional.", 0.82, 6.25, 11.0, 0.30, 11, MUTED)
    footer(slide, 1)

    slide = blank(prs)
    add_text(slide, "HEALTHCARE AGENT RELIABILITY", 0.72, 0.62, 6.0, 0.3, 11, CORAL, True)
    add_text(slide, "Accurate and PHI-Safe\nHealthcare AI Agents", 0.72, 1.35, 11.7, 1.65, 35, WARM, True)
    add_text(slide, "A 22-minute combined lab using nested MLflow traces", 0.76, 3.45, 10.5, 0.45, 18, SOFT)
    add_text(slide, "Minimum necessary context • Semantic redaction • Independent evaluation", 0.76, 4.10, 11.0, 0.35, 13, MUTED)
    footer(slide, 2)

    slide = blank(prs); heading(slide, "Healthcare agents must pass two independent tests", "Core tension")
    card(slide, 0.90, 1.75, 5.55, 3.80, "ACCURACY", "Correct interval\nControlling policy cited\nPrecedence explained\nClinical instruction preserved", GREEN)
    card(slide, 6.85, 1.75, 5.55, 3.80, "PHI SAFETY", "Direct identifiers absent\nTool scope authorized\nMinimum necessary context\nSafe memory and traces", CORAL)
    add_text(slide, "A correct answer can be unsafe. A private answer can be clinically useless.", 1.0, 6.05, 11.3, 0.42, 19, WARM, True, PP_ALIGN.CENTER)
    footer(slide, 2)

    slide = blank(prs); heading(slide, "Define purpose before accessing data", "Authorization boundary")
    bullets(slide, [
        "Intent: policy guidance—not a patient-specific recommendation.",
        "Authorized scope: clinical_policy; patient_record is not authorized.",
        "The authorization decision precedes retrieval, tool selection, and inference.",
        "The trace records purpose, patient specificity, and granted scopes.",
    ], size=21); footer(slide, 3)

    slide = blank(prs); heading(slide, "Four runs isolate four different outcomes", "Experiment matrix")
    labels = [
        ("BROKEN", "Accuracy ✕  Privacy ✕", "Conflicts, wrong tool, raw identifiers", CORAL),
        ("OVER-REDACTED", "Accuracy ✕  Privacy ✓", "Clinical concept removed", GREEN),
        ("ACCURATE / UNSAFE", "Accuracy ✓  Privacy ✕", "Correct answer leaks PHI", CORAL),
        ("GOVERNED", "Accuracy ✓  Privacy ✓", "Minimum necessary context", GREEN),
    ]
    for i, (label, score, body, accent) in enumerate(labels):
        x = 0.72 + (i % 2) * 6.20; y = 1.55 + (i // 2) * 2.35
        card(slide, x, y, 5.75, 1.90, label, score + "\n" + body, accent)
    footer(slide, 4)

    slide = blank(prs); heading(slide, "Naive redaction can destroy accuracy", "Semantic preservation")
    card(slide, 0.75, 1.70, 5.75, 3.65, "OVER-REDACT", "[PATIENT] was discharged with [CONDITION].\n\nResult: the retriever cannot select the cardiology policy.", CORAL)
    card(slide, 6.83, 1.70, 5.75, 3.65, "MINIMUM NECESSARY", "[PATIENT_1], [MRN_1] ... governed concept: heart failure.\n\nResult: identifiers are transformed while clinical meaning survives.", GREEN)
    footer(slide, 5)

    slide = blank(prs); heading(slide, "Govern retrieval with scope and precedence", "Accuracy boundary")
    bullets(slide, [
        "Retrieve only active policy content permitted by the authorized scope.",
        "CP-104 applies specifically to cardiology discharge and carries precedence 100.",
        "CP-104 explicitly overrides the general CM-220 standard for this scenario.",
        "The answer cites both the controlling source and why it controls.",
    ], size=20); footer(slide, 6)

    slide = blank(prs); heading(slide, "Validate every tool return before inference", "Tool boundary")
    stages = [("INTENT", "policy guidance"), ("DISCLOSE", "policy tool only"), ("AUTHORIZE", "scope allowed"), ("VALIDATE", "provenance valid"), ("INFER", "minimum context")]
    for i, (label, body) in enumerate(stages):
        x = 0.55 + i * 2.55
        card(slide, x, 2.20, 2.15, 2.15, label, body, GREEN if i else CORAL)
        if i < 4:
            add_text(slide, "→", x + 2.17, 2.95, 0.35, 0.4, 24, CORAL, True, PP_ALIGN.CENTER)
    footer(slide, 7)

    slide = blank(prs); heading(slide, "The governed answer is accurate, cited, and de-identified", "Expected result")
    add_text(slide, "“" + governed["answer"] + "”", 1.10, 1.70, 11.1, 2.0, 25, WARM, True, PP_ALIGN.CENTER)
    card(slide, 1.10, 4.25, 3.30, 1.35, "SOURCE", "CP-104", GREEN)
    card(slide, 5.00, 4.25, 3.30, 1.35, "INTERVAL", "Within 7 days", GREEN)
    card(slide, 8.90, 4.25, 3.30, 1.35, "IDENTIFIERS", "None retained", GREEN)
    footer(slide, 8)

    slide = blank(prs); heading(slide, "Compare evidence—not impressions", "Scorecard")
    table = slide.shapes.add_table(5, 5, Inches(0.65), Inches(1.55), Inches(12.05), Inches(4.60)).table
    widths = [2.45, 2.05, 2.05, 2.90, 2.60]
    for i, width in enumerate(widths): table.columns[i].width = Inches(width)
    headers = ["RUN", "ACCURACY", "PRIVACY", "TOOL", "POLICIES"]
    for col, value in enumerate(headers): table.cell(0, col).text = value
    for r, row in enumerate(rows, 1):
        values = [row["run"], "PASS" if row["accuracy_pass"] else "FAIL", "PASS" if row["privacy_pass"] else "FAIL", row["selected_tool"], row["retrieved_policies"]]
        for col, value in enumerate(values): table.cell(r, col).text = value
    for r in range(5):
        for c in range(5):
            cell = table.cell(r, c); cell.fill.solid(); cell.fill.fore_color.rgb = CORAL if r == 0 else PANEL
            for p in cell.text_frame.paragraphs:
                p.font.name = "DM Sans"; p.font.size = Pt(12); p.font.bold = r == 0; p.font.color.rgb = WARM
    footer(slide, 9)

    slide = blank(prs); heading(slide, "22-minute participant journey", "Lab flow")
    bullets(slide, [
        "0–2 — Define purpose and authorization",
        "2–8 — Run four controlled experiments",
        "8–12 — Inspect semantic redaction",
        "12–16 — Verify precedence and tool scope",
        "16–20 — Evaluate accuracy and privacy independently",
        "20–22 — Trace exit check",
    ], size=20); footer(slide, 10)

    slide = blank(prs); heading(slide, "Inspect six boundaries in MLflow", "Exit check")
    bullets(slide, [
        "authorize_request — purpose and scopes",
        "transform_patient_context — identifiers removed, meaning preserved",
        "retrieve_governed_context — source selection and precedence",
        "select_and_validate_tool — progressive disclosure and authorization",
        "generate_healthcare_answer — cited clinical result",
        "write_governed_memory — allowlisted persistence",
    ], size=18); footer(slide, 11)

    slide = blank(prs)
    add_text(slide, "THE DURABLE RULE", 0.72, 0.72, 4.0, 0.3, 11, CORAL, True)
    add_text(slide, "Minimize unnecessary disclosure.\nPreserve necessary clinical meaning.\nProve both in the trace.", 0.72, 1.55, 11.7, 2.60, 32, WARM, True)
    add_text(slide, "/Shared/context-engineering-healthcare-agents/notebooks/04_Accuracy_PHISafety_Combined_Lab", 0.76, 5.28, 12.0, 0.35, 12, MUTED)
    footer(slide, 12)

    prs.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
