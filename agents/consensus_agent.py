import json
import yaml
from pathlib import Path
from crewai import Agent, Task, Crew
from models.outputs import ActionOutput, StrategicOutput, RiskOutput, ConsensusOutput
from agents._llm import local_llm

_CONFIG_DIR = Path(__file__).parent.parent / "config"


def _cfg(yaml_file: str, key: str) -> dict:
    return yaml.safe_load((_CONFIG_DIR / yaml_file).read_text())[key]


def _compact_action(o: ActionOutput) -> str:
    lines = [f"Summary: {o.summary}", "Action items:"]
    for item in o.action_items:
        lines.append(f"  - {item.description} [owner: {item.owner}, deadline: {item.deadline}]")
    return "\n".join(lines)


def _compact_strategic(o: StrategicOutput) -> str:
    lines = [f"Summary: {o.summary}", "Decisions:"]
    for d in o.decisions:
        shift = f" [priority shift: {d.priority_shift}]" if d.priority_shift else ""
        lines.append(f"  - {d.description}{shift}")
    return "\n".join(lines)


def _compact_risk(o: RiskOutput) -> str:
    lines = [f"Summary: {o.summary}", "Risks:"]
    for r in o.risks:
        cross = f" [contradicts {r.contradicts_meeting_id}]" if r.contradicts_meeting_id else ""
        lines.append(f"  - [{r.severity.upper()}] {r.description}{cross}")
    return "\n".join(lines)


class ConsensusAgentCrew:
    def run(
        self,
        meeting_id: str,
        action_output: ActionOutput,
        strategic_output: StrategicOutput,
        risk_output: RiskOutput,
    ) -> ConsensusOutput:
        a = _cfg("agents.yaml", "consensus_agent")
        t = _cfg("tasks.yaml", "synthesize_consensus")

        agent = Agent(role=a["role"], goal=a["goal"], backstory=a["backstory"], llm=local_llm(max_tokens=2048), verbose=True)
        task = Task(
            description=t["description"].format(
                meeting_id=meeting_id,
                action_output=_compact_action(action_output),
                strategic_output=_compact_strategic(strategic_output),
                risk_output=_compact_risk(risk_output),
            ),
            expected_output=t["expected_output"],
            agent=agent,
        )
        result = Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
        return _parse(result, ConsensusOutput)


def _parse(result, model):
    raw = (result.raw if hasattr(result, "raw") else str(result)).strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return model.model_validate(json.loads(raw.strip()))
