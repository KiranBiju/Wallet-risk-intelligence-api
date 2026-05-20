# 🚀 Wallet Risk Intelligence API

<p align="center">
  <img src="wallet-risk-api/assets/thumnail.png" width="850"/>
</p>


> **Production-grade AI + Blockchain Risk Scoring System**
> Detect scams, fraudulent wallets, and suspicious on-chain behavior **before transactions happen**

---

## 🔥 Overview

Wallet Risk Intelligence API is a **high-performance backend system** that analyzes Ethereum wallet activity in real-time and assigns a **risk score, level, and explainable reasoning** using:

* 📊 Feature Engineering (on-chain signals)
* 🧠 Rule-based Risk Engine
* 🤖 RAG (Retrieval-Augmented Generation) with FAISS
* ⚡ FastAPI (low-latency API)
* 🗄 PostgreSQL (persistent storage)
* 🧩 Redis (caching layer)

---

## 🧠 Key Capabilities

* 🔍 Analyze wallet transaction behavior
* ⚠️ Detect scam patterns (rug pull, phishing, wash trading, etc.)
* 📈 Generate explainable risk scores
* 🧬 Combine ML + Rule Engine + RAG
* ⚡ Sub-second API responses (with caching)
* 🧾 Store historical risk reports

---
## 🔥 Demo Video

[Watch the demo](https://drive.google.com/file/d/1N9_oiaAKqsl3diC_FsJ1xmbL1phI9dRK/view?usp=sharing)

---

## 🏗 Architecture

```
Client (Streamlit Frontend / API User)
            ↓
      FastAPI Backend
            ↓
 ┌───────────────┬───────────────┬───────────────┐
 │ Data Service  │ Feature Engg  │ Risk Engine   │
 │ (Etherscan)   │               │ (Rules + RAG) │
 └───────────────┴───────────────┴───────────────┘
            ↓
     FAISS Vector DB (RAG)
            ↓
   PostgreSQL (Storage)
            ↓
      Redis (Caching)
```

---

## ⚙️ Tech Stack

* **Backend**: FastAPI
* **Frontend**: Streamlit
* **ML / NLP**: Sentence Transformers (`all-MiniLM-L6-v2`)
* **LLM**: Groq
* **Vector DB**: FAISS
* **Database**: PostgreSQL
* **Cache**: Redis
* **Containerization**: Docker
* **API Source**: Etherscan API

---

## 📁 Project Structure

```
wallet-risk-api/
│
├── app/
│   ├── main.py
│──assets/
│   ├── demo.wdmb
│   └── thumnail.png
│   └── working.png
│──db/
│   ├── db.py
│   └── models.py
│──frontend/
│   ├── streamli.py
│   └── requirements.txt
│   └── Dockerfile
├── schemas/
|    ├── risk_schema.py
│── services/
│   ├── data_service.py
│   ├── feature_service.py
│   ├── risk_service.py
│   ├── rag_service.py
│   └── cache_service.py
│── scripts/
│   ├── fetch_data.py
│   ├── feature_pipeline.py
│   ├── train_model.py
│   ├── wallet_crawler.py
│   └── test_model.py
├── rag/
│   ├── scam_patterns.json
│   ├── build_rag.py
│   ├── faiss_index.bin
│   └── patterns.pkl
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Clone Repo

```bash
git clone https://github.com/your-username/wallet-risk-api.git
cd wallet-risk-api
```

---

### 2️⃣ Create and Activate Virtual Environment

```bash
python -m venv venv
```

```bash
Windows: venv\Scripts\activate
```

```bash
Linux: source venv/bin/activate
```

---

### 3️⃣ Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Install Frontend Dependencies

```bash
pip install -r frontend/requirements.txt
```

---

### 5️⃣ Create Your .env

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/wallet_db
REDIS_HOST=localhost
REDIS_PORT=6379
ETHERSCAN_API_KEY=your_etherscan_api_key
GROQ_API_KEY=your_groq_api_key
```

---

### 6️⃣ Build the RAG Index

```bash
python -m rag.build_rag
```

---

### 7️⃣ Start the FastAPI Backend

```bash
uvicorn app.main:app --reload
```

👉 Open Swagger UI:
http://127.0.0.1:8000/docs

---

### 7️⃣ Start the Streamlit Frontend

```bash
streamlit run frontend/streamlit_app.py
```

👉 Open Streamlit UI:
Streamlit UI: http://localhost:8501

---

## 🐳 Run with Docker (Recommended)

```bash
docker-compose up --build
```

### Services

| Service    | Port |
| ---------- | ---- |
| Backend    | http://localhost:8000/docs |
| Frontend   | http://localhost:8501 |
| PostgreSQL | localhost:5432 |
| Redis      | localhost:6379 |

---


## 📡 API Endpoint

### POST `/risk/score`

#### Request

```json
{
  "wallet": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
}
```

---

### ✅ Response

```json
{
  "status": "success",
  "data": {
    "wallet": "0x742d...",
    "risk_score": 0.6,
    "risk_level": "MEDIUM",
    "confidence": 0.75,
    "reason": "High value transfers",
    "explanation": "Related patterns detected: large transfer anomaly, burst transfers",
    "patterns_matched": [...],
    "explainability": {
      "ml_features": {...},
      "decision_path": "RULE → RAG"
    }
  }
}
```

---

## 🧠 How It Works

### 1. Data Collection

* Fetch last 100 transactions via Etherscan

### 2. Feature Engineering

* Transaction frequency
* Average transaction value
* Unique interactions
* High-risk interaction ratio

### 3. Rule-Based Scoring

* Detect anomalies like:

  * High-value transfers
  * Burst activity
  * Contract interactions

### 4. RAG Layer (FAISS)

* Matches wallet behavior to known scam patterns
* Returns top similar risk patterns

### 5. Final Risk Decision

* Combines rules + RAG signals
* Outputs risk score, level, and explanation

---

<p align="center">
  <img src="wallet-risk-api/assets/working.png" width="850"/>
</p>

---

## 📊 Example Risk Patterns

* Rug Pull
* Honeypot
* Phishing Interaction
* Wash Trading
* Flash Loan Attack
* Sandwich Attack
* Sybil Attack
* Liquidity Draining

(60+ patterns supported)

---

## ⚡ Performance Optimizations

* Redis caching (TTL-based)
* FAISS vector search (fast retrieval)
* Async API calls
* Lightweight embedding model

---

## 🗄 Database Schema

**RiskReport Table**

| Field      | Type     |
| ---------- | -------- |
| id         | Integer  |
| wallet     | String   |
| risk_level | String   |
| confidence | Float    |
| timestamp  | DateTime |

---

## 🚧 Future Improvements

* Multi-chain support (Polygon, BSC)
* ML-based anomaly detection
* Graph-based wallet clustering
* Real-time monitoring
* Web3 wallet integration

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Kiran Biju**

AI Engineer | GenAI Developer | Backend Developer | Blockchain Developer

---

## ⭐ Support

If you like this project:

* ⭐ Star the repo
* 🍴 Fork it
* 🧠 Contribute ideas

