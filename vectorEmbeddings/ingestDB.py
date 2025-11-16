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


async def insert_documents(
        docs: Union[Document, List[Document]],
        collection: AsyncCollection
):
    """
    Insert a single Document or a list of Document objects into Chroma.
    """
    # Normalize for single document
    if isinstance(docs, Document):
        docs = [docs]

    # Prepare lists for Chroma
    ids = [doc.id for doc in docs]
    texts = [doc.text for doc in docs]
    metadatas = [doc.metadata for doc in docs]

    await collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )

    return {"inserted": len(docs)}
