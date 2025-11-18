import requests


# TODO: Add config for host and port changes for ollama
def embed_texts(texts, model="nomic-embed-text", host="http://localhost:11434"):
    embeddings = []
    for text in texts:
        r = requests.post(
            f"{host}/api/embeddings",
            json={"model": model, "prompt": text}
        )
        r.raise_for_status()
        embeddings.append(r.json()["embedding"])
    return embeddings


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
