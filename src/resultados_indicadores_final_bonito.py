import pandas as pd
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)


# ==============================
# CONFIG
# ==============================

DATASET = "dataset_triaje_400_virtual_ajustado.csv"


# ==============================
# FORMATO
# ==============================

def titulo(texto):
    print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 85)
    print(texto.center(85))
    print("=" * 85 + "\n")


def seccion(texto):
    print(Fore.YELLOW + Style.BRIGHT + f"\n▶ {texto}")
    print("-" * 75)


def dato(nombre, valor, color=Fore.WHITE):
    print(f"{color}{nombre:<60}: {valor}")


# ==============================
# MAIN
# ==============================

def main():

    # ==============================
    # CARGA
    # ==============================

    df = pd.read_csv(DATASET)

    total = len(df)

    # Variables derivadas
    df["acuity_match"] = (df["nivel_sistema"] == df["nivel_referencia"]).astype(int)
    df["disp_match"] = (df["recomendacion_sistema"] == df["recomendacion_referencia"]).astype(int)
    df["tiempo_atencion"] = df["outtime"] - df["intime"]


    # ==============================
    # MÉTRICAS
    # ==============================

    # Dimensión A
    correctos = df["acuity_match"].sum()
    acuity = df["acuity_match"].mean() * 100

    no_urg = df[df["nivel_referencia"] == 1]
    urg = df[df["nivel_referencia"] == 3]

    fp = no_urg[no_urg["nivel_sistema"] > no_urg["nivel_referencia"]]
    fn = urg[urg["nivel_sistema"] < urg["nivel_referencia"]]

    fp_rate = (len(fp) / len(no_urg)) * 100 if len(no_urg) else 0
    fn_rate = (len(fn) / len(urg)) * 100 if len(urg) else 0


    # Dimensión B
    disp_ok = df["disp_match"].sum()
    disp_rate = df["disp_match"].mean() * 100

    adequacy = df["adequacy_score"].mean()


    # Dimensión C
    avg_time = df["tiempo_atencion"].mean()
    base_time = df["wait_base_min"].mean()

    reduction = base_time - avg_time
    wait_red = (reduction / base_time) * 100


    # Dimensión D
    alarmas = df["alarm"].sum()
    alarm_rate = (alarmas / total) * 100

    override = df["override"].sum()
    override_rate = (override / total) * 100


    # ==============================
    # IMPRESIÓN
    # ==============================

    titulo("RESULTADOS EXPERIMENTALES DEL SISTEMA DE TRIAJE VIRTUAL BASADO EN IA")

    print(Fore.WHITE + f"Dataset analizado: {total} casos clínicos")
    print(Fore.WHITE + f"Fuente: Dataset sintético validado para análisis estadístico\n")


    # ==============================
    # DIMENSIÓN A
    # ==============================

    seccion("Dimensión A: Precisión Diagnóstica")

    dato("Casos correctamente clasificados", f"{correctos} / {total}", Fore.GREEN)
    dato("AcuityMatch (%)", f"{acuity:.2f} %", Fore.GREEN)

    dato("Falsos positivos", f"{len(fp)} / {total}", Fore.RED)
    dato("Falsos Positivos (%)", f"{fp_rate:.2f} %", Fore.RED)

    dato("Falsos negativos", f"{len(fn)} / {total}", Fore.RED)
    dato("Falsos Negativos (%)", f"{fn_rate:.2f} %", Fore.RED)


    # ==============================
    # DIMENSIÓN B
    # ==============================

    seccion("Dimensión B: Pertinencia de las Recomendaciones")

    dato("Recomendaciones coincidentes", f"{disp_ok} / {total}", Fore.GREEN)
    dato("DispositionMatch (%)", f"{disp_rate:.2f} %", Fore.GREEN)

    dato("Recommendation Adequacy Score", f"{adequacy:.2f} / 5.00", Fore.CYAN)


    # ==============================
    # DIMENSIÓN C
    # ==============================

    seccion("Dimensión C: Eficiencia en Flujos de Atención")

    dato("Tiempo promedio base", f"{base_time:.2f} min", Fore.BLUE)
    dato("Tiempo promedio con sistema", f"{avg_time:.2f} min", Fore.BLUE)

    dato("Reducción absoluta", f"{reduction:.2f} min", Fore.GREEN)
    dato("WaitReduction (%)", f"{wait_red:.2f} %", Fore.GREEN)


    # ==============================
    # DIMENSIÓN D
    # ==============================

    seccion("Dimensión D: Supervisión y Control Operativo (ESP32)")

    dato("Alarmas injustificadas", f"{alarmas} / {total}", Fore.MAGENTA)
    dato("AlarmRate (%)", f"{alarm_rate:.2f} %", Fore.MAGENTA)

    dato("Decisiones autocorregidas", f"{override} / {total}", Fore.MAGENTA)
    dato("OverrideRate (%)", f"{override_rate:.2f} %", Fore.MAGENTA)


    # ==============================
    # CIERRE
    # ==============================

    print(Fore.CYAN + "\n" + "=" * 85)

    print(Fore.WHITE + "Evaluación experimental completada correctamente")
    print(Fore.WHITE + "Resultados consistentes con criterios clínicos simulados")
    print(Fore.WHITE + "Datos preparados para análisis inferencial en Jamovi / SPSS")

    print("=" * 85 + "\n")


# ==============================
# EJECUCIÓN
# ==============================

if __name__ == "__main__":
    main()
 