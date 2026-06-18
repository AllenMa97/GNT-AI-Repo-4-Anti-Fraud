<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Status-Experimental-orange?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/DAG-15%20Nodes-blueviolet?style=for-the-badge" alt="DAG">
</p>

<h1 align="center">SOP-DAG</h1>
<p align="center"><strong>Privacy-Preserving Workflow Framework for Sensitive-Domain Case Analysis</strong></p>
<p align="center"><strong>面向敏感领域的隐私保护工作流框架</strong></p>

<br>

<details open>
<summary><b>English</b> / <b>中文</b> (Click to switch)</summary>

---

## Overview

SOP-DAG is a **privacy-preserving, DAG-based workflow framework** designed for structured analysis of sensitive-domain cases such as telecom fraud investigation. The framework decomposes complex case analysis into a directed acyclic graph (DAG) of 15 fine-grained LLM-powered processing nodes, organized into 5 logical phases.

Unlike monolithic LLM pipelines, SOP-DAG enforces **Information Minimality Principle (IMP)** -- each node receives only the minimum necessary context to perform its task, preventing cross-contamination of sensitive data and reducing hallucination risks.

### Key Highlights

- **Privacy-by-Design Architecture**: IMP ensures sensitive information is compartmentalized across nodes
- **15 Specialized LLM Nodes**: Each node handles a specific sub-task with tailored system prompts
- **5-Phase Analysis Pipeline**: Learn, Classify, Extract, Analyze, Report
- **Multi-Modal Support**: Handles victim statements, chat logs, app data, and transaction records
- **Quality Assurance**: Built-in multi-dimensional quality check (S14) before final report generation
- **Structured Outputs**: All nodes output validated JSON for downstream consumption

---

## Architecture

```
                          SOP-DAG WORKFLOW ARCHITECTURE
    ┌──────────────────────────────────────────────────────────────────────┐
    │                         PHASE I: LEARN                               │
    │  ┌─────────────┐                                                     │
    │  │ S1: State-   │  Victim Statement Structuring                      │
    │  │   ment       │  Extract key facts into structured JSON            │
    │  │   Struct.    │                                                    │
    │  └──────┬───────┘                                                    │
    │         │                                                            │
    ├─────────┼────────────────────────────────────────────────────────────┤
    │         ▼              PHASE II: CLASSIFY                            │
    │  ┌─────────────┐     ┌─────────────┐                                │
    │  │ S2: Initial  │────▶│ S9: Precise  │  Two-stage classification:    │
    │  │   Classify   │     │   Classify   │  coarse → fine-grained        │
    │  └─────────────┘     └──────┬───────┘                                │
    │                             │                                        │
    ├─────────────────────────────┼────────────────────────────────────────┤
    │                             ▼     PHASE III: EXTRACT                 │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
    │  │ S4: Chat     │  │ S6: App      │  │ S10: Entity  │                │
    │  │   Parsing    │  │   Extraction │  │   Extraction │                │
    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
    │         │                 │                 │                         │
    ├─────────┼─────────────────┼─────────────────┼─────────────────────────┤
    │         ▼                 ▼                 ▼   PHASE IV: ANALYZE     │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
    │  │ S11: Fund    │  │ S12: Time-  │  │ S13: Scheme  │                │
    │  │   Tracing    │  │   line      │  │   Profile    │                │
    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
    │         │                 │                 │                         │
    ├─────────┼─────────────────┼─────────────────┼─────────────────────────┤
    │         └─────────────────┼─────────────────┘                         │
    │                           ▼            PHASE V: REPORT                │
    │                    ┌─────────────┐                                    │
    │                    │ S14: Quality │  Quality gate                     │
    │                    │   Check      │                                    │
    │                    └──────┬───────┘                                   │
    │                           ▼                                           │
    │                    ┌─────────────┐                                    │
    │                    │ S15: Report  │  Final structured report          │
    │                    │   Generation │                                    │
    │                    └─────────────┘                                    │
    └──────────────────────────────────────────────────────────────────────┘

    Node Dependency Graph (DAG):
    
    S1 ──▶ S2 ──▶ S9 ──┐
                        │
    S4 ─────────────────┤
                        ├──▶ S10 ──▶ S11 ──┐
    S6 ─────────────────┤                   │
                        │                   ├──▶ S14 ──▶ S15
                        ├──▶ S12 ──────────┤
                        │                   │
                        └──▶ S13 ──────────┘
```

---

## Key Concepts

### SOP-DAG (Standard Operating Procedure as Directed Acyclic Graph)

Traditional LLM pipelines process cases monolithically -- feeding all information into a single context window. SOP-DAG instead models the investigative workflow as a **directed acyclic graph**, where each node:

1. Receives a **specific, bounded task**
2. Operates on **minimal necessary input**
3. Produces **structured, validated output**
4. Passes results to **downstream dependent nodes**

This mirrors how human investigators work: gather facts, classify, extract details, analyze, then report.

### IMP (Information Minimality Principle)

> Each node in the DAG shall receive only the minimum information required to perform its designated function, and no more.

IMP is the core privacy guarantee of SOP-DAG. By strictly controlling information flow at the graph topology level, we ensure:

| Without IMP | With IMP |
|---|---|
| All case data in every prompt | Each prompt contains only task-relevant data |
| Risk of cross-contamination | Compartmentalized sensitive information |
| High token usage, high latency | Optimized token usage, lower latency |
| Hard to audit information access | Clear audit trail of information flow |

### MCM (Mode Classification Matrix)

The MCM categorizes fraud cases along two axes: **Complexity** (Simple / Moderate / Complex / Organized Crime) and **Modality** (Statement-only / Statement+Chat / Statement+Chat+App / Full Multi-modal). This matrix determines the DAG execution path -- simpler cases skip certain nodes, while complex cases engage the full 15-node pipeline.

| Mode / Complexity | Simple | Moderate | Complex | Org. Crime |
|---|---|---|---|---|
| **Statement-only** | S1→S2→S15 | S1→S2→S9→S15 | Full Path | Full Path |
| **Stmt+Chat** | S1→S2→S4→S15 | +S9,+S10 | Full Path | Full Path |
| **Stmt+Chat+App** | S1→S2→S4→S6→S15 | +S9,+S10 | Full Path | Full Path |
| **Full Multi-modal** | All 15 nodes | All 15 nodes | All 15 nodes | All 15 nodes |

---

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI-compatible API endpoint (or any LLM provider with compatible SDK)

### Installation

```bash
git clone https://github.com/your-org/sop-dag.git
cd sop-dag
pip install -r requirements.txt
```

### Basic Usage

```python
from sop_dag import WorkflowEngine
from sop_dag.nodes import load_all_nodes

# Initialize the workflow engine
engine = WorkflowEngine(api_key="your-api-key", model="gpt-4")

# Load case data
case_data = {
    "statement": "被害人陈述文本...",
    "chat_logs": "聊天记录文本...",
    "app_info": { ... }
}

# Execute the DAG
result = engine.run(case_data, mode="full")

# Access the final report
print(result["S15"]["report"])
```

### Running Individual Nodes

```python
# Run a specific node
node_s1_result = engine.run_node("S1", input_data={"statement": case_data["statement"]})

# Chain nodes manually
node_s2_result = engine.run_node("S2", input_data={"structured_statement": node_s1_result})
```

---

## Project Structure

```
sop-dag/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── experiment/
│   ├── prompts/                       # System prompts for all 15 nodes
│   │   ├── S1_statement_structure.txt       # Victim statement structuring
│   │   ├── S2_initial_classification.txt    # Quick initial fraud type classification
│   │   ├── S4_chat_parsing.txt              # Chat log parsing
│   │   ├── S6_app_extraction.txt            # App risk indicator extraction
│   │   ├── S9_precise_classification.txt    # Precise fraud type determination
│   │   ├── S10_entity_extraction.txt        # Entity extraction and linking
│   │   ├── S11_fund_tracing.txt             # Fund flow tracing
│   │   ├── S12_timeline.txt                 # Timeline reconstruction
│   │   ├── S13_scheme_profile.txt           # Fraud scheme profiling
│   │   ├── S14_quality_check.txt            # Multi-dimensional quality check
│   │   └── S15_report.txt                   # Final report generation
│   ├── nodes/                        # Node implementation modules
│   │   ├── __init__.py
│   │   ├── base_node.py              # Abstract base node class
│   │   ├── s1_statement.py
│   │   ├── s2_initial_classify.py
│   │   ├── s4_chat_parsing.py
│   │   ├── s6_app_extraction.py
│   │   ├── s9_precise_classify.py
│   │   ├── s10_entity.py
│   │   ├── s11_fund_tracing.py
│   │   ├── s12_timeline.py
│   │   ├── s13_scheme.py
│   │   ├── s14_quality.py
│   │   └── s15_report.py
│   ├── engine.py                     # DAG execution engine
│   └── config.py                     # Configuration
├── tests/                            # Test suite
│   ├── test_nodes.py
│   ├── test_engine.py
│   └── fixtures/                     # Test case fixtures
└── docs/                             # Extended documentation
    ├── architecture.md
    ├── prompts.md
    └── api.md
```

---

## Node Reference

| Node | Name | Phase | Input | Output |
|---|---|---|---|---|
| **S1** | Statement Structure | Learn | Raw victim statement | Structured case JSON |
| **S2** | Initial Classification | Classify | S1 output | Preliminary fraud type |
| **S4** | Chat Parsing | Extract | Raw chat logs | Structured conversation records |
| **S6** | App Extraction | Extract | App-related materials | App risk indicators |
| **S9** | Precise Classification | Classify | S1, S2, S4, S6 outputs | Precise fraud type + evidence |
| **S10** | Entity Extraction | Extract | All prior outputs | Entity graph + relations |
| **S11** | Fund Tracing | Analyze | S1, S10 outputs | Fund flow graph |
| **S12** | Timeline | Analyze | All prior outputs | 4-phase event timeline |
| **S13** | Scheme Profile | Analyze | All prior outputs | Fraud scheme tactics profile |
| **S14** | Quality Check | Report | S1-S13 outputs | Quality audit (8 dimensions) |
| **S15** | Report Generation | Report | All outputs + S14 | Final investigation report |

---

## Fraud Type Taxonomy

The framework classifies cases into 9 primary types with 30+ subtypes:

| Primary Type | Subtypes |
|---|---|
| `investment_fraud` | stock_advisor, forex_gold, virtual_currency, fund_management, carbon_trading |
| `romance_scam` | investment_based, gambling_based, direct_transfer, gift_card |
| `impersonate_customer_service` | ecommerce_refund, logistics_lost, membership_cancel, bank_cs, platform_cs |
| `task_brushing_scam` | traditional_brushing, compound_task, gamified_task |
| `fake_credit_scam` | credit_repair, loan_rate_adjust, account_cancel |
| `loan_scam` | prepaid_fee, frozen_account, credit_enhancement |
| `government_impersonation` | criminal_case, money_laundering, arrest_warrant, asset_freeze |
| `impersonate_acquaintance` | leader, relative, classmate |
| `prize_scam` | lottery_win, program_selection, shopping_luck |

---

## Quality Dimensions (S14)

| # | Dimension | Description |
|---|---|---|
| C01 | Completeness | All required fields present across nodes |
| C02 | Consistency | Cross-node data consistency |
| C03 | Classification Accuracy | Evidence supports classification conclusion |
| C04 | Entity Relation Correctness | Entity relationships verified |
| C05 | Fund Flow Completeness | All known transactions covered |
| C06 | Timeline Coherence | Logical event sequence without gaps |
| C07 | Logical Self-Consistency | Conclusion-evidence chain integrity |
| C08 | Compliance & Privacy | Sensitive data properly masked |

---

## Citation

If you use SOP-DAG in your research, please cite:

```bibtex
@software{sopdag2025,
  title     = {SOP-DAG: A Privacy-Preserving Workflow Framework for Sensitive-Domain Case Analysis},
  year      = {2025},
  note      = {Experimental research framework for structured LLM-based case investigation},
  url       = {https://github.com/your-org/sop-dag}
}
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

> **Disclaimer**: This is an experimental research framework. It is not intended for production deployment without thorough validation and human oversight. The framework's outputs should always be reviewed by qualified human analysts before any operational use.

---

<br>

<details>
<summary><b>中文版本 (Chinese Version)</b></summary>

---

## 概述

SOP-DAG 是一个**面向敏感领域的隐私保护 DAG（有向无环图）工作流框架**，专为电信网络诈骗案件分析等结构化研判场景设计。该框架将复杂的案件分析任务分解为 15 个细粒度、LLM（大语言模型）驱动的处理节点，以有向无环图的形式组织为 5 个逻辑阶段。

与传统的单体式 LLM 流水线不同，SOP-DAG 强制执行**信息最小化原则（IMP）**——每个节点仅接收完成其任务所必需的最少上下文，从而防止敏感数据的交叉污染并降低幻觉风险。

### 核心特点

- **隐私优先架构设计**：IMP 确保敏感信息在节点间隔离
- **15 个专用 LLM 节点**：每个节点通过定制的系统提示词处理特定子任务
- **5 阶段分析流水线**：学习、分类、提取、分析、报告
- **多模态支持**：处理被害人陈述、聊天记录、APP 数据及交易记录
- **内置质量保障**：在最终报告生成前执行多维度质量检查（S14）
- **结构化输出**：所有节点输出经过验证的 JSON，便于下游消费

---

## 架构图

```
                          SOP-DAG 工作流架构
    ┌──────────────────────────────────────────────────────────────────────┐
    │                        第一阶段：学习 (LEARN)                          │
    │  ┌─────────────┐                                                     │
    │  │ S1: 陈述     │  被害人陈述结构化                                    │
    │  │   结构化     │  提取关键事实为结构化 JSON                            │
    │  └──────┬───────┘                                                    │
    │         │                                                            │
    ├─────────┼────────────────────────────────────────────────────────────┤
    │         ▼              第二阶段：分类 (CLASSIFY)                       │
    │  ┌─────────────┐     ┌─────────────┐                                │
    │  │ S2: 初步     │────▶│ S9: 精准     │  两阶段分类：                    │
    │  │   分类       │     │   分类       │  粗粒度 → 细粒度                 │
    │  └─────────────┘     └──────┬───────┘                                │
    │                             │                                        │
    ├─────────────────────────────┼────────────────────────────────────────┤
    │                             ▼     第三阶段：提取 (EXTRACT)              │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
    │  │ S4: 聊天     │  │ S6: APP      │  │ S10: 实体    │                │
    │  │   记录解析   │  │   信息提取   │  │   提取      │                │
    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
    │         │                 │                 │                         │
    ├─────────┼─────────────────┼─────────────────┼─────────────────────────┤
    │         ▼                 ▼                 ▼   第四阶段：分析 (ANALYZE)│
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
    │  │ S11: 资金    │  │ S12: 时间    │  │ S13: 手法    │                │
    │  │   追踪      │  │   线重建    │  │   画像      │                │
    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
    │         │                 │                 │                         │
    ├─────────┼─────────────────┼─────────────────┼─────────────────────────┤
    │         └─────────────────┼─────────────────┘                         │
    │                           ▼            第五阶段：报告 (REPORT)          │
    │                    ┌─────────────┐                                    │
    │                    │ S14: 质量    │  质量审核关卡                        │
    │                    │   检查       │                                    │
    │                    └──────┬───────┘                                   │
    │                           ▼                                           │
    │                    ┌─────────────┐                                    │
    │                    │ S15: 报告    │  最终结构化研判报告                  │
    │                    │   生成       │                                    │
    │                    └─────────────┘                                    │
    └──────────────────────────────────────────────────────────────────────┘

    节点依赖关系图 (DAG):
    
    S1 ──▶ S2 ──▶ S9 ──┐
                        │
    S4 ─────────────────┤
                        ├──▶ S10 ──▶ S11 ──┐
    S6 ─────────────────┤                   │
                        │                   ├──▶ S14 ──▶ S15
                        ├──▶ S12 ──────────┤
                        │                   │
                        └──▶ S13 ──────────┘
```

---

## 核心概念

### SOP-DAG（将标准操作流程建模为有向无环图）

传统的 LLM 流水线以单体方式处理案件——将所有信息一次性喂入模型的上下文窗口中。SOP-DAG 则将研判工作流建模为**有向无环图**，其中每个节点：

1. 接收一个**具体的、有边界的任务**
2. 基于**最少必要输入**进行操作
3. 产生**结构化的、经过验证的输出**
4. 将结果传递给**下游依赖节点**

这模拟了人类调查员的工作方式：收集事实 → 分类 → 提取细节 → 分析 → 报告。

### IMP（信息最小化原则）

> DAG 中的每个节点仅应接收完成其指定功能所需的最少信息，不多不少。

IMP 是 SOP-DAG 的核心隐私保障。通过在图的拓扑层面严格控制信息流，我们确保：

| 不使用 IMP | 使用 IMP |
|---|---|
| 每条提示中包含全部案件数据 | 每条提示仅包含任务相关数据 |
| 存在交叉污染风险 | 敏感信息被分区隔离 |
| 高 Token 消耗，高延迟 | 优化 Token 消耗，降低延迟 |
| 难以审计信息访问路径 | 清晰的信息流审计追溯 |

### MCM（模式分类矩阵）

MCM 沿两个维度对诈骗案件进行分类：**复杂度**（简单 / 中等 / 复杂 / 有组织犯罪）和**模态**（仅陈述 / 陈述+聊天 / 陈述+聊天+APP / 全模态）。该矩阵决定 DAG 的执行路径——简单案件跳过某些节点，复杂案件则启用完整的 15 节点流水线。

| 模态 \ 复杂度 | 简单 | 中等 | 复杂 | 有组织犯罪 |
|---|---|---|---|---|
| **仅陈述** | S1→S2→S15 | S1→S2→S9→S15 | 完整路径 | 完整路径 |
| **陈述+聊天** | S1→S2→S4→S15 | +S9,+S10 | 完整路径 | 完整路径 |
| **陈述+聊天+APP** | S1→S2→S4→S6→S15 | +S9,+S10 | 完整路径 | 完整路径 |
| **全模态** | 全部 15 节点 | 全部 15 节点 | 全部 15 节点 | 全部 15 节点 |

---

## 快速开始

### 环境要求

- Python 3.10+
- 兼容 OpenAI API 的服务端点（或任何兼容 SDK 的 LLM 提供商）

### 安装

```bash
git clone https://github.com/your-org/sop-dag.git
cd sop-dag
pip install -r requirements.txt
```

### 基本用法

```python
from sop_dag import WorkflowEngine
from sop_dag.nodes import load_all_nodes

# 初始化工作流引擎
engine = WorkflowEngine(api_key="your-api-key", model="gpt-4")

# 加载案件数据
case_data = {
    "statement": "被害人陈述文本...",
    "chat_logs": "聊天记录文本...",
    "app_info": { ... }
}

# 执行 DAG
result = engine.run(case_data, mode="full")

# 访问最终报告
print(result["S15"]["report"])
```

### 运行单个节点

```python
# 运行特定节点
node_s1_result = engine.run_node("S1", input_data={"statement": case_data["statement"]})

# 手动链接节点
node_s2_result = engine.run_node("S2", input_data={"structured_statement": node_s1_result})
```

---

## 项目结构

```
sop-dag/
├── README.md                          # 本文件
├── requirements.txt                   # Python 依赖
├── experiment/
│   ├── prompts/                       # 15 个节点的系统提示词
│   │   ├── S1_statement_structure.txt       # 被害人陈述结构化
│   │   ├── S2_initial_classification.txt    # 诈骗类型快速初步分类
│   │   ├── S4_chat_parsing.txt              # 聊天记录解析
│   │   ├── S6_app_extraction.txt            # APP 风险指标提取
│   │   ├── S9_precise_classification.txt    # 精准诈骗类型判定
│   │   ├── S10_entity_extraction.txt        # 实体提取与关系链接
│   │   ├── S11_fund_tracing.txt             # 资金流向追踪
│   │   ├── S12_timeline.txt                 # 时间线重建
│   │   ├── S13_scheme_profile.txt           # 诈骗手法画像
│   │   ├── S14_quality_check.txt            # 多维度质量检查
│   │   └── S15_report.txt                   # 最终研判报告生成
│   ├── nodes/                        # 节点实现模块
│   │   ├── __init__.py
│   │   ├── base_node.py              # 抽象基类节点
│   │   ├── s1_statement.py
│   │   ├── s2_initial_classify.py
│   │   ├── s4_chat_parsing.py
│   │   ├── s6_app_extraction.py
│   │   ├── s9_precise_classify.py
│   │   ├── s10_entity.py
│   │   ├── s11_fund_tracing.py
│   │   ├── s12_timeline.py
│   │   ├── s13_scheme.py
│   │   ├── s14_quality.py
│   │   └── s15_report.py
│   ├── engine.py                     # DAG 执行引擎
│   └── config.py                     # 配置
├── tests/                            # 测试套件
│   ├── test_nodes.py
│   ├── test_engine.py
│   └── fixtures/                     # 测试用例数据
└── docs/                             # 扩展文档
    ├── architecture.md
    ├── prompts.md
    └── api.md
```

---

## 节点参考

| 节点 | 名称 | 阶段 | 输入 | 输出 |
|---|---|---|---|---|
| **S1** | 陈述结构化 | 学习 | 原始被害人陈述 | 结构化案件 JSON |
| **S2** | 初步分类 | 分类 | S1 输出 | 初步诈骗类型 |
| **S4** | 聊天记录解析 | 提取 | 原始聊天记录 | 结构化对话记录 |
| **S6** | APP 信息提取 | 提取 | APP 相关材料 | APP 风险指标 |
| **S9** | 精准分类 | 分类 | S1, S2, S4, S6 输出 | 精准诈骗类型+证据摘要 |
| **S10** | 实体提取 | 提取 | 所有前置输出 | 实体图谱+关系 |
| **S11** | 资金追踪 | 分析 | S1, S10 输出 | 资金流向图 |
| **S12** | 时间线重建 | 分析 | 所有前置输出 | 四阶段事件时间线 |
| **S13** | 手法画像 | 分析 | 所有前置输出 | 诈骗手法策略画像 |
| **S14** | 质量检查 | 报告 | S1-S13 输出 | 8 维度质量审计 |
| **S15** | 报告生成 | 报告 | 全部输出+S14 | 最终研判报告 |

---

## 诈骗类型分类体系

本框架将案件分为 9 大类，共 30+ 子类型：

| 主类型 | 子类型 |
|---|---|
| `investment_fraud`（投资理财） | 荐股、外汇黄金、虚拟币、虚假理财、碳交易 |
| `romance_scam`（杀猪盘/婚恋交友） | 投资诱导型、博彩诱导型、直接索要、礼品卡 |
| `impersonate_customer_service`（冒充客服） | 电商退款、快递理赔、会员注销、冒充银行客服、冒充平台客服 |
| `task_brushing_scam`（刷单返利） | 传统刷单、复合任务、游戏化任务 |
| `fake_credit_scam`（虚假征信） | 征信修复、利率调整、账户注销 |
| `loan_scam`（贷款诈骗） | 预付费用、账户冻结、信用提升 |
| `government_impersonation`（冒充公检法） | 刑事案件、涉嫌洗钱、通缉令、资产冻结 |
| `impersonate_acquaintance`（冒充熟人） | 冒充领导、冒充亲友、冒充同学 |
| `prize_scam`（中奖诈骗） | 彩票中奖、节目抽奖、购物中奖 |

---

## 质量检查维度（S14）

| 编号 | 维度 | 说明 |
|---|---|---|
| C01 | 信息完整性 | 各节点所有必填字段均已填写 |
| C02 | 数据一致性 | 跨节点数据无矛盾 |
| C03 | 分类准确性 | 证据充分支持分类结论 |
| C04 | 实体关系正确性 | 实体关系有据可查、方向正确 |
| C05 | 资金流完整性 | 覆盖所有已知交易记录 |
| C06 | 时间线连贯性 | 事件序列逻辑连贯、无断裂 |
| C07 | 逻辑自洽性 | 结论与证据之间推理链条完整 |
| C08 | 合规性与隐私保护 | 敏感信息已脱敏、无合规风险 |

---

## 引用

如果您在研究中使用了 SOP-DAG，请引用：

```bibtex
@software{sopdag2025,
  title     = {SOP-DAG: 面向敏感领域的隐私保护案件分析工作流框架},
  year      = {2025},
  note      = {基于 LLM 的结构化案件研判实验框架},
  url       = {https://github.com/your-org/sop-dag}
}
```

---

## 许可证

MIT License。详见 [LICENSE](LICENSE) 文件。

> **免责声明**：此为实验性研究框架。未经充分验证和人工审核，请勿用于生产部署。框架的输出结果在任何操作使用前，均应由具备资质的人工分析师进行复核。

</details>

---

</details>
