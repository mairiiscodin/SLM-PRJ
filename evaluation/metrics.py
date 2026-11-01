"""Evaluation metrics with explicit denominators and no truncated EX comparisons."""
from collections import Counter
from itertools import islice, product
import json
import statistics

from core.result_normalizer import normalize_value, requires_order


def _column_permutation_match(predicted: list, gold: list, ordered: bool) -> bool:
    """Spider test-suite result_eq: same rows (as a multiset unless ordered) up to a column permutation."""
    if len(predicted) != len(gold):
        return False
    if not gold:
        return True
    width = len(gold[0])
    if len(predicted[0]) != width:
        return False
    canon = [[json.dumps(normalize_value(v)) for v in row] for row in predicted]
    target = [[json.dumps(normalize_value(v)) for v in row] for row in gold]
    expected = target if ordered else Counter(map(tuple, target))
    # Only columns holding the same set of values can line up, which keeps the search tiny.
    options = [[j for j in range(width) if {r[j] for r in canon} == {r[i] for r in target}] for i in range(width)]
    for permutation in islice(product(*options), 10000):
        if len(set(permutation)) != width:
            continue
        rows = [tuple(row[j] for j in permutation) for row in canon]
        if (rows == [tuple(r) for r in expected]) if ordered else Counter(rows) == expected:
            return True
    return False


def execution_match(prediction, gold, gold_sql: str, mode: str = "strict") -> bool:
    """strict: multiset, ordered when gold sorts/limits. set: CSC-SQL's set(pred) == set(gold).
    spider: Spider test-suite matching (column order free, ordered only when gold has ORDER BY);
    needs untruncated rows, so it is false whenever either side was cut to the preview size."""
    if not prediction or not prediction.success or not gold.success:
        return False
    if mode == "set":
        return prediction.set_result == gold.set_result
    if mode == "spider":
        if prediction.truncated or gold.truncated:
            return False
        return _column_permutation_match(prediction.rows, gold.rows, "order by" in gold_sql.lower())
    if requires_order(gold_sql):
        return prediction.ordered_result == gold.ordered_result
    return prediction.unordered_result == gold.unordered_result


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * p
    lo = int(index)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (index - lo)


def summarize(records: list[dict]) -> dict:
    count = len(records)
    latency = [record["elapsed_ms"] for record in records]
    candidates = sum(record["candidate_count"] for record in records)
    attempts = sum(record["correction_attempts"] for record in records)
    return {
        "questions": count,
        "execution_accuracy": sum(r["correct"] for r in records) / count if count else 0,
        "exact_match": sum(r["exact_match"] for r in records) / count if count else 0,
        "valid_sql_rate": sum(r["valid_count"] for r in records) / candidates if candidates else 0,
        "average_candidates": candidates / count if count else 0,
        "average_latency_ms": statistics.mean(latency) if latency else 0,
        "p50_latency_ms": percentile(latency, 0.5),
        "p95_latency_ms": percentile(latency, 0.95),
        "early_stop_rate": sum(r["early_stop"] for r in records) / count if count else 0,
        "correction_attempts": attempts,
        "correction_success_rate": sum(r["correction_successes"] for r in records) / attempts if attempts else 0,
        "average_total_generations": (candidates + attempts) / count if count else 0,
        "error_breakdown": dict(Counter(r["error_type"] for r in records if r["error_type"])),
    }
