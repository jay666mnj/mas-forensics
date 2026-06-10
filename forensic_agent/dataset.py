from __future__ import annotations

from .models import EvidenceItem, ParsedRecord


EVIDENCE_ITEMS: list[EvidenceItem] = [
    EvidenceItem(
        evidence_id="EV-CHAT-001",
        source_path="mock/evidence/chat_export.db",
        source_type="chat",
        hash_sha256="8f2a8c8f6c1c4e78a3d6a4ef9e5b0a1e4f2b6d7c8e9f00112233445566778899",
    ),
    EvidenceItem(
        evidence_id="EV-DOC-001",
        source_path="mock/evidence/documents.zip",
        source_type="document",
        hash_sha256="4d2f82b0f7c2d9e17c47c1a508af75210758b4a9381cde6677889900aabbccdd",
    ),
]


PARSED_RECORDS: list[ParsedRecord] = [
    ParsedRecord(
        record_id="R-CHAT-001",
        evidence_id="EV-CHAT-001",
        record_type="chat",
        timestamp="2026-03-12T09:18:00",
        actors=("Zhang San", "Li Si"),
        content="3月12日先转5万，尾款等材料确认后再走。",
        source_ref="chat_export.db:message/1001",
        metadata={"group": "project-a"},
    ),
    ParsedRecord(
        record_id="R-CHAT-002",
        evidence_id="EV-CHAT-001",
        record_type="chat",
        timestamp="2026-04-03T20:11:00",
        actors=("Li Si", "Wang Wu"),
        content="资金往来不要写太细，文件名就叫报销清单。",
        source_ref="chat_export.db:message/1135",
        metadata={"group": "project-a"},
    ),
    ParsedRecord(
        record_id="R-CHAT-003",
        evidence_id="EV-CHAT-001",
        record_type="chat",
        timestamp="2026-05-09T14:30:00",
        actors=("Zhang San", "Wang Wu"),
        content="5月的转账记录和合同扫描件都放在共享目录。",
        source_ref="chat_export.db:message/1420",
        metadata={"group": "project-b"},
    ),
    ParsedRecord(
        record_id="R-DOC-001",
        evidence_id="EV-DOC-001",
        record_type="document",
        timestamp="2026-04-05T10:00:00",
        actors=("Unknown",),
        content="资金往来明细：3月12日 50000；4月3日 20000；备注：报销清单。",
        source_ref="documents.zip:/finance/报销清单.docx",
        metadata={"filename": "报销清单.docx"},
    ),
    ParsedRecord(
        record_id="R-DOC-002",
        evidence_id="EV-DOC-001",
        record_type="document",
        timestamp="2026-05-10T12:00:00",
        actors=("Unknown",),
        content="合同扫描件与转账记录截图，涉及Zhang San、Wang Wu。",
        source_ref="documents.zip:/contract/合同扫描件.pdf",
        metadata={"filename": "合同扫描件.pdf"},
    ),
]
