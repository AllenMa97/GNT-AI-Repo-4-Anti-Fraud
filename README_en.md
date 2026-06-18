# SOP-DAG: Privacy-Preserving Task Decomposition for LLM-Assisted Sensitive Domain Applications

> **Status**: Under submission to ACL / EMNLP / NAACL
> **Code & Data**: `https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud`
> **中文版**: [README.md](./README.md) (Default - Opens First)

---

## Latest News

- **2025-06**: v8.0 — Final version after 20-round adversarial scholar battle
- Added Information Minimization Principle (IMP) theoretical framework
- Added DAG Inference Completeness Lemma (Lemma 1)
- Added Privacy-Quality-Cost Impossible Triangle Hypothesis (Hypothesis 1)
- Added 4-layer reproducible data construction pipeline based on MSRA-NER
- Validated cross-domain generalization on FewIE (ACL 2023) and CoNLL-2003

---

## Background

Deploying LLMs for telecom fraud investigation faces a **"two-paths-blocked dilemma"**:

| Approach | Privacy Compliance | Analysis Quality |
|---------|-------------------|-----------------|
| **Send all data to LLM API** | ❌ Illegal (PIPL, Data Security Law) | ✅ Highest |
| **Send fully anonymized data** | ✅ Compliant | ❌ Low (removes noise AND signal) |
| **SOP-DAG (ours)** | ✅ Task-adaptive selective anonymization | ✅ Near-oracle (Δ<5%) |

### Key Contributions

1. **Information Minimization Principle (IMP)**: Each node receives only the fields it actually needs, not all data
2. **Task-adaptive anonymization**: The same PII field is handled differently for different tasks — masked for classification, preserved for fund-tracing
3. **DAG completeness guarantee**: Under standard conditions, task decomposition is provably lossless (Lemma 1)

---

## Theoretical Framework

### Hypothesis 1 (Privacy-Quality-Cost Impossible Triangle)

> For any task T and sensitive information set PII, there does not exist a minimum information set M such that simultaneously:
> - `I(M,PII) = 0` (Zero information leakage)
> - `Q(M,T) = Q*(T)` (Achieves optimal quality)
> - `C(M) ≤ C_baseline` (Cost not higher than baseline)

### Lemma 1 (DAG Inference Completeness)

> For any SOP-DAG satisfying Definition 1 (Information Complete DAG), end-to-end execution contains all key structured information without information loss. (Proof in Appendix A)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SOP-DAG: Privacy-Preserving Task Decomposition       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Phase I: Registration]                                                │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                            │
│  │ S1      │ → │ S2      │ → │ S3      │ [RULE]                      │
│  │Statement│    │Initial  │    │Urgency  │                            │
│  │Parsing  │    │Classify │    │Eval     │                            │
│  └─────────┘    └─────────┘    └─────────┘                            │
│       ↓               ↓               ↓                                 │
│  [Phase II: Evidence Access]                                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ S4      │  │ S5      │  │ S6      │  │ S7      │  │ S8      │    │
│  │Chat     │  │Trans.   │  │APP      │  │Call     │  │PII      │    │
│  │Parse[LLM]│ │Parse[RULE│ │Analyze[LLM│ │Record[RULE│ │Scan[RULE│    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │
│       ↓              ↓              ↓              ↓                           │
│  [Phase III: Core Analysis]                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ S9      │  │S10      │  │S11      │  │S12      │  │S13      │    │
│  │Precise  │  │Entity   │  │Fund     │  │Timeline │  │Scheme   │    │
│  │Classify │  │Extract  │  │Tracing  │  │Analysis │  │Profile  │    │
│  │[LLM]    │  │[HYBRID] │  │[LLM]    │  │[LLM]    │  │[LLM]    │    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │
│       ↓               ↓              ↓              ↓                          │
│  [Phase IV: Quality Check]                                               │
│  ┌─────────┐                                                                 │
│  │S14      │ [HYBRID]                                                     │
│  │Quality  │                                                                │
│  │Check    │                                                                │
│  └─────────┘                                                                 │
│       ↓                                                                     │
│  [Phase V: Report]                                                       │
│  ┌─────────┐                                                                 │
│  │S15      │ [LLM]                                                        │
│  │Structured│                                                                │
│  │Analysis  │                                                                │
│  └─────────┘                                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Node Mode Description

| Mode | Description | API Risk | Example Nodes |
|------|-------------|----------|---------------|
| **RULE** | Local rule engine, no API call | Near zero | S3, S5, S7, S8 |
| **LLM** | API call with filtered input | Medium | S1,S4,S6,S9,S11,S12,S13,S15 |
| **HYBRID** | API call + local verification | Medium | S10, S14 |

---

## Data Construction Pipeline

Following the methodology of DocRED (ACL 2019) and FewIE (ACL 2023), we developed a **4-layer reproducible pipeline**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Layer 0: Entity Pattern Layer                │
│  Source: MSRA-NER (Microsoft Research Asia)                    │
│  Content: 46,000+ sentences, 1.3M+ annotated characters       │
│  Output: Realistic Chinese person/location/organization names  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Layer 1: Domain Taxonomy Layer               │
│  Source: Ministry of Public Security Classification + Experts   │
│  Output: 9 fraud type patterns, keywords, channels, payments   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Layer 2: Entity Schema Layer                 │
│  Source: PII sensitivity analysis + Legal framework            │
│  Output: 7 entity types + sensitivity levels + mask strategies │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Layer 3: Hybrid Generation Layer              │
│  Source: Rule-based generation + Template filling               │
│  Output: Complete case records + Ground Truth (100% consistent)│
└─────────────────────────────────────────────────────────────────┘
```

### Fraud Type Taxonomy (Ministry of Public Security 9-Category Standard)

| ID | Type | Core Pattern | Amount Range (CNY) |
|----|------|--------------|---------------------|
| 1 | Fake Order Scam | Small reward → prepayment → freeze | 500-30,000 |
| 2 | Fake Investment | Group → fake platform → no withdrawal | 10,000-500,000 |
| 3 | Pig-Butchering | Social → emotional bond → crypto | 5,000-200,000 |
| 4 | Fake Customer Service | Accurate order → phishing | 500-50,000 |
| 5 | Fake Loan | Ad → approval → fees → no loan | 1,000-30,000 |
| 6 | Impersonating Law Enforcement | Fear → forged warrant → "safe account" | 10,000-1,000,000 |
| 7 | Impersonating Acquaintances | Voice mimic → emergency → cash | 1,000-50,000 |
| 8 | Prize Scam | Fake prize → taxes/fees → no reward | 500-20,000 |
| 9 | Crypto Pig-Butchering | Dating → fake exchange → USDT | 5,000-500,000 |

### PII Sensitivity Three-Level Classification

| Level | Definition | Mask Strategy | Example |
|-------|-----------|---------------|---------|
| **HIGH** | Direct PII (name, ID, phone) | Generate fictional | 张伟 → 陈明 |
| **MEDIUM** | Indirect PII (bank card, call log) | Partial mask | 6222****1234 |
| **LOW** | Non-PII (APP name, chat content) | Keep | "Congratulations!" |

### Dataset Statistics (CTFD)

| Statistic | Value |
|-----------|-------|
| Total Cases | 45 (9 types × 5 cases) |
| Train/Dev/Test | 27 / 9 / 9 (60/20/20) |
| Avg. Case Length | 1,247 characters |
| Avg. Chat Records | 8 per case |
| Avg. Transactions | 5 per case |
| PII Fields per Case | 12 (4 HIGH, 4 MEDIUM, 4 LOW) |

### Cross-Domain Validation Sets

| Dataset | Task | Size | Source |
|---------|------|------|--------|
| FewIE (ACL 2023) | Chinese IE | 16,000 sentences | Chinese NLP Community |
| CoNLL-2003 | NER | 22,000 sentences | CONLL Shared Task |

---

## Experiments

### Claim-Driven Evaluation

| Exp | Claim | Method | Key Finding |
|-----|-------|--------|-------------|
| **Exp 1** | SOP-DAG > Industry | vs Industry, Rule-only, TUB | Δ<6% vs TUB, 62% info reduction |
| **Exp 2** | DAG decomposition is lossless | Phase ablation | Any phase skip reduces quality (p<0.01) |
| **Exp 3** | IMP: minimal is optimal | IMPCurve (5 levels + control) | Inverted-U confirms minimal sufficiency |
| **Exp 4** | Privacy-Accuracy trade-off is real | Pareto Frontier | SOP-DAG on frontier; Industry inside |
| **Exp 5** | Cross-domain generalization | Leave-One-Type-Out + FewIE + CoNLL | All 9 types ≥0.80 F1; FewIE 0.84 F1 |
| **Exp 6** | Input vs Output filtering | Ablation | Input-level significantly better |
| **Exp 7** | LLM self-selects M_i | vs preset M_i | GPT-4 achieves 85% accuracy |

### Public Benchmark Validation

| Dataset | Task | SOP-DAG | Reported Baseline |
|--------|------|---------|-------------------|
| FewIE (ACL 2023) | Entity extraction | 0.84 F1 | GPT-3.5: 0.86 |
| CoNLL-2003 | NER | 0.91 F1 | BERT-base NER: 0.92 |

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud
cd GNT-AI-Repo-4-Anti-Fraud

# Install dependencies
pip install -r requirements.txt
cp .env.example .env  # Add your DeepSeek API key

# Generate test data
python experiment/generate_chinese_fraud_data.py --all --n 5

# Run experiments
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

## Paper Resources

| Resource | Description |
|----------|-------------|
| [Chinese Outline](./paper/论文纲要_中文.md) | Complete Chinese paper outline (v8.0) |
| [English Outline](./paper/论文纲要_英文.md) | Complete English paper outline (v8.0) |
| [Architecture Diagram](./paper/figures/tapf-architecture.html) | Paper architecture preview |
| [Design Philosophy](./paper/figures/design-philosophy.md) | Data Sentinel visual design philosophy |
| [Methodology Document](../论文_数据构建Pipeline方法论.md) | Detailed data construction pipeline methodology |

## Figure Resources

| File | Description |
|------|-------------|
| `paper/figures/tapf-architecture.html` | SOP-DAG architecture diagram (open in browser to preview) |
| `paper/figures/design-philosophy.md` | Visual design philosophy document |

---

## Ethical Considerations

| Principle | Implementation |
|-----------|----------------|
| **Privacy** | All PII is synthetically generated; no real person data |
| **No Harm** | Dataset used for fraud INVESTIGATION research, not fraud commission |
| **Transparency** | Full methodology disclosed; code available |
| **Benefit** | Aims to improve police efficiency in fraud investigation |

> Disclaimer: This is an experimental research framework. Do not use in production without validation and human oversight.

---

## Citation

```bibtex
@article{sopdag2025,
  title={SOP-DAG: Privacy-Preserving Task Decomposition for LLM-Assisted Sensitive Domain Applications},
  author={Ma, Allen and Shi, Authors},
  year={2025},
  url={https://github.com/AllenMa97/GNT-AI-Repo-4-Anti-Fraud}
}
```

---

## License

MIT License.
