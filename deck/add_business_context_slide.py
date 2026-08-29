"""Insert the fictional LumaCare business-context slide into the Google deck."""

import json
import sys
from pathlib import Path

RESOURCES = Path("/Users/antonio.farias/.codex/plugins/cache/isaac-sync-fe-vibe/fe-google-tools/1.1.2/skills/google-slides/resources")
sys.path.insert(0, str(RESOURCES))

from gslides_builder import add_slide, batch_update, create_shape, create_text_box, move_slides, set_slide_background

PRESENTATION_ID = "1FLhJBZ3l53plx3S4DUaJBGNOXS2eKT7ab33Ty_UcZ7k"
DARK = {"red": 0.106, "green": 0.106, "blue": 0.106}
CORAL = {"red": 1.0, "green": 0.373, "blue": 0.275}
WARM = {"red": 0.98, "green": 0.969, "blue": 0.949}
SOFT = {"red": 0.816, "green": 0.816, "blue": 0.816}
MUTED = {"red": 0.58, "green": 0.58, "blue": 0.58}


def build():
    def colored_shape(shape_type, x, y, width, height, color):
        result = create_shape(PRESENTATION_ID, page_id, shape_type, x, y, width, height)
        shape_id = result["shapeId"]
        batch_update(PRESENTATION_ID, [{
            "updateShapeProperties": {
                "objectId": shape_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": color}}},
                    "outline": {"propertyState": "NOT_RENDERED"},
                },
                "fields": "shapeBackgroundFill,outline",
            }
        }])

    page_id = add_slide(PRESENTATION_ID, layout="BLANK")["pageId"]
    set_slide_background(PRESENTATION_ID, page_id, DARK)
    create_text_box(PRESENTATION_ID, page_id, "FICTIONAL BUSINESS CONTEXT", 0.55, 0.38, 4.5, 0.25, 11, True, CORAL)
    colored_shape("ROUND_RECTANGLE", 0.58, 1.02, 1.03, 1.03, CORAL)
    colored_shape("RECTANGLE", 1.02, 1.20, 0.17, 0.64, WARM)
    colored_shape("RECTANGLE", 0.82, 1.43, 0.58, 0.17, WARM)
    create_text_box(PRESENTATION_ID, page_id, "LumaCare", 1.78, 1.00, 4.3, 0.52, 30, True, WARM)
    create_text_box(PRESENTATION_ID, page_id, "CLINICAL INTELLIGENCE", 1.81, 1.55, 4.2, 0.25, 10, True, CORAL)
    create_text_box(PRESENTATION_ID, page_id, "LumaCare provides clinical decision support that helps care teams determine appropriate follow-up after hospital discharge.", 0.60, 2.45, 8.75, 0.90, 23, True, WARM)
    create_text_box(PRESENTATION_ID, page_id, "Its healthcare agent must use current clinical policy and the minimum necessary patient context—producing an accurate, cited recommendation without exposing PHI in prompts, tools, traces, or memory.", 0.62, 3.55, 8.70, 0.85, 16, False, SOFT)
    create_text_box(PRESENTATION_ID, page_id, "The company, logo, policies, patients, and identifiers in this lab are entirely fictional.", 0.62, 4.78, 8.5, 0.24, 10, False, MUTED)
    create_text_box(PRESENTATION_ID, page_id, "DATABRICKS  |  ACCURATE AND PHI-SAFE HEALTHCARE AGENTS", 0.55, 5.29, 7.6, 0.16, 7, False, MUTED)
    move_slides(PRESENTATION_ID, [page_id], 0)
    print(json.dumps({"presentationId": PRESENTATION_ID, "pageId": page_id}, indent=2))


if __name__ == "__main__":
    build()
