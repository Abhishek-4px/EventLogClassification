# Security Event Log RAG Classifier

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with Streamlit](https://img.shields.io/badge/Made_with-Streamlit-red.svg)](https://streamlit.io)

An interactive web application built with Streamlit that uses a Retrieval-Augmented Generation (RAG) pipeline to classify security event logs into standardized categories.

---

## 📋 Table of Contents

- [Features](#-features)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Setup & Installation](#-setup--installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [License](#-license)

---

## ✨ Features

-   **Interactive UI**: Simple and intuitive web interface powered by Streamlit.
-   **CSV Upload**: Easily upload your log files in `.csv` format.
-   **RAG Pipeline**: Leverages a state-of-the-art RAG architecture for intelligent log classification.
-   **Vector Search**: Uses **FAISS** for efficient similarity search to find relevant context for each log.
-   **LLM-Powered Classification**: Utilizes **Google's Gemini models** to reason over log data and provide structured output.
-   **Downloadable Results**: Export the classification results in both **JSON** and **CSV** formats.
-   **Combined Confidence Score**: Calculates a hybrid confidence score based on both vector similarity and the LLM's own confidence.

---

## 🧠 How It Works

The application follows a Retrieval-Augmented Generation (RAG) pipeline to classify each log message:

1.  **Knowledge Base Creation**: A predefined set of classification rules and descriptions is encoded into vector embeddings using `sentence-transformers`.
2.  **Vector Database**: These embeddings are stored in a **FAISS** index for fast and efficient retrieval.
3.  **User Input**: The user uploads a CSV file containing raw log messages.
4.  **Retrieval**: For each log message, the system creates an embedding and queries the FAISS index to retrieve the most semantically similar rules and context from the knowledge base.
5.  **Generation**: The original log message, along with the retrieved context, is passed to a Google Gemini model within a structured prompt.
6.  **Output**: The LLM analyzes the information and generates a structured JSON object containing the classification for the 5 required fields (`eventClass`, `eventOutcome`, etc.) and a confidence score.

---

## 🛠️ Tech Stack

-   **Frontend**: [Streamlit](https://streamlit.io/)
-   **Backend**: Python
-   **Data Handling**: [Pandas](https://pandas.pydata.org/)
-   **Language Model**: [Google Gemini](https://ai.google.dev/)
-   **Embedding Model**: [Sentence-Transformers](https://www.sbert.net/)
-   **Vector Database**: [FAISS (Facebook AI Similarity Search)](https://faiss.ai/)

---

## 🚀 Setup & Installation

Follow these steps to set up and run the project locally.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Create a `requirements.txt` file with the following content:
```
streamlit
pandas
faiss-cpu
sentence-transformers
google-generativeai
```

Then, install the packages:
```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key

This project requires a Google AI API key. For security, do not hardcode your key in `app.py`. Use Streamlit's secrets management.

Create a folder and file: `.streamlit/secrets.toml`

Add your API key to the `secrets.toml` file:
```toml
# .streamlit/secrets.toml
GOOGLE_API_KEY = "AIzaSy..."
```

In `app.py`, replace the hardcoded API key with a call to Streamlit secrets:
```python
# In app.py, replace this line:
# api_key = "YYOU_GEMINI_API_KEY"

# With this line:
api_key = st.secrets["GOOGLE_API_KEY"]
```

---

## 📖 Usage

Run the Streamlit application from your terminal:
```bash
streamlit run app.py
```

1. Open your web browser and navigate to the local URL provided (usually `http://localhost:8501`).
2. Upload your CSV file. The CSV must contain a column named `Message` with the raw log text.
3. Adjust the number of samples you want to process.
4. Click the "Run Classification" button.
5. View the results in the interactive table and use the download buttons to save the output.

---

## 📝 Configuration

- **Knowledge Base**: You can customize the classification rules by editing the `knowledge_base` list inside the `create_knowledge_base()` function in `app.py`.
- **LLM Model**: The script automatically finds a working Gemini model. You can change the `preferred_models` list in `find_working_models()` to prioritize different versions.
- **Retriever**: The number of context snippets retrieved can be adjusted by changing the `k` value in the `classify_log` method call to `retrieve_context`.

---

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.
