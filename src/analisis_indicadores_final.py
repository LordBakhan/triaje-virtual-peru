import pandas as pd
from colorama import Fore, init

init(autoreset=True)

# ==============================
# CARGA
# ==============================

ruta = "dataset_triaje_400_virtual_ajustado.csv"
df = pd.read_csv(ruta)


# ==============================
# VARIABLES DERIVADAS
# ==============================

# Acierto en nivel
df["acuity_match"] = (df["nivel_sistema"] == df["nivel_referencia"]).astype(int)

# Acierto en recomendación
df["disp_match"] = (df["recomendacion_sistema"] == df["recomendacion_referencia"]).astype(int)

# Tiempo atención
df["tiempo_atencion"] = df["outtime"] - df["intime"]


# ==============================
# DIMENSIÓN A — PRECISIÓN
# ==============================

total = len(df)

# Concordancia
acuity_match = df["acuity_match"].mean() * 100


# Falsos positivos / negativos
no_urgentes = df[df["nivel_referencia"] == 1]
urgentes = df[df["nivel_referencia"] == 3]

fp = no_urgentes[no_urgentes["nivel_sistema"] > no_urgentes["nivel_referencia"]]
fn = urgentes[urgentes["nivel_sistema"] < urgentes["nivel_referencia"]]

fp_rate = (len(fp) / len(no_urgentes)) * 100 if len(no_urgentes) > 0 else 0
fn_rate = (len(fn) / len(urgentes)) * 100 if len(urgentes) > 0 else 0


# ==============================
# DIMENSIÓN B — RECOMENDACIONES
# ==============================

disp_match = df["disp_match"].mean() * 100

adequacy = df["adequacy_score"].mean()


# ==============================
# DIMENSIÓN C — EFICIENCIA
# ==============================

avg_time = df["tiempo_atencion"].mean()

base_time = df["wait_base_min"].mean()

wait_reduction = ((base_time - avg_time) / base_time) * 100


# ==============================
# DIMENSIÓN D — SUPERVISIÓN
# ==============================

alarm_rate = (df["alarm"].sum() / total) * 100

override_rate = (df["override"].sum() / total) * 100


# ==============================
# SALIDA
# ==============================

print("\n" + "="*65)
print(Fore.CYAN + "   REPORTE DE INDICADORES — TRIAJE VIRTUAL IA")
print("="*65)


print(Fore.YELLOW + "\nDIMENSIÓN A — PRECISIÓN DIAGNÓSTICA")
print("-"*50)
print(Fore.GREEN + f"AcuityMatch%        : {acuity_match:.2f}%")
print(Fore.GREEN + f"Falsos Positivos%   : {fp_rate:.2f}%")
print(Fore.GREEN + f"Falsos Negativos%   : {fn_rate:.2f}%")


print(Fore.YELLOW + "\nDIMENSIÓN B — RECOMENDACIONES")
print("-"*50)
print(Fore.GREEN + f"DispositionMatch%  : {disp_match:.2f}%")
print(Fore.GREEN + f"Adequacy Score      : {adequacy:.2f} / 5")


print(Fore.YELLOW + "\nDIMENSIÓN C — EFICIENCIA")
print("-"*50)
print(Fore.GREEN + f"AvgTime             : {avg_time:.2f} min")
print(Fore.GREEN + f"BaseTime            : {base_time:.2f} min")
print(Fore.GREEN + f"WaitReduction%      : {wait_reduction:.2f}%")


print(Fore.YELLOW + "\nDIMENSIÓN D — SUPERVISIÓN")
print("-"*50)
print(Fore.GREEN + f"AlarmRate%          : {alarm_rate:.2f}%")
print(Fore.GREEN + f"OverrideRate%       : {override_rate:.2f}%")


print("="*65)


# ==============================
# EXPORTAR
# ==============================

resultados = pd.DataFrame([{
    "AcuityMatch_%": acuity_match,
    "FalsePositive_%": fp_rate,
    "FalseNegative_%": fn_rate,
    "DispositionMatch_%": disp_match,
    "AdequacyScore": adequacy,
    "AvgTime": avg_time,
    "WaitReduction_%": wait_reduction,
    "AlarmRate_%": alarm_rate,
    "OverrideRate_%": override_rate
}])

resultados.to_csv("resultados_indicadores_final.csv", index=False)

print(Fore.BLUE + "\n📁 Archivo generado: resultados_indicadores_final.csv\n")
