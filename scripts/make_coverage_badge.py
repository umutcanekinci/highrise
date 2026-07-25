"""Turns coverage.json (from `coverage json`) into a shields.io endpoint
badge JSON file, committed to the repo so the README's badge stays current
without any external service/account. Run after the test suite:

    uv run --group dev pytest tests/ --cov --cov-report=json -q
    uv run python scripts/make_coverage_badge.py
"""
import json
from pathlib import Path


def badge_color(percent: float) -> str:
    if percent < 50:
        return "red"
    if percent < 80:
        return "yellow"
    return "brightgreen"


def main() -> None:
    totals = json.loads(Path("coverage.json").read_text(encoding="utf-8"))["totals"]
    percent = round(totals["percent_covered"])

    badge = {
        "schemaVersion": 1,
        "label": "coverage",
        "message": f"{percent}%",
        "color": badge_color(percent),
    }

    out = Path(".github/badges/coverage.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(badge, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}: {badge}")


if __name__ == "__main__":
    main()
