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
│   ├── __init__.py
│   └── settings.py          # Global Settings & Model Catalog
│
├── src/                     # 🧠 Source Code
│   ├── __init__.py
│   ├── backend/             # Backend Logic
│   │   ├── __init__.py
│   │   ├── knowledge_base.py    # ChromaDB Manager (RAG Logic)
│   │   └── model_engine.py      # Hugging Face Pipeline Engine
│   │
│   └── ui/                  # Frontend (Streamlit)
│       ├── __init__.py
│       ├── sidebar.py           # Sidebar Configuration Components
│       └── main_panel.py        # Main Workspace & Chat Components
│
└── data/                    # 💾 Persistent Data (Ignored by Git)
    └── chroma_store/        # Local Vector Database Storage
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

### 1\. Feeding the Knowledge Base (RAG)

1.  Open the **"📚 Feed Knowledge Base"** expander in the main panel.
2.  Paste text or upload a `.txt` file.
3.  Assign a **Topic/Tag** (e.g., "Finance", "History").
4.  Click **Save to DB**.

### 2\. Configuring the Pipeline

1.  Go to the **Sidebar** (left panel).
2.  **Context:** Select the topics you want the AI to consider for this query.
3.  **Model Pipeline:** Select a model from the dropdown and click **"➕ Add Step"**.

### 3\. Execution

1.  Type your prompt in the main workspace.
2.  Click **"🚀 Execute Pipeline"**.

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
