Here is a **clean, production-ready README.md** for your project — Vector → Embedding Service → ChromaDB semantic log ingestion pipeline.
You can paste this directly into your repo.

---

# 📘 Semantic Log Ingestion & Search Pipeline

### **Vector.dev → FastAPI Embedding Service → ChromaDB**

This project provides an end-to-end log ingestion and semantic search system using:

* **Vector.dev** – high-performance logs collector and shipper
* **Embedding Service (FastAPI)** – converts log messages into vector embeddings
* **ChromaDB** – persistent vector database for semantic search
* (Optional) **OpenTelemetry** – for metrics, tracing, and observability

This setup lets you perform **semantic queries** on logs such as:

> “Show me logs similar to ‘database timeout’ from the last hour.”

---

### Quick install

```bash
uv tool install "git+https://github.com/SumukhaS291299/Open-Log-RCA.git"
```


## 🚀 Features

* Collect logs from any application / Kubernetes environment
* Parse, enrich, and forward logs via Vector.dev
* Convert logs to embeddings using SentenceTransformers
* Store embeddings + metadata in ChromaDB
* Query logs semantically (vector similarity search)
* Fully local PoC via Docker Compose
* Can be deployed to Kubernetes easily
* Optional OpenTelemetry instrumentation

---

## 📂 Project Structure

```
log-semantic-ingest/
├── docker-compose.yml
├── vector/
│   └── vector.toml
├── embedding_service/
│   ├── Dockerfile
│   └── app.py
├── chromadbconf.yml        (optional: OTEL config)
└── requirements.txt
```

---

## 🧱 Architecture Overview

```
 Application Logs (K8s or local)
                ↓
          Vector.dev
  (collect, parse, enrich, ship)
                ↓
      Embedding Service (FastAPI)
  (generate embeddings using ML model)
                ↓
           ChromaDB
 (store embeddings + metadata for search)
                ↓
      Semantic Search / RCA via API
```

---

## 🛠️ Installation (Docker Compose)

### 1. Clone the repo

```bash
git clone https://github.com/your/repo.git
cd log-semantic-ingest
```

### 2. Start all services

```bash
docker compose up --build
```

Expected services:

* `chromadb` → [http://localhost:8001](http://localhost:8001)
* `embedding_service` → [http://localhost:8000](http://localhost:8000)
* `vector` → starts and waits for logs

---

## 🧮 Sending Logs into the Pipeline

You can manually pipe logs into Vector:

```bash
docker exec -it vector sh -c "cat > /dev/stdin"
```

Then paste a sample JSON log:

```json
{"message": "Database connection timeout", "metadata": {"service": "payment", "level": "error"}}
```

Vector → Embedding Service → ChromaDB 🚀

---

## 🔍 Query Semantic Logs

Query logs that semantically match a phrase:

```bash
curl "http://localhost:8000/search?query=database timeout"
```

Example response:

```json
{
  "documents": [["Database connection timeout"]],
  "metadatas": [[{"service":"payment", "level":"error"}]],
  "distances": [[0.13]]
}
```

---

## 🧩 Components

### ✔ Vector.dev

Configured via `vector/vector.toml` to:

* Read logs from stdin or Kubernetes
* Parse JSON logs
* Ship them to the embedding service via HTTP

### ✔ Embedding Service (FastAPI)

* Uses `sentence-transformers` (MiniLM model)
* Generates numeric embeddings
* Stores logs, metadata, and vectors into ChromaDB
* Provides search API

### ✔ ChromaDB

* Persistent vector database
* Supports metadata filtering
* Supports semantic similarity search

### ✔ OpenTelemetry (optional)

Enable by creating a config file:

```yaml
telemetry:
  opentelemetry:
    enabled: true
    exporter_otlp_endpoint: http://localhost:4317
    service_name: chromadb
    log_level: info
```

And running Chroma with a directory containing this config:

```bash
chroma run chroma_data/
```

---

## ⚙️ Kubernetes Deployment (Optional)

Once validated locally, deploy these components to Kubernetes:

* Vector as a DaemonSet collecting cluster logs
* Embedding service as a Deployment
* ChromaDB as a StatefulSet with PVC
* Use ConfigMaps for Vector config
* Use Services for inter-pod communication

(You can ask for full YAML manifests and I’ll generate them.)

---

## 🧪 Testing the Stack

1. Send logs into Vector
2. Ensure Embedding Service receives embeddings
3. Ensure Chroma stores documents
4. Query `/search` API
5. Validate semantic match quality

---

## 📄 Technologies Used

* **Vector.dev**
* **FastAPI**
* **SentenceTransformers**
* **ChromaDB**
* **Python 3.11**
* **Docker Compose**
* **OpenTelemetry (optional)**

---

## 📎 To Do / Roadmap

* [ ] Add metadata filtering (`namespace`, `pod`, `severity`)
* [ ] Add Kubernetes manifests
* [ ] Add log summarization using LLMs
* [ ] Add user-friendly web UI for log exploration
* [ ] Add retention/rotation strategy for large log volumes

---

## 🙌 Contributing

Pull requests are welcome!
If you'd like to request enhancements (UI, LLM integration, Kubernetes automation), feel free to open an issue.

---

If you want, I can also generate:

✅ A **logo/badge** for your README
✅ A **sequence diagram** in Mermaid
✅ A **full Wiki-style documentation**
✅ A **Kubernetes folder with all manifests**

Tell me what you want next!
