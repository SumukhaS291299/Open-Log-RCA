import json
import os


def validate_encoding(texts):
    """
    Validates that all texts:
    - are strings
    - are UTF-8 encodable
    - contain no null bytes
    - are not empty after stripping
    """
    for i, t in enumerate(texts):
        if not isinstance(t, str):
            raise ValueError(f"❌ Text at index {i} is not a string")

        if "\x00" in t:
            raise ValueError(f"❌ Null byte found in text at index {i}")

        try:
            t.encode("utf-8")
        except UnicodeEncodeError as e:
            raise ValueError(
                f"❌ UTF-8 encoding error at index {i}: {e}"
            )

        if not t.strip():
            raise ValueError(f"❌ Text at index {i} is empty after stripping")

    return True



files = os.listdir("output_batches")

for file in files:
    if file.endswith(".json"):
        with open(os.path.join("output_batches", file), "r", encoding="utf-8") as f:
            print("Seeing file", file)
            batch = json.load(f)

            documents = batch["documents"]  # ✅ List[str]
            validate_encoding(documents)