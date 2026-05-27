# 💰 AI Personal Wealth Dashboard

An enterprise-grade, 3-tier financial quantitative tracking application built to manage local asset ledgers and generate custom wealth optimization strategies using generative artificial intelligence.

## 🚀 Architecture Overview

The system architecture is engineered as a decoupled full-stack network:
1. **Frontend Presentation Layer (Streamlit):** A dynamic, state-managed single-page dashboard tracking real-time metrics (Inflow, Outflow, Net Liquid Wealth), dual-panel manual transaction logging, and interactive asynchronous AI report generation.
2. **Backend REST Gateway (FastAPI):** High-performance API routing endpoints powering data transactions, user session mapping, and a direct pipeline orchestration layer to the generative AI models.
3. **Storage Engine (SQLite):** A lightweight, self-contained relational database utilizing local disk persistence (`wealth.db`) to log transactional histories with explicit foreign-key user relationships.
4. **Security Vector (Native Cryptography):** Employs safe password isolation using Python's native `hashlib.pbkdf2_hmac` SHA-256 algorithm to protect member credentials without third-party library dependencies.
5. **AI Core Strategy Network (Gemini API):** Harnesses the ultra-fast `gemini-2.5-flash` model via the modern `google-genai` SDK to evaluate structured cash-flow parameters and output deep financial playbooks.

---

## 🛠️ Tech Stack & Requirements

* **Runtime:** Python 3.11+
* **Backend framework:** FastAPI, Uvicorn
* **Frontend UI:** Streamlit, Pandas
* **Database Engine:** SQLite3
* **GenAI Interface:** `google-genai` SDK

---

## 💾 Project Repository Map

```text
AI-Wealth-Dashboard/
├── backend/
│   ├── .env                 # Protected environment API variables
│   ├── database.py          # SQLite connection and schema initializers
│   ├── main.py              # FastAPI application endpoints & AI logic
│   └── wealth.db            # Local persistent relational database file
├── frontend/
│   └── app.py               # Streamlit UI layouts and session managers
├── README.md                # System documentation manual
└── .gitignore               # System file exclusion blocks