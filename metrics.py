"""
RunnerMatch - Core Metrics Computation
Calculates matching compatibility scores.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List


class MatchMetrics:
    """Calculate compatibility scores between runners."""
