"""
SOP-DAG Configuration
Privacy-Preserving Telecom Fraud Case Analysis Framework
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ─── DeepSeek API Configuration ──────────────────────────────────────────────

@dataclass
class APIConfig:
    """DeepSeek API settings."""

    api_key: str = os.environ.get("DEEPSEEK_API_KEY", "")
    base_url: str = os.environ.get(
        "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
    )
    model_fast: str = "deepseek-v4-flash"  # for standard nodes
    model_pro: str = "deepseek-v4-pro"  # for critical nodes (S9, S11, S14)
    max_tokens: int = 4096
    temperature: float = 0.0  # deterministic for reproducibility
    max_retries: int = 3
    retry_delay: float = 2.0


# ─── PII Classification ──────────────────────────────────────────────────────

@dataclass
class PIIConfig:
    """PII detection and classification rules."""

    # Patterns for PII detection (run locally, never sent to API)
    high_sensitivity_patterns: Dict[str, str] = field(
        default_factory=lambda: {
            "id_card": r"\b[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b",
            "bank_card": r"\b\d{16,19}\b",
            "phone": r"\b1[3-9]\d{9}\b",
        }
    )
    medium_sensitivity_patterns: Dict[str, str] = field(
        default_factory=lambda: {
            "chinese_name": r"(?:王|李|张|刘|陈|杨|黄|赵|周|吴|徐|孙|马|胡|朱|郭|何|罗|高|林|郑|梁|谢|唐|许|冯|宋|韩|邓|彭|曹|曾|萧|田|董|潘|袁|蔡|蒋|余|杜|叶|程|苏|魏|吕|丁|任|沈|姚|卢|姜|崔|钟|谭|陆|汪|范|金|石|廖|贾|夏|韦|傅|方|白|邹|孟|熊|秦|邱|江|尹|薛|阎|段|雷|侯|龙|史|陶|黎|贺|顾|毛|郝|龚|邵|万|钱|严|覃|武|戴|莫|孔|向|汤){1,3}",
        }
    )
    low_sensitivity_fields: List[str] = field(
        default_factory=lambda: [
            "timestamp", "amount", "app_name", "text_content",
            "duration", "caller_type", "transaction_type",
        ]
    )


# ─── SOP-DAG Node Configuration ──────────────────────────────────────────────

@dataclass
class SOPNodeConfig:
    """Configuration for a single SOP-DAG node."""

    node_id: str
    task_description: str
    mode: str  # "RULE", "LLM", or "HYBRID"
    minimal_info_set: List[str]  # M_i: minimally sufficient fields
    output_schema: Dict[str, str]  # expected output structure
    downstream_nodes: List[str] = field(default_factory=list)  # edges in DAG
    prompt_template: Optional[str] = None  # for LLM/HYBRID nodes
    rule_check: Optional[str] = None  # for HYBRID nodes


# ─── Experiment Configuration ────────────────────────────────────────────────

@dataclass
class ExperimentConfig:
    """Experiment setup."""

    # Data
    synthetic_cases: int = 10  # public Layer 1 benchmark
    real_cases_sample: int = 30  # private Layer 2 sample

    # Methods to compare
    methods: List[str] = field(
        default_factory=lambda: [
            "A_oracle",  # Full raw data → LLM (illegal, upper bound)
            "B_industry",  # Full masked data → LLM (legal, baseline)
            "C_rule_only",  # Pure rule engine (lower bound)
            "D_sop_dag",  # Our method: SOP-DAG with IMP/MCM
        ]
    )

    # Models
    models: List[str] = field(
        default_factory=lambda: ["deepseek-v4-flash"]
    )

    # Evaluation
    metrics: List[str] = field(
        default_factory=lambda: [
            "fraud_type_accuracy",
            "entity_f1",
            "fund_flow_completeness",
            "timeline_coverage",
            "quality_check_f1",
            "report_quality_score",
            "information_exposure",
            "api_cost_tokens",
            "privacy_leakage",
        ]
    )

    # Human baseline
    human_annotators: int = 3

    # Output
    results_dir: str = "../data/results"


# ─── Default Config ──────────────────────────────────────────────────────────

def get_default_config() -> ExperimentConfig:
    return ExperimentConfig()


def get_api_config() -> APIConfig:
    return APIConfig()


def get_pii_config() -> PIIConfig:
    return PIIConfig()
