import json
import yaml
from pathlib import Path
from crewai import Agent, Task, Crew
from models.outputs import ActionOutput
from agents._llm import local_llm

_CONFIG_DIR = Path(__file__).parent.parent / "config"


def _cfg(yaml_file: str, key: str) -> dict:
    return yaml.safe_load((_CONFIG_DIR / yaml_file).read_text())[key]


class ActionAnalyzerCrew:
    def run(self, meeting_id: str, transcript: str) -> ActionOutput:
        a = _cfg("agents.yaml", "action_analyzer")
        t = _cfg("tasks.yaml", "extract_actions")

        agent = Agent(role=a["role"], goal=a["goal"], backstory=a["backstory"], llm=local_llm(), verbose=True)
        task = Task(
            description=t["description"].format(meeting_id=meeting_id, transcript=transcript),
            expected_output=t["expected_output"],
            agent=agent,
        )
        result = Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
        return _parse(result, ActionOutput)


def _parse(result, model):
    raw = (result.raw if hasattr(result, "raw") else str(result)).strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return model.model_validate(json.loads(raw.strip()))
