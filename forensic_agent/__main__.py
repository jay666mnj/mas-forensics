from __future__ import annotations

import argparse

from .orchestrator import run_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the forensic agent mock demo.")
    parser.add_argument("question", nargs="?", default="分析检材中2026年3月至5月与资金往来相关的聊天和文档，找出重点联系人、关键词趋势和可疑文件。")
    parser.add_argument("--workspace", default="workspace/demo")
    args = parser.parse_args()
    result = run_demo(args.question, args.workspace)
    print(result["report"])
    if result["review_issues"]:
        print("\nReview issues:")
        for issue in result["review_issues"]:
            print(f"- {issue}")
    print(f"\nAudit log: {result['audit_path']}")
    print(f"Report file: {result['report_path']}")


if __name__ == "__main__":
    main()
