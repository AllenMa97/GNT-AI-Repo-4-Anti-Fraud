"""
SOP-DAG Core Framework
─────────────────────
Privacy-preserving workflow decomposition for sensitive-domain case analysis.

Architecture:
    Domain SOP → SOP-DAG (五元组 DAG) → IMP/MCM → Privacy-aware execution

Key concepts:
    - v_i = (Task, Input, Output, Mode, M_i)  — atomic case-processing step
    - IMP: Information Minimality Principle — each node only sees M_i
    - MCM: Mode Classification Matrix — auto-classifies RULE/LLM/HYBRID
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from .config import APIConfig, PIIConfig, SOPNodeConfig, get_api_config, get_pii_config
from .rule_engine import PIIFilter, RuleEngine
from .llm_client import DeepSeekClient

logger = logging.getLogger(__name__)


class NodeMode(Enum):
    RULE = "RULE"
    LLM = "LLM"
    HYBRID = "HYBRID"


@dataclass
class DAGNode:
    """A single node in the SOP-DAG."""

    node_id: str
    task: str
    mode: NodeMode
    minimal_info_set: List[str]  # M_i: IMP-defined minimal sufficient info
    output_schema_keys: List[str]
    prompt_path: Optional[str] = None  # path to prompt template
    downstream: List[str] = field(default_factory=list)  # DAG edges
    rule_function: Optional[str] = None  # for RULE/HYBRID nodes

    # Runtime state
    output: Optional[Dict[str, Any]] = None
    executed: bool = False
    api_tokens_used: int = 0


# ─── Telecom Fraud SOP-DAG Builder ───────────────────────────────────────────

def build_telecom_fraud_sop_dag() -> Dict[str, DAGNode]:
    """
    Build the complete 15-node SOP-DAG for telecom fraud investigation.

    Five phases:
        Phase I:   Case Registration & Initial Assessment (S1-S3)
        Phase II:  Multi-Source Evidence Integration (S4-S8)
        Phase III: Core Case Analysis (S9-S13)
        Phase IV:  Evidence Quality Check (S14)
        Phase V:   Report Generation (S15)
    """
    nodes = {}

    # ── Phase I: Registration & Assessment ───────────────────────────────
    nodes["S1"] = DAGNode(
        node_id="S1",
        task="Structure the victim's statement into a standardized format",
        mode=NodeMode.LLM,
        minimal_info_set=["victim_statement"],
        output_schema_keys=["structured_statement", "key_facts"],
        prompt_path="prompts/S1_statement_structure.txt",
        downstream=["S2", "S9"],
    )

    nodes["S2"] = DAGNode(
        node_id="S2",
        task="Quick initial fraud type classification",
        mode=NodeMode.LLM,
        minimal_info_set=["fraud_description", "app_type"],
        output_schema_keys=["preliminary_fraud_type", "confidence"],
        prompt_path="prompts/S2_initial_classification.txt",
        downstream=["S9"],
    )

    nodes["S3"] = DAGNode(
        node_id="S3",
        task="Assess case urgency (e-stop needed?)",
        mode=NodeMode.RULE,
        minimal_info_set=["latest_transaction_amount", "latest_transaction_time"],
        output_schema_keys=["is_urgent", "risk_level", "reason"],
        rule_function="check_urgency",
        downstream=["S9"],
    )

    # ── Phase II: Evidence Integration ───────────────────────────────────
    nodes["S4"] = DAGNode(
        node_id="S4",
        task="Parse chat logs into structured conversation records",
        mode=NodeMode.LLM,
        minimal_info_set=["chat_records"],
        output_schema_keys=["parsed_messages", "key_topics", "relationships"],
        prompt_path="prompts/S4_chat_parsing.txt",
        downstream=["S10", "S12", "S13"],
    )

    nodes["S5"] = DAGNode(
        node_id="S5",
        task="Parse and standardize transaction records",
        mode=NodeMode.RULE,
        minimal_info_set=["transactions"],
        output_schema_keys=["parsed_transactions"],
        rule_function="parse_transactions",
        downstream=["S11"],
    )

    nodes["S6"] = DAGNode(
        node_id="S6",
        task="Extract relevant info from involved APP descriptions",
        mode=NodeMode.LLM,
        minimal_info_set=["app_name", "app_description"],
        output_schema_keys=["app_type", "app_role", "risk_indicators"],
        prompt_path="prompts/S6_app_extraction.txt",
        downstream=["S9", "S10"],
    )

    nodes["S7"] = DAGNode(
        node_id="S7",
        task="Parse call records into standardized format",
        mode=NodeMode.RULE,
        minimal_info_set=["call_records"],
        output_schema_keys=["parsed_calls"],
        rule_function="parse_calls",
        downstream=["S12"],
    )

    nodes["S8"] = DAGNode(
        node_id="S8",
        task="Full PII scan and field classification",
        mode=NodeMode.RULE,
        minimal_info_set=["__ALL__"],  # Full access but local only
        output_schema_keys=["pii_map", "total_pii_fields"],
        rule_function="full_pii_scan",
        downstream=["S10", "S12"],  # Provides masking info to text-processing nodes
    )

    # ── Phase III: Core Analysis ─────────────────────────────────────────
    nodes["S9"] = DAGNode(
        node_id="S9",
        task="Precise fraud type determination based on all evidence",
        mode=NodeMode.LLM,
        minimal_info_set=["fraud_scheme", "investment_talk", "transaction_pattern"],
        output_schema_keys=["fraud_type", "subtype", "confidence", "evidence_summary"],
        prompt_path="prompts/S9_precise_classification.txt",
        downstream=["S10", "S13", "S14"],
    )

    nodes["S10"] = DAGNode(
        node_id="S10",
        task="Extract and link key entities (persons, accounts, apps, platforms)",
        mode=NodeMode.HYBRID,
        minimal_info_set=["masked_texts", "relation_hints"],
        output_schema_keys=["entities", "entity_relations"],
        prompt_path="prompts/S10_entity_extraction.txt",
        rule_function="verify_entities",
        downstream=["S11", "S12", "S15"],
    )

    nodes["S11"] = DAGNode(
        node_id="S11",
        task="Trace fund flow through the transaction chain",
        mode=NodeMode.LLM,
        minimal_info_set=["amounts", "timestamps", "counterparties"],
        output_schema_keys=["fund_flow_graph", "total_outflow", "total_inflow", "key_accounts"],
        prompt_path="prompts/S11_fund_tracing.txt",
        downstream=["S12", "S14", "S15"],
    )

    nodes["S12"] = DAGNode(
        node_id="S12",
        task="Reconstruct timeline across 引流→通联→网络→交易 phases",
        mode=NodeMode.LLM,
        minimal_info_set=["event_summaries", "timestamps", "entity_pseudonyms"],
        output_schema_keys=["timeline", "phase_classification"],
        prompt_path="prompts/S12_timeline.txt",
        downstream=["S14", "S15"],
    )

    nodes["S13"] = DAGNode(
        node_id="S13",
        task="Profile the fraud scheme: unique tactics and scripts used",
        mode=NodeMode.LLM,
        minimal_info_set=["fraud_script_fragments", "scheme_details"],
        output_schema_keys=["scheme_profile", "unique_tactics", "script_patterns"],
        prompt_path="prompts/S13_scheme_profile.txt",
        downstream=["S14", "S15"],
    )

    # ── Phase IV: Quality Check ─────────────────────────────────────────
    nodes["S14"] = DAGNode(
        node_id="S14",
        task="Multi-dimensional quality inspection (8 dimensions, 118 items)",
        mode=NodeMode.HYBRID,
        minimal_info_set=["all_outputs", "metadata"],
        output_schema_keys=["quality_report", "checks", "issues", "passed_count"],
        prompt_path="prompts/S14_quality_check.txt",
        rule_function="quality_check",
        downstream=["S15"],
    )

    # ── Phase V: Report ──────────────────────────────────────────────────
    nodes["S15"] = DAGNode(
        node_id="S15",
        task="Generate structured investigation report",
        mode=NodeMode.LLM,
        minimal_info_set=["all_previous_outputs"],
        output_schema_keys=["fraud_type", "timeline", "entities", "fund_flow", "scheme", "quality", "recommendations"],
        prompt_path="prompts/S15_report.txt",
        downstream=[],
    )

    return nodes


# ─── SOP-DAG Executor ────────────────────────────────────────────────────────

class SOPDAGExecutor:
    """
    Executes a SOP-DAG with privacy-preserving information filtering.

    For each node in topological order:
        1. Filter input: keep only M_i fields, mask/remove PII
        2. Dispatch by Mode: RULE → local, LLM → API, HYBRID → API + verify
        3. Cross-node privacy audit: check outputs for raw PII
        4. Pass results to downstream nodes
    """

    def __init__(
        self,
        api_config: Optional[APIConfig] = None,
        pii_config: Optional[PIIConfig] = None,
    ):
        self.api_config = api_config or get_api_config()
        self.pii_config = pii_config or get_pii_config()
        self.pii_filter = PIIFilter(self.pii_config)
        self.rule_engine = RuleEngine()
        self.llm_client = DeepSeekClient(self.api_config)
        self.nodes: Dict[str, DAGNode] = {}

    def load_dag(self, nodes: Dict[str, DAGNode]):
        """Load a SOP-DAG for execution."""
        self.nodes = nodes

    def _topological_order(self) -> List[str]:
        """Topological sort using Kahn's algorithm."""
        in_degree = {nid: 0 for nid in self.nodes}
        for node in self.nodes.values():
            for downstream in node.downstream:
                if downstream in in_degree:
                    in_degree[downstream] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            current = queue.pop(0)
            order.append(current)
            for downstream in self.nodes[current].downstream:
                if downstream in in_degree:
                    in_degree[downstream] -= 1
                    if in_degree[downstream] == 0:
                        queue.append(downstream)

        return order

    def _filter_fields(self, raw_data: Dict, minimal_set: List[str]) -> Dict:
        """
        Filter and mask fields according to IMP.

        Only fields in minimal_set are kept.
        PII fields are masked (HIGH) or pseudonymized (MEDIUM).
        """
        filtered = {}

        # Special case: "__ALL__" means full access (for local-only nodes)
        if "__ALL__" in minimal_set:
            fields_to_keep = set(raw_data.keys())
        else:
            fields_to_keep = set(minimal_set) & set(raw_data.keys())

        for field in fields_to_keep:
            value = raw_data[field]
            sensitivity = self.pii_filter.field_classification(field)

            if isinstance(value, str):
                if sensitivity == "HIGH":
                    scan_result = self.pii_filter.scan(value)
                    filtered[field] = scan_result.masked_text
                elif sensitivity == "MEDIUM":
                    scan_result = self.pii_filter.scan(value)
                    filtered[field] = scan_result.masked_text
                else:
                    filtered[field] = value

            elif isinstance(value, dict):
                # Recursively filter dicts
                filtered[field] = {
                    k: self._mask_if_needed(v, field)
                    for k, v in value.items()
                }
            elif isinstance(value, list):
                filtered[field] = [
                    self._mask_if_needed(item, field) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                filtered[field] = value

        return filtered

    def _mask_if_needed(self, value: Any, _field: str) -> Any:
        if not isinstance(value, str):
            return value
        scan = self.pii_filter.scan(value)
        return scan.masked_text if scan.has_pii else value

    def _audit_output(self, output: Any) -> bool:
        """Check if output contains raw PII. Returns True if clean."""
        if isinstance(output, str):
            return not self.pii_filter.check_leakage(output)
        if isinstance(output, dict):
            for v in output.values():
                if not self._audit_output(v):
                    return False
        if isinstance(output, list):
            for item in output:
                if not self._audit_output(item):
                    return False
        return True

    def _execute_rule_node(self, node: DAGNode, filtered_data: Dict) -> Dict:
        """Execute a RULE-mode node locally."""
        func_name = node.rule_function
        if func_name == "check_urgency":
            txn = filtered_data.get("latest_transaction", {})
            return self.rule_engine.check_urgency(txn)
        elif func_name == "parse_transactions":
            txns = filtered_data.get("transactions", [])
            return {"parsed_transactions": self.rule_engine.parse_transactions(txns)}
        elif func_name == "parse_calls":
            calls = filtered_data.get("call_records", [])
            return {"parsed_calls": self.rule_engine.parse_calls(calls)}
        elif func_name == "full_pii_scan":
            return self.rule_engine.full_pii_scan(filtered_data, self.pii_filter)
        else:
            logger.warning(f"Unknown rule function: {func_name}")
            return {}

    def _execute_llm_node(
        self, node: DAGNode, filtered_data: Dict, model: str
    ) -> Dict:
        """Execute a LLM-mode node via API."""
        system_prompt = self._build_system_prompt(node, filtered_data)
        user_prompt = json.dumps(filtered_data, ensure_ascii=False, indent=2)

        start_tokens = self.llm_client.total_tokens
        result = self.llm_client.call_structured_json(
            system_prompt=system_prompt, user_prompt=user_prompt, model=model
        )
        node.api_tokens_used = self.llm_client.total_tokens - start_tokens

        return result if result else {}

    def _execute_hybrid_node(
        self, node: DAGNode, filtered_data: Dict, model: str
    ) -> Dict:
        """Execute a HYBRID-mode node: LLM call + local rule verification."""
        # Step 1: LLM execution
        llm_output = self._execute_llm_node(node, filtered_data, model)

        # Step 2: Rule verification
        func_name = node.rule_function
        if func_name == "verify_entities":
            entities = llm_output.get("entities", [])
            verification = self.rule_engine.verify_entities(entities)
            llm_output["rule_verification"] = verification
        elif func_name == "quality_check":
            quality = self.rule_engine.quality_check(llm_output)
            llm_output["rule_verification"] = quality
            llm_output["quality_report"] = quality

        return llm_output

    def _build_system_prompt(
        self, node: DAGNode, _filtered_data: Dict
    ) -> str:
        """Build system prompt for a node."""
        # Try loading from prompt file
        if node.prompt_path:
            try:
                with open(node.prompt_path, "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                pass

        # Fallback: build from node definition
        return (
            f"You are an expert assistant for telecom fraud investigation.\n\n"
            f"Task: {node.task}\n\n"
            f"Output format: JSON with keys {node.output_schema_keys}\n\n"
            f"CRITICAL: Output ONLY valid JSON. No markdown, no explanations."
        )

    def execute(
        self,
        raw_case_data: Dict,
        model: str = "deepseek-v4-flash",
        critical_model: str = "deepseek-v4-pro",
    ) -> Dict[str, Any]:
        """
        Execute the entire SOP-DAG on a single case.

        Returns:
            Dictionary mapping node_id → node output
        """
        self.llm_client.reset_stats()
        order = self._topological_order()
        results = {}

        # Accumulate outputs for downstream consumption
        accumulated = dict(raw_case_data)

        for node_id in order:
            node = self.nodes[node_id]
            logger.info(f"Executing {node_id} (Mode={node.mode.value}): {node.task}")

            # Step 1: Filter information by IMP
            filtered = self._filter_fields(accumulated, node.minimal_info_set)

            # Step 2: Execute by mode
            if node.mode == NodeMode.RULE:
                output = self._execute_rule_node(node, filtered)

            elif node.mode == NodeMode.LLM:
                use_model = (
                    critical_model
                    if node_id in {"S9", "S11", "S14", "S15"}
                    else model
                )
                output = self._execute_llm_node(node, filtered, use_model)

            elif node.mode == NodeMode.HYBRID:
                use_model = (
                    critical_model if node_id == "S14" else model
                )
                output = self._execute_hybrid_node(node, filtered, use_model)

            else:
                output = {}

            # Step 3: Privacy audit
            if not self._audit_output(output):
                logger.error(
                    f"PRIVACY LEAK DETECTED in node {node_id}! Blocking output."
                )
                output = {
                    "__BLOCKED__": "Privacy leak detected, output suppressed"
                }

            # Step 4: Store and accumulate
            node.output = output
            node.executed = True
            results[node_id] = output
            accumulated[node_id] = output

        return results

    def get_exposure_measure(self) -> float:
        """Compute normalized information exposure across all nodes."""
        total_fields = 0
        exposed_fields = 0
        for node in self.nodes.values():
            total_fields += len(node.minimal_info_set)
            # LLM and HYBRID nodes expose data externally
            if node.mode in (NodeMode.LLM, NodeMode.HYBRID):
                exposed_fields += len(node.minimal_info_set)
        return exposed_fields / max(total_fields, 1) if total_fields > 0 else 0

    def get_privacy_leakage(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Check for PII leakage across all node outputs."""
        leaks = {}
        for node_id, output in results.items():
            output_str = json.dumps(output, ensure_ascii=False)
            if self.pii_filter.check_leakage(output_str):
                leaks[node_id] = "PII_DETECTED"

        return {
            "total_leaks": len(leaks),
            "leak_details": leaks,
            "is_clean": len(leaks) == 0,
        }
