# UI on
# General API's
from dataclasses import dataclass

import numpy as np


@dataclass
class Document:
    id: str
    text: str
    metadata: dict
    embedding: np.ndarray


