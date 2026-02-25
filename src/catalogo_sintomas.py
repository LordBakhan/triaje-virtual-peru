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
        "me duele la muela", "me duele el diente", "duele el diente", "dolor en el diente",
        "diente dolorido", "diente que duele", "doliendo los dientes"
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
        "tengo ansiedad", "estoy nervioso", "estoy ansioso", "estoy ansiosa"
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
        "musculos adoloridos", "musculos doloridos", "dolores musculares",
        "me duele el musculo", "mialgia"
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
        "falta de concentracion", "problemas para concentrarme", "mente nublada",
        "dificultad para concentrarme"
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
        "me duelen los ojos por detrás", "me duele detras de los ojos", "presion detras de los ojos",
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
    "dolor de encias": [
        "dolor de encias", "dolor en las encias", "me duelen las encias",
        "dolor de la encia", "encias adoloridas", "molestia en las encias"
    ],
    "sangrado de encias": [
        "sangrado de encias", "sangran las encias", "me sangran las encias",
        "sangrado en la encia", "encia sangrante"
    ],
    "encias inflamadas": [
        "encias inflamadas", "encia inflamada", "encias hinchadas",
        "inflamacion de encias", "se me inflaman las encias", "encias estan inflamadas",
        "tengo las encias inflamadas"
    ],
    "ulceras bucales": [
        "ulceras bucales", "llagas en la boca", "aftas", "aftas bucales",
        "heridas en la boca", "ulceras en la lengua", "ulcera en la boca", "ulcera bucal"
    ],
    "mal aliento": [
        "mal aliento", "halitosis", "aliento feo", "aliento fuerte",
        "me huele mal la boca"
    ],
    "boca seca": [
        "boca seca", "resequedad bucal", "sequedad en la boca",
        "tengo la boca seca", "se me seca la boca"
    ],
    "dolor de mandibula": [
        "dolor de mandibula", "dolor en la mandibula", "me duele la mandibula",
        "mandibula adolorida", "dolor al abrir la boca"
    ],
    "dolor de lengua": [
        "dolor de lengua", "me duele la lengua", "lengua adolorida",
        "molestia en la lengua", "ardor en la lengua"
    ],
    "dolor al masticar": [
        "dolor al masticar", "me duele al masticar", "masticar me duele",
        "dolor al comer", "molestia al masticar"
    ],
    "oido tapado": [
        "oido tapado", "oidos tapados", "tengo el oido tapado",
        "sensacion de oido tapado", "oido congestionado"
    ],
    "zumbido de oidos": [
        "zumbido de oidos", "zumbido en el oido", "pitido en el oido",
        "ruido en el oido", "tinnitus"
    ],
    "disminucion de audicion": [
        "disminucion de audicion", "escucho menos", "oigo menos",
        "perdida leve de audicion", "audicion baja"
    ],
    "picazon de garganta": [
        "picazon de garganta", "picor de garganta", "comezon de garganta",
        "garganta con picazon", "me pica la garganta"
    ],
    "ronquera": [
        "ronquera", "voz ronca", "estoy ronco", "estoy ronca",
        "afonia leve", "voz tomada"
    ],
    "carraspeo": [
        "carraspeo", "carraspeo frecuente", "tengo que aclarar la garganta",
        "aclaramiento de garganta", "carraspear"
    ],
    "picazon de ojos": [
        "picazon de ojos", "picor de ojos", "comezon en los ojos",
        "me pican los ojos", "ojos con picazon"
    ],
    "ardor de ojos": [
        "ardor de ojos", "me arden los ojos", "quemazon en los ojos",
        "ojos ardientes", "ardor ocular"
    ],
    "secrecion ocular": [
        "secrecion ocular", "leganas", "ojo con secrecion",
        "descarga ocular", "moco en los ojos"
    ],
    "parpados hinchados": [
        "parpados hinchados", "parpado hinchado", "inflamacion de parpados",
        "parpados inflamados", "hinchazon en los parpados"
    ],
    "sensibilidad a la luz": [
        "sensibilidad a la luz", "fotofobia", "la luz me molesta",
        "me molestan las luces", "intolerancia a la luz", "me molesta la luz",
        "la luz me incomoda"
    ],
    "fatiga visual": [
        "fatiga visual", "cansancio visual", "vista cansada",
        "ojos cansados", "me cansa la vista"
    ],
    "hinchazon abdominal": [
        "hinchazon abdominal", "abdomen hinchado", "panza hinchada",
        "barriga inflamada", "vientre hinchado"
    ],
    "distension abdominal": [
        "distension abdominal", "distension del abdomen", "abdomen distendido",
        "me siento distendido", "inflamacion abdominal"
    ],
    "colicos abdominales": [
        "colicos abdominales", "colicos", "retortijones",
        "dolor tipo colico", "espasmos abdominales"
    ],
    "reflujo": [
        "reflujo", "reflujo gastrico", "acido que sube",
        "regurgitacion", "se me sube la comida"
    ],
    "eructos frecuentes": [
        "eructos frecuentes", "muchos eructos", "eructo mucho",
        "eructos constantes", "gases por arriba"
    ],
    "saciedad temprana": [
        "saciedad temprana", "me lleno rapido", "me saturo rapido",
        "lleno con poca comida", "llenura precoz"
    ],
    "dolor pelvico": [
        "dolor pelvico", "dolor en la pelvis", "molestia pelvica",
        "dolor en la parte baja del vientre", "pelvis adolorida"
    ],
    "urgencia urinaria": [
        "urgencia urinaria", "urgencia de orinar", "ganas urgentes de orinar",
        "me dan ganas de orinar de golpe", "necesidad urgente de orinar"
    ],
    "frecuencia urinaria": [
        "frecuencia urinaria", "orino seguido", "orino muy frecuente",
        "voy al bano a cada rato", "miccion frecuente", "orino muy seguido"
    ],
    "orina turbia": [
        "orina turbia", "orina opaca", "orina con aspecto turbio",
        "pipi turbio", "orina nublada", "orino turbio", "la orina sale turbia"
    ],
    "orina con mal olor": [
        "orina con mal olor", "orina con olor fuerte", "mal olor de orina",
        "orina fetida", "pipi con mal olor", "orino con mal olor",
        "mi orina huele fuerte"
    ],
    "picazon vaginal": [
        "picazon vaginal", "comezon vaginal", "picor vaginal",
        "me pica la zona vaginal", "prurito vaginal"
    ],
    "flujo vaginal anormal": [
        "flujo vaginal anormal", "flujo vaginal", "secrecion vaginal anormal",
        "flujo con mal olor", "cambio en el flujo vaginal"
    ],
    "dolor menstrual": [
        "dolor menstrual", "dolor de regla", "dolor de periodo",
        "colicos menstruales", "dismenorrea"
    ],
    "sindrome premenstrual": [
        "sindrome premenstrual", "sintomas premenstruales", "spm",
        "malestar premenstrual", "cambios antes de la menstruacion"
    ],
    "contractura muscular": [
        "contractura muscular", "musculo contracturado", "contractura",
        "nudo muscular", "musculo tieso"
    ],
    "dolor de piernas": [
        "dolor de piernas", "me duelen las piernas", "piernas adoloridas",
        "dolor en las piernas", "piernas doloridas"
    ],
    "dolor de pies": [
        "dolor de pies", "me duelen los pies", "pies adoloridos",
        "dolor en los pies", "pies doloridos"
    ],
    "dolor de manos": [
        "dolor de manos", "me duelen las manos", "manos adoloridas",
        "dolor en las manos", "manos doloridas"
    ],
    "dolor de tobillo": [
        "dolor de tobillo", "dolor en el tobillo", "me duele el tobillo",
        "tobillo adolorido", "tobillo dolorido"
    ],
    "dolor de muneca": [
        "dolor de muneca", "dolor en la muneca", "me duele la muneca",
        "muneca adolorida", "muneca dolorida"
    ],
    "dolor de codo": [
        "dolor de codo", "dolor en el codo", "me duele el codo",
        "codo adolorido", "codo dolorido"
    ],
    "rigidez de hombro": [
        "rigidez de hombro", "hombro rigido", "hombro tieso",
        "dificultad para mover el hombro", "hombro duro"
    ],
    "pesadez en piernas": [
        "pesadez en piernas", "piernas pesadas", "sensacion de pesadez en las piernas",
        "piernas cansadas y pesadas", "pesadez de piernas"
    ],
    "piernas cansadas": [
        "piernas cansadas", "cansancio en las piernas", "fatiga en las piernas",
        "piernas fatigadas", "piernas sin fuerza"
    ],
    "mareo al levantarse": [
        "mareo al levantarse", "me mareo al ponerme de pie", "mareo al pararme",
        "aturdimiento al levantarme", "mareo postural", "me siento mareado al levantarme",
        "me siento mareada al levantarme"
    ],
    "sensibilidad al ruido": [
        "sensibilidad al ruido", "me molesta el ruido", "intolerancia al ruido",
        "sonidos me molestan", "hipersensibilidad al ruido"
    ],
    "niebla mental": [
        "niebla mental", "mente nublada", "cabeza nublada",
        "pensamiento lento", "me cuesta pensar claro"
    ],
    "falta de memoria leve": [
        "falta de memoria leve", "olvidos frecuentes", "se me olvidan las cosas",
        "memoria baja", "dificultad para recordar"
    ],
    "estres": [
        "estres", "estresado", "estresada", "tension emocional",
        "mucho estres", "sobrecarga mental"
    ],
    "animo bajo": [
        "animo bajo", "desanimo", "me siento decaido",
        "me siento decaida", "tristeza leve"
    ],
    "sueno no reparador": [
        "sueno no reparador", "duermo pero no descanso", "descanso insuficiente",
        "me levanto cansado", "me levanto cansada"
    ],
    "despertares nocturnos": [
        "despertares nocturnos", "me despierto en la noche", "despierto varias veces",
        "interrupciones del sueno", "sueño fragmentado"
    ],
    "piel seca": [
        "piel seca", "resequedad en la piel", "piel reseca",
        "piel tirante", "falta de hidratacion en la piel"
    ],
    "descamacion de la piel": [
        "descamacion de la piel", "piel descamada", "se me pela la piel",
        "escamas en la piel", "pelado de piel"
    ],
    "urticaria": [
        "urticaria", "habones", "ronchas que pican",
        "erupcion urticarial", "salida de ronchas"
    ],
    "acne": [
        "acne", "granitos", "espinillas", "barros",
        "brotes de acne", "piel acneica"
    ],
    "picazon en el cuero cabelludo": [
        "picazon en el cuero cabelludo", "comezon en el cuero cabelludo",
        "picor en el cuero cabelludo", "me pica la cabeza", "cuero cabelludo con picazon",
        "me pica el cuero cabelludo"
    ],
    "caspa": [
        "caspa", "descamacion del cuero cabelludo", "escamas en el cabello",
        "hombros con caspa", "caspa abundante"
    ],
    "caida de cabello": [
        "caida de cabello", "se me cae el cabello", "perdida de cabello",
        "caida del pelo", "pierdo mucho pelo"
    ],
    "dolor de talon": [
        "dolor de talon", "dolor en el talon", "me duele el talon",
        "talon adolorido", "talon dolorido"
    ],
    "dolor de pantorrilla": [
        "dolor de pantorrilla", "dolor en la pantorrilla", "me duele la pantorrilla",
        "pantorrilla adolorida", "pantorrilla dolorida"
    ],
    "dolor de antebrazo": [
        "dolor de antebrazo", "dolor en el antebrazo", "me duele el antebrazo",
        "antebrazo adolorido", "antebrazo dolorido"
    ],
    "dolor de dedos": [
        "dolor de dedos", "dolor en los dedos", "me duelen los dedos",
        "dedos adoloridos", "dedos doloridos"
    ],
    "dolor en la planta del pie": [
        "dolor en la planta del pie", "dolor en la planta de los pies",
        "me duele la planta del pie", "planta del pie adolorida",
        "dolor plantar"
    ],
    "calambres nocturnos": [
        "calambres nocturnos", "calambres en la noche", "me dan calambres de noche",
        "espasmos nocturnos", "calambres al dormir"
    ],
    "boca amarga": [
        "boca amarga", "sabor amargo en la boca", "amargor en la boca",
        "siento la boca amarga", "me sabe amarga la boca"
    ],
    "sabor metalico": [
        "sabor metalico", "sabor a metal", "sabor raro en la boca",
        "sabor ferrico", "gusto metalico"
    ],
    "dolor en la boca del estomago": [
        "dolor en la boca del estomago", "dolor en el epigastrio", "ardor en la boca del estomago",
        "me duele la boca del estomago", "molestia epigastrica"
    ],
    "hipo frecuente": [
        "hipo frecuente", "tengo hipo seguido", "hipo constante",
        "me da hipo a cada rato", "hipo repetitivo"
    ],
    "sensacion de llenura": [
        "sensacion de llenura", "me siento lleno", "llenura abdominal",
        "sensacion de estar lleno", "plenitud abdominal"
    ],
    "evacuacion incompleta": [
        "evacuacion incompleta", "siento que no evacuo completo", "no termino de evacuar",
        "sensacion de evacuacion incompleta", "evacuacion parcial"
    ],
    "nicturia": [
        "nicturia", "me levanto a orinar en la noche", "orino de noche",
        "miccion nocturna", "voy al bano por la noche"
    ],
    "dolor suprapubico": [
        "dolor suprapubico", "dolor sobre el pubis", "dolor en el bajo vientre",
        "me duele encima de la vejiga", "molestia suprapubica"
    ],
    "nariz seca": [
        "nariz seca", "resequedad nasal", "nariz resecada",
        "se me seca la nariz", "sequedad en la nariz"
    ],
    "sequedad de labios": [
        "sequedad de labios", "labios secos", "resequedad en los labios",
        "labios resecos", "siento secos los labios"
    ],
    "labios agrietados": [
        "labios agrietados", "labios partidos", "se me parten los labios",
        "grietas en los labios", "labios cuarteados"
    ],
    "tic en el ojo": [
        "tic en el ojo", "temblor en el parpado", "parpado que tiembla",
        "espasmo en el parpado", "me tiembla el ojo"
    ],
    "ojo lloroso": [
        "ojo lloroso", "ojos llorosos", "ojo que lagrimea",
        "lagrimeo en un ojo", "lloro del ojo"
    ],
    "sueno ligero": [
        "sueno ligero", "duermo ligero", "sueño liviano",
        "me despierto con cualquier ruido", "sueño superficial"
    ],
    "pesadillas frecuentes": [
        "pesadillas frecuentes", "tengo pesadillas", "malos suenos frecuentes",
        "pesadillas seguidas", "suenos desagradables recurrentes"
    ],
    "somnolencia diurna": [
        "somnolencia diurna", "me da sueno de dia", "sueño durante el dia",
        "me siento adormilado en el dia", "cansancio con sueno en el dia"
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
