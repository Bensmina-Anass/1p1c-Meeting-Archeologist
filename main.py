"""
Meeting Archeologist — full pipeline.

Usage:
    python main.py                   # runs MTG-001
    python main.py MTG-003           # runs a specific meeting
    python main.py MTG-001 MTG-002   # runs multiple meetings
"""
import json
import sys
from pathlib import Path

from models.inputs import MeetingTranscript
from agents import ActionAnalyzerCrew, StrategicAnalyzerCrew, RiskAnalyzerCrew, ConsensusAgentCrew
from memory.database import (
    init_db,
    save_meeting,
    save_action_output,
    save_strategic_output,
    save_risk_output,
    save_consensus_output,
    get_all_decisions_with_context,
    get_all_risks,
)

CORPUS = Path(__file__).parent / "corpus" / "transcripts"


def load_transcript(meeting_id: str) -> MeetingTranscript:
    path = CORPUS / f"{meeting_id}.json"
    return MeetingTranscript.model_validate(json.loads(path.read_text()))


def _build_prior_context(current_meeting_id: str) -> str:
    decisions = [d for d in get_all_decisions_with_context() if d["meeting_id"] != current_meeting_id]
    if not decisions:
        return ""

    # Keep only the 8 most recent decisions to bound prompt size
    decisions = decisions[-8:]

    # A sprint is closed when its review meeting has been processed.
    # MTG-003 = Sprint 12 Review, MTG-005 = Sprint 13 Mid (sprint 12 fully done),
    # MTG-009 = Sprint 14 Mid, MTG-010 opens "Sprint 14 is done".
    closed_sprint_meetings = {"MTG-001", "MTG-002", "MTG-003"}
    if current_meeting_id >= "MTG-006":
        closed_sprint_meetings |= {"MTG-004", "MTG-005"}
    if current_meeting_id >= "MTG-010":
        closed_sprint_meetings |= {"MTG-008", "MTG-009"}

    lines = [
        "--- PRIOR MEETING CONTEXT ---",
        "Use ONLY this context to set contradicts_meeting_id.",
        "A contradiction means the SAME specific commitment, deadline, or decision is being",
        "directly reversed or violated — NOT similar terminology used in a different project context.\n",
        "Decisions from past meetings (most recent first):",
    ]
    for d in reversed(decisions):
        closed = " [SPRINT CLOSED — this item is no longer active]" if d["meeting_id"] in closed_sprint_meetings else ""
        shift = f" | priority shift: {d['priority_shift']}" if d.get("priority_shift") else ""
        lines.append(f"  [{d['meeting_id']} | {d['meeting_title']} | {d['meeting_date']}]{closed}")
        lines.append(f"    Decision: {d['description']}{shift}")

    lines.append("\n--- END PRIOR CONTEXT ---\n")
    return "\n".join(lines)


def run_pipeline(meeting_id: str) -> None:
    print(f"\n{'='*65}")
    print(f"  Meeting Archeologist — {meeting_id}")
    print(f"{'='*65}")

    transcript = load_transcript(meeting_id)
    print(f"  Title    : {transcript.title}")
    print(f"  Date     : {transcript.date}")
    print(f"  Duration : {transcript.duration_minutes} min")
    print(f"{'='*65}\n")

    save_meeting(transcript)

    print("[ Phase 1 ] Running Action Analyzer ...")
    action_out = ActionAnalyzerCrew().run(transcript.meeting_id, transcript.raw_text)
    save_action_output(action_out)
    print(f"  -> {len(action_out.action_items)} action items extracted\n")

    print("[ Phase 1 ] Running Strategic Analyzer ...")
    strategic_out = StrategicAnalyzerCrew().run(transcript.meeting_id, transcript.raw_text)
    save_strategic_output(strategic_out)
    print(f"  -> {len(strategic_out.decisions)} strategic decisions extracted\n")

    print("[ Phase 1 ] Running Risk Analyzer ...")
    prior_context = _build_prior_context(transcript.meeting_id)
    risk_out = RiskAnalyzerCrew().run(transcript.meeting_id, transcript.raw_text, prior_context)
    save_risk_output(risk_out)
    cross_meeting = [r for r in risk_out.risks if r.contradicts_meeting_id]
    print(f"  -> {len(risk_out.risks)} risks identified ({len(cross_meeting)} cross-meeting)\n")

    print("[ Phase 2 ] Running Consensus Agent ...")
    consensus_out = ConsensusAgentCrew().run(
        meeting_id=transcript.meeting_id,
        action_output=action_out,
        strategic_output=strategic_out,
        risk_output=risk_out,
    )
    save_consensus_output(consensus_out)

    print(f"\n{'='*65}")
    print(f"  FINAL REPORT — {meeting_id}")
    print(f"{'='*65}")
    print(f"\nConfidence score : {consensus_out.confidence_score:.2f}")
    print(f"\nUnified Summary:\n{consensus_out.unified_summary}")

    if consensus_out.agreements:
        print(f"\nAgreements ({len(consensus_out.agreements)}):")
        for a in consensus_out.agreements:
            print(f"  + {a}")

    if consensus_out.conflicts:
        print(f"\nConflicts ({len(consensus_out.conflicts)}):")
        for c in consensus_out.conflicts:
            print(f"  ! {c.topic}")
            if c.resolution:
                print(f"    -> {c.resolution}")

    if cross_meeting:
        print(f"\nCross-meeting contradictions flagged:")
        for r in cross_meeting:
            print(f"  [vs {r.contradicts_meeting_id}] {r.description}")

    print(f"\n[Saved to SQLite]\n")


if __name__ == "__main__":
    init_db()
    meeting_ids = sys.argv[1:] if len(sys.argv) > 1 else ["MTG-001"]
    for mid in meeting_ids:
        run_pipeline(mid)
