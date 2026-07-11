import logging
import time
import uuid
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from config.constants import TaskType, Tier
from core.graph import graph
from core.state import initial_state

logger = logging.getLogger(__name__)


@dataclass
class EvalCase:
    query: str
    expected_task_type: Optional[TaskType] = None
    expected_tier: Optional[Tier] = None
    budget: float = 1.00


@dataclass
class EvalResult:
    query: str
    task_type_detected: Optional[str]
    tier_selected: Optional[str]
    served_from_cache: bool
    cost_usd: float
    latency_ms: int
    correct_task_type: Optional[bool]
    correct_tier: Optional[bool]
    response_length: int


class EvalHarness:

    def __init__(self, cases: list[EvalCase]):
        self.cases = cases
        self.results: list[EvalResult] = []

    def run(self) -> pd.DataFrame:
        logger.info(f"[Eval] Running {len(self.cases)} cases...")

        for i, case in enumerate(self.cases):
            logger.info(f"[Eval] Case {i+1}/{len(self.cases)}: {case.query[:60]}")

            session_id = str(uuid.uuid4())[:8]
            config = {"configurable": {"thread_id": session_id}}
            state = initial_state(case.query, session_id, case.budget)

            start = time.time()
            try:
                final = graph.invoke(state, config=config)
            except Exception as e:
                logger.error(f"[Eval] Case failed: {e}")
                continue
            elapsed_ms = int((time.time() - start) * 1000)

            result = EvalResult(
                query=case.query,
                task_type_detected=str(final.get("task_type")),
                tier_selected=str(final.get("selected_tier")),
                served_from_cache=final.get("served_from_cache", False),
                cost_usd=final.get("cost_usd", 0.0) or 0.0,
                latency_ms=final.get("latency_ms", elapsed_ms) or elapsed_ms,
                correct_task_type=(
                    str(final.get("task_type")) == str(case.expected_task_type)
                    if case.expected_task_type
                    else None
                ),
                correct_tier=(
                    str(final.get("selected_tier")) == str(case.expected_tier)
                    if case.expected_tier
                    else None
                ),
                response_length=len(final.get("final_response", "") or ""),
            )
            self.results.append(result)

        return self._to_dataframe()

    def _to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([r.__dict__ for r in self.results])

    def print_summary(self, df: pd.DataFrame):
        print("\n" + "=" * 60)
        print("TieredFlow Eval Summary")
        print("=" * 60)
        print(f"Total cases:        {len(df)}")
        print(f"Cache hit rate:     {df['served_from_cache'].mean():.1%}")
        print(f"Avg cost/query:     ${df['cost_usd'].mean():.6f}")
        print(f"Total cost:         ${df['cost_usd'].sum():.6f}")
        print(f"Avg latency:        {df['latency_ms'].mean():.0f}ms")
        print("\nTier distribution:")
        print(df["tier_selected"].value_counts().to_string())
        if df["correct_task_type"].notna().any():
            print(f"\nTask type accuracy: {df['correct_task_type'].mean():.1%}")
        if df["correct_tier"].notna().any():
            print(f"Tier accuracy:      {df['correct_tier'].mean():.1%}")
        print("=" * 60 + "\n")


EVAL_CASES = [
    EvalCase(
        "Classify this email as spam or not spam.",
        TaskType.CLASSIFICATION,
        Tier.ULTRA_CHEAP,
    ),
    EvalCase(
        "Extract all dates mentioned in this text.",
        TaskType.EXTRACTION,
        Tier.ULTRA_CHEAP,
    ),
    EvalCase(
        "Summarize the key points of this article.", TaskType.SUMMARIZATION, Tier.MID
    ),
    EvalCase("What is the capital of France?", TaskType.QA, Tier.MID),
    EvalCase(
        "Write a Python function to reverse a string.",
        TaskType.CODE_GENERATION,
        Tier.QUALITY,
    ),
    EvalCase(
        "Explain why inflation affects interest rates.", TaskType.REASONING, Tier.POWER
    ),
    EvalCase(
        "Classify this review as positive or negative.",
        TaskType.CLASSIFICATION,
        Tier.ULTRA_CHEAP,
    ),
    EvalCase("Summarize what neural networks are.", TaskType.SUMMARIZATION, Tier.MID),
    EvalCase(
        "Classify this email as spam or not spam.",
        TaskType.CLASSIFICATION,
        Tier.ULTRA_CHEAP,
    ),
]


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
    )
    harness = EvalHarness(EVAL_CASES)
    df = harness.run()
    harness.print_summary(df)
    df.to_csv("eval/results/eval_results.csv", index=False)
    print("Results saved to eval/results/eval_results.csv")
