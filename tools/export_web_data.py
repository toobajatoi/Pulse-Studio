"""Export notes and generation banks for the static Pulse website."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import engine
OUT = ROOT / "web" / "data.js"


def main() -> None:
    notes = pd.read_csv(ROOT / "data" / "usability_feedback.csv").to_dict("records")
    payload = {
        "notes": notes,
        "themes": {k: {"label": v["label"], "need": v["need"], "keywords": list(v["keywords"])} for k, v in engine.THEMES.items()},
        "copyBank": engine.COPY_BANK,
        "arOverlay": engine.AR_OVERLAY,
        "layouts": engine.LAYOUTS,
        "defaultLayouts": engine.DEFAULT_LAYOUTS,
        "constraints": engine.CONSTRAINTS,
        "severityWeight": engine.SEVERITY_WEIGHT,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("window.PULSE_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(notes)} notes)")


if __name__ == "__main__":
    main()
