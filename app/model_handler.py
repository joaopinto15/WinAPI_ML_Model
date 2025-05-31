import joblib, json
import pandas as pd
from flask import jsonify
from .api_mapper import mapear_chamadas
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, matthews_corrcoef
import logging
import os

# Ensure the logs directory exists
os.makedirs("data", exist_ok=True)

# Configure logger
logger = logging.getLogger("ml_model_logger")
logger.setLevel(logging.INFO)

log_file = "app_events.log"

# Avoid duplicate handlers if reloaded
if not logger.hasHandlers():
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# === Definir caminhos ===
os.makedirs("data", exist_ok=True)
BUFFER_FILE = "data/buffer_treino.csv"
FULL_DATASET_FILE = "data/treino_total.csv"

# === Carregar modelos ===
MODELOS = {
    "1": {
        "model": joblib.load("models/modelo_trabalho1.pkl"),
        "vectorizer": joblib.load("models/vectorizer_trabalho1.pkl"),
        "selector": joblib.load("models/selector_trabalho1.pkl")
    },
    "2": {
        "model": joblib.load("models/modelo_trabalho2.pkl"),
        "vectorizer": joblib.load("models/vectorizer_trabalho2.pkl"),
        "selector": joblib.load("models/selector_trabalho2.pkl")
    },
    "3": {
        "model": joblib.load("models/modelo_trabalho3.pkl"),
        "vectorizer": joblib.load("models/vectorizer_trabalho3.pkl"),
        "selector": joblib.load("models/selector_trabalho3.pkl")
    }
}

def predict(request):
    raw_data = request.data.decode("utf-8").strip().split("\n")
    trabalho = request.args.get("trabalho")

    logger.info(f"Received prediction request for trabalho={trabalho} with {len(raw_data)} entries")

    if trabalho not in MODELOS:
        return jsonify({"erro": "Trabalho inválido (1, 2 ou 3)"}), 400

    obj = MODELOS[trabalho]
    vectorizer = obj["vectorizer"]
    selector = obj["selector"]
    model = obj["model"]

    resultados = []
    for i, linha in enumerate(raw_data, 1):
        try:
            entrada = json.loads(linha)
            mapped = mapear_chamadas(entrada["data"])
            seq = ','.join(mapped)
            X = vectorizer.transform([seq])
            X_sel = selector.transform(X)
            pred = model.predict(X_sel)[0]

            process_name = entrada.get("process_name", "unknown")
            pid = entrada.get("pid", "unknown")
            resultados.append({
                "prediction": {
                    "entrada": i,
                    "previsao": "Malware" if pred == 1 else "Goodware",
                    "process_name": process_name,
                    "pid": pid
                }
            })
        except Exception as e:
            resultados.append({
                "entrada": i,
                "erro": str(e)
            })

    return jsonify(resultados)

def train_buffer(request):
    raw_lines = request.data.decode("utf-8").strip().split("\n")
    registros = []

    for linha in raw_lines:
        try:
            obj = json.loads(linha)
            mapped = mapear_chamadas(obj["data"])
            label = obj["malware"]

            linha_dict = {}
            for i in range(100):  # padding até 100 chamadas
                linha_dict[f"t_{i}"] = mapped[i] if i < len(mapped) else -1
            linha_dict["malware"] = label

            registros.append(linha_dict)
        except Exception as e:
            return jsonify({"erro": str(e)}), 400

    df_novos = pd.DataFrame(registros)

    if os.path.exists(BUFFER_FILE):
        df_novos.to_csv(BUFFER_FILE, mode='a', header=False, index=False)
    else:
        df_novos.to_csv(BUFFER_FILE, index=False)  # inclui header na primeira vez

    return jsonify({"mensagem": f"{len(df_novos)} amostras adicionadas ao buffer com header."})

def train_start():
    if not os.path.exists(BUFFER_FILE):
        return jsonify({"erro": "O buffer está vazio."}), 400

    df_buffer = pd.read_csv(BUFFER_FILE)

    if os.path.exists(FULL_DATASET_FILE):
        df_antigo = pd.read_csv(FULL_DATASET_FILE)
        df_total = pd.concat([df_antigo, df_buffer], ignore_index=True)
    else:
        df_total = df_buffer

    df_total.to_csv(FULL_DATASET_FILE, index=False)
    os.remove(BUFFER_FILE)

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df_total["sequencia"])
    y = df_total["malware"].values

    selector = SelectKBest(chi2, k=int(X.shape[1] * 0.3))
    X_sel = selector.fit_transform(X, y)
    X_train, X_test, y_train, y_test = train_test_split(X_sel, y, test_size=0.3, stratify=y)

    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    joblib.dump(model, "models/modelo_trabalho2.pkl")
    joblib.dump(vectorizer, "models/vectorizer_trabalho2.pkl")
    joblib.dump(selector, "models/selector_trabalho2.pkl")

    return jsonify({
        "mensagem": "Modelo re-treinado com sucesso.",
        "n_total": len(df_total),
        "accuracy": round(accuracy_score(y_test, y_pred), 3),
        "mcc": round(matthews_corrcoef(y_test, y_pred), 3)
    })
