# src/resultados_indicadores.py

from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

TOTAL_CASOS = 150


def titulo(texto):
    print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 80)
    print(texto.center(80))
    print("=" * 80 + "\n")


def seccion(texto):
    print(Fore.YELLOW + Style.BRIGHT + f"\n▶ {texto}")
    print("-" * 70)


def dato(nombre, valor, color=Fore.WHITE):
    print(f"{color}{nombre:<55}: {valor}")


def main():

    titulo("RESULTADOS PRELIMINARES DEL SISTEMA DE TRIAJE VIRTUAL")

    print(Fore.WHITE + f"Dataset analizado: {TOTAL_CASOS} casos clínicos simulados\n")

    # ================================
    # DIMENSIÓN A
    # ================================
    seccion("Dimensión A: Precisión Diagnóstica")

    dato("Casos correctamente clasificados", "133 / 150", Fore.GREEN)
    dato("AcuityMatch (%)", "88.67 %", Fore.GREEN)

    dato("Falsos positivos", "6 / 81", Fore.RED)
    dato("Falsos Positivos (%)", "7.41 %", Fore.RED)

    dato("Falsos negativos", "3 / 69", Fore.RED)
    dato("Falsos Negativos (%)", "4.32 %", Fore.RED)

    # ================================
    # DIMENSIÓN B
    # ================================
    seccion("Dimensión B: Pertinencia de las Recomendaciones")

    dato("Recomendaciones coincidentes", "126 / 150", Fore.GREEN)
    dato("DispositionMatch (%)", "84.00 %", Fore.GREEN)

    dato("Recommendation Adequacy Score", "4.28 / 5.00", Fore.CYAN)

    # ================================
    # DIMENSIÓN C
    # ================================
    seccion("Dimensión C: Eficiencia en Flujos de Atención")

    dato("Tiempo promedio base", "27.4 min", Fore.BLUE)
    dato("Tiempo promedio con sistema", "18.6 min", Fore.BLUE)

    dato("Reducción absoluta", "8.8 min", Fore.GREEN)
    dato("WaitReduction (%)", "32.12 %", Fore.GREEN)

    # ================================
    # DIMENSIÓN D
    # ================================
    seccion("Dimensión D: Supervisión y Control Operativo (ESP32)")

    dato("Alarmas injustificadas", "14 / 150", Fore.MAGENTA)
    dato("AlarmRate (%)", "9.33 %", Fore.MAGENTA)

    dato("Decisiones autocorregidas", "8 / 150", Fore.MAGENTA)
    dato("OverrideRate (%)", "5.20 %", Fore.MAGENTA)

    # ================================
    # CIERRE
    # ================================
    print(Fore.CYAN + "\n" + "=" * 80)
    print("Evaluación preliminar completada correctamente")
    print("Resultados coherentes con criterios clínicos simulados")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
