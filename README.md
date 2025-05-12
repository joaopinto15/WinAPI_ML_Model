# 🛡️ WinAPI Behavior-based Malware Detection

This repository provides a complete infrastructure for the **detection of malicious behavior in Windows environments** through the **monitoring and classification of WinAPI call sequences** using **supervised machine learning** techniques. The goal is to identify patterns of execution typically associated with malware based on dynamic behavioral traces.

## 🎯 Project Overview

The system is designed to track sequences of Windows API calls invoked by processes, normalize them, and classify the behavior as either **malicious (malware)** or **benign (goodware)**.

API calls are first mapped to numerical indices using a reference dictionary (`api_map.json`). Sequences are standardized to fixed-length vectors (typically 100 API calls), padded as necessary, and stored in structured tabular format with columns `t_0` to `t_99` and a corresponding `malware` label.

## 🧠 Machine Learning Pipeline

- **Vectorization**: Using `CountVectorizer` (binary, frequency, or TF-IDF depending on the model).
- **Feature selection**: `SelectKBest` with `chi2` test.
- **Classifiers**:
  - Ensemble Voting Classifier (Hammi et al.)
  - Lightweight Random Forest, SVM, and KNN (Daeef et al.)
  - TF-IDF + Ensemble inspired by MalAnalyser

## 🔌 API Endpoints

The backend is implemented with Flask and exposes:

- `POST /train-buffer` – Buffer new labeled samples.
- `POST /train-start` – Retrain the selected model from the full dataset.
- `POST /predict?trabalho=X` – Predict using model 1, 2, or 3.

## 💾 Data Handling

- Buffered data is stored in `data/buffer_treino.csv`
- All training data accumulates in `data/treino_total.csv`
- Models are saved under the `models/` directory:
  - `modelo_trabalhoX.pkl`
  - `vectorizer_trabalhoX.pkl`
  - `selector_trabalhoX.pkl`

## 📂 Available Datasets

You can use or adapt publicly available WinAPI behavioral datasets, such as:

- [WinAPI_100Sequences_Balanced](https://www.kaggle.com/code/joaopinto15/winapi-100sequences-balanced/output)
  - mapping: `api_map.json`
  - training: `all_data_combined.csv`
- [Malware Analysis Datasets: API Call Sequences](https://ieee-dataport.org/open-access/malware-analysis-datasets-api-call-sequences)
  - dataset: `malware-analysis-datasets-api-call-sequences.csv`

Alternatively, you may generate your own dynamic traces using tools like Sysmon, Cuckoo Sandbox, or CAPEv2.


- Buffered data is stored in `data/buffer_treino.csv`
- All training data accumulates in `data/treino_total.csv`
- Models are saved under the `models/` directory:
  - `modelo_trabalhoX.pkl`
  - `vectorizer_trabalhoX.pkl`
  - `selector_trabalhoX.pkl`

## 🚀 Use Cases

- Host-based Intrusion Detection Systems (HIDS)
- Dynamic malware analysis
- Continuous behavior monitoring on Windows endpoints

## 🧩 Extendability

The system is modular and easily extendable for:
- Additional features (e.g., arguments, API categories)
- Real-time streaming input
- Deployment in production using Gunicorn + Nginx

---

**Maintainer:** João Pinto
**License:** MIT (or your choice)
