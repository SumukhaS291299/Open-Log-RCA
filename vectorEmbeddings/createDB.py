import asyncio
import configparser

from vectorEmbeddings import RCAChromaPersistent, RCAChromaHttp
from utils import Readconfig, setup_logger


class CreateVectorDB:

    def __init__(self, config: configparser.ConfigParser):
        self.collections = None
        self.config = config
        self.client = None

# TODO Add AsyncChroma in HTTP DB option
class CreateHttpDB(CreateVectorDB):

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)

    def create_client(self):
        self.client = RCAChromaHttp(self.config).get_client()

    def get_collection(self, name: str):
        self.collections = self.client.get_or_create_collection(name)


class CreatePersistentDB(CreateVectorDB):

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)

    def create_client(self):
        self.client = RCAChromaPersistent(self.config).get_client()

    def get_collection(self, name: str):
        self.collections = self.client.get_or_create_collection(name)


def __testPersistentDB():
    config = Readconfig().read()

    chroma_client = CreatePersistentDB(config)

    chroma_client.create_client()

    chroma_client.get_collection("test_collection")
    chroma_client.collections.add(
        ids=["id1", "id2", "id3"],
        documents=[
            "lorem ipsum dolor sit amet",
            "second document content",
            "third document content",
        ],
        metadatas=[
            {"chapter": 3, "verse": 16},
            {"chapter": 3, "verse": 5},
            {"chapter": 29, "verse": 11},
        ],
    )


async def __testHttpDB():
    config = Readconfig().read()

    chroma_client = CreateHttpDB(config)

    chroma_client.create_client()

    chroma_client.get_collection("test_collection")
    chroma_client.collections.add(
        ids=["id1", "id2", "id3"],
        documents=[
            "lorem ipsum dolor sit amet",
            "second document content",
            "third document content",
        ],
        metadatas=[
            {"chapter": 3, "verse": 16},
            {"chapter": 3, "verse": 5},
            {"chapter": 29, "verse": 11},
        ],
    )


if __name__ == '__main__':
    # __testPersistentDB()
    asyncio.run(__testHttpDB())
