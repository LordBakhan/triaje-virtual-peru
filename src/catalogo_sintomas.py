# src/catalogo_sintomas.py
import re
import unicodedata

CATALOGO_SINTOMAS = {
    "dolor de cabeza": [
        "dolor de cabeza", "cefalea", "me duele la cabeza", "duele la cabeza",
        "dolor cabeza", "jaqueca", "migraña", "migrañas", "dolor en la cabeza",
        "estoy con dolor de cabeza", "dolor de mi cabeza", "doliendo la cabeza"
    ],
    "fiebre": [
        "fiebre", "temperatura alta", "calentura", "me subió la fiebre", "tengo fiebre",
        "fiebres", "febril", "estado febril"
    ],
    "dolor de garganta": [
        "dolor de garganta", "me duele la garganta", "duele la garganta",
        "molestia al tragar", "garganta inflamada", "dolor en la garganta",
        "dolor garganta", "doliendo la garganta", "ardor en la garganta"
    ],
    "tos seca": [
        "tos seca", "tos sin flema", "tos seca constante", "tos seca por dias", "tos seca por días",
        "tos reseca", "tos seca persistente"
    ],
    "tos persistente": [
        "tos persistente", "tos crónica", "tos cronica", "tos por dias", "tos por días",
        "tos continua", "tos que no se quita"
    ],
    "tos": [
        "tos", "tosiendo", "tos leve", "ataques de tos"
    ],
    "dolor de estómago": [
        "dolor de estómago", "dolor abdominal", "dolor estomacal", "dolor de barriga",
        "me duele el estómago", "me duele la barriga", "estoy con dolor de estómago",
        "dolor en el estómago", "doliendo el estómago"
    ],
    "diarrea": [
        "diarrea", "heces liquidas", "heces líquidas", "estoy con diarrea", "correrías",
        "me dio diarrea"
    ],
    "mareos": [
        "mareos", "mareo", "mareos repentinos", "mareado", "me siento mareado", "me mareo",
        "estoy mareado", "dando vueltas la cabeza"
    ],
    "vértigo": [
        "vértigo", "vertigo", "sensación de vértigo", "siento vértigo"
    ],
    "pérdida de equilibrio": [
        "pérdida de equilibrio", "perdida de equilibrio", "pérdida del equilibrio",
        "pierdo el equilibrio", "problemas de equilibrio", "no tengo equilibrio",
        "me caigo por falta de equilibrio"
    ],
    "sarpullido": [
        "sarpullido", "erupcion cutanea", "erupción cutánea", "erupcion", "ronchas",
        "salpullido", "manchas en la piel", "granitos en la piel"
    ],
    "picazón": [
        "picazón", "picazon", "comezon", "comezón", "prurito", "me pica la piel",
        "picor", "estoy con picazón"
    ],
    "dolor de diente": [
        "dolor de diente", "dolor dental", "dolor de muela", "me duele un diente",
        "me duele la muela", "diente dolorido", "doliendo los dientes"
    ],
    "hormigueo en la cara": [
        "hormigueo en la cara",
        "hormigueo facial", 
        "hormigueo en el rostro",
        "entumecimiento de la cara",
        "cosquilleo en la cara",
        "cosquilleo facial",
        "parestesia en la cara",
        "entumecido el rostro", 
        "rostro dormido",
        "cara dormida",
        "cara entumecida",
        "me hormiguea la cara",
        "siento cosquilleo en la cara",
        "se me duerme la cara",
    ],
   "dolor de pecho": [
        "dolor de pecho",
        "dolor en el pecho",
        "me duele el pecho",
        "dolor torácico",
        "molestia en el pecho",
        "malestar en el pecho",
        "ardor en el pecho",
        "dolor torax",
        "torax dolorido",
    ],

    "inflamación": [
        "inflamación",
        "inflamado",
        "hinchazón",
        "me hinché",
        "estoy hinchado",
        "hinchada",
        "se me inflamó",
        "se me hinchó",
        "zona inflamada",
        "parte hinchada",
        "enrojecimiento e inflamación",
    ],
    "dolor de hombro": [
        "dolor de hombro",
        "dolor en el hombro",
        "me duele el hombro",
        "hombro adolorido",
        "hombro dolorido",
        "punzada en el hombro",
        "molestia en el hombro",
        "hombro con dolor",
        "dolor en mis hombros",
        "me está doliendo el hombro",
        "dolor al mover el hombro",
    ],
    "dolor de oído": [
        "dolor de oído",
        "dolor en el oído",
        "me duele el oído",
        "otalgia",
        "oído adolorido",
        "oído dolorido",
        "punzada en el oído",
        "molestia en el oído",
        "incomodidad en el oído",
        "dolor en los oídos",
        "me está doliendo el oído",
        "dolor dentro del oído",
    ],
    "dolor de espalda": [
        "dolor de espalda", "dolor de espalda baja", "espalda adolorida",
        "me duele la espalda", "espalda dolorida"
    ],
    "dolor lumbar": [
        "dolor lumbar", "lumbalgia", "dolor en la zona lumbar", "me duele la zona lumbar",
        "zona lumbar dolorida"
    ],
    "presión en el pecho": [
        "presión en el pecho", "presion en el pecho", "opresión en el pecho",
        "opresion en el pecho", "siento presión en el pecho", "apretón en el pecho", "punzada en el pecho","punzadas en el pecho"
    ], 
    "falta de aire": [
        "falta de aire", "sin aliento", "sin aire", "no puedo respirar", "ahogo",
        "no entra aire", "me falta el aire"
    ],
    "dificultad para respirar": [
        "dificultad para respirar", "problemas para respirar", "dificultad respiratoria",
        "me cuesta respirar", "me cuesta trabajo respirar", "respiro con dificultad"
    ],
    "ardor al orinar": [
        "ardor al orinar", "dolor al orinar", "disuria", "me arde al orinar", "ardor cuando orino"
    ],
    "pérdida de apetito": [
        "pérdida de apetito", "falta de apetito", "no tengo apetito", "sin apetito",
        "perdi el apetito"
    ],
    "ojos rojos": [
        "ojos rojos", "ojos enrojecidos", "conjuntivitis", "ojos irritados", "rojez en los ojos"
    ],
    "lagrimeo": [
        "lagrimeo", "ojos llorosos", "lagrimeando", "lagrimeo constante", "ojos con lágrimas"
    ],
    "insomnio": [
        "insomnio", "dificultad para dormir", "no puedo dormir", "me cuesta dormir",
        "no duermo bien"
    ],
    "ansiedad": [
        "ansiedad", "nerviosismo", "ansiedad intensa", "me siento ansioso",
        "tengo ansiedad", "estoy nervioso"
    ],
    "congestión nasal": [
        "congestión nasal", "nariz tapada", "congestion nasal", "nariz congestionada",
        "tengo la nariz tapada"
    ],
    "estornudos": [
        "estornudos", "estornudar", "estornudando", "tengo muchos estornudos"
    ],
    "dolor de articulaciones": [
        "dolor de articulaciones", "dolor articular", "artralgia", "me duelen las articulaciones",
        "articulaciones adoloridas", "doliendo las articulaciones"
    ],
    "hinchazón": [
        "hinchazón", "hinchazon", "hinchado", "inflamación", "inflamacion",
        "estoy hinchado", "parte hinchada", "se me hinchó"
    ],
    "inflamación de rodilla": [
        "inflamación de rodilla", "inflamacion de rodilla", "hinchazon de rodilla",
        "hinchazón de rodilla", "rodilla inflamada", "rodilla hinchada"
    ],
    "dolor de brazo": [
        "dolor de brazo", "brazo adolorido", "me duele el brazo", "dolor en el brazo"
    ],
    "dolor de cuello": [
        "dolor de cuello", "rigidez de cuello", "me duele el cuello", "cuello adolorido"
    ],
    "rigidez": [
        "rigidez", "rigidez matutina", "cuello rígido", "cuerpo rígido"
    ],
    "náuseas": [
        "náuseas", "nauseas", "ganas de vomitar", "siento nauseas", "estoy con náuseas"
    ],
    "vómitos": [
        "vómitos", "vomitos", "vomitar", "arcadas", "devolver", "estoy vomitando"
    ],
    "visión borrosa": [
        "visión borrosa", "vision borrosa", "vista nublada", "veo borroso", "veo mal",
        "visión doble", "vision doble"
    ],
    "ardor": [
        "ardor", "sensación de ardor", "sensacion de ardor", "quemazon", "sensacion de quemazon",
        "me arde", "siento ardor"
    ],
    "fatiga": [
        "fatiga", "cansancio", "agotamiento", "fatiga intensa", "estoy fatigado",
        "me siento cansado"
    ],
    "somnolencia": [
        "somnolencia", "sueño excesivo", "somnoliento", "tengo sueño", "siento sueño"
    ],
    "malestar general": [
        "malestar general", "indisposición", "malestar", "me siento mal", "estoy mal"
    ],
    "palpitaciones": [
        "palpitaciones", "latidos rapidos", "latidos acelerados", "siento palpitaciones",
        "mi corazón late rápido"
    ],
    "flema": [
        "flema", "con flema", "mucosidad", "expulsando flema"
    ],
    "sangrado nasal": [
        "sangrado nasal", "epistaxis", "sangre por la nariz", "sangrado de nariz"
    ],
    "sensibilidad": [
        "sensibilidad", "hipersensibilidad", "estoy sensible"
    ],
    "gases": [
        "gases", "flatulencia", "estoy con gases", "muchos gases"
    ],
    "escalofrios": [
        "escalofrios", "escalofrios intensos", "chuchos", "tiritones",
        "tengo escalofrios", "me dan escalofrios", "siento frio con temblor"
    ],
    "temblores": [
        "temblores", "temblor", "estoy temblando", "me tiembla el cuerpo",
        "me tiemblan las manos", "tiritar"
    ],
    "sudoracion": [
        "sudoracion", "sudor", "sudor excesivo", "estoy sudando", "sudo mucho",
        "transpiro mucho"
    ],
    "sudores nocturnos": [
        "sudores nocturnos", "sudoracion nocturna", "sudo por la noche",
         "me despierto sudando", "sudor en la noche"
    ],
    "sibilancias": [
        "sibilancias", "silbido al respirar", "me silba el pecho",
        "respiracion con pitido", "pitos al respirar", "wheezing"
    ],
    "moqueo": [
        "moqueo", "moquera", "nariz que moquea", "me gotea la nariz",
        "secrecion nasal", "nariz chorreando"
    ],
    "ganglios inflamados": [
        "ganglios inflamados", "ganglios hinchados", "ganglios del cuello inflamados",
        "me salieron bolitas en el cuello", "glandulas inflamadas"
    ],
    "dolor muscular": [
        "dolor muscular", "dolor en los musculos", "me duelen los musculos",
        "musculos adoloridos", "musculos doloridos", "mialgia"
    ],
    "debilidad muscular": [
        "debilidad muscular", "musculos debiles", "falta de fuerza",
        "falta de fuerza en brazos y piernas", "me siento debil"
    ],
    "acidez": [
        "acidez", "agruras", "ardor estomacal", "me arde el estomago",
        "acido en el estomago", "me sube el acido"
    ],
    "indigestion": [
        "indigestion", "mala digestion", "digestión pesada", "digestion pesada",
        "empacho", "me cayo pesada la comida"
    ],
    "estreñimiento": [
        "estrenimiento", "estreñimiento", "constipacion", "constipacion intestinal",
        "estoy estrenido", "no puedo evacuar", "dificultad para evacuar"
    ],
    "hambre excesiva": [
        "hambre excesiva", "mucha hambre", "hambre constante",
        "apetito aumentado", "siento hambre todo el tiempo"
    ],
    "irritabilidad": [
        "irritabilidad", "irritable", "estoy irritable", "me irrito facil",
        "estoy de mal humor", "me enojo facilmente"
    ],
    "cambios de humor": [
        "cambios de humor", "cambios de animo", "humor variable",
        "altibajos emocionales"
    ],
    "inquietud": [
        "inquietud", "intranquilidad", "estoy inquieto", "estoy inquieta",
        "no puedo quedarme quieto", "no puedo quedarme quieta"
    ],
    "dificultad para concentrarse": [
        "dificultad para concentrarse", "me cuesta concentrarme",
        "falta de concentracion", "problemas para concentrarme", "mente nublada"
    ],
    "bochornos": [
        "bochornos", "bochorno", "sofocos", "calor subito",
        "oleadas de calor", "siento calor de golpe"
    ],
    "ojos secos": [
        "ojos secos", "sequedad ocular", "ojo seco",
        "ojos resecos", "sensacion de arena en los ojos"
    ],
    "sequedad vaginal": [
        "sequedad vaginal", "resequedad vaginal", "vagina seca",
        "molestia vaginal por resequedad"
    ],
    "menstruacion irregular": [
        "menstruacion irregular", "periodo irregular", "regla irregular",
        "ciclos irregulares", "periodos salteados"
    ],
    "perdida de peso": [
        "perdida de peso", "baje de peso", "estoy perdiendo peso",
        "adelgazamiento", "he adelgazado sin querer"
    ],
    "dolor de rodilla": [
        "dolor de rodilla", "dolor en la rodilla", "me duele la rodilla",
        "rodilla adolorida", "rodilla dolorida", "molestia en la rodilla"
    ],
    "dolor de cadera": [
        "dolor de cadera", "dolor en la cadera", "me duele la cadera",
        "cadera adolorida", "cadera dolorida", "molestia en la cadera"
    ],
    "dificultad para caminar": [
        "dificultad para caminar", "me cuesta caminar", "camino con dificultad",
        "caminar me duele", "caminar es incomodo", "dolor al caminar"
    ],
    "hormigueo en las extremidades": [
        "hormigueo en las extremidades",
        "hormigueo en extremidades",
        "hormigueo extremidades",
        "hormigueo brazos y piernas",
        "hormigueo en brazos y piernas",
        "hormigueo en manos y pies",
        "hormigueo manos y pies",
        "cosquilleo en las extremidades",
        "cosquilleo en extremidades",
        "parestesia en las extremidades",
        "entumecimiento en extremidades",
        "manos dormidas",
        "piernas dormidas",
        "brazos entumecidos",
        "piernas entumecidas",
        "me hormiguean las piernas",
        "me hormiguean los brazos",
        "sensación de corriente en las extremidades"
    ],
    "gripe": [
        "gripe", "gripa", "resfriado", "resfrio", "resfriado comun",
        "catarro", "catarro comun", "estado gripal", "sintomas gripales",
        "me dio gripe", "me dio gripa", "estoy agripado", "estoy agripada",
        "estoy resfriado", "estoy resfriada", "tengo gripe", "tengo gripa"
    ],
    "dolor detrás de los ojos": [
        "dolor detrás de los ojos", "dolor detras de los ojos",
        "dolor detrás del ojo", "dolor detras del ojo",
        "me duelen los ojos por detrás", "presion detras de los ojos",
        "presión detrás de los ojos", "dolor ocular profundo"
    ],
    "presion sinusal": [
        "presion sinusal", "presión sinusal", "presion en los senos paranasales",
        "presión en los senos paranasales", "senos paranasales congestionados",
        "dolor en los senos paranasales", "sinus pressure"
    ],
    "perdida del olfato": [
        "perdida del olfato", "pérdida del olfato", "no siento olores",
        "no huelo bien", "no puedo oler", "disminucion del olfato",
        "disminución del olfato", "anosmia"
    ],
    "dolor al defecar": [
        "dolor al defecar", "dolor al evacuar", "me duele al evacuar",
        "evacuar me duele", "dolor al hacer del cuerpo",
        "dolor durante las deposiciones", "dolor durante las heces"
    ],
    "irritacion anal": [
        "irritacion anal", "irritación anal", "ardor anal",
        "dolor en la zona anal", "comezon anal", "comezón anal",
        "molestia anal", "irritacion en el ano", "irritación en el ano"
    ],
    "calambres": [
        "calambres", "calambre", "espasmos musculares", "espasmo muscular",
        "me dan calambres", "tengo calambres", "musculo acalambrado",
        "piernas acalambradas"
    ],
    "aumento de apetito": [
        "aumento de apetito", "apetito aumentado", "mas apetito de lo normal",
        "mucho apetito", "tengo mas hambre de lo normal",
        "incremento del apetito", "hambre aumentada"
    ],
    "uñas quebradizas": [
        "uñas quebradizas", "unas quebradizas", "uñas fragiles", "unas fragiles",
        "uñas que se rompen facil", "unas que se rompen facil",
        "uñas debiles", "unas debiles"
    ],
    "frio en manos y pies": [
        "frio en manos y pies", "frío en manos y pies", "manos frias",
        "manos frías", "pies frios", "pies fríos", "extremidades frias",
        "extremidades frías", "siento las manos y pies frios"
    ],
    "hinchazon de piernas": [
        "hinchazon de piernas", "hinchazón de piernas", "piernas hinchadas",
        "piernas inflamadas", "se me hinchan las piernas",
        "edema en piernas", "piernas con hinchazon"
    ],
    "venas prominentes en pantorrilla": [
        "venas prominentes en pantorrilla", "venas marcadas en la pantorrilla",
        "venas saltadas en la pantorrilla", "venas visibles en pantorrilla",
        "venas abultadas en la pierna", "varices en pantorrilla"
    ],
}


def _quitar_tildes(texto: str) -> str:
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn")


def _normalizar_texto(texto: str) -> str:
    texto = texto.strip().lower()
    return re.sub(r"\s+", " ", texto)


def _agregar_variante(destino, vistos, texto):
    base = _normalizar_texto(texto)
    if not base:
        return

    for candidato in (base, _quitar_tildes(base)):
        if candidato and candidato not in vistos:
            vistos.add(candidato)
            destino.append(candidato)


def _expandir_patrones(destino, vistos, termino):
    if termino.startswith("dolor de "):
        zona = termino.replace("dolor de ", "", 1).strip()
        _agregar_variante(destino, vistos, f"dolor en {zona}")
        _agregar_variante(destino, vistos, f"me duele {zona}")
        _agregar_variante(destino, vistos, f"duele {zona}")
        _agregar_variante(destino, vistos, f"me esta doliendo {zona}")
        _agregar_variante(destino, vistos, f"{zona} adolorido")
        _agregar_variante(destino, vistos, f"{zona} adolorida")
        _agregar_variante(destino, vistos, f"{zona} dolorido")
        _agregar_variante(destino, vistos, f"{zona} dolorida")

    if termino.startswith("dolor en "):
        zona = termino.replace("dolor en ", "", 1).strip()
        _agregar_variante(destino, vistos, f"me duele {zona}")
        _agregar_variante(destino, vistos, f"duele {zona}")
        _agregar_variante(destino, vistos, f"me esta doliendo {zona}")

    if termino.startswith("me duele "):
        zona = termino.replace("me duele ", "", 1).strip()
        _agregar_variante(destino, vistos, f"duele {zona}")
        _agregar_variante(destino, vistos, f"me esta doliendo {zona}")

    if termino.startswith("duele "):
        zona = termino.replace("duele ", "", 1).strip()
        _agregar_variante(destino, vistos, f"me duele {zona}")
        _agregar_variante(destino, vistos, f"me esta doliendo {zona}")

    if termino.startswith("estoy con "):
        _agregar_variante(destino, vistos, termino.replace("estoy con ", "", 1).strip())

    if termino.startswith("tengo "):
        _agregar_variante(destino, vistos, termino.replace("tengo ", "", 1).strip())


for _sintoma, _variantes in list(CATALOGO_SINTOMAS.items()):
    _resultado = []
    _vistos = set()

    _agregar_variante(_resultado, _vistos, _sintoma)

    for _item in _variantes:
        _agregar_variante(_resultado, _vistos, _item)
        _expandir_patrones(_resultado, _vistos, _normalizar_texto(_item))

    _expandir_patrones(_resultado, _vistos, _normalizar_texto(_sintoma))
    CATALOGO_SINTOMAS[_sintoma] = _resultado
