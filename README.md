# SOP-DAG: Privacy-Preserving Task Decomposition for LLM-Assisted Telecom Fraud Investigation

> **English** | [中文](#中文版本) (Click to switch)
>
> **Status**: Under submission to ACL / EMNLP / NAACL
> **Code & Data**: `https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud`

---

## News

- **2025-06**: v7.0 — Major revision after multi-round expert review
- Added formal Lemma 1 (DAG Completeness) and Hypothesis 1 (Privacy-Quality-Cost Trade-off)
- Added reproducible 3-layer Synthetic Data methodology
- Cross-domain validation on FewIE (ACL 2023) and CoNLL-2003

---

## Overview

Deploying LLMs for telecom fraud investigation faces a **two-paths-blocked dilemma**:

| Approach | Privacy | Quality |
|---------|---------|---------|
| **Send all data to LLM API** | ❌ Illegal (PIPL, Data Security Law) | ✅ Highest |
| **Send fully anonymized data** | ✅ Compliant | ❌ Low (removes noise AND signal) |
| **SOP-DAG (ours)** | ✅ Task-adaptive selective anonymization | ✅ Near-oracle (Δ<5%) |

SOP-DAG models the police standard operating procedure (SOP) as a directed acyclic graph (DAG) of atomic tasks, where each node only accesses the **minimally sufficient information set** required for its specific subtask.

### Key Insights

1. **Information Minimization Principle (IMP)**: Each node receives only the fields it actually needs.
2. **Task-adaptive anonymization**: The same PII field (e.g., a phone number) is handled differently for different tasks — masked for classification, preserved for fund-tracing.
3. **DAG completeness guarantee**: Under standard conditions, task decomposition is provably lossless (Lemma 1).

---

## Architecture

```
[Phase I: Registration]
  S1(Statement) → S2(Initial Classify) → S3(Urgency[RULE])
         ↓                    ↓                      ↓
[Phase II: Evidence]
  S4(Chat[LLM])   S5(Tx[RULE])   S6(App[LLM])   S7(Call[RULE])   S8(PII[RULE])
         ↓              ↓              ↓              ↓
[Phase III: Analysis]
  S9(Classify[LLM])   S10(Entity[HYBRID])   S11(Fund[LLM])   S12(Timeline[LLM])   S13(Scheme[LLM])
         ↓                   ↓                      ↓              ↓
[Phase IV: QA]
  S14(Quality[HYBRID])
         ↓
[Phase V: Report]
  S15(Report[LLM])
```

### Node Modes

| Mode | Description | Risk | Examples |
|------|-----------|------|----------|
| **RULE** | Local regex/rule, no API | Near zero | S3, S5, S7, S8 |
| **LLM** | API call with filtered input | Medium | S1,S4,S6,S9,S11,S12,S13,S15 |
| **HYBRID** | API call + local verification | Medium | S10, S14 |

---

## Synthetic Data Methodology

Real telecom fraud case data is protected under PIPL. We developed a **reproducible 3-layer pipeline**:

### Layer 1: Fraud Type Taxonomy (from 公安部标准)

| # | Type | Pattern |
|---|------|---------|
| 1 | 刷单返利 | Small rewards →垫付任务→ freeze |
| 2 | 虚假投资 | Group → fake platform → no withdrawal |
| 3 | 杀猪盘 | Social → emotional bond → crypto |
| 4 | 冒充客服 | Accurate order → phishing |
| 5 | 虚假贷款 | Ad → approval → fees → no loan |
| 6 | 冒充公检法 | Fear → forged warrant |
| 7 | 冒充熟人 | Voice mimic → cash request |
| 8 | 中奖诈骗 | Prize → taxes/fees |
| 9 | 虚拟货币杀猪 | Dating → fake exchange |

### Layer 2: Entity Schema

Each fraud type has structured schemas (Suspect/Account/App) with fields annotated by **legal PII sensitivity level** (HIGH/MEDIUM/LOW).

### Layer 3: Hybrid Generation

- **Structured data**: rule-based generation following schema patterns
- **Victim statements**: LLM-augmented with few-shot prompts + role-play instructions
- **Ground Truth**: Derived from schema, not human annotation

To adapt to a new domain (financial fraud, healthcare), replace Layers 1-2. Layer 3 code requires no modification.

---

## Experiments

### Claim-Driven Evaluation

| Exp | Claim | Method | Finding |
|-----|-------|--------|---------|
| **Exp 1** | SOP-DAG vs industry | vs Industry, Rule-only, TUB | Δ<6% vs TUB, 62% info reduction |
| **Exp 2** | DAG decomposition is lossless | Phase ablation | Any phase removal reduces quality (p<0.01) |
| **Exp 3** | IMP: minimal info is optimal | IMPCurve (5 levels + control) | Inverted-U confirms minimal sufficiency |
| **Exp 4** | Privacy-Accuracy trade-off is real | Pareto Frontier | SOP-DAG on frontier; Industry inside |
| **Exp 5** | Cross-domain generalizability | Leave-One-Type-Out + FewIE + CoNLL | ≥0.80 F1 all types; FewIE 0.84 F1 |

### Public Benchmarks

| Dataset | Task | SOP-DAG | Baseline |
|--------|------|---------|---------|
| FewIE (ACL 2023) | Entity extraction | 0.84 F1 | GPT-3.5: 0.86 |
| CoNLL-2003 | NER | 0.91 F1 | BERT-base: 0.92 |

---

## Quick Start

```bash
git clone https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud
cd GNT-AI-Repo-4-Anti-Fraud
pip install -r requirements.txt
cp .env.example .env  # Add your DeepSeek API key

python -m experiment.run_experiments --all --method ALL
```

```python
from experiment.sop_dag import SOPDAGExecutor, build_telecom_fraud_sop_dag
from experiment.config import get_api_config

dag = build_telecom_fraud_sop_dag()
executor = SOPDAGExecutor(api_config=get_api_config())
executor.load_dag(dag)
results = executor.execute(case_data)
print(results["S15"])
```

---

## Theoretical Contributions

### Hypothesis 1 (Privacy-Quality-Cost Trade-off)
> For any task T and sensitive set PII, there does not exist M such that: I(M,PII)=0, Q(M,T)=Q*(T), and C(M)≤C_baseline simultaneously.

### Lemma 1 (DAG Completeness)
> For any SOP-DAG satisfying Definition 1 (Information Complete DAG), O_DAG contains all key structured information without information loss. (Proof in Appendix A)

---

## Citation

```bibtex
@article{sopdag2025,
  title={SOP-DAG: Privacy-Preserving Task Decomposition for LLM-Assisted Telecom Fraud Investigation},
  author={Ma, Allen and Shi, Authors},
  year={2025},
  url={https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud}
}
```

---

## Ethical Considerations

- **D1 — Dual-Use**: Auxiliary tool; certified officers make final decisions.
- **D2 — Synthetic Data**: All cases fictitious; no real person data.
- **D3 — Responsibility**: Outputs require human review; no automated conviction.
- **D4 — Transparency**: Every node produces traceable JSON; supports post-hoc auditing.

> Disclaimer: Experimental research framework. Not for production use without validation and human oversight.

---

## License

MIT License.

---

<br>

---

# SOP-DAG：面向敏感领域的隐私感知任务分解框架 {#chinese-version}

> **英文版** | [中文版本](#chinese-version) (当前页面)
>
> **投稿状态**：ACL / EMNLP / NAACL
> **代码与数据**：`https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud`

---

## 最新更新

- **2025-06**: v7.0 — 多轮专家评审后的重大修订版
- 新增 Lemma 1（DAG推理完备性）和 Hypothesis 1（隐私-质量-成本不可能三角）
- 新增可复现的三层Synthetic Data生成方法
- 在FewIE (ACL 2023) 和 CoNLL-2003上验证跨领域泛化能力

---

## 概述

将LLM应用于电信网络诈骗案件分析，面临**"两难困境"**：

| 方案 | 隐私合规 | 分析质量 |
|------|---------|---------|
| **全量数据发给LLM API** | ❌ 违法 | ✅ 最高 |
| **全量数据脱敏后发送** | ✅ 合规 | ❌ 低下（去除了噪音，也去除了线索） |
| **SOP-DAG（本文）** | ✅ 任务自适应选择性脱敏 | ✅ 接近理论上限（Δ<5%） |

SOP-DAG将标准作业流程（SOP）建模为有向无环图（DAG），每个节点仅访问完成其原子任务所需的**最小必要信息集**。

### 核心创新

1. **信息最小化原则（IMP）**：每个节点只接收其真正需要的字段。
2. **任务自适应脱敏**：同一PII字段在不同任务中有不同的处理方式——分类时脱敏，追踪时保留。
3. **DAG无损性保证**：在标准条件下，任务分解是无损的（Lemma 1）。

---

## 架构

```
[第一阶段：受案登记]
  S1(陈述结构化) → S2(初步分类) → S3(紧急性[RULE])
         ↓                    ↓                      ↓
[第二阶段：证据接入]
  S4(聊天解析[LLM])  S5(流水解析[RULE])  S6(APP[LLM])  S7(通话[RULE])  S8(PII扫描[RULE])
         ↓              ↓              ↓              ↓
[第三阶段：核心分析]
  S9(精准分类[LLM])  S10(实体提取[HYBRID])  S11(资金追踪[LLM])  S12(时间线[LLM])  S13(手法画像[LLM])
         ↓                   ↓                      ↓              ↓
[第四阶段：质检]
  S14(质量检查[HYBRID])
         ↓
[第五阶段：报告]
  S15(结构化研判报告[LLM])
```

### 节点模式

| 模式 | 说明 | 风险 | 示例节点 |
|------|------|------|---------|
| **RULE** | 本地规则引擎，无需API调用 | 几乎为零 | S3、S5、S7、S8 |
| **LLM** | API调用，输入经过过滤 | 中等 | S1、S4、S6、S9、S11、S12、S13、S15 |
| **HYBRID** | API调用+本地验证 | 中等 | S10、S14 |

---

## Synthetic Data方法论

真实案件数据受《个人信息保护法》保护。我们开发了**可复现的三层生成管道**：

### 第一层：诈骗类型分类体系（基于公安部标准）

| # | 类型 | 核心模式 |
|---|------|---------|
| 1 | 刷单返利 | 小额返利→垫付任务→账户冻结 |
| 2 | 虚假投资 | 群聊引流→虚假平台→无法提现 |
| 3 | 杀猪盘 | 社交软件→建立感情→诱导转账 |
| 4 | 冒充客服 | 准确报出订单→钓鱼链接 |
| 5 | 虚假贷款 | 广告→审核通过→层层收费 |
| 6 | 冒充公检法 | 制造恐慌→伪造文书 |
| 7 | 冒充熟人 | 电话变声→紧急求助 |
| 8 | 中奖诈骗 | 虚假中奖→税金/公证费 |
| 9 | 虚拟货币杀猪 | 交友平台→虚假交易所 |

### 第二层：实体Schema

每个诈骗类型定义了嫌疑人/账户/APP的Schema模板，每个字段均标注**法律PII敏感级别**（HIGH/MEDIUM/LOW）。

### 第三层：混合生成

- **结构化数据**：基于Schema规则生成
- **被害人陈述**：LLM增强，Few-shot prompt + Role-play指令
- **Ground Truth**：从Schema直接推导，非人工标注

迁移到新领域（金融诈骗、医疗欺诈）只需替换第一、二层代码，第三层代码零修改。

---

## 实验

### Claim驱动评估

| 实验 | Claim | 方法 | 核心发现 |
|-----|-------|------|---------|
| **Exp 1** | SOP-DAG优于业界 | vs业界、纯规则、TUB | Δ<6% vs TUB，信息暴露减少62% |
| **Exp 2** | DAG分解无损 | 各Phase消融 | 跳过任一Phase均显著降低质量(p<0.01) |
| **Exp 3** | IMP：最小集最优 | IMPCurve（5档+对照组） | 倒U型曲线证实最小充分性 |
| **Exp 4** | 隐私-质量权衡真实存在 | Pareto前沿 | SOP-DAG在帕累托边界；业界在边界内侧 |
| **Exp 5** | 跨领域泛化能力 | 留一法+FewIE+CoNLL | 9类型全部≥0.80 F1；FewIE达0.84 F1 |

### 公开基准验证

| 数据集 | 任务 | SOP-DAG | 已报道基线 |
|--------|------|---------|-----------|
| FewIE (ACL 2023) | 实体抽取 | 0.84 F1 | GPT-3.5: 0.86 |
| CoNLL-2003 | 命名实体识别 | 0.91 F1 | BERT-base NER: 0.92 |

---

## 快速开始

```bash
git clone https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud
cd GNT-AI-Repo-4-Anti-Fraud
pip install -r requirements.txt
cp .env.example .env  # 填入DeepSeek API密钥

python -m experiment.run_experiments --all --method ALL
```

```python
from experiment.sop_dag import SOPDAGExecutor, build_telecom_fraud_sop_dag
from experiment.config import get_api_config

dag = build_telecom_fraud_sop_dag()
executor = SOPDAGExecutor(api_config=get_api_config())
executor.load_dag(dag)
results = executor.execute(case_data)
print(results["S15"])
```

---

## 理论贡献

### Hypothesis 1（隐私-质量-成本不可能三角）
> 对于任意任务T和敏感信息集合PII，不存在同时满足 I(M,PII)=0、Q(M,T)=Q*(T)、C(M)≤C_baseline 的M。

### Lemma 1（DAG推理完备性）
> 对于任意满足Definition 1（信息完备DAG）的SOP-DAG，端到端执行包含所有关键结构化信息，且不存在信息损失。（证明见论文附录A）

---

## 引用

```bibtex
@article{sopdag2025,
  title={SOP-DAG: 面向敏感领域的隐私感知任务分解框架},
  author={马 Allen, 石 {Authors}},
  year={2025},
  url={https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud}
}
```

---

## 伦理声明

- **D1 — 双重使用**：SOP-DAG为辅助工具，所有决策由持证民警做出。
- **D2 — Synthetic Data边界**：所有案件使用虚构实体，无真实人员数据。
- **D3 — 责任归属**：输出结果需人工复核，不支持自动化定罪。
- **D4 — 透明度**：每个节点产生可追溯的JSON输出，支持事后审计。

> 免责声明：此为实验性研究框架。未经充分验证和人工审核，请勿用于生产部署。

---

## 许可证

MIT License.
