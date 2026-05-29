import json
from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, task
from models.outputs import RiskOutput


@CrewBase
class RiskAnalyzerCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def risk_analyzer(self) -> Agent:
        return Agent(config=self.agents_config["risk_analyzer"], verbose=True)

    @task
    def extract_risks(self) -> Task:
        return Task(config=self.tasks_config["extract_risks"])

    def run(self, meeting_id: str, transcript: str) -> RiskOutput:
        crew = Crew(
            agents=[self.risk_analyzer()],
            tasks=[self.extract_risks()],
            verbose=True,
        )
        result = crew.kickoff(inputs={"meeting_id": meeting_id, "transcript": transcript})
        raw = result.raw if hasattr(result, "raw") else str(result)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return RiskOutput.model_validate(json.loads(raw.strip()))
