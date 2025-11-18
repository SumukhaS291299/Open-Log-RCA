import sys
from pathlib import Path

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
import json
import csv

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

def ensure_template_files_exist():
    """
    Ensures template_chroma.csv and template_chroma.json exist.
    If missing, creates them using create_template_files().
    """
    csv_path = Path("template_chroma.csv")
    json_path = Path("template_chroma.json")

    if csv_path.exists() or json_path.exists():
        return  # At least one exists → no need to create both

    console.print("[bold yellow]No template files found. Generating CSV/JSON templates...[/bold yellow]")
    create_template_files()


def create_template_files():
    console.print("[bold green]Creating template files...[/bold green]")

    # CSV Template
    csv_path = "template_chroma.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "document", "metadata"])
        writer.writeheader()
        writer.writerow({
            "id": "1",
            "document": "Sample document text",
            "metadata": '{"category": "example", "value": 123}'
        })
        writer.writerow({
            "id": "2",
            "document": "Another sample text",
            "metadata": '{"tag": "demo"}'
        })

    # JSON Template
    json_path = "template_chroma.json"
    json_template = [
        {
            "id": "1",
            "document": "Sample document text",
            "metadata": {
                "category": "example",
                "value": 123
            }
        },
        {
            "id": "2",
            "document": "Another sample text",
            "metadata": {
                "tag": "demo"
            }
        }
    ]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_template, f, indent=4)

    console.print(f"[bold cyan]Templates created:[/bold cyan]")
    console.print(f" - {csv_path}")
    console.print(f" - {json_path}")


def collect_chroma_input_from_file():
    console.print("[bold green]File Input Mode[/bold green]")

    # Ensure templates exist
    ensure_template_files_exist()

    # Find .csv and .json files in CWD
    cwd = Path.cwd()
    files = list(cwd.glob("*.csv")) + list(cwd.glob("*.json"))

    if not files:
        console.print("[bold red]No CSV or JSON files found.[/bold red]")
        return None

    # If multiple files exist → let user choose
    console.print("\n[bold cyan]Available data files:[/bold cyan]")
    for i, f in enumerate(files, start=1):
        console.print(f"[bold yellow]{i}.[/bold yellow] {f.name}")

    choice = Prompt.ask(
        "[bold green]Choose a file number[/bold green]",
        choices=[str(i) for i in range(1, len(files) + 1)]
    )

    file_path = files[int(choice) - 1]
    console.print(f"[bold cyan]Using file:[/bold cyan] {file_path.name}")

    ids, documents, metadatas = [], [], []

    # --- Load JSON ---
    if file_path.suffix.lower() == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data:
            ids.append(str(entry["id"]))
            documents.append(entry["document"])
            metadatas.append(entry.get("metadata", {}))

        return ids, documents, metadatas

    # --- Load CSV ---
    if file_path.suffix.lower() == ".csv":
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            required = {"id", "document", "metadata"}
            if not required <= set(reader.fieldnames):
                console.print("[bold red]CSV must contain columns: id, document, metadata[/bold red]")
                return None

            for row in reader:
                ids.append(row["id"])
                documents.append(row["document"])
                try:
                    metadatas.append(json.loads(row["metadata"]))
                except json.JSONDecodeError:
                    console.print(f"[bold red]Invalid metadata JSON in row: {row}[/bold red]")
                    return None

        return ids, documents, metadatas

    console.print("[bold red]Unsupported file extension.[/bold red]")
    return None


def collect_chroma_input():
    console.print("[bold green]Collecting Chroma inputs...[/bold green]\n")

    console.print("[bold cyan]How do you want to provide data?[/bold cyan]")
    console.print("[bold yellow]1.[/bold yellow] Load from CSV/JSON file")
    console.print("[bold yellow]2.[/bold yellow] Enter manually")

    choice = Prompt.ask("[bold green]Choose an option[/bold green]", choices=["1", "2"])

    if choice == "1":
        result = collect_chroma_input_from_file()
        if result is not None:
            return result
        console.print("[bold red]Failed to load from file. Switching to manual input.[/bold red]")

    # Manual entry
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


def promptCollectInput():
    console.print("[bold cyan]Do you want to provide any extra data?[/bold cyan]")

    choice = Prompt.ask("[bold green]Choose an option[/bold green]", choices=["y", "n"])

    if choice.lower() == "y":
        return True
    return False

# TODO: Make Chunked Batch Add (When needed) [chroma_client.collections.add]
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
            if promptCollectInput():
                ids, documents, metadatas = collect_chroma_input()
                chroma_client.collections.add(ids=ids, documents=documents, metadatas=metadatas)

        case "2":
            chroma_client = CreateHttpDB(config)
            chroma_client.create_client()
            chroma_collection_name = prompt("[bold cyan]Enter your collection name[/bold cyan]: ")
            chroma_client.get_collection(chroma_collection_name)
            if promptCollectInput():
                ids, documents, metadatas = collect_chroma_input()
                chroma_client.collections.add(ids=ids, documents=documents, metadatas=metadatas)
        case "3":
            chroma_client = CreateHttpDB(config)
            chroma_client.create_client()
            chroma_collection_name = prompt("[bold cyan]Enter your collection name[/bold cyan]: ")
            chroma_client.get_collection(chroma_collection_name)
            if promptCollectInput():
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
