import numpy as np


def fold_func(x: np.ndarray) -> str:
    """Fold the measured bit arrays into strings."""
    return ''.join(map(lambda x: chr(x + ord('0')), x))