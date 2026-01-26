from typing import List

from threading import Thread
from vectorEmbeddings import RCAEmbedding
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, model_validator
from ingestQueue import ingestQ

app = FastAPI()


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

def run_ingest_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

def ConsumeAllmessagesFromQueue():
    while True:
        message = ingestQ.get()
        print(message)
        ingestQ.task_done()

if __name__ == '__main__':
    consumeMessage = Thread(target=ConsumeAllmessagesFromQueue,daemon=True)
    consumeMessage.start()

    run_ingest_server()
