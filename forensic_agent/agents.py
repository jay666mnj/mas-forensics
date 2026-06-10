from __future__ import annotations

import re

from .models import DataScope, RiskLevel, TaskPlan, UserIntent, new_step


class Receptionist:
    def parse(self, question: str) -> UserIntent:
        keywords = self._extract_keywords(question)
        data_types = self._extract_data_types(question)
        time_range = self._extract_time_range(question)
        expected_output = ["findings", "statistics", "report"]
        return UserIntent(
            question=question,
            intent_type="lead_analysis",
            keywords=keywords,
            data_types=data_types,
            time_range=time_range,
            expected_output=expected_output,
            risk_level=RiskLevel.ANALYSIS,
        )

    def _extract_keywords(self, question: str) -> list[str]:
        candidates = ["资金", "转账", "往来", "合同", "报销", "文件", "聊天"]
        found = [word for word in candidates if word in question]
        if "资金" in found and "转账" not in found:
            found.append("转账")
        return found or ["资金", "转账"]

    def _extract_data_types(self, question: str) -> list[str]:
        data_types = []
        if "聊天" in question:
            data_types.append("chat")
        if "文档" in question or "文件" in question:
            data_types.append("document")
        return data_types or ["chat", "document"]

    def _extract_time_range(self, question: str) -> tuple[str | None, str | None]:
        year = "2026"
        months = [int(item) for item in re.findall(r"(\d{1,2})月", question)]
        if not months:
            return (None, None)
        start_month = min(months)
        end_month = max(months)
        return (f"{year}-{start_month:02d}-01", f"{year}-{end_month:02d}-31")


class President:
    def plan(self, intent: UserIntent) -> TaskPlan:
        scope_args = {
            "data_types": intent.data_types,
            "keywords": intent.keywords,
            "time_range": intent.time_range,
        }
        steps = [
            new_step("List evidence datasets", "list_datasets", {}),
            new_step("Select data scope", "select_scope", scope_args),
            new_step("Search candidate records", "keyword_search", {"scope": "$select_scope"}),
            new_step("Semantic filter candidate records", "semantic_filter", {"records": "$keyword_search", "topic": "funds"}, RiskLevel.ANALYSIS),
            new_step("Build statistics", "statistics_summary", {"records": "$semantic_filter"}, RiskLevel.ANALYSIS),
            new_step("Build reverse scope suggestions", "reverse_scope", {"records": "$semantic_filter"}, RiskLevel.ANALYSIS),
            new_step("Build traceable findings", "build_findings", {"records": "$semantic_filter", "stats": "$statistics_summary"}),
            new_step(
                "Generate report draft",
                "generate_report",
                {
                    "question": intent.question,
                    "findings": "$build_findings",
                    "records": "$semantic_filter",
                    "stats": "$statistics_summary",
                    "reverse_scope_result": "$reverse_scope",
                },
                RiskLevel.EXPORT,
            ),
        ]
        return TaskPlan.create(intent.question, steps)


class Reviewer:
    def validate_traceability(self, report: str, records_count: int, finding_count: int) -> list[str]:
        issues = []
        if records_count <= 0:
            issues.append("No supporting records were found.")
        if finding_count <= 0:
            issues.append("No traceable findings were generated.")
        if "证据" not in report:
            issues.append("Report lacks evidence references.")
        return issues
