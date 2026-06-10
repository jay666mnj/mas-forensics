from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable

from .dataset import EVIDENCE_ITEMS, PARSED_RECORDS
from .models import DataScope, Finding, ParsedRecord, ToolResult


ToolFunc = Callable[..., ToolResult]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    permission_level: str
    side_effect: bool
    handler: ToolFunc


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise KeyError(f"Tool not registered: {name}")
        return self._tools[name]

    def call(self, name: str, **kwargs: Any) -> ToolResult:
        return self.get(name).handler(**kwargs)

    def list_specs(self) -> list[ToolSpec]:
        return list(self._tools.values())


def _in_time_range(record: ParsedRecord, time_range: tuple[str | None, str | None]) -> bool:
    start, end = time_range
    ts = record.timestamp[:10]
    if start and ts < start:
        return False
    if end and ts > end:
        return False
    return True


def list_datasets() -> ToolResult:
    result = [
        {
            "evidence_id": item.evidence_id,
            "source_type": item.source_type,
            "source_path": item.source_path,
            "hash_sha256": item.hash_sha256,
        }
        for item in EVIDENCE_ITEMS
    ]
    return ToolResult("list_datasets", result, [item.evidence_id for item in EVIDENCE_ITEMS], {"count": len(result)})


def select_scope(data_types: list[str], keywords: list[str], time_range: tuple[str | None, str | None]) -> ToolResult:
    selected_types = data_types or ["chat", "document"]
    scope = DataScope(
        scope_id="scope-demo-001",
        data_types=selected_types,
        keywords=keywords,
        time_range=time_range,
        source="system_auto",
    )
    return ToolResult("select_scope", scope, [], {"source": scope.source})


def keyword_search(scope: DataScope) -> ToolResult:
    keywords = [keyword.lower() for keyword in scope.keywords]
    records = []
    for record in PARSED_RECORDS:
        if record.record_type not in scope.data_types:
            continue
        if not _in_time_range(record, scope.time_range):
            continue
        text = record.content.lower()
        if not keywords or any(keyword.lower() in text for keyword in keywords):
            records.append(record)
    return ToolResult(
        "keyword_search",
        records,
        sorted({record.evidence_id for record in records}),
        {"record_count": len(records), "keywords": scope.keywords},
    )


def semantic_filter(records: list[ParsedRecord], topic: str = "funds") -> ToolResult:
    topic_keywords = {
        "funds": ["资金", "转账", "尾款", "报销", "明细", "合同", "截图"],
        "default": [],
    }
    keywords = topic_keywords.get(topic, topic_keywords["default"])
    filtered = [record for record in records if any(keyword in record.content for keyword in keywords)]
    return ToolResult(
        "semantic_filter",
        filtered,
        sorted({record.evidence_id for record in filtered}),
        {"topic": topic, "record_count": len(filtered)},
    )


def statistics_summary(records: list[ParsedRecord]) -> ToolResult:
    actor_counter: Counter[str] = Counter()
    month_counter: Counter[str] = Counter()
    type_counter: Counter[str] = Counter()
    suspicious_files: list[str] = []
    for record in records:
        actor_counter.update(actor for actor in record.actors if actor != "Unknown")
        month_counter.update([record.timestamp[:7]])
        type_counter.update([record.record_type])
        filename = record.metadata.get("filename")
        if filename and any(word in record.content for word in ["资金", "转账", "合同", "报销"]):
            suspicious_files.append(filename)
    summary = {
        "top_actors": actor_counter.most_common(5),
        "monthly_hits": sorted(month_counter.items()),
        "record_types": sorted(type_counter.items()),
        "suspicious_files": sorted(set(suspicious_files)),
    }
    return ToolResult(
        "statistics_summary",
        summary,
        sorted({record.evidence_id for record in records}),
        {"record_count": len(records)},
    )


def reverse_scope(records: list[ParsedRecord]) -> ToolResult:
    actors = sorted({actor for record in records for actor in record.actors if actor != "Unknown"})
    months = sorted({record.timestamp[:7] for record in records})
    evidence_ids = sorted({record.evidence_id for record in records})
    groups = sorted({record.metadata.get("group") for record in records if record.metadata.get("group")})
    filenames = sorted({record.metadata.get("filename") for record in records if record.metadata.get("filename")})
    suggestion = {
        "actors": actors,
        "months": months,
        "evidence_ids": evidence_ids,
        "groups": groups,
        "filenames": filenames,
        "source": "reverse_scope_from_high_confidence_records",
    }
    return ToolResult(
        "reverse_scope",
        suggestion,
        evidence_ids,
        {"record_count": len(records), "scope_source": suggestion["source"]},
    )


def build_findings(records: list[ParsedRecord], stats: dict[str, Any], call_ids: list[str]) -> ToolResult:
    findings: list[Finding] = []
    if records:
        findings.append(
            Finding(
                finding_id="F-001",
                claim=f"发现{len(records)}条与资金往来相关的聊天或文档记录。",
                confidence=0.86,
                supporting_record_ids=[record.record_id for record in records],
                supporting_tool_call_ids=call_ids,
                finding_type="semantic_lead",
            )
        )
    if stats.get("suspicious_files"):
        findings.append(
            Finding(
                finding_id="F-002",
                claim="发现疑似关联文件：" + "、".join(stats["suspicious_files"]),
                confidence=0.78,
                supporting_record_ids=[record.record_id for record in records if record.record_type == "document"],
                supporting_tool_call_ids=call_ids,
                finding_type="file_lead",
            )
        )
    return ToolResult("build_findings", findings, sorted({record.evidence_id for record in records}), {"count": len(findings)})


def generate_report(
    question: str,
    findings: list[Finding],
    records: list[ParsedRecord],
    stats: dict[str, Any],
    reverse_scope_result: dict[str, Any],
) -> ToolResult:
    record_map = {record.record_id: record for record in records}
    lines = [
        "# 取证分析报告草稿",
        "",
        f"## 用户问题",
        question,
        "",
        "## 统计概览",
        f"- 重点联系人：{stats.get('top_actors', [])}",
        f"- 月度命中：{stats.get('monthly_hits', [])}",
        f"- 数据类型：{stats.get('record_types', [])}",
        f"- 可疑文件：{stats.get('suspicious_files', [])}",
        "",
        "## 反向范围建议",
        f"- 关联人员：{reverse_scope_result.get('actors', [])}",
        f"- 关联月份：{reverse_scope_result.get('months', [])}",
        f"- 关联检材：{reverse_scope_result.get('evidence_ids', [])}",
        f"- 关联群组：{reverse_scope_result.get('groups', [])}",
        f"- 关联文件：{reverse_scope_result.get('filenames', [])}",
        "",
        "## 线索结论",
    ]
    for finding in findings:
        lines.append(f"- {finding.finding_id}：{finding.claim}（置信度 {finding.confidence:.2f}）")
        for record_id in finding.supporting_record_ids:
            record = record_map.get(record_id)
            if record:
                lines.append(f"  - 证据 {record.record_id} / {record.evidence_id} / {record.source_ref}")
    report = "\n".join(lines)
    return ToolResult("generate_report", report, sorted({record.evidence_id for record in records}), {"finding_count": len(findings)})


def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ToolSpec("list_datasets", "List mock evidence datasets.", "read", False, lambda: list_datasets()))
    registry.register(ToolSpec("select_scope", "Build a traceable data scope.", "read", False, select_scope))
    registry.register(ToolSpec("keyword_search", "Search records by keywords and scope.", "read", False, keyword_search))
    registry.register(ToolSpec("semantic_filter", "Filter candidate records by semantic topic.", "analysis", False, semantic_filter))
    registry.register(ToolSpec("statistics_summary", "Build basic statistics for records.", "analysis", False, statistics_summary))
    registry.register(ToolSpec("reverse_scope", "Build reverse scope suggestions from high-confidence records.", "analysis", False, reverse_scope))
    registry.register(ToolSpec("build_findings", "Build traceable findings.", "analysis", False, build_findings))
    registry.register(ToolSpec("generate_report", "Generate markdown report draft.", "export", True, generate_report))
    return registry
