from typing import Optional
from pydantic import BaseModel, Field

#1st agent
class ActionItem(BaseModel):
    description: str
    owner: Optional[str] = None
    deadline: Optional[str] = None
    depends_on: Optional[str] = None
    source_quote: Optional[str] = None


class ActionOutput(BaseModel):
    meeting_id: str
    action_items: list[ActionItem]
    summary: str

#2nd agent
class StrategicDecision(BaseModel):
    description: str
    rationale: Optional[str] = None
    priority_shift: Optional[str] = None
    source_quote: Optional[str] = None


class StrategicOutput(BaseModel):
    meeting_id: str
    decisions: list[StrategicDecision]
    summary: str

#3rd agent
class Risk(BaseModel):
    description: str
    severity: str = Field(..., description="low | medium | high")
    category: str = Field(..., description="e.g. timeline, ownership, contradiction, dependency")
    contradicts_meeting_id: Optional[str] = None
    source_quote: Optional[str] = None


class RiskOutput(BaseModel):
    meeting_id: str
    risks: list[Risk]
    summary: str

#consensus agent 4 that merges the output and checks if the 3 agents' stories matches hh
class ConflictItem(BaseModel):
    topic: str
    action_view: Optional[str] = None
    strategic_view: Optional[str] = None
    risk_view: Optional[str] = None
    resolution: Optional[str] = None


class ConsensusOutput(BaseModel):
    meeting_id: str
    agreements: list[str]
    conflicts: list[ConflictItem]
    unified_summary: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
