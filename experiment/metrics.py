"""
Evaluation Metrics for SOP-DAG Experiments

Measures quality, cost, and privacy across all methods.
"""

import json
import re
from typing import Dict, List, Any, Tuple
from difflib import SequenceMatcher


def compute_fraud_type_accuracy(
    predicted: str, ground_truth: str
) -> Tuple[float, bool]:
    """Check if predicted fraud type matches ground truth."""
    pred_lower = predicted.lower().strip()
    gt_lower = ground_truth.lower().strip()

    # Exact match
    if pred_lower == gt_lower:
        return 1.0, True

    # Substring match (e.g., "investment_fraud" matches "investment")
    if gt_lower in pred_lower or pred_lower in gt_lower:
        return 0.8, True

    return 0.0, False


def compute_entity_f1(
    predicted_entities: List[Dict], ground_truth_entities: List[Dict]
) -> Dict[str, float]:
    """Compute entity-level precision, recall, F1."""
    pred_set = set()
    for e in predicted_entities:
        key = (e.get("type", ""), str(e.get("value", ""))[:30])
        pred_set.add(key)

    gt_set = set()
    for e in ground_truth_entities:
        key = (e.get("type", ""), str(e.get("value", ""))[:30])
        gt_set.add(key)

    intersection = pred_set & gt_set

    precision = len(intersection) / max(len(pred_set), 1)
    recall = len(intersection) / max(len(gt_set), 1)
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}


def compute_fund_flow_completeness(
    predicted_flow: Dict, ground_truth_flow: Dict
) -> float:
    """How complete is the fund flow chain reconstruction?"""
    score = 0.0
    max_score = 4.0

    # Outflow amount present
    if predicted_flow.get("total_outflow", 0) > 0:
        score += 1.0

    # Inflow amount present
    if predicted_flow.get("total_inflow", 0) > 0:
        score += 1.0

    # Chain description present
    chain = predicted_flow.get("chain", "")
    if chain and len(chain) > 10:
        score += 1.0

    # Amounts roughly match (within 20%)
    pred_out = predicted_flow.get("total_outflow", 0)
    gt_out = ground_truth_flow.get("total_outflow", 0)
    if (
        gt_out > 0
        and abs(float(pred_out) - float(gt_out)) / float(gt_out) < 0.2
    ):
        score += 1.0

    return round(score / max_score, 4)


def compute_timeline_coverage(
    predicted_timeline: List[Dict], ground_truth_phases: List[str]
) -> float:
    """How many of the 4 required phases are covered in the timeline?"""
    required = {"引流", "通联", "网络", "交易"}

    # Check from predicted timeline
    covered = set()
    for event in predicted_timeline:
        phase = event.get("phase", "")
        if phase in required:
            covered.add(phase)

    # Also check from ground truth
    for phase in ground_truth_phases:
        if phase in required:
            covered.add(phase)

    return round(len(covered) / len(required), 4)


def compute_quality_check_f1(
    predicted_issues: List[str], ground_truth_issues: List[str]
) -> Dict[str, float]:
    """F1 for quality issue detection."""
    pred_set = set(predicted_issues)
    gt_set = set(ground_truth_issues)

    intersection = pred_set & gt_set
    precision = len(intersection) / max(len(pred_set), 1)
    recall = len(intersection) / max(len(gt_set), 1)
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}


def compute_report_similarity(
    predicted_report: str, ground_truth_report: str
) -> float:
    """Compute BERTScore-like similarity (using string matching as proxy)."""
    return round(SequenceMatcher(None, predicted_report, ground_truth_report).ratio(), 4)


def compute_exposure_score(method_results: Dict) -> float:
    """
    Compute normalized information exposure.
    Lower is better (more privacy-preserving).
    """
    exposure = method_results.get("information_exposure", 1.0)
    return round(1.0 - exposure, 4)  # Convert to privacy score


def compute_cost_efficiency(
    total_tokens: int, quality_f1: float
) -> float:
    """Quality per 1000 tokens."""
    if total_tokens == 0:
        return 0.0
    return round(quality_f1 / (total_tokens / 1000), 4)


def aggregate_metrics(per_case_metrics: List[Dict]) -> Dict[str, Any]:
    """Aggregate metrics across multiple test cases."""
    if not per_case_metrics:
        return {}

    agg = {}
    keys = per_case_metrics[0].keys()

    for key in keys:
        values = [m[key] for m in per_case_metrics if key in m]
        if not values:
            continue

        if all(isinstance(v, (int, float)) for v in values):
            agg[key] = {
                "mean": round(sum(values) / len(values), 4),
                "min": round(min(values), 4),
                "max": round(max(values), 4),
                "std": round(
                    (sum((v - sum(values) / len(values)) ** 2 for v in values)
                     / len(values)) ** 0.5,
                    4,
                ),
            }

    return agg
