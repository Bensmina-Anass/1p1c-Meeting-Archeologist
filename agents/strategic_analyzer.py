import json
from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, task
from models.outputs import StrategicOutput


@CrewBase
class StrategicAnalyzerCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def strategic_analyzer(self) -> Agent:
        return Agent(config=self.agents_config["strategic_analyzer"], verbose=True)

    @task
    def extract_strategic(self) -> Task:
        return Task(config=self.tasks_config["extract_strategic"])

    def run(self, meeting_id: str, transcript: str) -> StrategicOutput:
        crew = Crew(
            agents=[self.strategic_analyzer()],
            tasks=[self.extract_strategic()],
            verbose=True,
        )
        result = crew.kickoff(inputs={"meeting_id": meeting_id, "transcript": transcript})
        raw = result.raw if hasattr(result, "raw") else str(result)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return StrategicOutput.model_validate(json.loads(raw.strip()))
