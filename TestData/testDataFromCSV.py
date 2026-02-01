import csv
import uuid
import json
import re
import os

BATCH_SIZE = 25
CSV_FILE = "7817_1.csv"
OUTPUT_DIR = "output_batches"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove escaped control sequences
    text = re.sub(r"\\[ntrfv]", " ", text)

    # Normalize real whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove special characters
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)

    # Final whitespace cleanup
    text = re.sub(r"\s+", " ", text).strip()

    return text


batch_ids = []
batch_documents = []
batch_metadatas = []

batch_count = 1

def flush_batch():
    global batch_count

    output = {
        "ids": batch_ids.copy(),
        "documents": batch_documents.copy(),
        "metadatas": batch_metadatas.copy(),
    }

    output_path = os.path.join(
        OUTPUT_DIR, f"batch_{batch_count}.json"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Written {output_path} ({len(batch_ids)} records)")

    batch_ids.clear()
    batch_documents.clear()
    batch_metadatas.clear()

    batch_count += 1


with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        name = clean_text(row.get("name"))
        review = clean_text(row.get("reviews.text"))

        if not name and not review:
            continue

        document_parts = []
        if name:
            document_parts.append(f"Product: {name}")
        if review:
            document_parts.append(f"Review: {review}")

        document = " -- ".join(document_parts)

        metadata = {
            "brand": clean_text(row.get("brand")),
            "categories": clean_text(row.get("categories")),
            "colors": clean_text(row.get("colors")),
            "manufacturer": clean_text(row.get("manufacturer")),
            "prices": clean_text(row.get("prices")),
            "reviews_userCity": clean_text(row.get("reviews.userCity")),
        }

        metadata = {k: v for k, v in metadata.items() if v}

        batch_ids.append(str(uuid.uuid4()))
        batch_documents.append(document)
        batch_metadatas.append(metadata)

        if len(batch_ids) == BATCH_SIZE:
            flush_batch()


# Flush remaining records
if batch_ids:
    flush_batch()
