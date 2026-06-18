# SOP-DAG: Privacy-Preserving Task Decomposition for LLM-Assisted Telecom Fraud Investigation

> **中文版请向下滚动** | [中文版本](#中文版本)
>
> **Paper**: Under submission to ACL / EMNLP / NAACL
> **Authors**: [Your Name], Guangzhou Govnet Co., Ltd.
> **Code & Data**: `https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud`

---

## 📌 News

- **2025-06**: v7.0 released —经过5轮15人评审迭代的重大更新版
- Added formal Lemma 1 (DAG Completeness) and Hypothesis 1 (Privacy-Quality-Cost Trade-off)
- Added reproducible 3-layer Synthetic Data methodology
- Added cross-domain validation on FewIE (ACL 2023) and CoNLL-2003

---

## Overview

Deploying LLMs for telecom fraud investigation faces a fundamental **two-paths-blocked dilemma**:

| Approach | Privacy | Quality |
|----------|---------|---------|
| **Send all data to LLM API** | ❌ Illegal (PIPL, Data Security Law) | ✅ Highest |
| **Send fully anonymized data** | ✅ Compliant | ❌ Low (removes both noise AND signal) |
| **SOP-DAG (ours)** | ✅ Task-adaptive selective anonymization | ✅ Near-oracle (Δ<5%) |

**SOP-DAG** solves this by modeling the police standard operating procedure (SOP) as a directed acyclic graph (DAG) of atomic tasks, where each node only accesses the **minimally sufficient information set** required for its specific subtask.

### Key Insights

1. **Information Minimization Principle (IMP)**: Each node receives only the fields it actually needs — not all fields, not zero fields.
2. **Task-adaptive anonymization**: The same PII field (e.g., a phone number) is handled differently for different tasks — masked for fraud-type classification, preserved for fund-tracing.
3. **DAG completeness guarantee**: Under standard conditions, task decomposition is provably lossless (Lemma 1).

---

## The SOP-DAG Framework

```
[Phase I: Registration]  S1(Statement) → S2(Initial Classify) → S3(Urgency[RULE])
         ↓                    ↓                      ↓
[Phase II: Evidence]     S4(Chat Parse[LLM])    S5(Tx Parse[RULE])  S6(App[LLM])  S7(Call[RULE])  S8(PII Scan[RULE])
         ↓                    ↓                      ↓                      ↓
[Phase III: Analysis]     S9(Precise Classify[LLM])  S10(Entity[HYBRID])  S11(Fund Trace[LLM])  S12(Timeline[LLM])  S13(Scheme[LLM])
         ↓                    ↓                      ↓                      ↓
[Phase IV: QA]           S14(Quality Check[HYBRID])
         ↓
[Phase V: Report]        S15(Structured Report[LLM])
```

### Node Modes

| Mode | Description | Privacy Risk | Example Nodes |
|------|-------------|-------------|---------------|
| **RULE** | Local regex/rule engine, no API call | Near zero | S3(urgency), S5(tx parse), S7(call), S8(PII scan) |
| **LLM** | API call with filtered input | Medium | S1, S4, S6, S9, S11, S12, S13, S15 |
| **HYBRID** | API call + local verification | Medium | S10(entity extraction), S14(QA) |

---

## Synthetic Data Methodology

Real telecom fraud case data is protected under PIPL. We developed a **reproducible 3-layer pipeline**:

### Layer 1: Fraud Type Taxonomy
Based on the publicly available 公安部《电信网络诈骗及其关联违法犯罪分类细化》 — 9 official categories, not arbitrary:

| # | Type | Key Pattern |
|---|------|-------------|
| 1 | 刷单返利 | Small rewards →垫付任务→ account freeze |
| 2 | 虚假投资 | Group recruitment → fake platform → no withdrawal |
| 3 | 杀猪盘 | Social app → emotional bond → crypto |
| 4 | 冒充客服 | Accurate order info → phishing |
| 5 | 虚假贷款 | Ad → approval → fees → no loan |
| 6 | 冒充公检法 | Fear → forged warrant → "safe account" |
| 7 | 冒充熟人 | Voice mimic → urgent cash request |
| 8 | 中奖诈骗 | Prize → taxes/fees |
| 9 | 虚拟货币杀猪 | Dating → fake exchange → USDT drain |

### Layer 2: Entity Schema
Each fraud type has structured schemas for `Suspect`, `Account`, and `App` entities, with every field annotated by **legal PII sensitivity level** (HIGH/MEDIUM/LOW).

### Layer 3: Hybrid Generation
- **Structured data** (transactions, call records): rule-based generation following schema patterns
- **Victim statements**: LLM-augmented with few-shot prompts and role-play instructions
- **Ground Truth**: Derived from schema (not human annotation) — any researcher can reproduce identical GT

**Reproducibility**: The full schema definitions and generation prompts are in `experiment/data_synthetic.py`. To adapt to a new domain (financial fraud, healthcare), replace Layers 1-2. Layer 3 code requires no modification.

---

## Experiment Design

### Claim-Driven Evaluation (5 Claims → 5 Experiments)

| Exp | Claim | Method | Key Finding |
|-----|-------|--------|------------|
| **Exp 1** | SOP-DAG outperforms industry baseline | vs. Industry (uniform mask), Rule-only, TUB | Δ<6% vs TUB, 62% info reduction |
| **Exp 2** | DAG decomposition is lossless | Ablation on Phase inclusion | Removing any phase reduces quality (p<0.01) |
| **Exp 3** | IMP: minimal info is optimal | IMPCurve (controlled ablation: 5 info levels + control) | Inverted-U curve confirms minimal sufficiency |
| **Exp 4** | Privacy-Accuracy trade-off is real | Pareto Frontier analysis | SOP-DAG on Pareto frontier; Industry inside |
| **Exp 5** | Cross-domain generalizability | Leave-One-Type-Out + FewIE + CoNLL | ≥0.80 F1 on all 9 types; FewIE 0.84 F1 |

**Statistical rigor**: All experiments report 95% CI and paired t-test p-values. Code uses fixed random seed (42).

### Public Benchmarks

| Dataset | Task | SOP-DAG Score | Reported Baseline |
|--------|------|--------------|-----------------|
| FewIE (ACL 2023) | Entity extraction | 0.84 F1 | GPT-3.5: 0.86, RoBERTa-CRF: 0.79 |
| CoNLL-2003 | NER | 0.91 F1 | BERT-base NER: 0.92 |

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud
cd GNT-AI-Repo-4-Anti-Fraud

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your DeepSeek API key:
# DEEPSEEK_API_KEY=sk-your-key-here

# Run experiments on all 10 synthetic cases
python -m experiment.run_experiments --all --method ALL

# Run a specific case with SOP-DAG only
python -m experiment.run_experiments --case 0 --method D
```

### Python API

```python
from experiment.sop_dag import SOPDAGExecutor, build_telecom_fraud_sop_dag
from experiment.config import get_api_config

# Build the DAG
dag = build_telecom_fraud_sop_dag()

# Create executor
executor = SOPDAGExecutor(api_config=get_api_config())
executor.load_dag(dag)

# Execute on a case
case_data = {
    "victim_statement": "我在微信群里认识了一个自称分析师的人...",
    "chat_records": [...],
    "transactions": [...],
    "call_records": [...],
    "app_info": {...}
}

results = executor.execute(case_data, model="deepseek-v4-flash")

# Access final report
print(results["S15"])
```

---

## Project Structure

```
GNT-AI-Repo-4-Anti-Fraud/
├── README.md                      # This file
├── requirements.txt
├── .env.example
├── experiment/
│   ├── sop_dag.py               # Core SOP-DAG framework
│   ├── data_synthetic.py        # 3-layer synthetic data generation
│   ├── run_experiments.py       # Experiment runner (Exp 1-5)
│   ├── baselines.py              # Baseline methods (Industry, Rule-only)
│   ├── llm_client.py            # DeepSeek API client
│   ├── rule_engine.py           # Local rule execution (RULE nodes)
│   ├── metrics.py               # Evaluation metrics
│   ├── config.py                # Configuration
│   └── prompts/                 # System prompts for LLM nodes
│       ├── S1_statement_structure.txt
│       ├── S2_initial_classification.txt
│       ├── S4_chat_parsing.txt
│       ├── S6_app_extraction.txt
│       ├── S9_precise_classification.txt
│       ├── S10_entity_extraction.txt
│       ├── S11_fund_tracing.txt
│       ├── S12_timeline.txt
│       ├── S13_scheme_profile.txt
│       ├── S14_quality_check.txt
│       └── S15_report.txt
└── data/
    └── results/                  # Experiment results (auto-generated)
```

---

## Theoretical Contributions

### Hypothesis 1 (Privacy-Quality-Cost Trade-off)
> For any analytical task requiring domain-specific information and any sensitive information set PII, there does not exist an information set M such that: perfect privacy (I(M,PII)=0), perfect quality (Q=Q*), and acceptable cost (C≤C_baseline) hold simultaneously.

**Interpretation**: The three goals are mutually constrained. SOP-DAG does not achieve the impossible — it makes the trade-off explicit and navigable.

### Lemma 1 (DAG Completeness)
> For any SOP-DAG satisfying Definition 1 (Information Complete DAG), end-to-end execution O_DAG contains all key structured information (fraud_type, entities, timeline_phases) without information loss.

**Proof**: Structural induction over DAG depth. See Appendix A of the paper draft.

---

## Citation

```bibtex
@article{sopdag2025,
  title     = {SOP-DAG: Privacy-Preserving Task Decomposition for LLM-Assisted Telecom Fraud Investigation},
  author    = {Ma, Allen and Shi, {Authors}},
  year      = {2025},
  journal   = {arXiv preprint},
  url       = {https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud}
}
```

---

## Ethical Considerations

- **D1 — Dual-Use**: SOP-DAG is an auxiliary tool; all decisions rest with certified officers. Rate limiting and audit logging enforced at deployment.
- **D2 — Synthetic Data**: All cases use fictitious entities. No real person data.
- **D3 — Responsibility**: Outputs require human review. No automated conviction.
- **D4 — Transparency**: Every node produces traceable JSON. Supports post-hoc auditing.

> **Disclaimer**: Experimental research framework. Do not use in production without thorough validation and human oversight.

---

<br>

---

# SOP-DAG：面向敏感领域的隐私感知任务分解框架

**论文状态**：投稿 ACL / EMNLP / NAACL
**合作单位**：广州市高奈特网络科技有限公司 (govnet.com.cn)
**代码与数据**：`https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud`

---

## 概述

将LLM应用于电信网络诈骗案件分析，面临一个**"两难困境"**：

| 方案 | 隐私合规 | 分析质量 |
|------|---------|---------|
| **全量数据发给LLM API** | ❌ 违法（《个人信息保护法》《数据安全法》） | ✅ 最高 |
| **全量数据脱敏后发送** | ✅ 合规 | ❌ 低下（去除了噪音，也去除了线索） |
| **SOP-DAG（本文）** | ✅ 任务自适应选择性脱敏 | ✅ 接近理论上限（Δ<5%） |

**SOP-DAG**通过将民警标准作业流程（SOP）建模为有向无环图（DAG）来解决此问题，
其中每个节点仅访问完成其原子任务所需的**最小必要信息集**。

### 核心创新

1. **信息最小化原则（IMP）**：每个节点只接收其真正需要的字段——不是全部，也不是零。
2. **任务自适应脱敏**：同一PII字段（如手机号）在不同任务中有不同的处理方式——分类时脱敏，追踪时保留。
3. **DAG无损性保证**：在标准条件下，任务分解是无损的（Lemma 1）。

---

## SOP-DAG框架

```
[第一阶段：受案登记]  S1(陈述结构化) → S2(初步分类) → S3(紧急性[RULE])
         ↓                    ↓                      ↓
[第二阶段：证据接入]  S4(聊天解析[LLM])  S5(流水解析[RULE])  S6(APP[LLM])  S7(通话[RULE])  S8(PII扫描[RULE])
         ↓                    ↓                      ↓                      ↓
[第三阶段：核心分析]  S9(精准分类[LLM])  S10(实体提取[HYBRID])  S11(资金追踪[LLM])  S12(时间线[LLM])  S13(手法画像[LLM])
         ↓                    ↓                      ↓                      ↓
[第四阶段：质检]      S14(质量检查[HYBRID])
         ↓
[第五阶段：报告]      S15(结构化研判报告[LLM])
```

### 节点模式

| 模式 | 说明 | 隐私风险 | 示例节点 |
|------|------|---------|---------|
| **RULE** | 本地规则引擎，无需API调用 | 几乎为零 | S3(紧急性)、S5(流水解析)、S7(通话)、S8(PII扫描) |
| **LLM** | API调用，输入经过过滤 | 中等 | S1、S4、S6、S9、S11、S12、S13、S15 |
| **HYBRID** | API调用+本地验证 | 中等 | S10(实体提取)、S14(质检) |

---

## Synthetic Data方法论

真实案件数据受《个人信息保护法》保护。我们开发了**可复现的三层生成管道**：

### 第一层：诈骗类型分类体系

基于公开的公安部《电信网络诈骗及其关联违法犯罪分类细化》9大类型标准，非拍脑袋制定：

| # | 类型 | 核心模式 |
|---|------|---------|
| 1 | 刷单返利 | 小额返利→垫付任务→账户冻结 |
| 2 | 虚假投资 | 群聊引流→虚假平台→无法提现 |
| 3 | 杀猪盘 | 社交软件→建立感情→诱导转账/博彩 |
| 4 | 冒充客服 | 准确报出订单→钓鱼链接 |
| 5 | 虚假贷款 | 广告→审核通过→层层收费 |
| 6 | 冒充公检法 | 制造恐慌→伪造文书→"安全账户" |
| 7 | 冒充熟人 | 电话变声→紧急求助→线下取现 |
| 8 | 中奖诈骗 | 虚假中奖→税金/公证费 |
| 9 | 虚拟货币杀猪 | 交友平台→虚假交易所→USDT清零 |

### 第二层：实体Schema

每个诈骗类型定义了`嫌疑人`、`账户`、`APP`的Schema模板，
每个字段均标注**法律PII敏感级别**（HIGH/MEDIUM/LOW）。

### 第三层：混合生成

- **结构化数据**（交易流水、通话记录）：基于Schema规则生成
- **被害人陈述**：LLM增强，Few-shot prompt + Role-play指令
- **Ground Truth**：从Schema直接推导，非人工标注——任何研究者可独立复现一致答案

**可迁移性**：`experiment/data_synthetic.py`中提供完整的Schema定义和生成Prompt。
迁移到新领域（金融诈骗、医疗欺诈）只需替换第一、二层代码，第三层代码零修改。

---

## 实验设计

### Claim驱动评估（5条Claim → 5个实验）

| 实验 | Claim | 方法 | 核心发现 |
|-----|-------|------|---------|
| **Exp 1** | SOP-DAG优于业界做法 | vs.业界(统一脱敏)、纯规则、TUB | Δ<6% vs TUB，信息暴露减少62% |
| **Exp 2** | DAG分解无损 | 各Phase消融 | 跳过任一Phase均显著降低质量(p<0.01) |
| **Exp 3** | IMP：最小集最优 | IMPCurve（控制消融：5档信息量+对照组） | 倒U型曲线证实最小充分性 |
| **Exp 4** | 隐私-质量权衡真实存在 | Pareto前沿分析 | SOP-DAG在帕累托边界；业界在边界内侧 |
| **Exp 5** | 跨领域泛化能力 | 留一法+FewIE+CoNLL | 9类型全部≥0.80 F1；FewIE达0.84 F1 |

**统计严谨性**：所有实验报告95%置信区间和配对t检验p值。代码固定随机种子(42)。

### 公开基准验证

| 数据集 | 任务 | SOP-DAG得分 | 已报道基线 |
|--------|------|-----------|-----------|
| FewIE (ACL 2023) | 实体抽取 | 0.84 F1 | GPT-3.5: 0.86, RoBERTa-CRF: 0.79 |
| CoNLL-2003 | 命名实体识别 | 0.91 F1 | BERT-base NER: 0.92 |

---

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud
cd GNT-AI-Repo-4-Anti-Fraud

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp .env.example .env
# 编辑.env，填入DeepSeek API密钥

# 运行全部10个合成案件的实验
python -m experiment.run_experiments --all --method ALL

# 对特定案件运行SOP-DAG
python -m experiment.run_experiments --case 0 --method D
```

### Python API

```python
from experiment.sop_dag import SOPDAGExecutor, build_telecom_fraud_sop_dag
from experiment.config import get_api_config

# 构建DAG
dag = build_telecom_fraud_sop_dag()

# 创建执行器
executor = SOPDAGExecutor(api_config=get_api_config())
executor.load_dag(dag)

# 执行案件分析
case_data = {
    "victim_statement": "我在微信群里认识了一个自称分析师的人...",
    "chat_records": [...],
    "transactions": [...],
    "call_records": [...],
    "app_info": {...}
}

results = executor.execute(case_data, model="deepseek-v4-flash")

# 访问最终报告
print(results["S15"])
```

---

## 项目结构

```
GNT-AI-Repo-4-Anti-Fraud/
├── README.md                      # 本文件（中英文双语）
├── requirements.txt
├── .env.example                   # API密钥配置模板
├── experiment/
│   ├── sop_dag.py               # 核心SOP-DAG框架
│   ├── data_synthetic.py        # 三层合成数据生成方法
│   ├── run_experiments.py       # 实验运行器（Exp 1-5）
│   ├── baselines.py              # 基线方法（业界、纯规则）
│   ├── llm_client.py            # DeepSeek API客户端
│   ├── rule_engine.py            # 本地规则引擎（RULE节点）
│   ├── metrics.py               # 评估指标
│   ├── config.py                 # 配置管理
│   └── prompts/                  # 各LLM节点的系统提示词
│       ├── S1_statement_structure.txt
│       ├── S2_initial_classification.txt
│       ├── S4_chat_parsing.txt
│       ├── S6_app_extraction.txt
│       ├── S9_precise_classification.txt
│       ├── S10_entity_extraction.txt
│       ├── S11_fund_tracing.txt
│       ├── S12_timeline.txt
│       ├── S13_scheme_profile.txt
│       ├── S14_quality_check.txt
│       └── S15_report.txt
└── data/
    └── results/                  # 实验结果（自动生成）
```

---

## 理论贡献

### Hypothesis 1（隐私-质量-成本不可能三角）
> 对于任意需要领域特定信息的分析任务和任意敏感信息集合PII，
> 不存在同时满足以下三式的M：(1) I(M,PII)=0（完美隐私）；(2) Q(M,T)=Q*(T)（完美质量）；(3) C(M)≤C_baseline(T)（成本可控）。

**含义**：三个目标相互制约。SOP-DAG不追求同时最优，而是让权衡过程显式化、可配置化。

### Lemma 1（DAG推理完备性）
> 对于任意满足Definition 1（信息完备DAG）的SOP-DAG，端到端执行结果O_DAG包含所有关键结构化信息（fraud_type、entities、timeline_phases），且不存在信息损失。

**证明**：对DAG深度进行结构归纳。见论文草稿附录A。

---

## 引用

```bibtex
@article{sopdag2025,
  title     = {SOP-DAG: 面向敏感领域的隐私感知任务分解框架},
  author    = {马 Allen, 石 {Authors}},
  year      = {2025},
  journal   = {arXiv preprint},
  url       = {https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud}
}
```

---

## 伦理声明

- **D1 — 双重使用风险**：SOP-DAG为辅助工具，所有决策由持证民警做出。生产部署需执行速率限制和审计日志。
- **D2 — Synthetic Data边界**：所有案件使用虚构实体，无真实人员数据。
- **D3 — 责任归属**：输出结果需人工复核，不支持自动化定罪。
- **D4 — 透明度**：每个节点产生可追溯的JSON输出，支持事后审计。

> **免责声明**：此为实验性研究框架。未经充分验证和人工审核，请勿用于生产部署。

---

<br>

## License

MIT License.

