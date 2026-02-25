import argparse
import csv
import io
import json
import random
import time
from urllib import error, request
from pathlib import Path

from catalogo_sintomas import CATALOGO_SINTOMAS


DEFAULT_API_BASE = "http://localhost:8000"
DEFAULT_OUTPUT = "dataset_triaje_800_virtual_ajustado.csv"


def _frase_sintoma(rng: random.Random, sintoma: str) -> str:
    variantes = CATALOGO_SINTOMAS.get(sintoma, [])
    if variantes:
        return rng.choice(variantes)
    return sintoma


def _construir_caso(rng: random.Random) -> str:
    sintomas = list(CATALOGO_SINTOMAS.keys())
    n = rng.choices([1, 2, 3, 4], weights=[35, 35, 20, 10], k=1)[0]
    elegidos = rng.sample(sintomas, k=min(n, len(sintomas)))
    frases = [_frase_sintoma(rng, s) for s in elegidos]
    estilo = rng.choice(["corto", "medio", "largo"])

    if estilo == "corto":
        return f"Tengo {frases[0]}."

    if estilo == "medio":
        if len(frases) == 1:
            return f"Desde ayer tengo {frases[0]} y me siento mal."
        return f"Tengo {frases[0]} y {frases[1]} desde ayer."

    texto = (
        "Hola doctor, desde hace dos dias presento "
        f"{frases[0]}"
    )
    if len(frases) > 1:
        texto += f", tambien {frases[1]}"
    if len(frases) > 2:
        texto += f" y ademas {frases[2]}"
    if len(frases) > 3:
        texto += f", con episodios de {frases[3]}"
    texto += ". Quisiera una orientacion inicial."
    return texto


def _http_post_json(url: str, payload: dict, timeout: int):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def _http_get_text(url: str, timeout: int) -> str:
    req = request.Request(url, method="GET")
    with request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def _post_analizar(api_base: str, texto: str, timeout: int):
    intime = time.time() / 60
    payload = {
        "texto_paciente": texto,
        "caso": texto,
        "intime": intime,
    }
    return _http_post_json(f"{api_base}/api/analizar", payload, timeout)


def _descargar_csv(api_base: str, timeout: int) -> str:
    return _http_get_text(f"{api_base}/api/observaciones/csv", timeout)


def _guardar_ultimos_n(csv_text: str, n: int, output_path: Path):
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)
    if not rows:
        raise RuntimeError("El CSV de observaciones esta vacio.")

    ultimos = rows[-n:] if len(rows) >= n else rows
    fieldnames = reader.fieldnames or []
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ultimos)
    return len(ultimos), fieldnames


def main():
    parser = argparse.ArgumentParser(
        description="Genera casos sinteticos y construye dataset de observaciones."
    )
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="Base URL de la API.")
    parser.add_argument("--n", type=int, default=800, help="Cantidad de casos a generar.")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria.")
    parser.add_argument("--timeout", type=int, default=20, help="Timeout HTTP en segundos.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="CSV de salida.")
    args = parser.parse_args()

    api_base = args.api_base.rstrip("/")
    output_path = Path(args.output)
    rng = random.Random(args.seed)

    ok = 0
    errores = 0
    for i in range(args.n):
        texto = _construir_caso(rng)
        try:
            _post_analizar(api_base, texto, args.timeout)
            ok += 1
        except error.HTTPError as exc:
            errores += 1
            print(f"[{i + 1}/{args.n}] HTTP {exc.code}: {exc.reason}")
        except error.URLError as exc:
            errores += 1
            print(f"[{i + 1}/{args.n}] error de red: {exc.reason}")
        except Exception as exc:
            errores += 1
            print(f"[{i + 1}/{args.n}] error enviando caso: {exc}")

    csv_text = _descargar_csv(api_base, args.timeout)

    total_guardados, columnas = _guardar_ultimos_n(csv_text, ok, output_path)

    print(f"Casos solicitados: {args.n}")
    print(f"Casos enviados OK: {ok}")
    print(f"Casos con error: {errores}")
    print(f"Filas guardadas en dataset: {total_guardados}")
    print(f"Archivo generado: {output_path}")
    print(f"Columnas: {columnas}")


if __name__ == "__main__":
    main()
