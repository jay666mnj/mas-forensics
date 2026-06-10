from __future__ import annotations

from pathlib import Path
from typing import Any

from .agents import President, Receptionist, Reviewer
from .audit import AuditLogger
from .models import StepStatus, TaskPlan
from .tools import create_default_registry


class ExecutionContext:
    def __init__(self) -> None:
        self.results: dict[str, Any] = {}
        self.last_call_ids: list[str] = []

    def resolve(self, value: Any) -> Any:
        if isinstance(value, str) and value.startswith("$"):
            return self.results[value[1:]]
        if isinstance(value, dict):
            return {key: self.resolve(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self.resolve(item) for item in value]
        return value


class TaskExecutor:
    def __init__(self, workspace: Path) -> None:
        self.registry = create_default_registry()
        self.audit = AuditLogger(workspace)

    def execute(self, plan: TaskPlan) -> ExecutionContext:
        context = ExecutionContext()
        for step in plan.steps:
            step.status = StepStatus.RUNNING
            resolved_args = context.resolve(step.args)
            if step.tool_name == "build_findings":
                resolved_args["call_ids"] = context.last_call_ids.copy()
            result = self.registry.call(step.tool_name, **resolved_args)
            log = self.audit.record(plan.task_id, step.step_id, step.tool_name, resolved_args, result)
            context.last_call_ids.append(log.call_id)
            if not result.success:
                step.status = StepStatus.FAILED
                raise RuntimeError(result.error or f"Tool failed: {step.tool_name}")
            context.results[step.tool_name] = result.business_result
            step.result_ref = step.tool_name
            step.status = StepStatus.COMPLETED
        return context


def run_demo(
    question: str = "分析检材中2026年3月至5月与资金往来相关的聊天和文档，找出重点联系人、关键词趋势和可疑文件。",
    workspace: str | Path = "workspace/demo",
) -> dict[str, Any]:
    workspace_path = Path(workspace)
    receptionist = Receptionist()
    president = President()
    reviewer = Reviewer()
    intent = receptionist.parse(question)
    plan = president.plan(intent)
    executor = TaskExecutor(workspace_path)
    context = executor.execute(plan)
    report = context.results["generate_report"]
    workspace_path.mkdir(parents=True, exist_ok=True)
    report_path = workspace_path / "report.md"
    report_path.write_text(report, encoding="utf-8")
    records = context.results["semantic_filter"]
    findings = context.results["build_findings"]
    review_issues = reviewer.validate_traceability(report, len(records), len(findings))
    return {
        "intent": intent,
        "plan": plan,
        "report": report,
        "findings": findings,
        "statistics": context.results["statistics_summary"],
        "reverse_scope": context.results["reverse_scope"],
        "review_issues": review_issues,
        "audit_path": str(executor.audit.path),
        "report_path": str(report_path),
    }
