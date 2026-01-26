import configparser
import queue
import sys
from pathlib import Path
from threading import Lock, Thread
from rca_ingest.ingestQueue import ingestQ
from vectorEmbeddings import RCAEmbedding

# LOAD ROOT if RUN as py main.py

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# LOAD ROOT if RUN as py main.py

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from prompt_toolkit import prompt
from rich.table import Table


from utils import RCAconfig
from vectorEmbeddings.createDB import CreatePersistentDB, CreateHttpDB

console = Console()

batch_buffer = []
batch_lock = Lock()


def consume_all_messages_from_queue():
    while True:
        item = ingestQ.get()
        try:
            with batch_lock:
                batch_buffer.append(item)
        finally:
            ingestQ.task_done()



def collect_chroma_input_pipline(config: configparser.ConfigParser):
    with batch_lock:
        if not batch_buffer:
            return None

        items = batch_buffer.copy()
        batch_buffer.clear()

    ids, documents, metadatas = [], [], []

    for item in items:
        ids.extend(item.ids)
        documents.extend(item.documents)
        metadatas.extend(item.metadatas)

    embeddings = RCAEmbedding(config).embed_texts(documents)

    return ids, documents, metadatas, embeddings



def prompt_query_list():
    console.print("[bold cyan]Enter query texts. Blank = run query. 'q' to exit.[/bold cyan]")
    queries = []

    while True:
        q = prompt("> ").strip()

        # exit commands
        if q.lower() in ("q", "quit", "exit", "bye"):
            return None

        # blank → run query
        if q == "":
            if queries:
                return queries  # return collected queries
            else:
                # blank at very beginning → ask again
                console.print("[italic yellow]Enter at least one query or 'q' to exit.[/italic yellow]")
                continue

        # store normal query text
        queries.append(q)


def display_chroma_result(result):
    ids = result["ids"][0]
    docs = result["documents"][0]
    metas = result["metadatas"][0]
    distances = result["distances"][0]

    # Make a table
    table = Table(title="Chroma Query Results", show_lines=True)

    table.add_column("Rank", style="bold cyan")
    table.add_column("ID", style="bold yellow")
    table.add_column("Distance", style="bold magenta")
    table.add_column("Document", style="bold white")
    table.add_column("Metadata", style="bold green")

    # Sort by distance (ascending)
    sorted_results = sorted(
        zip(ids, docs, metas, distances),
        key=lambda x: x[3]
    )

    # Fill rows
    for idx, (id_, doc, meta, dist) in enumerate(sorted_results, start=1):
        table.add_row(
            str(idx),
            id_,
            f"{dist:.4f}",
            doc,
            str(meta)
        )

    console.print(table)


# TODO: Make Chunked Batch Add (When needed) [chroma_client.collections.add]
def main():
    console.print(Panel("[bold cyan]Main Menu[/bold cyan]", expand=False))
    config = RCAconfig.Readconfig().read()

    console.print("[bold cyan] Welcome to Chroma ingest toolkit![/bold cyan]")
    console.print("[bold yellow]1.[/bold yellow] Use Persistent Chroma DB")
    console.print("[bold yellow]2.[/bold yellow] Connect to a web (HTTP) Chroma DB")
    console.print("[bold yellow]3.[/bold yellow] Connect to a web (HTTP) Async Chroma DB\n")
    console.print("[bold yellow]4.[/bold yellow] Exit\n")

    console.print("[bold brown]Starting ingestion server[/bold brown]")


    choice = Prompt.ask("[bold green]Choose an option[/bold green]")

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

    # This will not work LoL
    consumer_thread = Thread(target=consume_all_messages_from_queue,daemon=True)
    consumer_thread.start()

    console.print("[bold cyan] Query Chroma vector Database![/bold cyan]")

    while True:
        # I need to call the collect_chroma_input_pipline in regular intervals
        ids, documents, metadatas, embeddings = collect_chroma_input_pipline(config)
        chroma_client.collections.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        # Remove the interactive CLI and use HTTP
        query_texts = prompt_query_list()

        if query_texts is None:
            console.print("[bold yellow]Exiting query mode...[/bold yellow]")
            break

        query_embeddings = RCAEmbedding(config).embed_texts(query_texts)

        result = chroma_client.collections.query(
            query_embeddings=query_embeddings,
            n_results=10
        )

        display_chroma_result(result)

if __name__ == '__main__':
    main()
