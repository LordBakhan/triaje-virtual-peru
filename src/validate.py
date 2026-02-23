# src/validate.py
from nlp_extractor import SintomaExtractor


def main():
    extractor = SintomaExtractor()

    print("=== Modo interactivo de extraccion ===")
    print("Escribe una frase del paciente y presiona Enter.")
    print("Para salir: salir, exit, q")
    print()

    while True:
        try:
            texto = input("Texto> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo del modo interactivo.")
            break

        if not texto:
            continue

        if texto.lower() in {"salir", "exit", "q"}:
            print("Saliendo del modo interactivo.")
            break

        detectados = extractor.extraer(texto)
        print(f"Detectados ({len(detectados)}): {detectados}\n")


if __name__ == "__main__":
    main()
