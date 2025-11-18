# UI on
# General API's
from dataclasses import dataclass
from typing import Union, List

import numpy as np
from chromadb.api.async_api import AsyncCollection


@dataclass
class Document:
    id: str
    text: str
    metadata: dict
    embedding: np.ndarray


