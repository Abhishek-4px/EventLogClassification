# Security Event Log RAG Classifier

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with Streamlit](https://img.shields.io/badge/Made_with-Streamlit-red.svg)](https://streamlit.io)

An interactive web application built with Streamlit that uses a Retrieval-Augmented Generation (RAG) pipeline to classify security event logs into standardized categories.

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Features](#-features)
- [RAG Architecture](#-rag-architecture)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Setup & Installation](#-setup--installation)
- [Steps to Run](#-steps-to-run)
- [Usage](#-usage)
- [Example Input/Output](#-example-inputoutput)
- [Configuration](#-configuration)
- [Future Improvements](#-future-improvements)
- [License](#-license)

---

## 🎯 Problem Statement

Security teams deal with thousands of security event logs daily from various sources (firewalls, IDS/IPS, authentication systems, etc.). These logs need to be classified into standardized categories for:

- **Compliance Requirements**: Meeting regulatory standards (SIEM, SOC reporting)
- **Incident Response**: Quick identification and prioritization of security events
- **Threat Detection**: Pattern recognition across different log formats
- **Automation**: Reducing manual classification effort and human error

### Challenges:
- Logs come in different formats and structures
- Manual classification is time-consuming and error-prone
- Need for consistent categorization across different log sources
- Requirement for confidence scoring to identify uncertain classifications

### Solution:
This application uses a RAG (Retrieval-Augmented Generation) pipeline to automatically classify security logs into five standardized fields:
- `eventClass`: Type of security event
- `eventOutcome`: Result of the event (success/failure)
- `eventSeverity`: Impact level
- `eventAction`: Action taken or required
- `eventCategory`: High-level category

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

## 🏗️ RAG Architecture

The application implements a Retrieval-Augmented Generation architecture with the following components:

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                               │
│  User uploads CSV with raw security log messages                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EMBEDDING LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Sentence-Transformers Model                             │  │
│  │  (all-MiniLM-L6-v2)                                      │  │
│  │  Converts text to 384-dimensional vectors               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RETRIEVAL LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FAISS Vector Database                                   │  │
│  │  • Stores knowledge base embeddings                      │  │
│  │  • Performs similarity search                            │  │
│  │  • Returns top-k relevant contexts                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AUGMENTATION LAYER                             │
│  Combines:                                                       │
│  • Original log message                                          │
│  • Retrieved context (classification rules)                      │
│  • Structured prompt template                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GENERATION LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Google Gemini LLM                                       │  │
│  │  • Analyzes log + context                               │  │
│  │  • Generates structured JSON output                     │  │
│  │  • Provides confidence score                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                │
│  Structured Classification:                                      │
│  • eventClass, eventOutcome, eventSeverity                       │
│  • eventAction, eventCategory                                    │
│  • Combined confidence score                                     │
│  • Export as JSON/CSV                                            │
└─────────────────────────────────────────────────────────────────┘
```

### Component Details

1. **Knowledge Base**: 
   - Predefined classification rules and examples
   - Covers common security event patterns
   - Encoded into vector embeddings

2. **Vector Store (FAISS)**:
   - Fast similarity search
   - Efficient indexing of embeddings
   - Low memory footprint

3. **Embedding Model**:
   - `sentence-transformers/all-MiniLM-L6-v2`
   - 384-dimensional embeddings
   - Optimized for semantic similarity

4. **LLM (Google Gemini)**:
   - Context-aware classification
   - Structured JSON output
   - Confidence estimation

5. **Hybrid Scoring**:
   - Combines vector similarity score
   - LLM confidence score
   - Weighted average for final confidence

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

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Google AI API key ([Get it here](https://ai.google.dev/))

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
# api_key = "AIzaSyDPIzRvmlT70wpmYt3LmnWxKl8QuW5K5pk"

# With this line:
api_key = st.secrets["GOOGLE_API_KEY"]
```

---

## ▶️ Steps to Run

### Method 1: Local Development

1. **Ensure all dependencies are installed**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key** in `.streamlit/secrets.toml`

3. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** to `http://localhost:8501`

### Method 2: Docker (Optional)

If you prefer using Docker:

```bash
# Build the image
docker build -t log-classifier .

# Run the container
docker run -p 8501:8501 log-classifier
```

---

## 📖 Usage

1. Open your web browser and navigate to the local URL provided (usually `http://localhost:8501`).
2. Upload your CSV file. The CSV must contain a column named `Message` with the raw log text.
3. Adjust the number of samples you want to process using the slider.
4. Click the "Run Classification" button.
5. View the results in the interactive table.
6. Use the download buttons to save the output as JSON or CSV.

---

## 📊 Example Input/Output

### Sample Input CSV

```csv
Message
"Failed login attempt for user admin from IP 192.168.1.100"
"Firewall blocked incoming connection from 10.0.0.50 on port 443"
"User john.doe successfully authenticated via SSO"
"Malware detected in file document.exe, quarantined by antivirus"
"Suspicious outbound traffic to known C2 server detected"
```

### Sample Output

**JSON Format:**
```json
[
  {
    "original_message": "Failed login attempt for user admin from IP 192.168.1.100",
    "eventClass": "Authentication Failure",
    "eventOutcome": "Failure",
    "eventSeverity": "Medium",
    "eventAction": "Alert",
    "eventCategory": "Authentication",
    "confidence": 0.89,
    "retrieval_score": 0.92,
    "llm_confidence": 0.85
  },
  {
    "original_message": "Firewall blocked incoming connection from 10.0.0.50 on port 443",
    "eventClass": "Network Access Control",
    "eventOutcome": "Blocked",
    "eventSeverity": "Low",
    "eventAction": "Block",
    "eventCategory": "Network Security",
    "confidence": 0.93,
    "retrieval_score": 0.95,
    "llm_confidence": 0.90
  },
  {
    "original_message": "User john.doe successfully authenticated via SSO",
    "eventClass": "Authentication Success",
    "eventOutcome": "Success",
    "eventSeverity": "Informational",
    "eventAction": "Allow",
    "eventCategory": "Authentication",
    "confidence": 0.96,
    "retrieval_score": 0.98,
    "llm_confidence": 0.94
  }
]
```

**CSV Format:**
| original_message | eventClass | eventOutcome | eventSeverity | eventAction | eventCategory | confidence |
|------------------|------------|--------------|---------------|-------------|---------------|------------|
| Failed login attempt for user admin from IP 192.168.1.100 | Authentication Failure | Failure | Medium | Alert | Authentication | 0.89 |
| Firewall blocked incoming connection from 10.0.0.50 on port 443 | Network Access Control | Blocked | Low | Block | Network Security | 0.93 |
| User john.doe successfully authenticated via SSO | Authentication Success | Success | Informational | Allow | Authentication | 0.96 |

### Field Descriptions

- **eventClass**: Specific type of security event (e.g., "Authentication Failure", "Malware Detection")
- **eventOutcome**: Result of the event (Success, Failure, Blocked, Detected, etc.)
- **eventSeverity**: Impact level (Critical, High, Medium, Low, Informational)
- **eventAction**: Recommended or taken action (Alert, Block, Allow, Quarantine, Investigate)
- **eventCategory**: High-level category (Authentication, Network Security, Malware, etc.)
- **confidence**: Combined score (0-1) indicating classification certainty

---

## 📝 Configuration

### Customizing the Knowledge Base

Edit the `knowledge_base` list in the `create_knowledge_base()` function in `app.py`:

```python
knowledge_base = [
    "Authentication failures indicate unsuccessful login attempts...",
    "Firewall blocks represent denied network connections...",
    # Add your custom classification rules here
]
```

### Adjusting the LLM Model

Change the `preferred_models` list in `find_working_models()`:

```python
preferred_models = [
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-pro'
]
```

### Tuning Retrieval Parameters

Modify the number of context snippets retrieved:

```python
# In classify_log method
context = self.retrieve_context(message, k=5)  # Change k value
```

### Adjusting Confidence Weighting

Modify the hybrid confidence calculation:

```python
# In classify_log method
combined_confidence = (
    0.6 * retrieval_score +  # Change weights as needed
    0.4 * llm_confidence
)
```

---

## 🔮 Future Improvements

### Short-term Enhancements
1. **Batch Processing**: Add parallel processing for large CSV files
2. **Custom Knowledge Base Upload**: Allow users to upload their own classification rules
3. **Filtering Options**: Add filters for confidence threshold and severity levels
4. **Visualization Dashboard**: Add charts for classification distribution and confidence scores
5. **Error Handling**: Improve error messages and validation

### Medium-term Enhancements
6. **Multi-language Support**: Extend to non-English security logs
7. **Fine-tuning**: Train a custom model on domain-specific security logs
8. **Active Learning**: Allow users to correct classifications and retrain
9. **API Endpoint**: Create REST API for programmatic access
10. **Real-time Processing**: Support streaming log ingestion

### Long-term Enhancements
11. **Integration with SIEM**: Connect to popular SIEM platforms
12. **Anomaly Detection**: Add unsupervised learning for novel threat detection
13. **Contextual Analysis**: Include temporal and relational analysis of events
14. **Multi-modal Input**: Support for logs with additional metadata
15. **Explainability**: Add LIME/SHAP explanations for classifications

### Performance Optimizations
- Cache embeddings for repeated queries
- Use GPU acceleration for embedding generation
- Implement incremental FAISS index updates
- Add Redis for session management
- Optimize prompt engineering for faster LLM responses

### Security Enhancements
- Add authentication and authorization
- Implement rate limiting
- Add audit logging
- Support for on-premise deployment
- Data encryption at rest and in transit

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## 📧 Contact

For questions or support, please open an issue on GitHub or contact the maintainers.

---

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **Google AI** for the Gemini API
- **Sentence-Transformers** for embedding models
- **Facebook AI** for FAISS vector search
- The open-source community for inspiration and support
