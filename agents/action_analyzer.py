import json
from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, task
from models.outputs import ActionOutput


@CrewBase
class ActionAnalyzerCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def action_analyzer(self) -> Agent:
        return Agent(config=self.agents_config["action_analyzer"], verbose=True)

    @task
    def extract_actions(self) -> Task:
        return Task(config=self.tasks_config["extract_actions"])

    def run(self, meeting_id: str, transcript: str) -> ActionOutput:
        crew = Crew(
            agents=[self.action_analyzer()],
            tasks=[self.extract_actions()],
            verbose=True,
        )
        result = crew.kickoff(inputs={"meeting_id": meeting_id, "transcript": transcript})
        raw = result.raw if hasattr(result, "raw") else str(result)
        # strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return ActionOutput.model_validate(json.loads(raw.strip()))
