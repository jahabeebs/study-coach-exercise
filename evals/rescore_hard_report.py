"""Offline deterministic rescoring for a saved hard-suite report.

This reuses the report's exact model outputs with the current hard cases and
programmatic evaluators. It never invokes the study model or an LLM judge, so
it isolates evaluator changes from generation variance.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pydantic_evals.evaluators import EvaluatorContext  # noqa: E402

from app.models import ChatResponse  # noqa: E402
from hard_dataset import HARD_CASES, build_hard_dataset  # noqa: E402


def rescore_hard_report(source: dict[str, Any]) -> dict[str, Any]:
    """Rescore saved hard outputs under the current deterministic contract."""
    if source.get("dataset") != "study-coach-hard":
        raise ValueError("source report is not a study-coach-hard report")

    definitions = {case.name: case for case in HARD_CASES}
    evaluators = build_hard_dataset(include_judge=False).evaluators
    rescored_cases = []
    passed = total = 0

    for saved_case in source.get("cases", []):
        name = saved_case.get("case")
        definition = definitions.get(name)
        if definition is None:
            raise ValueError(f"unknown hard-suite case: {name!r}")
        output = ChatResponse.model_validate(saved_case.get("output"))
        ctx = EvaluatorContext(
            name=name,
            inputs=definition.inputs,
            metadata=definition.metadata,
            expected_output=None,
            output=output,
            duration=0,
            _span_tree=None,
            attributes={},
            metrics={},
        )
        assertions = {}
        for evaluator in evaluators:
            evaluator_name = type(evaluator).__name__
            verdict = evaluator.evaluate(ctx)
            if not isinstance(verdict, bool):
                raise TypeError(
                    f"{evaluator_name} is not deterministic boolean evaluator"
                )
            assertions[evaluator_name] = {"passed": verdict, "reason": None}
            passed += int(verdict)
            total += 1
        rescored_cases.append(
            {
                "case": name,
                "question": definition.inputs,
                "metadata": definition.metadata,
                "output": output.model_dump(),
                "assertions": assertions,
            }
        )

    return {
        "rescored_from": source.get("run_at"),
        "dataset": "study-coach-hard-offline-rescore",
        "evaluators": [type(evaluator).__name__ for evaluator in evaluators],
        "summary": {
            "cases": len(rescored_cases),
            "assertions_passed": passed,
            "assertions_total": total,
        },
        "cases": rescored_cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Saved hard-suite JSON report")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path; otherwise the rescored artifact prints to stdout.",
    )
    args = parser.parse_args()

    source = json.loads(args.source.read_text())
    rescored = rescore_hard_report(source)
    serialized = json.dumps(rescored, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized)
        print(f"Offline rescore written to {args.output}")
    else:
        print(serialized, end="")
    return 0 if (
        rescored["summary"]["assertions_passed"]
        == rescored["summary"]["assertions_total"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
