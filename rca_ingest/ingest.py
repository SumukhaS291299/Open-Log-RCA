from threading import Thread
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel, model_validator
from pydantic import Field
from typing_extensions import Annotated

from rca_ingest.ingestQueue import ingestQ

app = FastAPI()

def beautify_chroma_result(result):
    ids = result["ids"][0]
    docs = result["documents"][0]
    metas = result["metadatas"][0]
    distances = result["distances"][0]

    sorted_results = sorted(
        zip(ids, docs, metas, distances),
        key=lambda x: x[3]
    )

    output = []
    for rank, (id_, doc, meta, dist) in enumerate(sorted_results, start=1):
        output.append({
            "rank": rank,
            "id": id_,
            "distance": round(dist, 4),
            "document": doc,
            "metadata": meta
        })

    return output



class QueryRequest(BaseModel):
    query_texts: Annotated[List[str], Field(min_length=1)]
    n_results: int = Field(default=10, ge=1, le=50)


class IngestRequest(BaseModel):
    ids: List[str]
    documents: List[str]
    metadatas: List[dict]

    @model_validator(mode="after")
    def validate_lengths(self):
        if not (
            len(self.ids) == len(self.documents) == len(self.metadatas)
        ):
            raise ValueError(
                "ids, documents, and metadatas must have the same length"
            )
        return self

@app.post("/ingest")
def ingest(payload: IngestRequest):
    # If we are here
    ingestQ.put(payload)
    print(ingestQ.qsize())
    return {
        "status": "success",
        "count": len(payload.ids)
    }

@app.post("/query")
def query(payload: QueryRequest):
    if not hasattr(app.state, "embeddingQueryClient"):
        return {"status": "Service Not initialised", "message": "Query service not initialised"}
    chroma_client = app.state.chroma_client
    embeddingQueryClient = app.state.embeddingQueryClient
    query_embeddings = embeddingQueryClient.embed_texts(payload.query_texts)
    result = chroma_client.collections.query(
        query_embeddings=query_embeddings,
        n_results=payload.n_results
    )

    return {
        "results": beautify_chroma_result(result)
    }


def run_ingest_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080,log_level="info")

# def ConsumeAllmessagesFromQueue():
#     while True:
#         message = ingestQ.get()
#         print(message)
#         ingestQ.task_done()

if __name__ == '__main__':
    # consumeMessage = Thread(target=ConsumeAllmessagesFromQueue,daemon=True)
    # consumeMessage.start()

    run_ingest_server()
