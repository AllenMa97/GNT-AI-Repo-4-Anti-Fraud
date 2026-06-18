#!/usr/bin/env python3
"""
SOP-DAG Experiment Runner
─────────────────────────
Runs all four methods (A/B/C/D) on synthetic benchmark cases and reports metrics.

Usage:
    python -m experiment.run_experiments [--all] [--case N] [--method D]
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from experiment.config import get_default_config, get_api_config
from experiment.data_synthetic import SYNTHETIC_CASES
from experiment.sop_dag import build_telecom_fraud_sop_dag, SOPDAGExecutor
from experiment.baselines import BaselineMethods
from experiment.metrics import (
    compute_fraud_type_accuracy,
    compute_entity_f1,
    compute_fund_flow_completeness,
    compute_timeline_coverage,
    compute_quality_check_f1,
    compute_exposure_score,
    aggregate_metrics,
)
from experiment.rule_engine import PIIFilter
from experiment.config import get_pii_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Constants ───────────────────────────────────────────────────────────────

MODEL = os.environ.get("SOPDAG_MODEL", "deepseek-v4-flash")
CRITICAL_MODEL = os.environ.get("SOPDAG_CRITICAL_MODEL", "deepseek-v4-pro")
RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_ground_truth(case: dict) -> dict:
    """Extract ground truth labels from a synthetic case."""
    return {
        "fraud_type": case.get("ground_truth", {}).get("fraud_type", ""),
        "entities": case.get("ground_truth", {}).get("entities", []),
        "fund_flow": case.get("ground_truth", {}).get("fund_flow", {}),
        "timeline_phases": case.get("ground_truth", {}).get("timeline_phases", []),
        "quality_issues": case.get("ground_truth", {}).get("quality_issues", []),
    }


def evaluate_method_d(outputs: dict, ground_truth: dict) -> dict:
    """Evaluate SOP-DAG (Method D) outputs against ground truth."""
    s9 = outputs.get("S9", {})
    s10 = outputs.get("S10", {})
    s11 = outputs.get("S11", {})
    s12 = outputs.get("S12", {})
    s14 = outputs.get("S14", {})

    type_acc, _ = compute_fraud_type_accuracy(
        s9.get("fraud_type", ""), ground_truth["fraud_type"]
    )

    entity_metrics = compute_entity_f1(
        s10.get("entities", []), ground_truth["entities"]
    )

    flow_comp = compute_fund_flow_completeness(
        s11, ground_truth["fund_flow"]
    )

    timeline_cov = compute_timeline_coverage(
        s12.get("timeline", []), ground_truth["timeline_phases"]
    )

    quality_verification = s14.get("rule_verification", {})
    quality_passed = quality_verification.get("passed", 0)
    quality_total = quality_verification.get("total_checks", 8)
    quality_score = quality_passed / max(quality_total, 1)

    return {
        "fraud_type_accuracy": round(type_acc, 4),
        "entity_precision": entity_metrics["precision"],
        "entity_recall": entity_metrics["recall"],
        "entity_f1": entity_metrics["f1"],
        "fund_flow_completeness": flow_comp,
        "timeline_coverage": timeline_cov,
        "quality_score": round(quality_score, 4),
    }


def evaluate_method_ab(output: dict, ground_truth: dict) -> dict:
    """Evaluate Method A/B (single LLM call) outputs."""
    type_acc, _ = compute_fraud_type_accuracy(
        output.get("fraud_type", ""), ground_truth["fraud_type"]
    )
    entity_f1 = compute_entity_f1(
        output.get("entities", []), ground_truth["entities"]
    )
    flow_comp = compute_fund_flow_completeness(
        output.get("fund_flow", {}), ground_truth["fund_flow"]
    )
    timeline_cov = compute_timeline_coverage(
        output.get("timeline", []), ground_truth["timeline_phases"]
    )

    issues = output.get("quality_issues", [])
    gt_issues = ground_truth["quality_issues"]
    quality_f1 = compute_quality_check_f1(issues, gt_issues)

    return {
        "fraud_type_accuracy": round(type_acc, 4),
        "entity_precision": entity_f1["precision"],
        "entity_recall": entity_f1["recall"],
        "entity_f1": entity_f1["f1"],
        "fund_flow_completeness": flow_comp,
        "timeline_coverage": timeline_cov,
        "quality_f1": quality_f1["f1"],
    }


def evaluate_method_c(output: dict, ground_truth: dict) -> dict:
    """Evaluate Method C (rule-only) outputs."""
    # Rule-only can't determine fraud type
    flow_comp = compute_fund_flow_completeness(
        output.get("fund_flow", {}), ground_truth["fund_flow"]
    )

    return {
        "fraud_type_accuracy": 0.0,  # Rule-only can't classify
        "entity_f1": 0.0,  # No entity extraction
        "fund_flow_completeness": flow_comp,
        "timeline_coverage": 0.0,  # No timeline reconstruction
        "quality_f1": 0.0,
    }


# ─── Main Experiment ─────────────────────────────────────────────────────────

def run_single_case(
    case_idx: int,
    case_data: dict,
    methods: List[str],
) -> Dict[str, Any]:
    """Run all specified methods on a single case."""
    logger.info(f"{'='*60}")
    logger.info(f"Case #{case_idx}: {case_data.get('case_name', 'Unknown')}")
    logger.info(f"{'='*60}")

    ground_truth = get_ground_truth(case_data)
    baselines = BaselineMethods()
    pii_filter = PIIFilter(get_pii_config())

    results = {
        "case_id": case_idx,
        "case_name": case_data.get("case_name", ""),
        "ground_truth_fraud_type": ground_truth["fraud_type"],
        "methods": {},
    }

    # ── Method A: Oracle (full raw data) ─────────────────────────────────
    if "A" in methods:
        logger.info("  Running Method A (Oracle)...")
        t0 = time.time()
        output_a = baselines.method_a_oracle(case_data["raw_data"], MODEL)
        t_a = time.time() - t0
        metrics_a = evaluate_method_ab(output_a, ground_truth)
        metrics_a["latency_seconds"] = round(t_a, 2)
        metrics_a["api_calls"] = 1
        metrics_a["information_exposure"] = 1.0  # Full exposure
        results["methods"]["A_oracle"] = {
            "output": output_a,
            "metrics": metrics_a,
        }
        logger.info(f"    A result: type_acc={metrics_a['fraud_type_accuracy']:.2f}")

    # ── Method B: Industry (full masked data) ────────────────────────────
    if "B" in methods:
        logger.info("  Running Method B (Industry)...")
        t0 = time.time()
        masked = _mask_full_data(case_data["raw_data"], pii_filter)
        output_b = baselines.method_b_industry(
            case_data["raw_data"], masked, MODEL
        )
        t_b = time.time() - t0
        metrics_b = evaluate_method_ab(output_b, ground_truth)
        metrics_b["latency_seconds"] = round(t_b, 2)
        metrics_b["api_calls"] = 1
        metrics_b["information_exposure"] = 0.6  # Masked but all fields
        results["methods"]["B_industry"] = {
            "output": output_b,
            "metrics": metrics_b,
        }
        logger.info(f"    B result: type_acc={metrics_b['fraud_type_accuracy']:.2f}")

    # ── Method C: Rule-only ─────────────────────────────────────────────
    if "C" in methods:
        logger.info("  Running Method C (Rule-only)...")
        t0 = time.time()
        output_c = baselines.method_c_rule_only(case_data["raw_data"])
        t_c = time.time() - t0
        metrics_c = evaluate_method_c(output_c, ground_truth)
        metrics_c["latency_seconds"] = round(t_c, 2)
        metrics_c["api_calls"] = 0
        metrics_c["information_exposure"] = 0.0  # Zero exposure
        results["methods"]["C_rule_only"] = {
            "output": output_c,
            "metrics": metrics_c,
        }
        logger.info(f"    C result: flow_comp={metrics_c['fund_flow_completeness']:.2f}")

    # ── Method D: SOP-DAG ───────────────────────────────────────────────
    if "D" in methods:
        logger.info("  Running Method D (SOP-DAG)...")
        dag = build_telecom_fraud_sop_dag()
        executor = SOPDAGExecutor()
        executor.load_dag(dag)

        t0 = time.time()
        outputs_d = executor.execute(
            case_data["raw_data"], model=MODEL, critical_model=CRITICAL_MODEL
        )
        t_d = time.time() - t0

        metrics_d = evaluate_method_d(outputs_d, ground_truth)
        metrics_d["latency_seconds"] = round(t_d, 2)
        metrics_d["api_calls"] = executor.llm_client.total_calls
        metrics_d["total_tokens"] = executor.llm_client.total_tokens
        metrics_d["information_exposure"] = round(
            executor.get_exposure_measure(), 4
        )
        metrics_d["privacy_leakage"] = executor.get_privacy_leakage(outputs_d)

        results["methods"]["D_sop_dag"] = {
            "outputs": {
                k: v for k, v in outputs_d.items()
                if k in {"S9", "S10", "S11", "S12", "S14", "S15"}
            },
            "metrics": metrics_d,
        }
        logger.info(
            f"    D result: type_acc={metrics_d['fraud_type_accuracy']:.2f}, "
            f"entity_f1={metrics_d.get('entity_f1', 0):.2f}"
        )

    return results


def _mask_full_data(raw_data: dict, pii_filter: PIIFilter) -> dict:
    """Mask all PII in the raw data (for Method B)."""
    masked = {}
    for key, value in raw_data.items():
        if isinstance(value, str):
            scan = pii_filter.scan(value)
            masked[key] = scan.masked_text
        elif isinstance(value, list):
            masked[key] = [
                pii_filter.scan(item).masked_text
                if isinstance(item, str)
                else item
                for item in value
            ]
        elif isinstance(value, dict):
            masked[key] = _mask_full_data(value, pii_filter)
        else:
            masked[key] = value
    return masked


def print_comparison(all_results: List[Dict]):
    """Print comparison table across all methods."""
    print("\n" + "=" * 80)
    print("  COMPARISON: SOP-DAG vs Baselines")
    print("=" * 80)

    method_names = {
        "A_oracle": "A (Oracle/Illegal)",
        "B_industry": "B (Industry/Masked)",
        "C_rule_only": "C (Rule-Only)",
        "D_sop_dag": "D (SOP-DAG/Ours)",
    }

    metric_keys = [
        ("fraud_type_accuracy", "Fraud Type Acc"),
        ("entity_f1", "Entity F1"),
        ("fund_flow_completeness", "Fund Flow Comp"),
        ("timeline_coverage", "Timeline Cov"),
        ("information_exposure", "Info Exposure"),
    ]

    print(f"\n{'Metric':<25}", end="")
    for mkey in method_names.values():
        print(f"{mkey:<25}", end="")
    print()

    print("-" * 125)

    for mkey, mlabel in metric_keys:
        print(f"{mlabel:<25}", end="")
        for method_id, _ in method_names.items():
            values = []
            for r in all_results:
                mdata = r.get("methods", {}).get(method_id, {})
                metrics = mdata.get("metrics", {})
                if mkey == "information_exposure":
                    # For info exposure, lower is better (except for rule-only)
                    values.append(metrics.get(mkey, 1.0))
                else:
                    values.append(metrics.get(mkey, 0.0))

            avg = sum(values) / max(len(values), 1)
            print(f"{avg:<25.4f}", end="")
        print()

    print("=" * 80)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SOP-DAG Experiments")
    parser.add_argument(
        "--all", action="store_true", help="Run all 10 cases"
    )
    parser.add_argument(
        "--case", type=int, default=0, help="Run specific case (0-9)"
    )
    parser.add_argument(
        "--method",
        type=str,
        default="D",
        help="Methods to run: A, B, C, D, or ALL (comma-separated)",
    )
    parser.add_argument(
        "--output", type=str, default=None, help="Output JSON file path"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"Model for standard nodes (default: {MODEL})",
    )

    args = parser.parse_args()

    global MODEL
    if args.model:
        MODEL = args.model

    # Select cases
    if args.all:
        case_indices = list(range(len(SYNTHETIC_CASES)))
    else:
        case_indices = [args.case]

    # Select methods
    if args.method.upper() == "ALL":
        methods = ["A", "B", "C", "D"]
    else:
        methods = [m.strip().upper() for m in args.method.split(",")]

    all_results = []

    for idx in case_indices:
        if idx >= len(SYNTHETIC_CASES):
            logger.warning(f"Case {idx} not found (max {len(SYNTHETIC_CASES)-1})")
            continue

        case = SYNTHETIC_CASES[idx]
        result = run_single_case(idx, case, methods)
        all_results.append(result)

        # Save intermediate
        case_file = RESULTS_DIR / f"case_{idx:02d}.json"
        with open(case_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"  Results saved to {case_file}")

    # Aggregate and save
    if len(all_results) > 0:
        agg_file = RESULTS_DIR / "aggregated.json"
        with open(agg_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print_comparison(all_results)
        logger.info(f"Aggregated results saved to {agg_file}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
