"""Runtime configuration.

The model is resolved lazily (at request time, not import time) so the app and
its tests can be imported without any API key present.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# .env lives at the assessment root, one level above backend/
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DEFAULT_MODEL = "anthropic:claude-sonnet-4-6"


def get_model_name() -> str:
    """Model identifier for the study agent and the eval judge.

    The assessment is calibrated on the default model; see the README before
    changing it.
    """
    return os.environ.get("STUDY_COACH_MODEL", DEFAULT_MODEL)
