# src/validate_ml.py
import joblib
from nlp_extractor import SintomaExtractor

MODEL_PATH = "models/model_bundle.joblib"
extractor = SintomaExtractor()

def cargar_modelo():
    try:
        bundle = joblib.load(MODEL_PATH)
        return bundle["vectorizer"], bundle["clf"]
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        return None, None

def main():
    print("=== Validación de ML con extractor activo ===")
    vectorizer, model = cargar_modelo()

    if not vectorizer or not model:
        print("No se pudo cargar el modelo.")
        return

    while True:
        texto = input("\nIngrese texto del paciente (o 'salir'/'exit'): ")
        if texto.lower() in ["salir", "exit"]:
            break

        sintomas_detectados = extractor.extraer(texto)
        sintomas_detectados = [s.lower().strip() for s in sintomas_detectados if s]

        # Predicción ML solo si hay múltiples síntomas
        if len(sintomas_detectados) > 1:
            X_vec = vectorizer.transform([texto])
            pred = int(model.predict(X_vec)[0])
        elif len(sintomas_detectados) == 1:
            # Un solo síntoma → nivel por defecto (prioridad)
            from api import sintomas_prioridad
            pred = sintomas_prioridad.get(sintomas_detectados[0], 1)
        else:
            pred = 0

        print("\n--- Resultados ---")
        print(f"Sintomas detectados: {sintomas_detectados}")
        print(f"Nivel de urgencia predicho: {pred}")

if __name__ == "__main__":
    main()
 