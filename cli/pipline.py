import sys
import time
from pathlib import Path
from threading import Thread

from rca_ingest.ingestQueue import ingestQ

# LOAD ROOT if RUN as py main.py

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# LOAD ROOT if RUN as py main.py

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from prompt_toolkit import prompt
from rca_ingest.ingest import app, run_ingest_server

from utils import RCAconfig
from vectorEmbeddings.createDB import CreatePersistentDB, CreateHttpDB
from vectorEmbeddings.embedding import RCAEmbedding

console = Console()


def flushToChroma(embeddingQueryClient: RCAEmbedding, chroma_client):
    while True:
        payload = ingestQ.get()  # BLOCKS until data is available
        try:
            console.print("Data was found in the ingest queue")
            embeddings = embeddingQueryClient.embed_texts(payload.documents)
            console.print("[green]embeddings was flushed[/green]")
            chroma_client.collections.add(
                ids=payload.ids,
                documents=payload.documents,
                metadatas=payload.metadatas,
                embeddings=embeddings
            )

            console.print("Current Queue size: "+ str(ingestQ.qsize()))

        except Exception as e:
            console.print(e)

        finally:
            ingestQ.task_done()


# TODO: Make Chunked Batch Add (When needed) [chroma_client.collections.add]
def main():
    global chroma_client
    console.print(Panel("[bold cyan]Main Menu[/bold cyan]", expand=False))
    config = RCAconfig.Readconfig().read()

    console.print("[bold cyan] Welcome to Chroma ingest toolkit![/bold cyan]")
    console.print("[bold yellow]1.[/bold yellow] Use Persistent Chroma DB")
    console.print("[bold yellow]2.[/bold yellow] Connect to a web (HTTP) Chroma DB")
    console.print("[bold yellow]3.[/bold yellow] Connect to a web (HTTP) Async Chroma DB\n")
    console.print("[bold yellow]4.[/bold yellow] Exit\n")

    console.print("[bold brown]Starting ingestion server[/bold brown]")

    choice = Prompt.ask("[bold green]Choose an option[/bold green]")

    waitThread = Thread()

    match choice:
        case "1":
            chroma_client = CreatePersistentDB(config)
            chroma_client.create_client()
            chroma_collection_name = prompt("[bold cyan]Enter your collection name[/bold cyan]: ")
            chroma_client.get_collection(chroma_collection_name)

        case "2":
            chroma_client = CreateHttpDB(config)
            chroma_client.create_client()
            chroma_collection_name = prompt("[bold cyan]Enter your collection name[/bold cyan]: ")
            chroma_client.get_collection(chroma_collection_name)

        case "3":
            chroma_client = CreateHttpDB(config)
            chroma_client.create_client()
            chroma_collection_name = prompt("[bold cyan]Enter your collection name[/bold cyan]: ")
            chroma_client.get_collection(chroma_collection_name)

        case "4":
            sys.exit(0)
        case _:
            console.print("[bold red]Invalid choice[/bold red]")

    app.state.chroma_client = chroma_client
    embeddingQueryClient = RCAEmbedding(config)
    app.state.embeddingQueryClient = embeddingQueryClient

    FlushConfigThread = Thread(target=flushToChroma, args=(embeddingQueryClient, chroma_client), daemon=True)

    FlushConfigThread.start()
    # Create 2 thread from main
    #   --> API listener for ingest and query
    #   --> periodic load and empty the queue

    run_ingest_server()


if __name__ == '__main__':
    main()
