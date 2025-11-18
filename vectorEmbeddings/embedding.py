import requests

# TODO: Add config for host and port changes for ollama

class OllamaEmbeddingFunction:
    def __init__(self, model="nomic-embed-text", host="localhost", port=11434):
        self.url = f"http://{host}:{port}/api/embeddings"
        self.model = model

    def __call__(self, input):
        """Embeds documents one-by-one (Ollama limitation)."""
        embeddings = []
        for text in input:
            resp = requests.post(
                self.url,
                json={"model": self.model, "prompt": text},
            )
            resp.raise_for_status()
            data = resp.json()

            # Ollama returns { "embedding": [...] }
            embeddings.append(data["embedding"])

        return embeddings

    def name(self):
        return f"ollama-{self.model}"



class OpenAIEmbeddingFunction:

    def __init__(self):
        raise NotImplemented


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
