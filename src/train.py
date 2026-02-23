# src/train.py
import argparse
import csv
from collections import Counter
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split

from nlp_extractor import _normalizar


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = BASE_DIR / "data" / "dataset.csv"
DEFAULT_MODEL_PATH = BASE_DIR / "models" / "model_bundle.joblib"


def cargar_dataset(path):
    dataset = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("id_caso", "").strip():
                continue
            dataset.append(
                {
                    "id_caso": int(row["id_caso"]),
                    "texto_paciente": row["texto_paciente"],
                    "nivel_urgencia": int(row["nivel_urgencia"]),
                }
            )
    return dataset


def preparar_datos(dataset):
    textos = []
    y = []

    for fila in dataset:
        texto = _normalizar(fila["texto_paciente"])
        if not texto:
            continue
        textos.append(texto)
        y.append(fila["nivel_urgencia"])

    return textos, y


def entrenar_y_evaluar(textos, y, test_size=0.2, random_state=42):
    if len(set(y)) < 2:
        raise ValueError("Se requieren al menos 2 clases de urgencia para entrenar.")

    x_train, x_test, y_train, y_test = train_test_split(
        textos,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    vectorizer_eval = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
    x_train_vec = vectorizer_eval.fit_transform(x_train)
    x_test_vec = vectorizer_eval.transform(x_test)

    clf_eval = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=random_state,
    )
    clf_eval.fit(x_train_vec, y_train)

    y_pred = clf_eval.predict(x_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    report = classification_report(y_test, y_pred, digits=4, zero_division=0)

    return {
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "report": report,
        "n_train": len(y_train),
        "n_test": len(y_test),
    }


def entrenar_final(textos, y, random_state=42):
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
    x_vec = vectorizer.fit_transform(textos)

    clf = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=random_state,
    )
    clf.fit(x_vec, y)

    return vectorizer, clf


def main():
    parser = argparse.ArgumentParser(description="Entrenamiento de modelo de triaje.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH), help="Ruta del CSV.")
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH), help="Ruta de salida .joblib")
    parser.add_argument("--test-size", type=float, default=0.2, help="Proporcion para test.")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria.")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    model_path = Path(args.model)

    print(f"Cargando dataset: {dataset_path}")
    dataset = cargar_dataset(dataset_path)
    textos, y = preparar_datos(dataset)

    if not textos:
        raise ValueError("No hay textos validos para entrenar.")

    distribucion = dict(sorted(Counter(y).items()))
    print(f"Total muestras utiles: {len(y)}")
    print(f"Distribucion de clases: {distribucion}")

    print("Evaluando modelo (holdout)...")
    metricas = entrenar_y_evaluar(
        textos=textos,
        y=y,
        test_size=args.test_size,
        random_state=args.seed,
    )
    print(f"Accuracy holdout: {metricas['accuracy']:.4f}")
    print(f"Macro-F1 holdout: {metricas['macro_f1']:.4f}")
    print("Reporte por clase:")
    print(metricas["report"])

    print("Entrenando modelo final con todos los datos...")
    vectorizer, clf = entrenar_final(textos=textos, y=y, random_state=args.seed)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "vectorizer": vectorizer,
        "clf": clf,
        "meta": {
            "n_samples": len(y),
            "class_distribution": distribucion,
            "test_size": args.test_size,
            "random_state": args.seed,
            "holdout_accuracy": metricas["accuracy"],
            "holdout_macro_f1": metricas["macro_f1"],
        },
    }
    joblib.dump(bundle, model_path)

    print(f"Modelo guardado en: {model_path}")
    print("Entrenamiento completado.")


if __name__ == "__main__":
    main()
