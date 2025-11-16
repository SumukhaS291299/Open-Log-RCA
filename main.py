import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from prompt_toolkit import prompt
from rich.table import Table

from utils import RCAconfig
from vectorEmbeddings.createDB import CreatePersistentDB, CreateHttpDB

console = Console()


def prompt_list(label: str):
    """
    Prompt the user to enter multiple values for a list.
    Blank input stops the loop.
    """
    console.print(f"[bold cyan]Enter {label} (blank to stop):[/bold cyan]")
    items = []
    while True:
        value = prompt("> ")
        if not value.strip():
            break
        items.append(value.strip())
    return items


def prompt_metadata_list():
    console.print("[bold cyan]Enter metadata objects (leave first key blank to stop):[/bold cyan]")
    metadata_list = []

    while True:
        console.print("\n[bold yellow]New metadata object[/bold yellow]")
        meta = {}

        # First key decides whether we stop completely
        first_key = prompt(" key: ").strip()
        if not first_key:
            # Stop all metadata entries
            break

        # First key has a value → collect value
        first_value = prompt(" value: ").strip()
        if first_value.isdigit():
            first_value = int(first_value)
        meta[first_key] = first_value

        # Now collect remaining keys
        while True:
            key = prompt(" key (blank to finish this object): ").strip()
            if not key:
                break
            value = prompt(" value: ").strip()
            if value.isdigit():
                value = int(value)
            meta[key] = value

        metadata_list.append(meta)

    return metadata_list


def collect_chroma_input():
    """
    Collects ids, documents, metadata in the same structure needed by Chroma.
    """
    console.print("[bold green]Collecting Chroma inputs...[/bold green]\n")

    ids = prompt_list("IDs")
    documents = prompt_list("documents")
    metadatas = prompt_metadata_list()

    return ids, documents, metadatas

def prompt_query_list():
    console.print("[bold cyan]Enter query texts (blank to stop):[/bold cyan]")
    queries = []

    while True:
        q = prompt("> ").strip()
        if not q:
            break
        queries.append(q)

    return queries


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



def main():
    console.print(Panel("[bold cyan]Main Menu[/bold cyan]", expand=False))
    config = RCAconfig.Readconfig().read()

    console.print("[bold cyan] Welcome to Chroma ingest toolkit![/bold cyan]")
    console.print("[bold yellow]1.[/bold yellow] Use Persistent Chroma DB")
    console.print("[bold yellow]2.[/bold yellow] Connect to a web (HTTP) Chroma DB")
    console.print("[bold yellow]3.[/bold yellow] Connect to a web (HTTP) Async Chroma DB\n")
    console.print("[bold yellow]4.[/bold yellow] Exit\n")

    choice = Prompt.ask("[bold green]Choose an option[/bold green]")

    match choice:
        case "1":
            chroma_client = CreatePersistentDB(config)
            chroma_client.create_client()
            chroma_collection_name = prompt("[bold cyan]Enter your collection name[/bold cyan]: ")
            chroma_client.get_collection(chroma_collection_name)
            ids, documents, metadatas = collect_chroma_input()
            chroma_client.collections.add(ids=ids, documents=documents, metadatas=metadatas)

        case "2":
            chroma_client = CreateHttpDB(config)
            chroma_client.create_client()
            chroma_collection_name = prompt("[bold cyan]Enter your collection name[/bold cyan]: ")
            chroma_client.get_collection(chroma_collection_name)
            ids, documents, metadatas = collect_chroma_input()
            chroma_client.collections.add(ids=ids, documents=documents, metadatas=metadatas)
        case "3":
            chroma_client = CreateHttpDB(config)
            chroma_client.create_client()
            chroma_collection_name = prompt("[bold cyan]Enter your collection name[/bold cyan]: ")
            chroma_client.get_collection(chroma_collection_name)
            ids, documents, metadatas = collect_chroma_input()
            chroma_client.collections.add(ids=ids, documents=documents, metadatas=metadatas)

        case "4":
            sys.exit(0)
        case _:
            console.print("[bold red]Invalid choice[/bold red]")

    console.print("[bold cyan] Query Chroma vector Database![/bold cyan]")

    query_texts = prompt_query_list()
    display_chroma_result(chroma_client.query(query_texts))



if __name__ == '__main__':
    main()
