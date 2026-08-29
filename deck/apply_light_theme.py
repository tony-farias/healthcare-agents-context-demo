"""Convert the published combined-lab deck to a Databricks-style light theme."""

import json
import sys
from pathlib import Path

RESOURCES = Path("/Users/antonio.farias/.codex/plugins/cache/isaac-sync-fe-vibe/fe-google-tools/1.1.2/skills/google-slides/resources")
sys.path.insert(0, str(RESOURCES))

from gslides_builder import batch_update, get_presentation

PRESENTATION_ID = "1FLhJBZ3l53plx3S4DUaJBGNOXS2eKT7ab33Ty_UcZ7k"
LIGHT = {"red": 0.969, "green": 0.969, "blue": 0.969}
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
NAVY = {"red": 0.0, "green": 0.192, "blue": 0.349}
INK = {"red": 0.10, "green": 0.12, "blue": 0.15}
MUTED = {"red": 0.38, "green": 0.42, "blue": 0.46}
CORAL = {"red": 1.0, "green": 0.373, "blue": 0.275}
GREEN = {"red": 0.16, "green": 0.55, "blue": 0.36}


def rgb(fill):
    return fill.get("solidFill", {}).get("color", {}).get("rgbColor", {})


def close(color, target, tolerance=0.08):
    return color and all(abs(color.get(k, 0) - target.get(k, 0)) <= tolerance for k in ("red", "green", "blue"))


def first_text_color(text):
    for element in text.get("textElements", []):
        color = element.get("textRun", {}).get("style", {}).get("foregroundColor", {}).get("opaqueColor", {}).get("rgbColor")
        if color is not None:
            return color
    return {}


def update_text(object_id, color, cell=None):
    request = {
        "objectId": object_id,
        "textRange": {"type": "ALL"},
        "style": {"foregroundColor": {"opaqueColor": {"rgbColor": color}}},
        "fields": "foregroundColor",
    }
    if cell is not None:
        request["cellLocation"] = cell
    return {"updateTextStyle": request}


def choose_text_color(current, on_accent=False):
    if on_accent:
        return WHITE
    if close(current, CORAL):
        return CORAL
    if close(current, {"red": 0.314, "green": 0.784, "blue": 0.569}):
        return GREEN
    if close(current, {"red": 0.58, "green": 0.58, "blue": 0.58}):
        return MUTED
    if close(current, {"red": 0.816, "green": 0.816, "blue": 0.816}):
        return INK
    return NAVY


def build_requests(presentation):
    requests = []
    for slide in presentation["slides"]:
        requests.append({
            "updatePageProperties": {
                "objectId": slide["objectId"],
                "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": LIGHT}}}},
                "fields": "pageBackgroundFill",
            }
        })
        for element in slide.get("pageElements", []):
            object_id = element["objectId"]
            if "shape" in element:
                shape = element["shape"]
                fill = rgb(shape.get("shapeProperties", {}).get("shapeBackgroundFill", {}))
                accent_fill = close(fill, CORAL) or close(fill, {"red": 0.314, "green": 0.784, "blue": 0.569})
                if close(fill, {"red": 0.165, "green": 0.165, "blue": 0.165}) or close(fill, {"red": 0.106, "green": 0.106, "blue": 0.106}):
                    requests.append({
                        "updateShapeProperties": {
                            "objectId": object_id,
                            "shapeProperties": {
                                "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": WHITE}}},
                                "outline": {"outlineFill": {"solidFill": {"color": {"rgbColor": LIGHT}}}},
                            },
                            "fields": "shapeBackgroundFill,outline.outlineFill",
                        }
                    })
                if "text" in shape:
                    current = first_text_color(shape["text"])
                    requests.append(update_text(object_id, choose_text_color(current, accent_fill)))
            elif "table" in element:
                table = element["table"]
                for row_index, row in enumerate(table.get("tableRows", [])):
                    for col_index, cell in enumerate(row.get("tableCells", [])):
                        location = {"rowIndex": row_index, "columnIndex": col_index}
                        fill = rgb(cell.get("tableCellProperties", {}).get("tableCellBackgroundFill", {}))
                        accent_fill = close(fill, CORAL)
                        new_fill = CORAL if accent_fill else WHITE
                        requests.append({
                            "updateTableCellProperties": {
                                "objectId": object_id,
                                "tableRange": {"location": location, "rowSpan": 1, "columnSpan": 1},
                                "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": new_fill}}}},
                                "fields": "tableCellBackgroundFill",
                            }
                        })
                        current = first_text_color(cell.get("text", {}))
                        requests.append(update_text(object_id, choose_text_color(current, accent_fill), location))
    return requests


def main():
    presentation = get_presentation(PRESENTATION_ID)
    requests = build_requests(presentation)
    for start in range(0, len(requests), 100):
        result = batch_update(PRESENTATION_ID, requests[start:start + 100])
        if "error" in result:
            raise RuntimeError(result["error"])
    print(json.dumps({"presentationId": PRESENTATION_ID, "slides": len(presentation["slides"]), "updates": len(requests)}, indent=2))


if __name__ == "__main__":
    main()
