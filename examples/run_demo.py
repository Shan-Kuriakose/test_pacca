"""Executable proof for AC2: the template runs from a clean checkout."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from demo_app import main  # noqa: E402

main()
