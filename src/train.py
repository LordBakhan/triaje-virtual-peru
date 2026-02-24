# src/train.py
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib
from sklearn import __version__ as sklearn_version
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split

from catalogo_sintomas import CATALOGO_SINTOMAS
from nlp_extractor import _normalizar


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = BASE_DIR / "data" / "dataset.csv"
DEFAULT_MODEL_PATH = BASE_DIR / "models" / "model_bundle.joblib"
DEFAULT_REPORT_PATH = BASE_DIR / "models" / "train_report.json"


def cargar_dataset(path):
    dataset = []
    filas_invalidas = 0
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"id_caso", "texto_paciente", "nivel_urgencia"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                "El CSV no contiene columnas requeridas: "
                + ", ".join(sorted(missing))
            )
        for row in reader:
            if not row.get("id_caso", "").strip():
                filas_invalidas += 1
                continue
            try:
                id_caso = int(row["id_caso"])
                texto_paciente = str(row.get("texto_paciente", "")).strip()
                nivel_urgencia = int(row["nivel_urgencia"])
                if nivel_urgencia not in {1, 2, 3}:
                    filas_invalidas += 1
                    continue
                if not texto_paciente:
                    filas_invalidas += 1
                    continue
            except (TypeError, ValueError, KeyError):
                filas_invalidas += 1
                continue

            dataset.append(
                {
                    "id_caso": id_caso,
                    "texto_paciente": texto_paciente,
                    "nivel_urgencia": nivel_urgencia,
                }
            )
    return dataset, filas_invalidas


def preparar_datos(dataset):
    textos = []
    y = []
    omitidos = 0

    for fila in dataset:
        texto = _normalizar(fila["texto_paciente"])
        if not texto:
            omitidos += 1
            continue
        textos.append(texto)
        y.append(fila["nivel_urgencia"])

    return textos, y, omitidos


def entrenar_y_evaluar(textos, y, test_size=0.2, random_state=42):
    if not 0 < test_size < 1:
        raise ValueError("--test-size debe estar entre 0 y 1 (exclusivo).")
    if len(set(y)) < 2:
        raise ValueError("Se requieren al menos 2 clases de urgencia para entrenar.")

    try:
        x_train, x_test, y_train, y_test = train_test_split(
            textos,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y,
        )
    except ValueError as exc:
        raise ValueError(
            f"No se pudo crear holdout estratificado. Ajusta dataset/test-size. Detalle: {exc}"
        ) from exc

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
    report_dict = classification_report(y_test, y_pred, zero_division=0, output_dict=True)
    cm = confusion_matrix(y_test, y_pred, labels=sorted(set(y)))

    return {
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "report": report,
        "report_dict": report_dict,
        "confusion_matrix": cm.tolist(),
        "n_train": len(y_train),
        "n_test": len(y_test),
        "test_distribution": dict(sorted(Counter(y_test).items())),
    }


def evaluar_cv(textos, y, n_splits=5, random_state=42):
    if n_splits < 2:
        raise ValueError("--cv-splits debe ser >= 2.")
    min_class_count = min(Counter(y).values())
    n_splits_real = min(n_splits, min_class_count)
    if n_splits_real < 2:
        return None

    skf = StratifiedKFold(n_splits=n_splits_real, shuffle=True, random_state=random_state)
    acc_scores = []
    f1_scores = []

    for train_idx, test_idx in skf.split(textos, y):
        x_train = [textos[i] for i in train_idx]
        y_train = [y[i] for i in train_idx]
        x_test = [textos[i] for i in test_idx]
        y_test = [y[i] for i in test_idx]

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        x_train_vec = vectorizer.fit_transform(x_train)
        x_test_vec = vectorizer.transform(x_test)

        clf = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=random_state,
        )
        clf.fit(x_train_vec, y_train)
        y_pred = clf.predict(x_test_vec)

        acc_scores.append(float(accuracy_score(y_test, y_pred)))
        f1_scores.append(float(f1_score(y_test, y_pred, average="macro")))

    acc_mean = sum(acc_scores) / len(acc_scores)
    f1_mean = sum(f1_scores) / len(f1_scores)
    acc_std = (sum((x - acc_mean) ** 2 for x in acc_scores) / len(acc_scores)) ** 0.5 if len(acc_scores) > 1 else 0.0
    f1_std = (sum((x - f1_mean) ** 2 for x in f1_scores) / len(f1_scores)) ** 0.5 if len(f1_scores) > 1 else 0.0

    return {
        "n_splits": n_splits_real,
        "accuracy_mean": acc_mean,
        "accuracy_std": acc_std,
        "macro_f1_mean": f1_mean,
        "macro_f1_std": f1_std,
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


def guardar_reporte_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Entrenamiento de modelo de triaje.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH), help="Ruta del CSV.")
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH), help="Ruta de salida .joblib")
    parser.add_argument("--test-size", type=float, default=0.2, help="Proporcion para test.")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria.")
    parser.add_argument("--cv-splits", type=int, default=5, help="Numero de folds para CV.")
    parser.add_argument(
        "--report-json",
        default=str(DEFAULT_REPORT_PATH),
        help="Ruta para guardar reporte JSON de entrenamiento.",
    )
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    model_path = Path(args.model)
    report_path = Path(args.report_json)
    if not dataset_path.exists():
        raise FileNotFoundError(f"No existe dataset: {dataset_path}")
    if args.cv_splits < 2:
        raise ValueError("--cv-splits debe ser >= 2.")

    print(f"Cargando dataset: {dataset_path}")
    dataset, filas_invalidas = cargar_dataset(dataset_path)
    textos, y, textos_omitidos = preparar_datos(dataset)

    if not textos:
        raise ValueError("No hay textos validos para entrenar.")

    distribucion = dict(sorted(Counter(y).items()))
    dataset_hash = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    min_class = min(distribucion.values())
    clase_mayoritaria, n_mayoritaria = max(distribucion.items(), key=lambda x: x[1])
    baseline_acc = n_mayoritaria / len(y)
    print(f"Total muestras utiles: {len(y)}")
    print(f"Filas invalidas/omitidas en carga: {filas_invalidas}")
    print(f"Textos omitidos por normalizacion vacia: {textos_omitidos}")
    print(f"Distribucion de clases: {distribucion}")
    print(f"Minimo por clase: {min_class}")
    print(
        f"Baseline (clase mayoritaria={clase_mayoritaria}): "
        f"{baseline_acc:.4f}"
    )

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
    print(f"Distribucion en test: {metricas['test_distribution']}")
    print("Matriz de confusion (holdout):")
    print(metricas["confusion_matrix"])

    metricas_cv = evaluar_cv(
        textos=textos,
        y=y,
        n_splits=args.cv_splits,
        random_state=args.seed,
    )
    if metricas_cv is None:
        print("CV omitida: no hay suficientes muestras por clase.")
    else:
        print(
            f"CV ({metricas_cv['n_splits']} folds) | "
            f"Accuracy: {metricas_cv['accuracy_mean']:.4f} +/- {metricas_cv['accuracy_std']:.4f} | "
            f"Macro-F1: {metricas_cv['macro_f1_mean']:.4f} +/- {metricas_cv['macro_f1_std']:.4f}"
        )

    print("Entrenando modelo final con todos los datos...")
    vectorizer, clf = entrenar_final(textos=textos, y=y, random_state=args.seed)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    trained_at = datetime.now(timezone.utc).isoformat()
    bundle = {
        "vectorizer": vectorizer,
        "clf": clf,
        "meta": {
            "n_samples": len(y),
            "class_distribution": distribucion,
            "majority_class": clase_mayoritaria,
            "majority_baseline_accuracy": baseline_acc,
            "test_size": args.test_size,
            "random_state": args.seed,
            "cv_splits_requested": args.cv_splits,
            "holdout_accuracy": metricas["accuracy"],
            "holdout_macro_f1": metricas["macro_f1"],
            "holdout_confusion_matrix": metricas["confusion_matrix"],
            "cv_metrics": metricas_cv,
            "dataset_path": str(dataset_path.resolve()),
            "dataset_sha256": dataset_hash,
            "catalog_size": len(CATALOGO_SINTOMAS),
            "filas_invalidas": filas_invalidas,
            "textos_omitidos": textos_omitidos,
            "trained_at_utc": trained_at,
            "sklearn_version": sklearn_version,
        },
    }
    joblib.dump(bundle, model_path)

    reporte_payload = {
        "trained_at_utc": trained_at,
        "dataset_path": str(dataset_path.resolve()),
        "dataset_sha256": dataset_hash,
        "n_samples": len(y),
        "class_distribution": distribucion,
        "majority_class": clase_mayoritaria,
        "majority_baseline_accuracy": baseline_acc,
        "filas_invalidas": filas_invalidas,
        "textos_omitidos": textos_omitidos,
        "holdout": {
            "accuracy": metricas["accuracy"],
            "macro_f1": metricas["macro_f1"],
            "n_train": metricas["n_train"],
            "n_test": metricas["n_test"],
            "test_distribution": metricas["test_distribution"],
            "confusion_matrix": metricas["confusion_matrix"],
            "classification_report": metricas["report_dict"],
        },
        "cv": metricas_cv,
        "model_path": str(model_path.resolve()),
        "catalog_size": len(CATALOGO_SINTOMAS),
        "sklearn_version": sklearn_version,
    }
    guardar_reporte_json(report_path, reporte_payload)

    print(f"Modelo guardado en: {model_path}")
    print(f"Reporte JSON guardado en: {report_path}")
    print("Entrenamiento completado.")


if __name__ == "__main__":
    main()
