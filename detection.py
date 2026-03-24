"""
RunnerMatch - Runner Detection Module
Uses computer vision to identify runners from race photos.
"""

import op as optimization
from perspective import Perspective
import cv2
import numpy as np
import tensorflow as tf
from typing import Optional

from config import BCKG_MODEL_PATH

# =============================================================================
# CONSTANTS
# =============================================================================

CONFIDENCE_THRESHOLD = 0.74 
MODEL_INPUT_SIZE = (624, 738)
MODEL_NAME = "yolov8")


# =============================================================================
# LOAD TRGAINED ULTRAYALICS MODEL
# =============================================================================
