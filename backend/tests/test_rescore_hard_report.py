import json
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parents[2] / "evals"
sys.path.insert(0, str(EVALS_DIR))

from rescore_hard_report import rescore_hard_report  # noqa: E402


def test_offline_rescore_reuses_baseline_outputs_with_current_evaluators():
    report_path = (
        EVALS_DIR
        / "reports"
        / "eval-report-study-coach-hard-2026-08-10T175142Z.json"
    )
    rescored = rescore_hard_report(json.loads(report_path.read_text()))

    assert rescored["rescored_from"] == "2026-08-10T17:51:42+00:00"
    assert rescored["summary"] == {
        "cases": 12,
        "assertions_passed": 36,
        "assertions_total": 36,
    }
    assert rescored["evaluators"] == [
        "CitationsGrounded",
        "ExpectedSectionCited",
        "AnswerMentionsFact",
    ]
