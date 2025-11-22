import configparser

import requests

from utils import setup_logger, Readconfig


class RCAEmbedding:
    def __init__(self, config: configparser.ConfigParser):
        self.logger = setup_logger("Embeddings")
        try:
            self.model = config.get("Embedding", "model", fallback="").strip()
            self.host = config.get("Embedding", "host", fallback="").strip()
            self.batchsize = int(config.get("Embedding", "batch_size", fallback="100").strip())
        except configparser.NoSectionError:
            self.logger.error("❌ Missing [Embedding] section in configuration file.")
            self.logger.error("""Create a file like:
[Embedding]
model = nomic-embed-text
host = http://localhost:11434""")

    def embed_texts(self, texts):
        # 1️⃣ CLEAN TEXTS
        clean_texts = [t.strip() if isinstance(t, str) else "" for t in texts]

        # Remove truly empty docs (but track original index!)
        indexed = [(i, t) for i, t in enumerate(clean_texts) if t]
        if not indexed:
            raise ValueError("❌ No valid text provided for embedding.")

        indices, valid_texts = zip(*indexed)

        all_embeddings = []
        total = len(valid_texts)

        for i in range(0, total, self.batchsize):
            batch = valid_texts[i:i + self.batchsize]

            r = requests.post(
                f"{self.host}/api/embed",
                json={
                    "model": self.model,
                    "input": list(batch)
                }
            )

            r.raise_for_status()
            data = r.json()

            if "embeddings" not in data:
                raise ValueError(f"❌ Missing 'embeddings' in response: {data}")

            batch_embeddings = data["embeddings"]

            # STRICT validation
            if not isinstance(batch_embeddings, list):
                raise ValueError(f"❌ Embeddings must be a list, got {type(batch_embeddings)}")

            if len(batch_embeddings) != len(batch):
                raise ValueError(
                    f"❌ Embedding count mismatch!\n"
                    f"Sent {len(batch)} items\nGot {len(batch_embeddings)} embeddings\n"
                    f"Response (trimmed): {str(data)[:300]}"
                )

            all_embeddings.extend(batch_embeddings)

        # 2️⃣ RE-EXPAND TO MATCH ORIGINAL ORDER
        final_embeddings = [None] * len(texts)

        for emb, original_index in zip(all_embeddings, indices):
            final_embeddings[original_index] = emb

        # 3️⃣ GUARANTEE: no missing embedding
        if any(e is None for e in final_embeddings):
            raise ValueError("❌ Some texts failed to embed — index mismatch!")

        return final_embeddings


# import torch
# from transformers import AutoTokenizer, AutoModel
#
class HFTransformersEmbeddingFunction:
    def __init__(self):
        raise NotImplemented
#     def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
#         self.device = "cuda" if torch.cuda.is_available() else "cpu"
#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#         self.model = AutoModel.from_pretrained(model_name).to(self.device)
#
#     def __call__(self, texts):
#         inputs = self.tokenizer(
#             texts,
#             padding=True,
#             truncation=True,
#             return_tensors="pt"
#         ).to(self.device)
#
#         with torch.no_grad():
#             outputs = self.model(**inputs)
#
#         # Mean pooling
#         embeddings = outputs.last_hidden_state.mean(dim=1)
#
#         return embeddings.cpu().numpy().tolist()

if __name__ == '__main__':
    config = Readconfig().read()
    RCAEmbedding(config).embed_texts(["Hello","world"])