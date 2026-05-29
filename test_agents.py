"""Quick smoke test — run each analyzer on MTG-001 and print the result."""
import json
from pathlib import Path
from models.inputs import MeetingTranscript
from agents import ActionAnalyzerCrew, StrategicAnalyzerCrew, RiskAnalyzerCrew


def load(meeting_id: str) -> MeetingTranscript:
    path = Path(f"corpus/transcripts/{meeting_id}.json")
    return MeetingTranscript.model_validate(json.loads(path.read_text()))


if __name__ == "__main__":
    for mid in ["MTG-001", "MTG-002"]:
        t = load(mid)
        print(f"\n{'='*60}")
        print(f"Testing on {mid}: {t.title}")
        print("="*60)

        print("\n--- Action Analyzer ---")
        action_out = ActionAnalyzerCrew().run(t.meeting_id, t.raw_text)
        print(action_out.model_dump_json(indent=2))

        print("\n--- Strategic Analyzer ---")
        strategic_out = StrategicAnalyzerCrew().run(t.meeting_id, t.raw_text)
        print(strategic_out.model_dump_json(indent=2))

        print("\n--- Risk Analyzer ---")
        risk_out = RiskAnalyzerCrew().run(t.meeting_id, t.raw_text)
        print(risk_out.model_dump_json(indent=2))
