# 基于多智能体协同的取证分析 AI 工具研发

当前仓库已启动 v0.1 原型，目标是先验证“自然语言输入 -> 任务规划 -> Mock工具调用 -> 证据溯源 -> 报告草稿”的最小闭环。

## 运行演示

```bash
python -m forensic_agent
```

可传入自定义问题：

```bash
python -m forensic_agent "分析检材中2026年3月至5月与资金往来相关的聊天和文档，找出重点联系人、关键词趋势和可疑文件。"
```

## 运行测试

```bash
python -m unittest discover -s tests -v
```

## 当前范围

- `forensic_agent/agents.py`：接待智能体、主控规划智能体、复核器。
- `forensic_agent/tools.py`：Mock工具注册中心、检索、语义过滤、统计、线索和报告工具。
- `forensic_agent/models.py`：证据、记录、任务计划、工具日志、线索等核心数据对象。
- `forensic_agent/audit.py`：工具调用审计日志。
- `forensic_agent/orchestrator.py`：端到端执行闭环。

当前版本不调用真实大模型和真实取证软件，后续应按 `技术路线.md` 接入 MCP/取证软件接口、真实数据解析、混合检索和安全沙箱。

## v0.1 输出

演示运行后会输出：

- 带证据ID、记录ID和来源引用的报告草稿。
- 重点联系人、月度命中、数据类型和可疑文件统计。
- 基于高置信记录生成的反向范围建议。
- `workspace/demo/audit.jsonl` 工具调用审计日志。
- `workspace/demo/report.md` 报告草稿文件。
