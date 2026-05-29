import json
import sqlite3
from pathlib import Path

from models.inputs import MeetingTranscript
from models.outputs import ActionOutput, StrategicOutput, RiskOutput, ConsensusOutput

DB_PATH = Path(__file__).parent / "memory.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS meetings (
            meeting_id   TEXT PRIMARY KEY,
            date         TEXT NOT NULL,
            title        TEXT NOT NULL,
            duration_min INTEGER,
            location     TEXT
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id   TEXT NOT NULL,
            description  TEXT NOT NULL,
            owner        TEXT,
            deadline     TEXT,
            depends_on   TEXT,
            source_quote TEXT,
            FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
        );

        CREATE TABLE IF NOT EXISTS decisions (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id     TEXT NOT NULL,
            description    TEXT NOT NULL,
            rationale      TEXT,
            priority_shift TEXT,
            source_quote   TEXT,
            FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
        );

        CREATE TABLE IF NOT EXISTS risks (
            id                     INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id             TEXT NOT NULL,
            description            TEXT NOT NULL,
            severity               TEXT NOT NULL,
            category               TEXT NOT NULL,
            contradicts_meeting_id TEXT,
            source_quote           TEXT,
            FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
        );

        CREATE TABLE IF NOT EXISTS consensus_results (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id       TEXT NOT NULL UNIQUE,
            unified_summary  TEXT NOT NULL,
            agreements       TEXT NOT NULL,
            conflicts        TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
        );
    """)

    conn.commit()
    conn.close()


# --- WRITE ---

def save_meeting(transcript: MeetingTranscript):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO meetings VALUES (?, ?, ?, ?, ?)",
        (transcript.meeting_id, str(transcript.date), transcript.title,
         transcript.duration_minutes, transcript.location)
    )
    conn.commit()
    conn.close()


def save_action_output(output: ActionOutput):
    conn = get_connection()
    conn.executemany(
        "INSERT INTO tasks (meeting_id, description, owner, deadline, depends_on, source_quote) VALUES (?, ?, ?, ?, ?, ?)",
        [(output.meeting_id, item.description, item.owner, item.deadline, item.depends_on, item.source_quote)
         for item in output.action_items]
    )
    conn.commit()
    conn.close()


def save_strategic_output(output: StrategicOutput):
    conn = get_connection()
    conn.executemany(
        "INSERT INTO decisions (meeting_id, description, rationale, priority_shift, source_quote) VALUES (?, ?, ?, ?, ?)",
        [(output.meeting_id, d.description, d.rationale, d.priority_shift, d.source_quote)
         for d in output.decisions]
    )
    conn.commit()
    conn.close()


def save_risk_output(output: RiskOutput):
    conn = get_connection()
    conn.executemany(
        "INSERT INTO risks (meeting_id, description, severity, category, contradicts_meeting_id, source_quote) VALUES (?, ?, ?, ?, ?, ?)",
        [(output.meeting_id, r.description, r.severity, r.category, r.contradicts_meeting_id, r.source_quote)
         for r in output.risks]
    )
    conn.commit()
    conn.close()


def save_consensus_output(output: ConsensusOutput):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO consensus_results (meeting_id, unified_summary, agreements, conflicts, confidence_score) VALUES (?, ?, ?, ?, ?)",
        (output.meeting_id, output.unified_summary,
         json.dumps(output.agreements),
         json.dumps([c.model_dump() for c in output.conflicts]),
         output.confidence_score)
    )
    conn.commit()
    conn.close()


# --- READ ---

def get_tasks(meeting_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks WHERE meeting_id = ?", (meeting_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_decisions(meeting_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM decisions WHERE meeting_id = ?", (meeting_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_risks(meeting_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM risks WHERE meeting_id = ?", (meeting_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_consensus(meeting_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM consensus_results WHERE meeting_id = ?", (meeting_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    result = dict(row)
    result["agreements"] = json.loads(result["agreements"])
    result["conflicts"] = json.loads(result["conflicts"])
    return result


def get_all_risks() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM risks").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_decisions() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM decisions ORDER BY meeting_id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_decisions_with_context() -> list[dict]:
    """Returns decisions joined with meeting title/date for richer prior context."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT d.*, m.title as meeting_title, m.date as meeting_date
        FROM decisions d
        JOIN meetings m ON d.meeting_id = m.meeting_id
        ORDER BY d.meeting_id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
