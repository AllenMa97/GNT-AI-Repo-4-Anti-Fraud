import json
import os
import logging

from .llm_client import DeepSeekClient
from .config import get_api_config

logger = logging.getLogger(__name__)


class BaselineMethods:
    """
    Four comparison methods for the experiment.

    Method A (Oracle, illegal):
        Full raw data → single LLM call → structured report.
        Upper bound on quality, violates data protection laws.

    Method B (Industry, legal):
        Full masked data → single LLM call → structured report.
        Current industry practice. All PII replaced with type markers.

    Method C (Rule-only):
        Pure rule engine. Only 5 RULE nodes run (S3, S5, S7, S8, partially S14).
        LLM-reliant nodes are skipped or use template-filled outputs.
        Lower bound on quality, zero privacy risk.

    Method D (SOP-DAG, our method):
        15-node SOP-DAG with IMP field filtering and MCM mode dispatch.
    """

    SYSTEM_PROMPT = (
        "你是一名专业的电信诈骗案件分析专家。请根据提供的案件材料，"
        "输出结构化的案件分析结果。\n\n"
        "输出格式（JSON）：\n"
        "{\n"
        '  "fraud_type": "诈骗类型",\n'
        '  "fraud_subtype": "子类型",\n'
        '  "timeline": [{"phase": "阶段", "time": "时间", "event": "事件描述"}],\n'
        '  "entities": [{"type": "类型", "value": "值", "role": "作用"}],\n'
        '  "fund_flow": {"total_outflow": 0, "total_inflow": 0, "chain": "描述"},\n'
        '  "scheme_profile": {"tactics": [], "script_patterns": []},\n'
        '  "quality_issues": ["质量问题1"],\n'
        '  "recommendations": ["建议1"]\n'
        "}"
    )

    def __init__(self):
        api_config = get_api_config()
        self.llm_client = DeepSeekClient(api_config)

    def method_a_oracle(self, case_data: dict, model: str = "deepseek-v4-flash") -> dict:
        """
        Method A: Full raw data → single LLM call.
        ⚠️ ILLEGAL in production — PII in raw data sent to API.
        """
        user_prompt = json.dumps(case_data, ensure_ascii=False, indent=2)
        result = self.llm_client.call_structured_json(
            system_prompt=self.SYSTEM_PROMPT, user_prompt=user_prompt, model=model
        )
        return result if result else {"error": "API call failed"}

    def method_b_industry(
        self,
        case_data: dict,
        masked_data: dict,
        model: str = "deepseek-v4-flash",
    ) -> dict:
        """
        Method B: Full masked data → single LLM call.
        Current industry practice — mask all PII, then send everything.
        """
        user_prompt = json.dumps(masked_data, ensure_ascii=False, indent=2)
        result = self.llm_client.call_structured_json(
            system_prompt=self.SYSTEM_PROMPT, user_prompt=user_prompt, model=model
        )
        return result if result else {"error": "API call failed"}

    def method_c_rule_only(self, case_data: dict) -> dict:
        """
        Method C: Pure rule engine, no LLM.
        """
        from .rule_engine import RuleEngine, PIIFilter
        from .config import get_pii_config

        engine = RuleEngine()
        pii_filter = PIIFilter(get_pii_config())

        result = {"fraud_type": "unknown", "timeline": [], "entities": [], "fund_flow": {}, "quality_issues": [], "recommendations": []}

        # RULE nodes that can run
        urgency = engine.check_urgency(
            case_data.get("latest_transaction", {})
        )

        transactions = engine.parse_transactions(
            case_data.get("transactions", [])
        )

        calls = engine.parse_calls(case_data.get("call_records", []))

        pii_scan = engine.full_pii_scan(case_data, pii_filter)

        # Fill in what we can
        result["fund_flow"]["parsed_transactions"] = transactions
        result["fund_flow"]["transaction_count"] = len(transactions)
        total = sum(t.get("amount", 0) for t in transactions if t.get("direction") == "outgoing")
        result["fund_flow"]["total_outflow"] = total

        result["quality_issues"].append(
            "Rule-only mode: fraud_type not determined (needs LLM)"
        )

        if urgency.get("is_urgent"):
            result["recommendations"].append("URGENT: Consider emergency stop-payment")

        result["pii_scan"] = pii_scan

        return result
