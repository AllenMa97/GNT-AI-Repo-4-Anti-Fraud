"""
Local Rule Engine
─────────────────
All operations run LOCALLY — no data leaves the machine through this module.
Handles PII detection, field classification, and deterministic checks.
"""

import re
import json
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field

from .config import get_pii_config, PIIConfig

logger = logging.getLogger(__name__)


# ─── PII Detection ───────────────────────────────────────────────────────────

@dataclass
class PIIDetectionResult:
    """Result of scanning a text for PII."""

    original_text: str
    masked_text: str
    detections: List[Dict[str, Any]] = field(default_factory=list)
    has_pii: bool = False
    pii_types: Set[str] = field(default_factory=set)


class PIIFilter:
    """
    Local PII scanner and masker.
    NEVER sends data to external services.
    """

    def __init__(self, config: Optional[PIIConfig] = None):
        self.config = config or get_pii_config()
        self._compile_patterns()

    def _compile_patterns(self):
        self._high_patterns = {
            name: re.compile(pattern)
            for name, pattern in self.config.high_sensitivity_patterns.items()
        }
        self._med_patterns = {
            name: re.compile(pattern)
            for name, pattern in self.config.medium_sensitivity_patterns.items()
        }

    def scan(self, text: str) -> PIIDetectionResult:
        """Scan text and replace PII with type markers."""
        result = PIIDetectionResult(original_text=text, masked_text=text)

        # High-sensitivity: replace with type marker
        for pii_type, pattern in self._high_patterns.items():
            for match in pattern.finditer(text):
                original = match.group()
                marker = f"[{pii_type.upper()}]"
                result.masked_text = result.masked_text.replace(original, marker)
                result.detections.append(
                    {
                        "type": pii_type,
                        "level": "HIGH",
                        "start": match.start(),
                        "end": match.end(),
                        "marker": marker,
                    }
                )
                result.pii_types.add(pii_type)
                result.has_pii = True

        # Medium-sensitivity: replace with pseudonym
        name_counter = {}
        for pii_type, pattern in self._med_patterns.items():
            for match in pattern.finditer(text):
                original = match.group()
                idx = name_counter.get(original, len(name_counter))
                name_counter[original] = idx
                pseudonym = f"[{pii_type.upper()}_{idx}]"
                result.masked_text = result.masked_text.replace(original, pseudonym)
                result.detections.append(
                    {
                        "type": pii_type,
                        "level": "MEDIUM",
                        "start": match.start(),
                        "end": match.end(),
                        "pseudonym": pseudonym,
                        "index": idx,
                    }
                )
                result.pii_types.add(pii_type)
                result.has_pii = True

        return result

    def check_leakage(self, text: str) -> bool:
        """Check if any PII appears in raw form. Returns True if leaked."""
        for pattern in self._high_patterns.values():
            if pattern.search(text):
                return True
        return False

    def field_classification(self, field_name: str) -> str:
        """
        Classify a field into sensitivity tier.

        Returns: 'HIGH', 'MEDIUM', or 'LOW'
        """
        high_keywords = ["身份证", "id_card", "bank_card", "银行卡", "手机", "phone"]
        med_keywords = ["姓名", "name", "地址", "address"]

        fn = field_name.lower()
        if any(kw in fn for kw in high_keywords):
            return "HIGH"
        if any(kw in fn for kw in med_keywords):
            return "MEDIUM"
        return "LOW"


# ─── Deterministic Rule Checks ────────────────────────────────────────────────

class RuleEngine:
    """
    Deterministic checks that run locally.
    Used by RULE-mode nodes and HYBRID node verification.
    """

    # ── S3: Urgency Assessment ───────────────────────────────────────────
    @staticmethod
    def check_urgency(latest_transaction: Dict) -> Dict[str, Any]:
        """
        Check if the case requires immediate action (e-stop payment).
        Rules: amount > 50000 AND within last 2 hours → URGENT
        """
        amount = float(latest_transaction.get("amount", 0))
        minutes_ago = float(latest_transaction.get("minutes_ago", 999))

        is_urgent = amount > 50000 and minutes_ago < 120

        return {
            "is_urgent": is_urgent,
            "risk_level": "HIGH" if is_urgent else "LOW",
            "reason": (
                f"Amount ¥{amount:,.0f}, {minutes_ago:.0f}min ago"
                if is_urgent
                else "Does not meet urgency threshold"
            ),
        }

    # ── S5: Transaction Parsing ──────────────────────────────────────────
    @staticmethod
    def parse_transactions(raw_txns: List[Dict]) -> List[Dict]:
        """Standardize transaction records."""
        parsed = []
        for tx in raw_txns:
            parsed.append(
                {
                    "time": tx.get("time", ""),
                    "amount": float(tx.get("amount", 0)),
                    "direction": tx.get("direction", "unknown"),
                    "counterparty_type": tx.get("counterparty_type", "unknown"),
                    "channel": tx.get("channel", "unknown"),
                }
            )
        return parsed

    # ── S7: Call Record Parsing ──────────────────────────────────────────
    @staticmethod
    def parse_calls(raw_calls: List[Dict]) -> List[Dict]:
        """Standardize call records."""
        parsed = []
        for call in raw_calls:
            parsed.append(
                {
                    "time": call.get("time", ""),
                    "duration_seconds": int(call.get("duration", 0)),
                    "direction": call.get("direction", "incoming"),
                }
            )
        return parsed

    # ── S8: Full PII Scan ────────────────────────────────────────────────
    @staticmethod
    def full_pii_scan(data: Dict, pii_filter: PIIFilter) -> Dict[str, Any]:
        """Scan all text fields for PII and return classification map."""
        pii_map = {}
        for key, value in data.items():
            if isinstance(value, str):
                result = pii_filter.scan(value)
                if result.has_pii:
                    pii_map[key] = {
                        "pii_types": list(result.pii_types),
                        "masked_version": result.masked_text,
                    }

        return {
            "total_pii_fields": len(pii_map),
            "pii_map": pii_map,
        }

    # ── S10: Entity Extraction Verification ──────────────────────────────
    @staticmethod
    def verify_entities(extracted: List[Dict]) -> Dict[str, List[str]]:
        """
        Verify extracted entities against domain rules.
        Returns list of issues found.
        """
        issues = []

        valid_entity_types = {
            "suspect", "victim", "account", "app", "phone", "bank", "platform"
        }

        for entity in extracted:
            etype = entity.get("type", "")
            if etype not in valid_entity_types:
                issues.append(f"Invalid entity type: {etype}")

            # Account numbers should match patterns
            if etype == "account" and "value" in entity:
                val = entity["value"]
                if not re.match(r"^(?:\[\w+\]|\d{4,})$", str(val)):
                    issues.append(f"Suspicious account value: {val}")

        return {"issues": issues, "is_valid": len(issues) == 0}

    # ── S14: Multi-Dimensional Quality Check ────────────────────────────
    @staticmethod
    def quality_check(case_output: Dict) -> Dict[str, Any]:
        """
        Check case analysis quality across multiple dimensions.

        Checks:
        1. Fraud type consistency: type matches supporting evidence
        2. Entity completeness: key entity types present
        3. Fund flow logic: total outflow ≈ total inflow within tolerance
        4. Timeline consistency: events are chronologically ordered
        5. Evidence coverage: all four phases (引流/通联/网络/交易) covered
        6. Format correctness: output schema matches expected format
        7. Absence of contradictions: no conflicting statements
        8. Annotation completeness: required fields populated
        """
        result = {
            "checks": [],
            "total_checks": 8,
            "passed": 0,
            "issues": [],
        }

        # Check 1: Fraud type consistency
        fraud_type = case_output.get("fraud_type", "")
        supporting = case_output.get("supporting_evidence", {})
        investment_keywords = ["投资", "理财", "股票", "基金", "收益", "回报"]
        if "investment" in fraud_type.lower() or "投资" in fraud_type:
            evidence_text = str(supporting).lower()
            has_investment_evidence = any(
                kw in evidence_text for kw in investment_keywords
            )
            result["checks"].append(
                {
                    "id": "fraud_type_consistency",
                    "passed": has_investment_evidence,
                }
            )
            if has_investment_evidence:
                result["passed"] += 1
            else:
                result["issues"].append(
                    "Fraud type is 'investment' but no investment-related "
                    "evidence found"
                )
        else:
            result["checks"].append(
                {"id": "fraud_type_consistency", "passed": True}
            )
            result["passed"] += 1

        # Check 2: Entity completeness
        entities = case_output.get("entities", {})
        required_types = {"suspect", "victim"}
        entity_complete = all(
            t in str(entities).lower() for t in required_types
        )
        result["checks"].append(
            {"id": "entity_completeness", "passed": entity_complete}
        )
        if entity_complete:
            result["passed"] += 1
        else:
            result["issues"].append("Missing key entity types")

        # Check 3: Fund flow logic
        fund_flow = case_output.get("fund_flow", {})
        outflow = float(fund_flow.get("total_outflow", 0))
        inflow = float(fund_flow.get("total_inflow", 0))
        flow_consistent = True
        if outflow > 0 and inflow > 0:
            flow_consistent = abs(outflow - inflow) / max(outflow, inflow) < 0.2
        result["checks"].append(
            {"id": "fund_flow_consistency", "passed": flow_consistent}
        )
        if flow_consistent:
            result["passed"] += 1
        else:
            result["issues"].append("Fund flow imbalance")

        # Check 4: Timeline consistency
        timeline = case_output.get("timeline", [])
        times = [item.get("time", "") for item in timeline if item.get("time")]
        timeline_ok = times == sorted(times)
        result["checks"].append(
            {"id": "timeline_consistency", "passed": timeline_ok}
        )
        if timeline_ok:
            result["passed"] += 1
        else:
            result["issues"].append("Timeline not chronological")

        # Check 5: Phase coverage
        required_phases = {"引流", "通联", "网络", "交易"}
        phase_text = str(case_output).lower()
        phases_found = sum(1 for p in required_phases if p in phase_text)
        phase_ok = phases_found >= 3
        result["checks"].append(
            {"id": "phase_coverage", "passed": phase_ok}
        )
        if phase_ok:
            result["passed"] += 1
        else:
            result["issues"].append(f"Only {phases_found}/4 phases covered")

        # Check 6: Output format
        required_fields = ["fraud_type", "timeline", "entities", "fund_flow"]
        format_ok = all(f in case_output for f in required_fields)
        result["checks"].append(
            {"id": "output_format", "passed": format_ok}
        )
        if format_ok:
            result["passed"] += 1
        else:
            missed = [f for f in required_fields if f not in case_output]
            result["issues"].append(f"Missing output fields: {missed}")

        # Check 7: Absence of contradictions
        # Simple check: no negative amounts
        contradictions = False
        for item in timeline:
            if isinstance(item.get("amount"), (int, float)) and item["amount"] < 0:
                contradictions = True
        result["checks"].append(
            {"id": "no_contradictions", "passed": not contradictions}
        )
        if not contradictions:
            result["passed"] += 1
        else:
            result["issues"].append("Negative amounts in timeline")

        # Check 8: Annotation completeness
        filled = sum(
            1 for v in case_output.values()
            if v and v != [] and v != {}
        )
        total = len(case_output)
        annot_ok = filled / max(total, 1) > 0.7
        result["checks"].append(
            {"id": "annotation_completeness", "passed": annot_ok}
        )
        if annot_ok:
            result["passed"] += 1
        else:
            result["issues"].append(
                f"Only {filled}/{total} fields populated"
            )

        return result
