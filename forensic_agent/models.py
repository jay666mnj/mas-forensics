from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class RiskLevel(str, Enum):
    READ_ONLY = "read_only"
    ANALYSIS = "analysis"
    EXPORT = "export"
    HIGH_RISK = "high_risk"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    source_path: str
    source_type: str
    hash_sha256: str
    acquisition_method: str = "mock"


@dataclass(frozen=True)
class ParsedRecord:
    record_id: str
    evidence_id: str
    record_type: str
    timestamp: str
    actors: tuple[str, ...]
    content: str
    source_ref: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UserIntent:
    question: str
    intent_type: str
    keywords: list[str]
    data_types: list[str]
    time_range: tuple[str | None, str | None]
    expected_output: list[str]
    risk_level: RiskLevel = RiskLevel.READ_ONLY


@dataclass
class DataScope:
    scope_id: str
    data_types: list[str]
    keywords: list[str]
    time_range: tuple[str | None, str | None]
    source: str


@dataclass
class TaskStep:
    step_id: str
    name: str
    tool_name: str
    args: dict[str, Any]
    risk_level: RiskLevel = RiskLevel.READ_ONLY
    requires_approval: bool = False
    status: StepStatus = StepStatus.PENDING
    result_ref: str | None = None


@dataclass
class TaskPlan:
    task_id: str
    goal: str
    steps: list[TaskStep]
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @classmethod
    def create(cls, goal: str, steps: list[TaskStep]) -> "TaskPlan":
        return cls(task_id=f"task-{uuid4().hex[:8]}", goal=goal, steps=steps)


@dataclass
class ToolResult:
    tool_name: str
    business_result: Any
    evidence_refs: list[str]
    metadata: dict[str, Any]
    success: bool = True
    error: str | None = None


@dataclass
class ToolCallLog:
    call_id: str
    task_id: str
    step_id: str
    tool_name: str
    input_args: dict[str, Any]
    evidence_refs: list[str]
    status: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    error: str | None = None


@dataclass
class Finding:
    finding_id: str
    claim: str
    confidence: float
    supporting_record_ids: list[str]
    supporting_tool_call_ids: list[str]
    finding_type: str = "lead"


def new_step(name: str, tool_name: str, args: dict[str, Any], risk: RiskLevel = RiskLevel.READ_ONLY) -> TaskStep:
    return TaskStep(
        step_id=f"step-{uuid4().hex[:8]}",
        name=name,
        tool_name=tool_name,
        args=args,
        risk_level=risk,
        requires_approval=risk in {RiskLevel.EXPORT, RiskLevel.HIGH_RISK},
    )
