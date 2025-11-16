# UI on
# General API's
from dataclasses import dataclass
from typing import Union, List

from chromadb.api.async_api import AsyncCollection


@dataclass
class Document:
    id: str
    text: str
    metadata: dict


