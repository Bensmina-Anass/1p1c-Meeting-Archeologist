"""
Evaluation: check which planted contradictions were detected.

Planted cross-meeting contradictions in the corpus:
  1. MTG-001 → MTG-002  : Deadline pushed March 14 → March 17
  2. MTG-004 → MTG-005  : Dashboard deadline April 4 → April 11
  3. MTG-004 → MTG-006  : PostgreSQL kept as permanent (MTG-004) vs. Sarah proposes dropping it (MTG-006)
  4. MTG-006             : Budget figure error — Sarah says 30k when budget is 50k
  5. MTG-007 → MTG-008  : Notifications = priority #1 (MTG-007) flipped to tech debt first (MTG-008)
  6. MTG-008 → MTG-010  : Client demo date — Sarah says May 15 (MTG-008), sales told Lina May 8 (MTG-010)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.database import get_all_risks, get_consensus

PLANTED = [
    {
        "id": 1,
        "description": "Deadline change: March 14 (MTG-001) → March 17 (MTG-002)",
        "source_meeting": "MTG-002",
        "contradicts": "MTG-001",
        "keywords": ["march 14", "march 17", "deadline", "migration"],
    },
    {
        "id": 2,
        "description": "Dashboard deadline change: April 4 (MTG-004) → April 11 (MTG-005)",
        "source_meeting": "MTG-005",
        "contradicts": "MTG-004",
        "keywords": ["april 4", "april 11", "dashboard", "deadline"],
    },
    {
        "id": 3,
        "description": "PostgreSQL permanence: kept forever (MTG-004) vs. drop it (MTG-006)",
        "source_meeting": "MTG-006",
        "contradicts": "MTG-004",
        "keywords": ["postgresql", "mongodb", "consolidat", "drop"],
    },
    {
        "id": 4,
        "description": "Budget figure error in MTG-006: Sarah says 30k, actual budget is 50k",
        "source_meeting": "MTG-006",
        "contradicts": None,
        "keywords": ["30,000", "50,000", "budget", "30k", "50k"],
    },
    {
        "id": 5,
        "description": "Priority flip: notifications first (MTG-007) → tech debt first (MTG-008)",
        "source_meeting": "MTG-008",
        "contradicts": "MTG-007",
        "keywords": ["notification", "tech debt", "priority", "orm"],
    },
    {
        "id": 6,
        "description": "Demo date conflict: May 15 (Sarah, MTG-008) vs May 8 (sales, MTG-010)",
        "source_meeting": "MTG-010",
        "contradicts": "MTG-008",
        "keywords": ["may 15", "may 8", "demo", "client"],
    },
]


def _risk_matches(risk: dict, planted: dict) -> bool:
    text = (risk["description"] + " " + (risk.get("source_quote") or "")).lower()
    keyword_hit = any(kw in text for kw in planted["keywords"])
    meeting_hit = (
        planted["contradicts"] is None
        or risk.get("contradicts_meeting_id") == planted["contradicts"]
        or risk["meeting_id"] == planted["source_meeting"]
    )
    return keyword_hit and meeting_hit


def evaluate():
    all_risks = get_all_risks()
    cross_risks = [r for r in all_risks if r.get("contradicts_meeting_id")]

    print("=" * 65)
    print("  EVALUATION — Planted Contradiction Detection")
    print("=" * 65)
    print(f"\nTotal risks in DB : {len(all_risks)}")
    print(f"Cross-meeting     : {len(cross_risks)}")

    detected = 0
    print("\n--- Per-contradiction results ---")
    for p in PLANTED:
        matching = [r for r in all_risks if _risk_matches(r, p)]
        status = "DETECTED" if matching else "MISSED"
        if matching:
            detected += 1
        print(f"\n[{status}] #{p['id']}: {p['description']}")
        if matching:
            for r in matching:
                cm = f" -> contradicts {r['contradicts_meeting_id']}" if r.get("contradicts_meeting_id") else ""
                print(f"         [{r['meeting_id']}] [{r['severity'].upper()}] {r['description'][:80]}{cm}")

    recall = detected / len(PLANTED)
    print(f"\n{'='*65}")
    print(f"  Recall: {detected}/{len(PLANTED)} = {recall:.0%}")
    print(f"{'='*65}\n")

    print("--- Confidence scores per meeting ---")
    for mid in [f"MTG-{i:03d}" for i in range(1, 11)]:
        c = get_consensus(mid)
        if c:
            print(f"  {mid}: {c['confidence_score']:.2f}")
        else:
            print(f"  {mid}: not processed yet")


if __name__ == "__main__":
    evaluate()
