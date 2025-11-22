import os
import json
import re
import time
import warnings
import pandas as pd
import faiss
import io

from sentence_transformers import SentenceTransformer
import google.generativeai as genai

warnings.filterwarnings('ignore') 

def create_knowledge_base():
    knowledge_base = [
        "eventClass 'System' refers to events related to system operations, startup, shutdown, and core system functions.",
        "eventClass 'Security' refers to events involving authentication, authorization, account management, and security audits.",
        "eventClass 'Application' refers to events related to application lifecycle, crashes, and software operations.",
        "eventClass 'Network' refers to events related to network connectivity, adapters, and network services.",
        "eventClass 'Hardware' refers to events related to hardware components, drivers, and device operations.",
        "eventOutcome 'Success' indicates the operation completed successfully without errors.",
        "eventOutcome 'Failure' indicates the operation failed to complete due to an error or issue.",
        "eventOutcome 'Warning' indicates the operation completed with warnings or potential issues.",
        "eventOutcome 'Information' indicates informational message about system status or operation progress.",
        "eventSeverity 1 is for informational events that provide general information about system operations.",
        "eventSeverity 2 is for low severity events that indicate minor issues not affecting system functionality.",
        "eventSeverity 3 is for medium severity events that may affect some functionality but system remains operational.",
        "eventSeverity 4 is for high severity events that may affect critical system functionality.",
        "eventSeverity 5 is for critical events that may cause system failure or security breach.",
        "eventDeviceCat 'Server' refers to server systems that provide services to clients.",
        "eventDeviceCat 'Workstation' refers to client machines used by end users.",
        "eventDeviceCat 'Network Device' refers to network infrastructure devices like switches, routers, and firewalls.",
        "eventDeviceCat 'Storage' refers to storage devices and systems.",
        "eventDeviceCat 'Security Device' refers to security-related devices and software.",
        "eventDeviceCat 'Application Server' refers to servers running specific applications.",
        "eventOperation 'Create' refers to operations that create new resources or entities.",
        "eventOperation 'Delete' refers to operations that remove resources or entities.",
        "eventOperation 'Modify' refers to operations that change existing resources or entities.",
        "eventOperation 'Read' refers to operations that read or retrieve information.",
        "eventOperation 'Login' refers to user authentication and session establishment.",
        "eventOperation 'Logout' refers to user session termination.",
        "eventOperation 'Start' refers to operations that initiate services or processes.",
        "eventOperation 'Stop' refers to operations that terminate services or processes.",
        "eventOperation 'Restart' refers to operations that restart services or systems.",
        "eventOperation 'Install' refers to operations that install software or updates.",
        "eventOperation 'Update' refers to operations that update existing software or configurations.",
        "eventOperation 'Scan' refers to operations that scan or check system resources."
    ]
    with open('knowledge_base.txt', 'w') as f:
        for line in knowledge_base:
            f.write(line + '\n')
    return knowledge_base

def build_vector_database():
    with open('knowledge_base.txt', 'r') as f:
        knowledge_lines = f.readlines()
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(knowledge_lines)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    faiss.write_index(index, 'faiss_index.bin')
    with open('knowledge_lines.json', 'w') as f:
        json.dump([line.strip() for line in knowledge_lines], f)
    return index, [line.strip() for line in knowledge_lines]

def find_working_models(api_key):
    genai.configure(api_key=api_key)
    working_models = []
    preferred_models = [
        'models/gemini-2.5-flash','models/gemini-2.5-pro','models/gemini-2.0-flash',
        'models/gemini-2.0-flash-lite','models/gemini-2.5-flash-preview-05-20','models/gemini-2.5-flash-lite-preview-06-17'
    ]
    for model_name in preferred_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, respond with just 'Test successful'")
            working_models.append(model_name)
            if len(working_models) >= 1:
                break
        except Exception:
            continue
    return working_models


class RAGLogClassifier:
    def __init__(self, api_key, working_models):
        self.api_key = api_key
        self.working_models = working_models
        genai.configure(api_key=api_key)
        self.model_name = working_models[0]
        self.llm = genai.GenerativeModel(self.model_name)
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.index = faiss.read_index('faiss_index.bin')
        with open('knowledge_lines.json', 'r') as f:
            self.knowledge_lines = json.load(f)

    def retrieve_context(self, query, k=5):
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, k)
        context = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.knowledge_lines):
                context.append({
                    "text": self.knowledge_lines[idx],
                    "distance": float(distance),
                    "rank": i + 1
                })
        return context

    def classify_log(self, log_message):
        context = self.retrieve_context(log_message, k=5)
        context_text = "\n".join([f"{c['rank']}. {c['text']}" for c in context])
        similarity_scores = [1 / (1 + c['distance']) for c in context]
        vector_confidence = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
        prompt = f"""
You are a security log classification expert. Based on the provided knowledge base and the log message, classify the log into the following fields:

Knowledge Base:
{context_text}

Log Message: "{log_message}"

Please analyze the log message and provide a classification in JSON format with the following structure:
{{
    "eventClass": "...",
    "eventOutcome": "...",
    "eventSeverity": "...",
    "eventDeviceCat": "...",
    "eventOperation": "...",
    "confidence": "..."
}}

Where:
- eventClass is one of: System, Security, Application, Network, Hardware
- eventOutcome is one of: Success, Failure, Warning, Information
- eventSeverity is a number from 1 to 5 (1=Informational, 5=Critical)
- eventDeviceCat is one of: Server, Workstation, Network Device, Storage, Security Device, Application Server
- eventOperation is one of: Create, Delete, Modify, Read, Login, Logout, Start, Stop, Restart, Install, Update, Scan
- confidence is a number from 0.0 to 1.0 indicating your confidence in the classification

Only respond with the JSON object, nothing else.
"""
        try:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.llm.generate_content(prompt)
                    response_text = response.text
                    break
                except Exception as e:
                    if "quota" in str(e).lower() and attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    else:
                        raise e
            json_match = re.search(r'``````', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    return {"error": "Could not extract JSON from LLM response"}
            classification = json.loads(json_str)
            llm_confidence = float(classification.get("confidence", 0.0))
            combined_confidence = (llm_confidence + vector_confidence) / 2
            classification["vector_confidence"] = round(vector_confidence, 3)
            classification["combined_confidence"] = round(combined_confidence, 3)
            if combined_confidence < 0.4:
                classification.update({
                    "eventClass": "unknown","eventOutcome": "unknown","eventSeverity": 0,
                    "eventDeviceCat": "unknown","eventOperation": "unknown","confidence": combined_confidence})
            return classification
        except Exception as e:
            return {"error": f"Error processing LLM response: {str(e)}"}

api_key = "YOUR_API_KEY"
create_knowledge_base()
build_vector_database()
working_models = find_working_models(api_key)
classifier = RAGLogClassifier(api_key, working_models)

import streamlit as st

st.title("Event Log RAG Classification")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
sample_limit = st.number_input("Number of samples", value=10, min_value=1, max_value=100)

if st.button("Run Classification"):
    if uploaded_file is None:
        st.warning("Please upload a CSV file!")
    else:
        raw_bytes = uploaded_file.read()
        encodings = ['cp1252', 'utf-8', 'latin1']
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(io.StringIO(raw_bytes.decode(enc)))
                break
            except Exception:
                continue
        if df is None or 'Message' not in df.columns:
            st.error("Could not read your CSV or missing 'Message' column.")
        else:
            st.info(f"Classifying up to {min(sample_limit, len(df))} samples")
            results = []
            for i, row in enumerate(df.iloc[:sample_limit].itertuples()):
                classification = classifier.classify_log(row.Message)
                result = {
                    "event_id": getattr(row, 'eventid', i + 1 if hasattr(row, 'eventid') else i + 1),
                    "eventClass": classification.get("eventClass", "unknown"),
                    "eventDeviceCat": classification.get("eventDeviceCat", "unknown"),
                    "eventOperation": classification.get("eventOperation", "unknown"),
                    "eventOutcome": classification.get("eventOutcome", "unknown"),
                    "eventSeverity": int(classification.get("eventSeverity", classification.get("severity", 0)) or 0),
                    "confidence": round(float(classification.get("combined_confidence", classification.get("confidence", 0.0))),3),
                    "fallbackApplied": classification.get("eventClass", "") == "unknown"
                }
                results.append(result)
                time.sleep(1)
            st.dataframe(pd.DataFrame(results))
            json_out = json.dumps(results, indent=2)
            csv_out = pd.DataFrame(results).to_csv(index=False)
            st.download_button("Download JSON", json_out, file_name="classified_output.json", mime="application/json")
            st.download_button("Download CSV", csv_out, file_name="classified_output.csv", mime="text/csv")

