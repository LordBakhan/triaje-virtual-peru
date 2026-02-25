# src/api.py
import csv
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Union

import joblib
from fastapi import FastAPI
from fastapi import HTTPException
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
    "dolor de encias": 2,
    "sangrado de encias": 2,
    "encias inflamadas": 2,
    "ulceras bucales": 2,
    "dolor de mandibula": 2,
    "dolor de lengua": 2,
    "dolor al masticar": 2,
    "oido tapado": 2,
    "zumbido de oidos": 2,
    "disminucion de audicion": 2,
    "sensibilidad a la luz": 2,
    "hinchazon abdominal": 2,
    "distension abdominal": 2,
    "colicos abdominales": 2,
    "reflujo": 2,
    "dolor pelvico": 2,
    "urgencia urinaria": 2,
    "frecuencia urinaria": 2,
    "orina turbia": 2,
    "orina con mal olor": 2,
    "picazon vaginal": 2,
    "flujo vaginal anormal": 2,
    "dolor menstrual": 2,
    "contractura muscular": 2,
    "dolor de piernas": 2,
    "dolor de pies": 2,
    "dolor de manos": 2,
    "dolor de tobillo": 2,
    "dolor de muneca": 2,
    "dolor de codo": 2,
    "rigidez de hombro": 2,
    "pesadez en piernas": 2,
    "mareo al levantarse": 2,
    "urticaria": 2,
    "dolor de talon": 2,
    "dolor de pantorrilla": 2,
    "dolor de antebrazo": 2,
    "dolor de dedos": 2,
    "dolor en la planta del pie": 2,
    "calambres nocturnos": 2,
    "dolor en la boca del estomago": 2,
    "evacuacion incompleta": 2,
    "nicturia": 2,
    "dolor suprapubico": 2,
    "labios agrietados": 2,
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
    "dolor de encias": "Odontológico",
    "sangrado de encias": "Odontológico",
    "encias inflamadas": "Odontológico",
    "ulceras bucales": "Odontológico",
    "mal aliento": "Odontológico",
    "boca seca": "Odontológico",
    "dolor de mandibula": "Odontológico",
    "dolor de lengua": "Odontológico",
    "dolor al masticar": "Odontológico",
    "oido tapado": "Otorrinolaringológico",
    "zumbido de oidos": "Otorrinolaringológico",
    "disminucion de audicion": "Otorrinolaringológico",
    "picazon de garganta": "Otorrinolaringológico",
    "ronquera": "Otorrinolaringológico",
    "carraspeo": "Otorrinolaringológico",
    "picazon de ojos": "Oftalmológico",
    "ardor de ojos": "Oftalmológico",
    "secrecion ocular": "Oftalmológico",
    "parpados hinchados": "Oftalmológico",
    "sensibilidad a la luz": "Oftalmológico",
    "fatiga visual": "Oftalmológico",
    "hinchazon abdominal": "Digestivo",
    "distension abdominal": "Digestivo",
    "colicos abdominales": "Digestivo",
    "reflujo": "Digestivo",
    "eructos frecuentes": "Digestivo",
    "saciedad temprana": "Digestivo",
    "dolor pelvico": "Ginecológico",
    "urgencia urinaria": "Urinario",
    "frecuencia urinaria": "Urinario",
    "orina turbia": "Urinario",
    "orina con mal olor": "Urinario",
    "picazon vaginal": "Ginecológico",
    "flujo vaginal anormal": "Ginecológico",
    "dolor menstrual": "Ginecológico",
    "sindrome premenstrual": "Ginecológico",
    "contractura muscular": "Musculoesquelético",
    "dolor de piernas": "Musculoesquelético",
    "dolor de pies": "Musculoesquelético",
    "dolor de manos": "Musculoesquelético",
    "dolor de tobillo": "Musculoesquelético",
    "dolor de muneca": "Musculoesquelético",
    "dolor de codo": "Musculoesquelético",
    "rigidez de hombro": "Musculoesquelético",
    "pesadez en piernas": "Vascular",
    "piernas cansadas": "General",
    "mareo al levantarse": "Neurológico",
    "sensibilidad al ruido": "Neurológico",
    "niebla mental": "Neurológico",
    "falta de memoria leve": "Neurológico",
    "estres": "Psicológico",
    "animo bajo": "Psicológico",
    "sueno no reparador": "Psicológico",
    "despertares nocturnos": "Psicológico",
    "piel seca": "Dermatológico",
    "descamacion de la piel": "Dermatológico",
    "urticaria": "Dermatológico",
    "acne": "Dermatológico",
    "picazon en el cuero cabelludo": "Dermatológico",
    "caspa": "Dermatológico",
    "caida de cabello": "Dermatológico",
    "dolor de talon": "Musculoesquelético",
    "dolor de pantorrilla": "Musculoesquelético",
    "dolor de antebrazo": "Musculoesquelético",
    "dolor de dedos": "Musculoesquelético",
    "dolor en la planta del pie": "Musculoesquelético",
    "calambres nocturnos": "Musculoesquelético",
    "boca amarga": "Digestivo",
    "sabor metalico": "Digestivo",
    "dolor en la boca del estomago": "Digestivo",
    "hipo frecuente": "Digestivo",
    "sensacion de llenura": "Digestivo",
    "evacuacion incompleta": "Digestivo",
    "nicturia": "Urinario",
    "dolor suprapubico": "Urinario",
    "nariz seca": "Otorrinolaringológico",
    "sequedad de labios": "Dermatológico",
    "labios agrietados": "Dermatológico",
    "tic en el ojo": "Oftalmológico",
    "ojo lloroso": "Oftalmológico",
    "sueno ligero": "Psicológico",
    "pesadillas frecuentes": "Psicológico",
    "somnolencia diurna": "General",
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
OBSERVACIONES_CSV = BASE_DIR / "data" / "ficha_observacion.csv"
OBS_FIELDS = [
    "id",
    "caso",
    "sintomas_texto",
    "nivel_sistema",
    "nivel_referencia",
    "recomendacion_sistema",
    "recomendacion_referencia",
    "adequacy_score",
    "intime",
    "outtime",
    "wait_base_min",
    "alarm",
    "override",
]


class _ObservacionStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = Lock()
        self.last_id = 0
        self.total_cases = 0
        self.total_alarmas = 0
        self.total_alarmas_injustificadas = 0
        self.total_overrides = 0
        self._ensure_schema()
        self._bootstrap()

    @staticmethod
    def _to_int(value) -> int:
        try:
            return int(float(value))
        except Exception:
            return 0

    @staticmethod
    def _to_optional_int(value):
        if value is None:
            return None
        s = str(value).strip()
        if not s:
            return None
        try:
            return int(float(s))
        except Exception:
            return None

    @staticmethod
    def _recomendacion_por_nivel(nivel: int) -> str:
        if nivel == 3:
            return "Acudir a emergencias inmediatamente."
        if nivel == 2:
            return "Buscar atencion medica en las proximas horas."
        if nivel == 1:
            return "Reposo y observacion."
        return "No se detectaron sintomas, intente de nuevo."

    @staticmethod
    def _wait_base_min_por_nivel(nivel_referencia: int) -> float:
        # Base presencial inventada para comparacion de tiempos.
        # Menor urgencia suele esperar mas en triaje presencial.
        tabla = {
            0: 0.0,
            1: 58.0,
            2: 34.0,
            3: 16.0,
        }
        return tabla.get(int(nivel_referencia), 34.0)

    @classmethod
    def _eventos_desde_fila(cls, row):
        nivel_sistema = cls._to_optional_int(row.get("nivel_sistema"))
        nivel_referencia = cls._to_int(row.get("nivel_referencia"))
        alarm_event = int(
            nivel_sistema is not None and nivel_sistema != nivel_referencia
        )
        override_event = 1 if cls._to_int(row.get("override")) > 0 else 0
        alarm_unjustified_event = 1 if cls._to_int(row.get("alarm")) > 0 else int(
            alarm_event and nivel_sistema is not None and nivel_sistema > nivel_referencia and nivel_referencia <= 2
        )
        return alarm_event, alarm_unjustified_event, override_event

    def _bootstrap(self):
        if not self.path.exists():
            return
        try:
            with self.path.open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.total_cases += 1
                    self.last_id = max(self.last_id, self._to_int(row.get("id")))
                    alarm_event, alarm_unjustified_event, override_event = self._eventos_desde_fila(row)
                    self.total_alarmas += alarm_event
                    self.total_alarmas_injustificadas += alarm_unjustified_event
                    self.total_overrides += override_event
        except Exception as exc:
            print(f"Advertencia: no se pudo leer historial de observaciones ({exc}).")

    def _ensure_schema(self):
        if not self.path.exists() or self.path.stat().st_size == 0:
            return
        try:
            with self.path.open(encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                header = next(reader, [])
        except Exception:
            return

        if header == OBS_FIELDS:
            return

        legacy = self.path.with_name(
            f"{self.path.stem}_legacy_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        )
        try:
            self.path.replace(legacy)
            print(
                f"Advertencia: esquema CSV antiguo detectado. "
                f"Se movio a {legacy.name} y se inicia un CSV nuevo."
            )
            self.last_id = 0
            self.total_cases = 0
            self.total_alarmas = 0
            self.total_alarmas_injustificadas = 0
            self.total_overrides = 0
        except Exception as exc:
            print(f"Advertencia: no se pudo migrar CSV legado ({exc}).")

    def append(
        self,
        *,
        caso: str,
        sintomas_texto: str,
        nivel_sistema,
        nivel_referencia: int,
        recomendacion_sistema: str,
        adequacy_score: float,
        intime: int,
        outtime: int,
        urgencia_final: int,
    ):
        with self._lock:
            self._ensure_schema()

            alarm_event = int(
                nivel_sistema is not None and int(nivel_sistema) != int(nivel_referencia)
            )
            alarm_unjustified_event = int(
                alarm_event and nivel_sistema is not None and int(nivel_sistema) > int(nivel_referencia) and int(nivel_referencia) <= 2
            )
            override_event = int(
                nivel_sistema is not None and int(nivel_sistema) < int(nivel_referencia) and int(urgencia_final) == int(nivel_referencia)
            )

            self.total_cases += 1
            self.last_id += 1
            self.total_alarmas += alarm_event
            self.total_alarmas_injustificadas += alarm_unjustified_event
            self.total_overrides += override_event

            row = {
                "id": self.last_id,
                "caso": caso,
                "sintomas_texto": sintomas_texto,
                "nivel_sistema": "" if nivel_sistema is None else int(nivel_sistema),
                "nivel_referencia": int(nivel_referencia),
                "recomendacion_sistema": recomendacion_sistema,
                "recomendacion_referencia": self._recomendacion_por_nivel(int(nivel_referencia)),
                "adequacy_score": f"{float(adequacy_score):.2f}",
                "intime": intime,
                "outtime": outtime,
                "wait_base_min": f"{self._wait_base_min_por_nivel(int(nivel_referencia)):.2f}",
                "alarm": alarm_unjustified_event,
                "override": override_event,
            }

            self.path.parent.mkdir(parents=True, exist_ok=True)
            write_header = (not self.path.exists()) or self.path.stat().st_size == 0
            with self.path.open("a", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=OBS_FIELDS)
                if write_header:
                    writer.writeheader()
                writer.writerow(row)
            return row

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

observacion_store = _ObservacionStore(OBSERVACIONES_CSV)


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
    caso: Optional[str] = None
    intime: Optional[Union[str, int, float]] = None
    adequacy: Optional[float] = None


def _ahora_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def _parse_epoch_ms(value):
    if value is None:
        return _ahora_ms()

    if isinstance(value, (int, float)):
        raw = float(value)
    else:
        s = str(value).strip()
        if not s:
            return _ahora_ms()
        try:
            raw = float(s)
        except Exception:
            try:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
                return int(dt.timestamp() * 1000)
            except Exception:
                return _ahora_ms()

    # microsegundos -> ms
    if raw > 1e14:
        return int(raw / 1000)
    # milisegundos
    if raw > 1e12:
        return int(raw)
    # segundos (unix)
    if raw > 1e9:
        return int(raw * 1000)
    return int(raw)


def _clamp_adequacy(value: Optional[float], overall_urgency: int, nivel_referencia: int, tiene_sintomas: bool):
    if value is not None:
        try:
            return max(0.0, min(5.0, float(value)))
        except Exception:
            pass
    if not tiene_sintomas:
        return 0.0
    delta = abs(int(overall_urgency) - int(nivel_referencia))
    if delta == 0:
        return 5.0
    if delta == 1:
        return 3.0
    return 1.0


def _registrar_ficha_observacion(
    *,
    req: TriageRequest,
    texto_original: str,
    sintomas: List[str],
    urgencia_ml,
    urgencia_reglas: int,
    urgencia_final: int,
    recomendacion: str,
):
    intime = _parse_epoch_ms(req.intime)
    outtime = _ahora_ms()
    adequacy = _clamp_adequacy(req.adequacy, urgencia_final, urgencia_reglas, bool(sintomas))
    caso = (req.caso or texto_original or "").strip()
    sintomas_texto = ";".join(sintomas)
    nivel_sistema = urgencia_ml if urgencia_ml is not None else urgencia_final

    return observacion_store.append(
        caso=caso,
        sintomas_texto=sintomas_texto,
        nivel_sistema=nivel_sistema,
        nivel_referencia=urgencia_reglas,
        recomendacion_sistema=recomendacion,
        adequacy_score=adequacy,
        intime=intime,
        outtime=outtime,
        urgencia_final=urgencia_final,
    )


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
        "observation_csv": str(OBSERVACIONES_CSV),
        "observations_total": observacion_store.total_cases,
    }


@app.post("/analizar")
def analizar(req: TriageRequest):
    texto_original = req.texto_paciente or ""
    texto = _normalizar(texto_original)

    # Defaults para salida y ficha de observacion
    all_sintomas: List[str] = []
    categorias: Dict[str, List[str]] = {}
    prioridades: Dict[str, int] = {}
    urgencia = 0
    urgencia_reglas = 0
    urgencia_ml = None
    ml_used = False
    urgency_source = "none"
    recomendacion = "No se detectaron sintomas, intente de nuevo."

    if not texto:
        ficha = _registrar_ficha_observacion(
            req=req,
            texto_original=texto_original,
            sintomas=all_sintomas,
            urgencia_ml=urgencia_ml,
            urgencia_reglas=urgencia_reglas,
            urgencia_final=urgencia,
            recomendacion=recomendacion,
        )
        return {
            "sintomas": [],
            "categorias": {},
            "prioridades": {},
            "overall_urgency": 0,
            "rule_based_urgency": 0,
            "recommended_action": recomendacion,
            "ml_enabled": bool(vectorizer and clf),
            "ml_predicted_urgency": None,
            "ml_used": False,
            "urgency_source": "none",
            "observation_id": ficha["id"],
            "observation_csv": str(OBSERVACIONES_CSV),
        }

    # Prediccion ML siempre que el modelo este disponible (para comparacion).
    if vectorizer is not None and clf is not None:
        try:
            x_vec = vectorizer.transform([texto])
            urgencia_ml = int(clf.predict(x_vec)[0])
        except Exception as exc:
            print(f"Advertencia: fallo inferencia ML ({exc}).")

    sintomas_detectados = extractor.extraer(texto)
    vistos = set()
    for s in sintomas_detectados:
        if s in sintomas_prioridad and s not in vistos:
            vistos.add(s)
            all_sintomas.append(s)

    if all_sintomas:
        for s in all_sintomas:
            categoria = categorias_map.get(s, "General")
            categorias.setdefault(categoria, []).append(s)

        prioridades = {s: sintomas_prioridad.get(s, 1) for s in all_sintomas}
        urgencia_reglas = max(prioridades.values(), default=1)

        set_sintomas = set(all_sintomas)
        for combo in combinaciones_urgencia:
            if combo["sintomas"].issubset(set_sintomas):
                urgencia_reglas = max(urgencia_reglas, combo["nivel"])

        urgencia = urgencia_reglas
        urgency_source = "reglas"

        # Politica: decision final usa ML solo si hay >= MIN_SINTOMAS_PARA_ML.
        if urgencia_ml is not None and len(all_sintomas) >= MIN_SINTOMAS_PARA_ML:
            urgencia = max(urgencia_reglas, urgencia_ml)
            ml_used = True
            urgency_source = "ml+reglas" if urgencia_ml != urgencia_reglas else "reglas=ml"

        if urgencia == 3:
            recomendacion = "Acudir a emergencias inmediatamente."
        elif urgencia == 2:
            recomendacion = "Buscar atencion medica en las proximas horas."
        else:
            recomendacion = "Reposo y observacion."

    ficha = _registrar_ficha_observacion(
        req=req,
        texto_original=texto_original,
        sintomas=all_sintomas,
        urgencia_ml=urgencia_ml,
        urgencia_reglas=urgencia_reglas,
        urgencia_final=urgencia,
        recomendacion=recomendacion,
    )

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
        "observation_id": ficha["id"],
        "observation_csv": str(OBSERVACIONES_CSV),
    }


@app.get("/api/health", include_in_schema=False)
def health_api():
    return health()


@app.post("/api/analizar", include_in_schema=False)
def analizar_api(req: TriageRequest):
    return analizar(req)


@app.get("/observaciones")
def observaciones_estado():
    return {
        "csv_path": str(OBSERVACIONES_CSV),
        "exists": OBSERVACIONES_CSV.exists(),
        "observations_total": observacion_store.total_cases,
        "alarm_rate": (
            observacion_store.total_alarmas / observacion_store.total_cases
            if observacion_store.total_cases > 0
            else 0.0
        ),
        "alarm_unjustified_ratio": (
            observacion_store.total_alarmas_injustificadas / observacion_store.total_alarmas
            if observacion_store.total_alarmas > 0
            else 0.0
        ),
        "override_ratio": (
            observacion_store.total_overrides / observacion_store.total_cases
            if observacion_store.total_cases > 0
            else 0.0
        ),
    }


@app.get("/observaciones/csv")
def observaciones_csv():
    if not OBSERVACIONES_CSV.exists():
        raise HTTPException(status_code=404, detail="CSV de observaciones aun no creado.")
    return FileResponse(
        OBSERVACIONES_CSV,
        media_type="text/csv",
        filename="ficha_observacion.csv",
    )


@app.get("/api/observaciones", include_in_schema=False)
def observaciones_estado_api():
    return observaciones_estado()


@app.get("/api/observaciones/csv", include_in_schema=False)
def observaciones_csv_api():
    return observaciones_csv()


@app.get("/", include_in_schema=False)
def home():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"status": "ok", "message": "API de triaje activa"}
