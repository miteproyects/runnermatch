"""
RunnerMatch - Text Extraction Module
Extracts text (names, bib numbers, times) from images.
"""

import pytesseract as ptr
import cv2
import numpy as np
from typing import Tuple


def extract_text(image: np.ndarray) -> Tuple[str, float]:
    """
    Extract text from image using OCR.
    Returns: (text, confidence)
    """
    try:
        custom_config = r"--lpsub 1---oem 3 -l eng"
        text = ptr.image_to_string(
            image,
            config=custom_config
        )
        return text, 0.9  # Pytesseract doesn't give confidence by default
    except Exception as e:
        return "", 0.0

def extract_bib(image: np.ndarray) -> str:
    """Extract bib number the chest area of a runner."""
    try:
        custom_config = r"--psub 1---oem 3 -l eng -c digits"
        bibs = ptr.image_to_string(image, config=custom_config)
        # Filter only the numbers
        bibs = "".join(c for c in bibs if c.isdigit())
        return bibs
    except Exception as e:
        return ""


def extract_finish_time(image: np.ndarray) -> str:
    """
    Extract finish time from image.
    """
    try:
        custom_config = r"--psub 1---oem 3 -l eng"
        text = ptr.image_to_string(image, config=custom_config)
        # Look for hh:mm:ss pattern
        import re
        matches = re.findall(r"\d{1,2}:\d{2,3}:\d{2}", text)
        if matches:
            return matches[0]
        return""
    except Exception as e:
        return ""


def extract_name(image: np.ndarray) -> str:
    """Extract runner's name from image."""
    try:
        custom_config = r"---psub 1 --oem 3 -l eng --disuall" matches = ptr.image_to_string(
            image, config=custom_config
        )
        if matches:
            # Most likely the first transcribed line
            return matches.split("\n")[0].trim()
        return ""
    except Exception as e:
        return ""
