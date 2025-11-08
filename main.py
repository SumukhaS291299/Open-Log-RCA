from utils import RCALogger
from utils import RCAconfig
from vectorEmbeddings import RCAChromaPersistent

if __name__ == '__main__':
    logger = RCALogger.setup_logger("wow")
    config = RCAconfig.Readconfig().read()
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    chroma_client_persist = RCAChromaPersistent(config)

    # chroma_client = chroma_client_http.get_client()
    chroma_client = chroma_client_persist.get_client()
    collection = chroma_client.get_or_create_collection("test_collection1")
    collection.add(
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
