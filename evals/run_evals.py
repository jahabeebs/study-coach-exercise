"""Run the Study Coach evals and write a report artifact.

Usage (from assessment/):
    make evals            # or: cd backend && uv run python ../evals/run_evals.py

Requires ANTHROPIC_API_KEY. Every run writes a JSON report to evals/reports/;
COMMIT THESE FILES — reviewers read them, and they are your evidence.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.agent import ask  # noqa: E402
from app.config import get_model_name  # noqa: E402
from app.models import ChatResponse  # noqa: E402
from dataset import build_dataset  # noqa: E402

REPORTS_DIR = Path(__file__).resolve().parent / "reports"


async def study_task(question: str) -> ChatResponse:
    return await ask(question)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite",
        choices=["core", "hard"],
        default="core",
        help="core = the main Q&A evals; hard = the senior-track hard set.",
    )
    parser.add_argument(
        "--no-judge",
        action="store_true",
        help="Skip the LLM-judge evaluator (faster, cheaper, deterministic only).",
    )
    args = parser.parse_args()

    if args.suite == "hard":
        from hard_dataset import build_hard_dataset

        dataset = build_hard_dataset()
    else:
        dataset = build_dataset(include_judge=not args.no_judge)
    report = dataset.evaluate_sync(study_task)
    report.print(include_input=True, include_output=False)

    cases = []
    total_assertions = passed_assertions = 0
    for case in report.cases:
        assertions = {
            name: {"passed": bool(r.value), "reason": r.reason}
            for name, r in case.assertions.items()
        }
        total_assertions += len(assertions)
        passed_assertions += sum(1 for a in assertions.values() if a["passed"])
        cases.append(
            {
                "case": case.name,
                "question": case.inputs,
                "metadata": case.metadata,
                # Full task output so reviewers can re-score offline with their
                # own evaluators (no API key, no candidate code) — see
                # review/rescore.py.
                "output": case.output.model_dump(),
                "assertions": assertions,
                "scores": {name: r.value for name, r in case.scores.items()},
            }
        )

    artifact = {
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": get_model_name(),
        "dataset": dataset.name,
        "summary": {
            "cases": len(cases),
            "assertions_passed": passed_assertions,
            "assertions_total": total_assertions,
        },
        "cases": cases,
    }

    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = artifact["run_at"].replace(":", "").replace("+0000", "Z")
    out_path = REPORTS_DIR / f"eval-report-{dataset.name}-{stamp}.json"
    out_path.write_text(json.dumps(artifact, indent=2) + "\n")

    print(f"\nAssertions: {passed_assertions}/{total_assertions} passed")
    print(f"Report written to {out_path.relative_to(Path.cwd().resolve())}"
          if out_path.is_relative_to(Path.cwd().resolve())
          else f"Report written to {out_path}")
    return 0 if passed_assertions == total_assertions else 1


if __name__ == "__main__":
    raise SystemExit(main())
