from queue import Queue

from utils import setup_logger

logger = setup_logger("Embeddings")
logger.info("Queue will be initialized")
ingestQ = Queue(maxsize=2000)
logger.info("Queue initialized successfully")