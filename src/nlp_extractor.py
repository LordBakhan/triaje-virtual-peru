# src/nlp_extractor.py
import re
import unicodedata
from catalogo_sintomas import CATALOGO_SINTOMAS


def _normalizar(texto: str) -> str:
    if texto is None:
        return ""
    t = str(texto).lower()
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


class SintomaExtractor:
    _NEGACION_PATRONES = (
        r"\bno\b(?:\s+\w+){0,3}\s*$",
        r"\bsin\b(?:\s+\w+){0,3}\s*$",
        r"\bniega\b(?:\s+\w+){0,3}\s*$",
        r"\bniego\b(?:\s+\w+){0,3}\s*$",
        r"\bdescarta\b(?:\s+\w+){0,3}\s*$",
        r"\bdescarto\b(?:\s+\w+){0,3}\s*$",
        r"\bausencia\s+de\b(?:\s+\w+){0,3}\s*$",
        r"\blibre\s+de\b(?:\s+\w+){0,3}\s*$",
    )
    _NEGACION_EXCEPCIONES = (
        r"\bno\s+solo(?:\s+\w+){0,2}\s*$",
        r"\bno\s+solamente(?:\s+\w+){0,2}\s*$",
        r"\bno\s+unicamente(?:\s+\w+){0,2}\s*$",
    )
    _RESETEAR_NEGACION = re.compile(
        r"\b(pero|aunque|sin embargo|excepto|salvo)\b"
    )

    def __init__(self, catalogo=None):
        self.catalogo = catalogo if catalogo is not None else CATALOGO_SINTOMAS
        self._orden = list(self.catalogo.keys())
        self._negacion_regex = [re.compile(p) for p in self._NEGACION_PATRONES]
        self._negacion_excepcion_regex = [
            re.compile(p) for p in self._NEGACION_EXCEPCIONES
        ]

        variantes = []
        vistos = set()
        for canon, lista in self.catalogo.items():
            all_variantes = [canon] + list(lista)
            for v in all_variantes:
                vn = _normalizar(v)
                if not vn:
                    continue
                key = (canon, vn)
                if key in vistos:
                    continue
                vistos.add(key)
                pat = re.compile(r"\b" + re.escape(vn) + r"\b")
                variantes.append(
                    {
                        "canon": canon,
                        "vn": vn,
                        "pat": pat,
                        "len_chars": len(vn),
                        "len_tokens": len(vn.split()),
                    }
                )
        variantes.sort(key=lambda x: (x["len_tokens"], x["len_chars"]), reverse=True)
        self._variantes = variantes

    def _esta_negado(self, texto_norm, start):
        contexto = texto_norm[max(0, start - 60) : start].strip()
        if not contexto:
            return False

        # Si hay un conector ("pero", "aunque"...), solo evaluamos
        # el fragmento mas cercano al sintoma para no arrastrar negaciones previas.
        ult_reset = None
        for m in self._RESETEAR_NEGACION.finditer(contexto):
            ult_reset = m
        if ult_reset is not None:
            contexto = contexto[ult_reset.end() :].strip()
            if not contexto:
                return False

        for patron_exc in self._negacion_excepcion_regex:
            if patron_exc.search(contexto):
                return False

        for patron in self._negacion_regex:
            if patron.search(contexto):
                return True

        # Maneja casos como: "no ... ni <sintoma>"
        if re.search(r"\bni\s*$", contexto) and re.search(r"\b(no|sin)\b", contexto):
            return True

        return False

    def _detectar_menciones(self, texto):
        txt_norm = _normalizar(texto)
        if not txt_norm:
            return txt_norm, []

        menciones = []
        for item in self._variantes:
            canon = item["canon"]
            vn = item["vn"]
            pat = item["pat"]
            for m in pat.finditer(txt_norm):
                if self._esta_negado(txt_norm, m.start()):
                    continue
                menciones.append(
                    {
                        "canon": canon,
                        "vn": vn,
                        "start": m.start(),
                        "end": m.end(),
                        "len_chars": item["len_chars"],
                        "len_tokens": item["len_tokens"],
                    }
                )
        return txt_norm, menciones

    @staticmethod
    def _se_solapan(a, b):
        return not (a["end"] <= b["start"] or b["end"] <= a["start"])

    def _resolver_solapamientos(self, menciones):
        if not menciones:
            return []

        # Priorizamos menciones mas especificas (mas largas) cuando se solapan.
        ordenadas = sorted(
            menciones,
            key=lambda x: (x["len_tokens"], x["len_chars"], -x["start"]),
            reverse=True,
        )

        seleccionadas = []
        for m in ordenadas:
            if any(self._se_solapan(m, s) for s in seleccionadas):
                continue
            seleccionadas.append(m)

        seleccionadas.sort(key=lambda x: x["start"])
        return seleccionadas

    def _ordenar_detectados(self, detectados):
        resultado = [c for c in self._orden if c in detectados]
        resto = [c for c in detectados if c not in self._orden]
        resultado.extend(sorted(resto))
        return resultado

    def extraer(self, texto):
        _, menciones = self._detectar_menciones(texto)
        if not menciones:
            return []

        menciones = self._resolver_solapamientos(menciones)
        detectados = {m["canon"] for m in menciones}
        return self._ordenar_detectados(detectados)

    def extraer_bool(self, texto):
        detectados = set(self.extraer(texto))
        return {canon: canon in detectados for canon in self._orden}
