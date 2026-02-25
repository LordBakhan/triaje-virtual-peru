import argparse
import csv
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from api import TriageRequest, analizar
from nlp_extractor import SintomaExtractor, _normalizar


def _resolve_default_cases_path() -> Path:
    here = Path(__file__).resolve()
    candidate = here.parents[1] / "data" / "regression_cases.csv"
    if candidate.exists():
        return candidate
    return Path("data/regression_cases.csv")


def _split_expected(raw: str) -> List[str]:
    if not raw:
        return []
    return [x.strip() for x in raw.split(";") if x.strip()]


def _norm_set(items: List[str]) -> Set[str]:
    return {_normalizar(x) for x in items if _normalizar(x)}


def cargar_casos(path: Path) -> List[Dict]:
    casos: List[Dict] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            caso_id = str(row.get("id", "")).strip()
            texto = str(row.get("texto", "")).strip()
            esperados_raw = str(row.get("esperados", "")).strip()
            urg_raw = str(row.get("urgencia_reglas", "")).strip()

            if not texto:
                continue

            casos.append(
                {
                    "id": caso_id or str(len(casos) + 1),
                    "texto": texto,
                    "esperados": _split_expected(esperados_raw),
                    "urgencia_reglas": int(urg_raw) if urg_raw else None,
                }
            )
    return casos


def evaluar(
    casos: List[Dict],
    strict: bool = False,
    max_fallos: int = 25,
) -> int:
    extractor = SintomaExtractor()

    total = len(casos)
    if total == 0:
        print("No hay casos para evaluar.")
        return 1

    casos_ok_extractor = 0
    casos_ok_urgencia = 0
    casos_ok_global = 0

    sintomas_esperados_total = 0
    sintomas_detectados_correctos = 0

    fallos_extractor = []
    fallos_urgencia = []

    for caso in casos:
        texto = caso["texto"]
        esperados = caso["esperados"]
        urg_esperada = caso["urgencia_reglas"]

        detectados = extractor.extraer(texto)

        expected_norm = _norm_set(esperados)
        detected_norm = _norm_set(detectados)

        missing_norm = expected_norm - detected_norm
        extras_norm = detected_norm - expected_norm

        sintomas_esperados_total += len(expected_norm)
        sintomas_detectados_correctos += len(expected_norm & detected_norm)

        extractor_ok = (not missing_norm) and (not strict or not extras_norm)
        if extractor_ok:
            casos_ok_extractor += 1
        else:
            fallos_extractor.append(
                {
                    "id": caso["id"],
                    "texto": texto,
                    "esperados": esperados,
                    "detectados": detectados,
                    "faltantes_norm": sorted(missing_norm),
                    "extras_norm": sorted(extras_norm),
                }
            )

        resp = analizar(TriageRequest(texto_paciente=texto))
        urg_reglas_real = int(resp.get("rule_based_urgency", resp.get("overall_urgency", 0)))
        urg_global_real = int(resp.get("overall_urgency", 0))

        urgencia_ok = True
        if urg_esperada is not None:
            urgencia_ok = urg_reglas_real == urg_esperada

        if urgencia_ok:
            casos_ok_urgencia += 1
        else:
            fallos_urgencia.append(
                {
                    "id": caso["id"],
                    "texto": texto,
                    "urgencia_esperada_reglas": urg_esperada,
                    "urgencia_real_reglas": urg_reglas_real,
                    "urgencia_real_global": urg_global_real,
                    "sintomas": resp.get("sintomas", []),
                }
            )

        if extractor_ok and urgencia_ok:
            casos_ok_global += 1

    tasa_casos_extractor = (casos_ok_extractor / total) * 100
    tasa_casos_urgencia = (casos_ok_urgencia / total) * 100
    tasa_casos_global = (casos_ok_global / total) * 100
    tasa_sintoma = (
        (sintomas_detectados_correctos / sintomas_esperados_total) * 100
        if sintomas_esperados_total
        else 0.0
    )

    print("=== Validacion de regresion ===")
    print(f"Casos totales: {total}")
    print(f"Casos correctos extractor: {casos_ok_extractor} ({tasa_casos_extractor:.2f}%)")
    print(f"Casos correctos urgencia (reglas): {casos_ok_urgencia} ({tasa_casos_urgencia:.2f}%)")
    print(f"Casos correctos globales: {casos_ok_global} ({tasa_casos_global:.2f}%)")
    print(f"Sintomas esperados totales: {sintomas_esperados_total}")
    print(
        f"Sintomas detectados correctamente: {sintomas_detectados_correctos} "
        f"({tasa_sintoma:.2f}%)"
    )
    print(f"Modo extractor estricto: {'si' if strict else 'no'}")

    if fallos_extractor:
        print("\n=== Fallos extractor (primeros) ===")
        for e in fallos_extractor[:max_fallos]:
            print(f"[Caso {e['id']}] {e['texto']}")
            print(f"  Esperados: {e['esperados']}")
            print(f"  Detectados: {e['detectados']}")
            print(f"  Faltantes(norm): {e['faltantes_norm']}")
            if strict:
                print(f"  Extras(norm): {e['extras_norm']}")
            print()

    if fallos_urgencia:
        print("\n=== Fallos urgencia reglas (primeros) ===")
        for e in fallos_urgencia[:max_fallos]:
            print(f"[Caso {e['id']}] {e['texto']}")
            print(f"  Esperada reglas: {e['urgencia_esperada_reglas']}")
            print(f"  Real reglas: {e['urgencia_real_reglas']}")
            print(f"  Real global: {e['urgencia_real_global']}")
            print(f"  Sintomas API: {e['sintomas']}")
            print()

    return 0 if not fallos_extractor and not fallos_urgencia else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida extractor y urgencia por reglas con casos controlados."
    )
    parser.add_argument(
        "--cases",
        default=str(_resolve_default_cases_path()),
        help="Ruta al CSV de casos de regresion.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exige coincidencia exacta de sintomas (sin extras detectados).",
    )
    parser.add_argument(
        "--max-fallos",
        type=int,
        default=25,
        help="Numero maximo de fallos a imprimir por bloque.",
    )
    args = parser.parse_args()

    path = Path(args.cases)
    if not path.exists():
        print(f"No se encontro archivo de casos: {path}")
        return 1

    casos = cargar_casos(path)
    return evaluar(casos=casos, strict=args.strict, max_fallos=args.max_fallos)


if __name__ == "__main__":
    raise SystemExit(main())
