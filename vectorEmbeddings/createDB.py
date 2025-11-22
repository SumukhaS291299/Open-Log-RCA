import asyncio
import configparser

from vectorEmbeddings import RCAChromaPersistent, RCAChromaHttp
from utils import Readconfig, setup_logger
from vectorEmbeddings.setUpDB import RCAChromaHttpAsync


# TODO: Add async client compatibility

class CreateVectorDB:

    def __init__(self, config: configparser.ConfigParser):
        self.collections = None
        self.config = config
        self.client = None

    def insert(self, log_id, message, metadata):
        self.collections.add(
            ids=[log_id],
            documents=[message],
            metadatas=[metadata]
        )

        return [log_id]
    # TODO add n_results to ini file and enable where query
    def query(self, queryText: list):
        return self.collections.query(
            query_texts=queryText,
            n_results=10,
            # where=where or {}
        )


class CreateHttpDB(CreateVectorDB):

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)

    def create_client(self):
        self.client = RCAChromaHttp(self.config).get_client()

    def get_collection(self, name: str):
        self.collections = self.client.get_or_create_collection(name=name)


class CreateHttpAsync(CreateVectorDB):

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)

    async def create_asyncClient(self):
        self.client = RCAChromaHttpAsync(self.config).get_client()

    def get_asyncCollection(self, name: str):
        self.collections = self.client.get_or_create_collection(name=name)


class CreatePersistentDB(CreateVectorDB):

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)

    def create_client(self):
        self.client = RCAChromaPersistent(self.config).get_client()

    def get_collection(self, name: str):
        self.collections = self.client.get_or_create_collection(name=name)


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
    print(chroma_client.query(queryText=["lorem"]))


def __testHttpDB():
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


async def __testHttpDBAsync():
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
    __testPersistentDB()
    # __testHttpDB()
    # asyncio.run(__testHttpDBAsync())
