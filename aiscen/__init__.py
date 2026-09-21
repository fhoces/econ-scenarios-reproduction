"""An independent reimplementation of the model in

    Korinek, Anton, Charles I. Jones, Szymon Sacher, Tess Cotter and Peter McCrory
    (2026), "Economic Scenarios for Transformative AI", The Anthropic Institute
    Working Paper No. 2026-02, September 2026.

No replication package was published with the paper; every equation here is
transcribed from the paper itself (Proposition 1, p. 15; Table A.1, pp. 42-43;
Tables 1 and A.2, pp. 23-25 and 43-45) and the implementation is validated
against the paper's own published numbers (see tests/).
"""

from .params import Fixed, Scenario, SCENARIOS, MODEST, SUBSTANTIAL, EXTREME  # noqa: F401
from .paths import Paths  # noqa: F401
from . import steady, statics, simulate, report  # noqa: F401

__all__ = [
    "Fixed", "Scenario", "SCENARIOS", "MODEST", "SUBSTANTIAL", "EXTREME",
    "Paths", "steady", "statics", "simulate", "report",
]
