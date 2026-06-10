from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from .models import ToolCallLog, ToolResult


class AuditLogger:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path = self.workspace / "audit.jsonl"
        self.call_ids: list[str] = []

    def record(self, task_id: str, step_id: str, tool_name: str, args: dict, result: ToolResult) -> ToolCallLog:
        log = ToolCallLog(
            call_id=f"call-{uuid4().hex[:8]}",
            task_id=task_id,
            step_id=step_id,
            tool_name=tool_name,
            input_args=args,
            evidence_refs=result.evidence_refs,
            status="success" if result.success else "failed",
            error=result.error,
        )
        self.call_ids.append(log.call_id)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_to_jsonable(log), ensure_ascii=False) + "\n")
        return log


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(item) for item in value]
    return value
