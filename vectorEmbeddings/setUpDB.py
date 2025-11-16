import configparser
from pathlib import Path
import chromadb

from utils import Readconfig, setup_logger


class RCAChroma:
    """Base class for Chroma client connection management."""

    def __init__(self, config: configparser.ConfigParser):
        self.client = None
        self.logger = setup_logger("Chroma")
        self.config = config

    def get_client(self):
        """Return the Chroma client instance."""
        return self.client


class RCAChromaPersistent(RCAChroma):
    """Persistent (local) mode — stores embeddings locally."""

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)

        self.PersistenPATH = Path.cwd() / "Embeddings"
        self.PersistenPATH.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"💾 Using Chroma persistent client at: {self.PersistenPATH}")
        self.client = chromadb.PersistentClient(path=str(self.PersistenPATH))


class RCAChromaHttp(RCAChroma):
    """HTTP (Client-Server) mode — requires both host and port."""

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)

        try:
            host = self.config.get("Chroma", "HttpClient_Host", fallback="").strip()
            port_str = self.config.get("Chroma", "HttpClient_Port", fallback="").strip()
            port = int(port_str) if port_str.isdigit() else None

            if host and port:
                # ✅ Client-Server mode
                self.HTTPConnectHOST = host
                self.HTTPConnectPORT = port
                self.logger.info(f"🌐 Using remote Chroma server at {host}:{port}")
                self.client = chromadb.HttpClient(host=host, port=port)
            else:
                # ❌ Strict mode: no fallback
                self.HTTPConnectHOST = None
                self.HTTPConnectPORT = None
                self.logger.error(
                    "❌ Missing HttpClient_Host or HttpClient_Port in [Chroma]. "
                    "HTTP mode cannot start. Please check your configuration file."
                )
                self.client = None

        except configparser.NoSectionError:
            self.logger.error("❌ Missing [Chroma] section in configuration file.")
            self.logger.error("""Create a file like
            [Chroma]
HttpClient_Host = localhost
HttpClient_Port = 8000""")
            self.client = None

        except configparser.Error as e:
            self.logger.error(f"❌ Config parsing error: {e}")
            self.client = None


class RCAChromaHttpAsync(RCAChroma):
    """HTTP (Client-Server) mode — requires both host and port."""

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)

        try:
            host = self.config.get("Chroma", "HttpClient_Host", fallback="").strip()
            port_str = self.config.get("Chroma", "HttpClient_Port", fallback="").strip()
            port = int(port_str) if port_str.isdigit() else None

            if host and port:
                # ✅ Client-Server mode
                self.HTTPConnectHOST = host
                self.HTTPConnectPORT = port
                self.logger.info(f"🌐 Using remote Chroma server at {host}:{port}")
                self.client = chromadb.AsyncHttpClient(host=host, port=port)
            else:
                # ❌ Strict mode: no fallback
                self.HTTPConnectHOST = None
                self.HTTPConnectPORT = None
                self.logger.error(
                    "❌ Missing HttpClient_Host or HttpClient_Port in [Chroma]. "
                    "HTTP mode cannot start. Please check your configuration file."
                )
                self.client = None

        except configparser.NoSectionError:
            self.logger.error("❌ Missing [Chroma] section in configuration file.")
            self.logger.error("""Create a file like
                        [Chroma]
            HttpClient_Host = localhost
            HttpClient_Port = 8000""")
            self.client = None

        except configparser.Error as e:
            self.logger.error(f"❌ Config parsing error: {e}")
            self.client = None


# --- Script Entry Point ---
if __name__ == "__main__":
    config = Readconfig().read()

    # Instantiate HTTP client
    # chroma_client_http = RCAChromaHttp(config)
    # Instantiate Persistent client
    chroma_client_persist = RCAChromaPersistent(config)

    # chroma_client = chroma_client_http.get_client()
    chroma_client = chroma_client_persist.get_client()
    collection = chroma_client.get_or_create_collection("test_collection")
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
    # chroma_client.
    # print(chroma_client_persist.get_client())
