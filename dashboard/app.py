import json
import sys
from pathlib import Path
from flask import Flask, jsonify, render_template, abort

CORPUS = Path(__file__).parent.parent / "corpus" / "transcripts"

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.database import (
    get_connection,
    get_tasks,
    get_decisions,
    get_risks,
    get_consensus,
)

app = Flask(__name__)

# Project grouping — derived from meeting sequence and titles
PROJECTS = {
    "Sprint 12 — DB Migration": {
        "meetings": ["MTG-001", "MTG-002", "MTG-003"],
        "color": "#4f8ef7",
    },
    "Sprint 13 — Dashboard": {
        "meetings": ["MTG-004", "MTG-005"],
        "color": "#a78bfa",
    },
    "Infrastructure & Budget": {
        "meetings": ["MTG-006"],
        "color": "#f59e0b",
    },
    "Product Roadmap": {
        "meetings": ["MTG-007"],
        "color": "#10b981",
    },
    "Sprint 14 — ORM & Search": {
        "meetings": ["MTG-008", "MTG-009"],
        "color": "#f97316",
    },
    "Sprint 15 — Notifications": {
        "meetings": ["MTG-010"],
        "color": "#ec4899",
    },
}

MEETING_TO_PROJECT = {}
for proj, data in PROJECTS.items():
    for mid in data["meetings"]:
        MEETING_TO_PROJECT[mid] = {"name": proj, "color": data["color"]}


def get_all_meetings() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM meetings ORDER BY meeting_id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    conn = get_connection()
    stats = {
        "meetings": conn.execute("SELECT COUNT(*) FROM meetings").fetchone()[0],
        "tasks": conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],
        "decisions": conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0],
        "risks": conn.execute("SELECT COUNT(*) FROM risks").fetchone()[0],
        "cross_meeting_risks": conn.execute(
            "SELECT COUNT(*) FROM risks WHERE contradicts_meeting_id IS NOT NULL"
        ).fetchone()[0],
    }
    conn.close()
    return stats


def get_all_cross_meeting_risks() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM risks WHERE contradicts_meeting_id IS NOT NULL ORDER BY meeting_id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/meetings")
def api_meetings():
    meetings = get_all_meetings()
    result = []
    for m in meetings:
        c = get_consensus(m["meeting_id"])
        proj = MEETING_TO_PROJECT.get(m["meeting_id"], {"name": "Other", "color": "#6b7280"})
        result.append({
            **m,
            "confidence_score": c["confidence_score"] if c else None,
            "agreements_count": len(c["agreements"]) if c else 0,
            "conflicts_count": len(c["conflicts"]) if c else 0,
            "project": proj["name"],
            "project_color": proj["color"],
        })
    return jsonify(result)


@app.route("/api/projects")
def api_projects():
    meetings = get_all_meetings()
    mtg_map = {m["meeting_id"]: m for m in meetings}
    result = []
    for proj_name, proj_data in PROJECTS.items():
        items = []
        for mid in proj_data["meetings"]:
            m = mtg_map.get(mid)
            if not m:
                continue
            c = get_consensus(mid)
            items.append({
                **m,
                "confidence_score": c["confidence_score"] if c else None,
                "agreements_count": len(c["agreements"]) if c else 0,
                "conflicts_count": len(c["conflicts"]) if c else 0,
            })
        result.append({
            "name": proj_name,
            "color": proj_data["color"],
            "meetings": items,
        })
    return jsonify(result)


@app.route("/api/meeting/<meeting_id>")
def api_meeting(meeting_id):
    tasks = get_tasks(meeting_id)
    decisions = get_decisions(meeting_id)
    risks = get_risks(meeting_id)
    consensus = get_consensus(meeting_id)
    proj = MEETING_TO_PROJECT.get(meeting_id, {"name": "Other", "color": "#6b7280"})
    return jsonify({
        "tasks": tasks,
        "decisions": decisions,
        "risks": risks,
        "consensus": consensus,
        "project": proj["name"],
        "project_color": proj["color"],
    })


@app.route("/api/meeting/<meeting_id>/transcript")
def api_transcript(meeting_id):
    path = CORPUS / f"{meeting_id}.json"
    if not path.exists():
        abort(404)
    data = json.loads(path.read_text())
    return jsonify({
        "meeting_id": data["meeting_id"],
        "title": data["title"],
        "date": str(data["date"]),
        "raw_text": data["raw_text"],
    })


@app.route("/api/contradictions")
def api_contradictions():
    risks = get_all_cross_meeting_risks()
    for r in risks:
        proj = MEETING_TO_PROJECT.get(r["meeting_id"], {"name": "Other", "color": "#6b7280"})
        r["project_color"] = proj["color"]
    return jsonify(risks)


if __name__ == "__main__":
    app.run(debug=True, port=5050)
