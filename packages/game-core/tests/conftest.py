"""Make the module's own source tree importable without installation."""

import sys
from pathlib import Path

MODULE_SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"

if str(MODULE_SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_SOURCE_ROOT))
