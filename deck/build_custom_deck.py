"""Build the workshop deck when the shared corporate template is unavailable."""

from __future__ import annotations

import json
import sys
from pathlib import Path


SLIDES_RESOURCES = Path(
    "/Users/antonio.farias/.codex/plugins/cache/isaac-sync-fe-vibe/"
    "fe-google-tools/1.1.2/skills/google-slides/resources"
)
sys.path.insert(0, str(SLIDES_RESOURCES))

from gslides_builder import (  # noqa: E402
    add_slide,
    create_presentation,
    create_text_box,
    get_slide_ids,
    set_slide_background,
)


NAVY = {"red": 0.0, "green": 0.192, "blue": 0.349}
DARK_NAVY = {"red": 0.071, "green": 0.165, "blue": 0.271}
RED = {"red": 1.0, "green": 0.224, "blue": 0.161}
ORANGE = {"red": 1.0, "green": 0.439, "blue": 0.204}
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
INK = {"red": 0.10, "green": 0.12, "blue": 0.15}
LIGHT = {"red": 0.969, "green": 0.969, "blue": 0.969}
MUTED = {"red": 0.38, "green": 0.42, "blue": 0.46}


def add_footer(pres_id: str, page_id: str, number: int, dark: bool = False) -> None:
    color = WHITE if dark else MUTED
    create_text_box(
        pres_id,
        page_id,
        "DATABRICKS  |  CONTEXT ENGINEERING FOR HEALTHCARE AI AGENTS",
        0.55,
        5.30,
        7.7,
        0.18,
        font_size=7,
        font_color=color,
    )
    create_text_box(
        pres_id,
        page_id,
        str(number),
        9.02,
        5.28,
        0.55,
        0.18,
        font_size=8,
        bold=True,
        font_color=color,
    )


def build(spec_path: Path) -> dict[str, object]:
    specs = json.loads(spec_path.read_text())
    title = "Context Engineering for Healthcare AI Agents"
    pres_id = create_presentation(title)
    initial = get_slide_ids(pres_id)[0]
    slide_ids: list[str] = []

    for index, spec in enumerate(specs, start=1):
        page_id = initial if index == 1 else add_slide(pres_id, layout="BLANK")["pageId"]
        slide_ids.append(page_id)
        layout = spec.get("layout", "content_basic")
        title_text = spec.get("title", "")
        body = spec.get("body", "")

        if layout == "title":
            set_slide_background(pres_id, page_id, DARK_NAVY)
            create_text_box(pres_id, page_id, "CONTEXT ENGINEERING", 0.65, 0.58, 4.8, 0.35, 12, True, ORANGE)
            create_text_box(pres_id, page_id, title_text, 0.65, 1.25, 8.4, 1.65, 34, True, WHITE)
            create_text_box(pres_id, page_id, body, 0.70, 3.35, 7.8, 0.85, 16, False, WHITE)
            create_text_box(pres_id, page_id, "━━", 0.65, 4.55, 1.0, 0.30, 22, True, RED)
            add_footer(pres_id, page_id, index, dark=True)
            continue

        if layout in {"power_statement", "section_break_3", "closing"}:
            background = RED if layout == "power_statement" else DARK_NAVY
            set_slide_background(pres_id, page_id, background)
            label = "WHY NOW" if layout == "power_statement" else "HANDS-ON WORKSHOP"
            if layout == "closing":
                label = "THANK YOU"
            create_text_box(pres_id, page_id, label, 0.72, 0.72, 3.0, 0.30, 11, True, WHITE)
            create_text_box(pres_id, page_id, title_text, 0.72, 1.45, 8.45, 1.65, 30, True, WHITE)
            create_text_box(pres_id, page_id, body, 0.75, 3.45, 8.0, 0.80, 16, False, WHITE)
            add_footer(pres_id, page_id, index, dark=True)
            continue

        dark = layout == "industry_healthcare"
        set_slide_background(pres_id, page_id, NAVY if dark else LIGHT)
        title_color = WHITE if dark else NAVY
        body_color = WHITE if dark else INK
        accent = ORANGE if dark else RED
        create_text_box(pres_id, page_id, "━━", 0.55, 0.28, 0.75, 0.20, 18, True, accent)
        create_text_box(pres_id, page_id, title_text, 0.58, 0.63, 8.85, 0.82, 24, True, title_color)
        body_size = 14 if len(body) > 650 else 15 if len(body) > 430 else 17
        create_text_box(pres_id, page_id, body, 0.72, 1.62, 8.60, 3.38, body_size, False, body_color)
        add_footer(pres_id, page_id, index, dark=dark)

    return {
        "presentationId": pres_id,
        "url": f"https://docs.google.com/presentation/d/{pres_id}/edit",
        "slideIds": slide_ids,
    }


if __name__ == "__main__":
    result = build(Path(__file__).with_name("slide_spec.json"))
    print(json.dumps(result, indent=2))
