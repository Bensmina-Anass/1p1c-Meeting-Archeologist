from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class Participant(BaseModel):
    name: str
    role: Optional[str] = None


class AgendaItem(BaseModel):
    title: str
    description: Optional[str] = None


class MeetingTranscript(BaseModel):
    meeting_id: str = Field(..., description="Unique identifier, e.g. 'MTG-001'")
    date: date
    title: str
    participants: list[Participant]
    agenda: list[AgendaItem]
    raw_text: str = Field(..., description="Full verbatim transcript text")
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
