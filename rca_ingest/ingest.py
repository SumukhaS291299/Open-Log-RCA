# Will mostly be removed in next upcoming commits!

# from fastapi import FastAPI, Request
# import uvicorn
#
# from vectorEmbeddings.ingestDB import Document
#
# app = FastAPI()
# from fastapi.responses import JSONResponse
# from fastapi.concurrency import run_in_threadpool
#
# # UI on statistics
# @app.get("/")
# def root():
#     return {"message": "RCA Ingestion API is running"}
#
# @app.get("/health")
# def health():
#     return JSONResponse("Healthy",status_code=200)
#
# # Ingest logs
# @app.post("/ingest/log")
# async def ingest_log(doc: Document):
#     """Ingest one document into Chroma."""
#     await run_in_threadpool(Document, doc)
#     return {"status": "ok", "id": doc.id}
#
#
#
# @app.post("/query")
# async def query_logs(query: QueryRequest):
#
#     async def _run_query():
#         return collection.query(
#             query_texts=[query.text],
#             n_results=query.n_results
#         )
#
#     result = await run_in_threadpool(_run_query)
#
#     return {"results": result}
#
# # uvicorn path:app --reload --host 0.0.0.0 --port 8000
# if __name__ == '__main__':
#     uvicorn.run("rca_ingest.ingest:app", host="0.0.0.0", port=8000, reload=True)