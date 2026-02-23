# src/api.py
from pathlib import Path
from typing import Dict, List, Optional

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from catalogo_sintomas import CATALOGO_SINTOMAS
from nlp_extractor import SintomaExtractor, _normalizar


# -------------------------------------------------
# Inicializar extractor
# -------------------------------------------------
extractor = SintomaExtractor()


# -------------------------------------------------
# Sintomas, prioridades y categorias
# -------------------------------------------------
DEFAULT_PRIORIDAD = 1
MIN_SINTOMAS_PARA_ML = 2
sintomas_prioridad: Dict[str, int] = {s: DEFAULT_PRIORIDAD for s in CATALOGO_SINTOMAS.keys()}

prioridades_override = {
    # Alta prioridad
    "dolor de pecho": 3,
    "presión en el pecho": 3,
    "falta de aire": 3,
    "dificultad para respirar": 3,
    "palpitaciones": 3,
    "hormigueo en las extremidades": 3,
    "tos persistente": 3,
    "sibilancias": 3,
    # Prioridad media
    "tos": 2,
    "tos seca": 2,
    "dolor de estómago": 2,
    "diarrea": 2,
    "mareos": 2,
    "vértigo": 2,
    "pérdida de equilibrio": 2,
    "dolor de diente": 2,
    "hormigueo en la cara": 2,
    "inflamación": 2,
    "dolor de hombro": 2,
    "dolor lumbar": 2,
    "ardor al orinar": 2,
    "dolor de articulaciones": 2,
    "hinchazón": 2,
    "inflamación de rodilla": 2,
    "dolor de brazo": 2,
    "rigidez": 2,
    "náuseas": 2,
    "vómitos": 2,
    "visión borrosa": 2,
    "ardor": 2,
    "flema": 2,
    "sangrado nasal": 2,
    "sensibilidad": 2,
    "escalofrios": 2,
    "temblores": 2,
    "sudores nocturnos": 2,
    "ganglios inflamados": 2,
    "dolor muscular": 2,
    "debilidad muscular": 2,
    "menstruacion irregular": 2,
    "perdida de peso": 2,
    "dolor de rodilla": 2,
    "dolor de cadera": 2,
    "dificultad para caminar": 2,
    "dolor detrás de los ojos": 2,
    "dolor al defecar": 2,
    "irritacion anal": 2,
    "hinchazon de piernas": 2,
    "venas prominentes en pantorrilla": 2,
}

for sintoma, prioridad in prioridades_override.items():
    if sintoma in sintomas_prioridad:
        sintomas_prioridad[sintoma] = prioridad

categorias_map: Dict[str, str] = {s: "General" for s in CATALOGO_SINTOMAS.keys()}

categorias_override = {
    "dolor de cabeza": "Neurológico",
    "mareos": "Neurológico",
    "vértigo": "Neurológico",
    "pérdida de equilibrio": "Neurológico",
    "visión borrosa": "Neurológico",
    "hormigueo en la cara": "Neurológico",
    "hormigueo en las extremidades": "Neurológico",
    "fiebre": "Infeccioso",
    "escalofrios": "Infeccioso",
    "sudores nocturnos": "Infeccioso",
    "ganglios inflamados": "Infeccioso",
    "dolor de garganta": "Infeccioso",
    "tos seca": "Respiratorio",
    "tos persistente": "Respiratorio",
    "tos": "Respiratorio",
    "flema": "Respiratorio",
    "congestión nasal": "Respiratorio",
    "moqueo": "Respiratorio",
    "estornudos": "Respiratorio",
    "falta de aire": "Respiratorio",
    "dificultad para respirar": "Respiratorio",
    "sibilancias": "Respiratorio",
    "presión en el pecho": "Respiratorio",
    "dolor de pecho": "Cardíaco",
    "palpitaciones": "Cardíaco",
    "dolor de estómago": "Digestivo",
    "diarrea": "Digestivo",
    "náuseas": "Digestivo",
    "vómitos": "Digestivo",
    "pérdida de apetito": "Digestivo",
    "gases": "Digestivo",
    "acidez": "Digestivo",
    "indigestion": "Digestivo",
    "estreñimiento": "Digestivo",
    "ardor al orinar": "Urinario",
    "dolor lumbar": "Musculoesquelético",
    "dolor de espalda": "Musculoesquelético",
    "dolor de articulaciones": "Musculoesquelético",
    "rigidez": "Musculoesquelético",
    "hinchazón": "Musculoesquelético",
    "inflamación": "Musculoesquelético",
    "inflamación de rodilla": "Musculoesquelético",
    "dolor de brazo": "Musculoesquelético",
    "dolor de cuello": "Musculoesquelético",
    "dolor de hombro": "Musculoesquelético",
    "dolor muscular": "Musculoesquelético",
    "debilidad muscular": "Musculoesquelético",
    "dolor de rodilla": "Musculoesquelético",
    "dolor de cadera": "Musculoesquelético",
    "dificultad para caminar": "Musculoesquelético",
    "dolor de diente": "Odontológico",
    "dolor de oído": "Odontológico",
    "sensibilidad": "Odontológico",
    "sarpullido": "Dermatológico",
    "picazón": "Dermatológico",
    "ojos rojos": "Oftalmológico",
    "lagrimeo": "Oftalmológico",
    "ojos secos": "Oftalmológico",
    "insomnio": "Psicológico",
    "ansiedad": "Psicológico",
    "irritabilidad": "Psicológico",
    "cambios de humor": "Psicológico",
    "inquietud": "Psicológico",
    "dificultad para concentrarse": "Psicológico",
    "bochornos": "Endocrino",
    "hambre excesiva": "Endocrino",
    "aumento de apetito": "Endocrino",
    "uñas quebradizas": "Endocrino",
    "frio en manos y pies": "Endocrino",
    "gripe": "Infeccioso",
    "dolor detrás de los ojos": "Oftalmológico",
    "presion sinusal": "Respiratorio",
    "perdida del olfato": "Respiratorio",
    "dolor al defecar": "Digestivo",
    "irritacion anal": "Digestivo",
    "calambres": "Musculoesquelético",
    "hinchazon de piernas": "Vascular",
    "venas prominentes en pantorrilla": "Vascular",
    "fatiga": "General",
    "somnolencia": "General",
    "malestar general": "General",
    "temblores": "General",
    "sudoracion": "General",
    "sequedad vaginal": "Ginecológico",
    "menstruacion irregular": "Ginecológico",
    "perdida de peso": "General",
}

for sintoma, categoria in categorias_override.items():
    if sintoma in categorias_map:
        categorias_map[sintoma] = categoria


# -------------------------------------------------
# Reglas de combinaciones (elevan urgencia)
# -------------------------------------------------
combinaciones_urgencia = [
    {"sintomas": {"fiebre", "mareos"}, "nivel": 3},
    {"sintomas": {"fiebre", "tos seca", "dificultad para respirar"}, "nivel": 3},
    {"sintomas": {"presión en el pecho", "falta de aire"}, "nivel": 3},
    {"sintomas": {"tos persistente", "fiebre", "mareos"}, "nivel": 3},
    {"sintomas": {"dolor lumbar", "ardor al orinar"}, "nivel": 3},
    {"sintomas": {"fiebre", "dolor de garganta", "tos persistente"}, "nivel": 3},
    {"sintomas": {"ardor al orinar", "dolor lumbar", "fatiga"}, "nivel": 3},
    {"sintomas": {"tos persistente", "presión en el pecho"}, "nivel": 3},
    {"sintomas": {"palpitaciones", "falta de aire"}, "nivel": 3},
    {"sintomas": {"sibilancias", "falta de aire"}, "nivel": 3},
]


# -------------------------------------------------
# Cargar modelo ML para urgencia
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "model_bundle.joblib"
FRONTEND_DIR = BASE_DIR / "frontend"

vectorizer = None
clf = None

if MODEL_PATH.exists():
    try:
        bundle = joblib.load(MODEL_PATH)
        vectorizer = bundle.get("vectorizer")
        clf = bundle.get("clf")
    except Exception as exc:
        print(f"Advertencia: no se pudo cargar modelo ML ({exc}). Se usaran reglas.")
else:
    print("Advertencia: modelo ML no encontrado. Se usaran reglas de urgencia.")


# -------------------------------------------------
# FastAPI
# -------------------------------------------------
app = FastAPI(title="API Triaje Virtual", version="0.8.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TriageRequest(BaseModel):
    texto_paciente: Optional[str] = None


def _respuesta_sin_sintomas(mensaje: str):
    return {
        "sintomas": [],
        "categorias": {},
        "prioridades": {},
        "overall_urgency": 0,
        "rule_based_urgency": 0,
        "recommended_action": mensaje,
        "ml_enabled": bool(vectorizer and clf),
        "ml_predicted_urgency": None,
        "ml_used": False,
        "urgency_source": "none",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "sintomas_registrados": len(sintomas_prioridad),
        "ml_enabled": bool(vectorizer and clf),
        "ml_min_sintomas": MIN_SINTOMAS_PARA_ML,
        "model_path": str(MODEL_PATH),
    }


@app.post("/analizar")
def analizar(req: TriageRequest):
    texto_original = req.texto_paciente or ""
    texto = _normalizar(texto_original)
    if not texto:
        return _respuesta_sin_sintomas("No se detectaron sintomas, intente de nuevo.")

    sintomas_detectados = extractor.extraer(texto)

    all_sintomas: List[str] = []
    vistos = set()
    for s in sintomas_detectados:
        if s in sintomas_prioridad and s not in vistos:
            vistos.add(s)
            all_sintomas.append(s)

    if not all_sintomas:
        return _respuesta_sin_sintomas("No se detectaron sintomas, intente de nuevo.")

    categorias: Dict[str, List[str]] = {}
    for s in all_sintomas:
        categoria = categorias_map.get(s, "General")
        categorias.setdefault(categoria, []).append(s)

    prioridades: Dict[str, int] = {s: sintomas_prioridad.get(s, 1) for s in all_sintomas}
    urgencia_reglas = max(prioridades.values(), default=1)

    set_sintomas = set(all_sintomas)
    for combo in combinaciones_urgencia:
        if combo["sintomas"].issubset(set_sintomas):
            urgencia_reglas = max(urgencia_reglas, combo["nivel"])

    urgencia = urgencia_reglas
    urgencia_ml = None
    ml_used = False
    urgency_source = "reglas"

    # Política: el ML solo se aplica si hay >= MIN_SINTOMAS_PARA_ML síntomas detectados.
    # Esto evita sobre-escalamiento en casos simples (p.ej. solo "fiebre").
    if vectorizer is not None and clf is not None and len(all_sintomas) >= MIN_SINTOMAS_PARA_ML:
        try:
            x_vec = vectorizer.transform([texto])
            urgencia_ml = int(clf.predict(x_vec)[0])
            urgencia = max(urgencia_reglas, urgencia_ml)
            ml_used = True
            urgency_source = "ml+reglas" if urgencia_ml != urgencia_reglas else "reglas=ml"
        except Exception as exc:
            print(f"Advertencia: fallo inferencia ML ({exc}). Se mantienen reglas.")

    if urgencia == 3:
        recomendacion = "Acudir a emergencias inmediatamente."
    elif urgencia == 2:
        recomendacion = "Buscar atencion medica en las proximas horas."
    else:
        recomendacion = "Reposo y observacion."

    return {
        "sintomas": all_sintomas,
        "categorias": categorias,
        "prioridades": prioridades,
        "overall_urgency": urgencia,
        "rule_based_urgency": urgencia_reglas,
        "recommended_action": recomendacion,
        "ml_enabled": bool(vectorizer and clf),
        "ml_predicted_urgency": urgencia_ml,
        "ml_used": ml_used,
        "urgency_source": urgency_source,
    }


@app.get("/api/health", include_in_schema=False)
def health_api():
    return health()


@app.post("/api/analizar", include_in_schema=False)
def analizar_api(req: TriageRequest):
    return analizar(req)


@app.get("/", include_in_schema=False)
def home():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"status": "ok", "message": "API de triaje activa"}
