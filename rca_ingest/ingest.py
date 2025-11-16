from fastapi import FastAPI, Request
import uvicorn
app = FastAPI()
from fastapi.responses import JSONResponse

# UI on statistics
@app.get("/")
def root():
    return {"message": "RCA Ingestion API is running"}

@app.get("/health")
def health():
    return JSONResponse("Healthy",status_code=200)

# Ingest logs
@app.post("/ingest/log")
async def ingest_log(request: Request):
    body = await request.json()
    raw_log = body.get("message", "")

    print("Received log:", raw_log)

    return {
        "status": "received",
        "log": raw_log
    }

# uvicorn path:app --reload --host 0.0.0.0 --port 8000
if __name__ == '__main__':
    uvicorn.run("rca_ingest.ingest:app", host="0.0.0.0", port=8000, reload=True)