# pItAgorin

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.10-yellow)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://www.docker.com/)

**pItAgorin** is a modular AI orchestration platform designed to execute Hugging Face models sequentially while leveraging a **Local Knowledge Base (RAG)**.

It allows users to build dynamic pipelines (e.g., *Summarization -> Translation*) and augment prompts with private data stored locally in a vector database, all through a user-friendly **Streamlit** interface.

> **License Warning:** This project is released under the **GNU General Public License v3.0**. You are free to copy, distribute, and modify the software as long as you track changes/dates in source files and keep modifications under GPLv3.

---

## ✨ Key Features

* **🧠 Local RAG (Retrieval-Augmented Generation):** Store and retrieve information from a local **ChromaDB** vector store. No external APIs required.
* **⛓️ Sequential Model Chaining:** Connect multiple Hugging Face models. The output of *Model A* automatically becomes the input for *Model B*.
* **🐳 Fully Dockerized:** Deployed via Docker Compose with volume persistence for both the database and the downloaded models.
* **🧩 Modular Architecture:** Clean separation between UI, Backend Logic, and Configuration.
* **📂 Multi-Modal Input:** Support for text and file ingestion to feed the knowledge base.



---

## 🤖 Available Models

By default, **pItAgorin** comes pre-configured with the following optimized models for local execution. These are defined in `config/settings.py`.

| Name | Task | Model ID (Hugging Face) | Description |
| :--- | :--- | :--- | :--- |
| **Assistant** | `text2text-generation` | `google/flan-t5-base` | A versatile model good for answering questions and following instructions. |
| **Translator** | `translation_en_to_es` | `Helsinki-NLP/opus-mt-en-es` | Specialized model for translating English text to Spanish. |
| **Summarizer** | `summarization` | `sshleifer/distilbart-cnn-12-6` | Creates concise summaries from long texts. |

### ➕ How to add new models?
You can easily extend the capabilities by editing the `config/settings.py` file. Add a new entry to the `MODEL_CATALOG` dictionary:

```python
MODEL_CATALOG = {
    # ... existing models ...
    "My New Model": {
        "task": "text-generation", 
        "model_id": "gpt2" 
    }
}
```
Aquí tienes el archivo README.md completamente actualizado.

He añadido dos nuevas secciones importantes:

🔌 Database Configuration: Explica cómo crear el archivo .env para conectar bases de datos SQL y Mongo.

⚡ GPU Acceleration: Explica cómo configurar Docker para usar tu tarjeta gráfica NVIDIA.

Markdown

# 🐍 pItAgorin

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.10-yellow)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://www.docker.com/)
[![GPU Support](https://img.shields.io/badge/NVIDIA-CUDA-green)](https://developer.nvidia.com/cuda-zone)

**pItAgorin** is a modular AI orchestration platform designed to execute Hugging Face models sequentially while leveraging a **Local Knowledge Base (RAG)**.

It allows users to build dynamic pipelines (e.g., *Summarization -> Translation*) and augment prompts with private data stored locally in a vector database or fetched dynamically from **SQL/NoSQL databases**, all through a user-friendly **Streamlit** interface.

> **License Warning:** This project is released under the **GNU General Public License v3.0**. You are free to copy, distribute, and modify the software as long as you track changes/dates in source files and keep modifications under GPLv3.

---

## ✨ Key Features

* **🧠 Local RAG (Retrieval-Augmented Generation):** Store and retrieve information from a local **ChromaDB** vector store.
* **🗄️ Universal Data Ingestion:** Import data from Text, PDF, Word, CSV, JSON, XML, **SQL Databases** (Postgres, MySQL), and **MongoDB**.
* **⛓️ Sequential Model Chaining:** Connect multiple Hugging Face models. The output of *Model A* automatically becomes the input for *Model B*.
* **🐳 Fully Dockerized:** Deployed via Docker Compose with volume persistence.
* **⚡ GPU Ready:** Optimized to use NVIDIA GPUs via Docker for faster inference.
* **🎨 Cyberpunk UI:** A sleek, dark-themed interface optimized for prompt engineering.

-----

## 📂 Project Structure
The project follows a modular architecture:

```text
pItAgorin/
│
├── app.py                   # 🚀 Main Application Entry Point
├── docker-compose.yml       # 🐙 Docker Orchestration (Services & Volumes)
├── Dockerfile               # 🐳 Container Definition
├── requirements.txt         # 📦 Python Dependencies
├── .gitignore               # 🙈 Git Ignore Rules
│
├── config/                  # ⚙️ Configuration
│   └── settings.py          # Global Settings & Model Catalog
│
├── src/                     # 🧠 Source Code
│   ├── backend/             # Backend Logic
│   │   ├── db_connectors.py     # SQL/Mongo Connectors
│   │   ├── parsers.py           # File Parsers (PDF, JSON, etc.)
│   │   ├── knowledge_base.py    # ChromaDB Manager (RAG Logic)
│   │   └── model_engine.py      # Hugging Face Pipeline Engine
│   │
│   └── ui/                  # Frontend (Streamlit)
│       ├── assets/              # Images & Logos
│       ├── layout.py            # UI Orchestrator
│       ├── sidebar.py           # Sidebar Configuration Components
│       └── main_panel.py        # Main Workspace & Chat Components
│
└── data/                    # 💾 Persistent Data (Ignored by Git)
    └── chroma_store/        # Local Vector Database Storage
```

---

## 🤖 Available Models

By default, **pItAgorin** comes pre-configured with the following optimized models. You can add more in `config/settings.py`.

| Name | Task | Model ID (Hugging Face) | Description |
| :--- | :--- | :--- | :--- |
| **Assistant** | `text2text-generation` | `google/flan-t5-base` | A versatile model good for answering questions. |
| **Translator** | `translation_en_to_es` | `Helsinki-NLP/opus-mt-en-es` | Specialized model for translating English to Spanish. |
| **Summarizer** | `summarization` | `sshleifer/distilbart-cnn-12-6` | Creates concise summaries from long texts. |

---

## 🔌 Database Configuration (SQL & Mongo)

To connect **pItAgorin** to your external databases, do not modify the code. Instead, create a **`.env`** file in the project root and define your credentials there.

1.  Create a file named `.env` in the root folder.
2.  Add your connection details following this template:

```ini
# .env file

# --- SQL Database Configuration (MySQL, PostgreSQL, etc.) ---
DB_SQL_HOST=localhost
DB_SQL_PORT=5432
DB_SQL_USER=admin
DB_SQL_PASS=your_secure_password
DB_SQL_NAME=production_db

# --- MongoDB Configuration ---
DB_MONGO_URI=mongodb://user:pass@mongo-server:27017/
DB_MONGO_DEFAULT_DB=analytics_db
```

-----

## 🚀 Quick Start (Docker)

The recommended way to run **pItAgorin** is via Docker to ensure all system dependencies (like `sentencepiece` or `torch` libraries) are correctly isolated.

### 1\. Clone the Repository

```bash
git clone [https://github.com/amarala931/pItAgorin.git](https://github.com/amarala931/pItAgorin.git)
cd pItAgorin
```

### 2\. Build and Run

This command builds the image and starts the container. It uses volumes to persist your Knowledge Base (`./data`) and cache Hugging Face models (`hf_cache`), so you don't have to re-download them on restart.

```bash
docker-compose up --build
```

### 3\. Access the App

Open your browser and navigate to:
👉 **http://localhost:8501**

-----

## 💻 Local Installation (Manual)

If you prefer running it directly on your host machine (Python 3.10+ required):

1.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the App:**

    ```bash
    streamlit run app.py
    ```

-----

## 📖 Usage Guide

### 1. Feeding the Knowledge Base (RAG)
**pItAgorin** allows you to ingest knowledge from three different sources via the main panel:

* **✍️ Manual Text:** Paste raw text directly.
* **📁 Upload File:** Supports rich documents and structured data.
    * *Documents:* `.pdf`, `.docx`, `.txt`, `.md`
    * *Data:* `.csv`, `.json`, `.yaml`, `.xml` (Automatically formatted for LLM readability).
* **🗄️ Databases:** Select a pre-configured SQL or NoSQL connection, write your query (e.g., `SELECT * FROM users`), and preview the data before ingesting it.

**Tagging your Data:**
Use the **Unified Input Field**:
* **Type** to create a new topic tag.
* **Click a "Pill"** below the input to quickly select an existing topic.

Click **💾 Save** to vectorize and store the content in ChromaDB.

### 2. Configuring the Pipeline (Sidebar)
1.  **RAG Context:** Select the specific **Topics** you want the AI to access for this session (e.g., select "Finance" to ignore "HR" documents).
2.  **Build the Chain:**
    * Choose a model from the dropdown (e.g., `Assistant`).
    * Click **"➕ Add Step"**.
    * Repeat to chain models (e.g., *Summarizer* -> *Translator*).

### 3. Advanced Prompt Engineering (The "Cockpit")
Before executing, expand the **"⚙️ Advanced Prompt Engineering"** section in the main workspace to supercharge your prompt:

* **🎭 Role / Persona:** Define who the AI is (e.g., *"Senior Data Scientist"*).
* **🎯 Target Audience:** Define who the answer is for (e.g., *"Executive Board"*).
* **🎨 Tone & Style:** Choose a vibe (e.g., *Socratic, Formal, ELI5*).
* **📝 Output Format:** Force specific structures (e.g., *Markdown Table, JSON, Python Code*).
* **🚫 Constraints:** Set negative rules (e.g., *"No preambles", "No passive voice"*).

**pItAgorin** will automatically assemble these parameters into a robust "System Prompt".

### 4. Execution
1.  Type your main instruction in the **Workspace** text area.
2.  Click **"🚀 Execute Pipeline"**.

The system will:
1.  **Retrieve** relevant context from the Local DB (RAG).
2.  **Construct** the Mega-Prompt (Context + System Instructions + User Task).
3.  **Execute** the defined Model Pipeline sequentially.

-----
👥 Contributors
We would like to thank the following people for their contributions to the project:

* Alberto Márquez Alarcón  [@amarala931](https://github.com/amarala931)

-----

## ⚖️ License

**pItAgorin** is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License** as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see [https://www.gnu.org/licenses/](https://www.gnu.org/licenses/).

Copyright (C) 2023-2024 pItAgorin Contributors.
