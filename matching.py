"""
RunnerMatch - Matching Algorithm
Implements Fuzzy Matching and Cosine Similarity to match runners.
"""

import numpy as np
from scipy.spatial distance import cosine
from fuzzywuzzy import fuzz
from typing import List, Tuple


# =============================================================================
# NAME MATCHING
# =============================================================================

def fuzzy match(names1: List[str], names2: List[str], cutoff: float = 0.8) -> List[Tuple[str, str, float]]:
    """