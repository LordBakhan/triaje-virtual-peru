# src/nlp_extractor.py
import re
import unicodedata
from catalogo_sintomas import CATALOGO_SINTOMAS

def _normalizar(texto: str) -> str:
    if texto is None:
        return ""
    t = str(texto).lower()
    t = unicodedata.normalize('NFD', t)
    t = ''.join(ch for ch in t if unicodedata.category(ch) != 'Mn')
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

class SintomaExtractor:
    def __init__(self, catalogo=None):
        self.catalogo = catalogo if catalogo is not None else CATALOGO_SINTOMAS
        variantes = []
        for canon, lista in self.catalogo.items():
            all_variantes = [canon] + list(lista)
            for v in all_variantes:
                vn = _normalizar(v)
                if not vn:
                    continue
                pat = re.compile(r'\b' + re.escape(vn) + r'\b', flags=re.IGNORECASE)
                variantes.append((canon, vn, pat))
        variantes.sort(key=lambda x: len(x[1]), reverse=True)
        self._variantes = variantes

    def extraer(self, texto):
        txt_norm = _normalizar(texto)
        detectados = set()
        if not txt_norm:
            return []
        for canon, vn, pat in self._variantes:
            if canon in detectados:
                continue
            if pat.search(txt_norm):
                detectados.add(canon)
        detected_list = list(detectados)
        norm_map = {c: _normalizar(c) for c in detected_list}
        to_remove = set()
        for a in detected_list:
            for b in detected_list:
                if a == b: continue
                na = norm_map[a]; nb = norm_map[b]
                if len(na) < len(nb) and na in nb:
                    to_remove.add(a)
        detectados -= to_remove
        orden = list(self.catalogo.keys())
        resultado = [c for c in orden if c in detectados]
        resto = [c for c in detectados if c not in orden]
        resultado.extend(sorted(resto))
        return resultado

    def extraer_bool(self, texto):
        txt_norm = _normalizar(texto)
        res = {canon: False for canon in self.catalogo.keys()}
        if not txt_norm:
            return res
        for canon, vn, pat in self._variantes:
            if not res.get(canon) and pat.search(txt_norm):
                res[canon] = True
        detected = [k for k, v in res.items() if v]
        norm_map = {c: _normalizar(c) for c in detected}
        for a in detected:
            for b in detected:
                if a == b: continue
                na = norm_map[a]; nb = norm_map[b]
                if len(na) < len(nb) and na in nb:
                    res[a] = False
        return res
 