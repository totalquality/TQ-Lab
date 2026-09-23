# ============================================================
# EURACHEM — LDM / LCM
# Estimación a partir de resultados de blanco a bajo nivel
#
# Estructura esperada del Excel:
#   Columna A -> número de determinación
#   Columnas B, C, D... -> réplicas
#
# Ejemplo:
#   7 filas de determinaciones
#   3 columnas de réplicas
#       m = 7
#       n = 3
#       GL = m - 1 = 6
#
# Para cada determinación se calcula primero el promedio de sus
# réplicas. Luego s0 se calcula con esos m promedios.
#
# Fórmulas implementadas según el enfoque EURACHEM trabajado:
#
#   s0  = desviación estándar de los m resultados independientes
#         (cada resultado independiente = promedio de n réplicas)
#
#   s0' = s0 * sqrt(1/n + 1/nB)
#
#   CV  = 1.645 * s0'
#   LOD = 3 * s0'
#   LCM5  = 5 * s0'
#   LCM6  = 6 * s0'
#   LCM10 = 10 * s0'
#
# No se suma el promedio del blanco a CV, LOD ni LCM cuando
# los límites se expresan en unidades de concentración.
#
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ------------------------------------------------------------
# 1. ARCHIVO
# ------------------------------------------------------------

archivo = Path(
    r"D:\Ciencia_de_Datos\Validación de métodos químicos\LDM_LCM_EURACHEM.xlsx"
)

if not archivo.exists():
    raise FileNotFoundError(
        f"\nNo se encontró el archivo:\n{archivo}\n\n"
        "Verifique la ruta y el nombre del archivo."
    )

# Solo se utiliza la primera hoja
datos = pd.read_excel(archivo, sheet_name=0)

print("\n" + "=" * 80)
print("EURACHEM — LDM / LCM")
print("=" * 80)
print(f"Archivo : {archivo.name}")
print(f"Hoja    : primera hoja ({datos.columns.tolist()})")

# ------------------------------------------------------------
# 2. IDENTIFICACIÓN DE LAS RÉPLICAS
# ------------------------------------------------------------
# La columna A se considera identificador/número de determinación.
# Desde B en adelante se buscan las columnas numéricas.

if datos.shape[1] < 2:
    raise ValueError(
        "El archivo debe tener al menos dos columnas: "
        "A = identificación y B = primera réplica."
    )

columnas_replica = []

for col in datos.columns[1:]:
    serie = pd.to_numeric(datos[col], errors="coerce")

    # Se considera réplica si contiene al menos un valor numérico
    if serie.notna().any():
        columnas_replica.append(col)

if len(columnas_replica) == 0:
    raise ValueError(
        "No se encontraron columnas numéricas de réplicas desde la columna B."
    )

# Convertir réplicas a numérico
replicas = datos[columnas_replica].apply(pd.to_numeric, errors="coerce")

# ------------------------------------------------------------
# 3. DETERMINACIONES INDEPENDIENTES
# ------------------------------------------------------------
# Cada fila = una determinación independiente.
# Cada columna B, C, D... = una réplica.

# Se conservan únicamente filas con todas las réplicas disponibles.
filas_completas = replicas.notna().all(axis=1)

filas_incompletas = (~filas_completas).sum()

if filas_incompletas > 0:
    print(
        f"\nAVISO: se encontraron {filas_incompletas} fila(s) "
        "con datos incompletos."
    )
    print(
        "Esas filas no se utilizarán para calcular los promedios "
        "de las determinaciones."
    )

replicas_completas = replicas.loc[filas_completas].copy()

if len(replicas_completas) < 2:
    raise ValueError(
        "Se necesitan al menos 2 determinaciones independientes "
        "completas para calcular una desviación estándar."
    )

# ------------------------------------------------------------
# 4. m, n y GRADOS DE LIBERTAD
# ------------------------------------------------------------

m = len(replicas_completas)
n = len(columnas_replica)
gl = m - 1

print("\n" + "-" * 80)
print("ESTRUCTURA EXPERIMENTAL")
print("-" * 80)
print(f"Determinaciones independientes (m) = {m}")
print(f"Réplicas por determinación (n)     = {n}")
print(f"Grados de libertad (m - 1)         = {gl}")

print("\nColumnas identificadas como réplicas:")
for i, col in enumerate(columnas_replica, start=1):
    print(f"  Réplica {i}: {col}")

# ------------------------------------------------------------
# 5. PROMEDIO DE CADA DETERMINACIÓN
# ------------------------------------------------------------

promedios_determinacion = replicas_completas.mean(axis=1)

# Media global de los resultados independientes
promedio_blanco = promedios_determinacion.mean()

# ------------------------------------------------------------
# 6. s0
# ------------------------------------------------------------
# s0 se obtiene con los m resultados independientes.
# Cada resultado independiente es el promedio de n réplicas.

s0 = promedios_determinacion.std(ddof=1)

print("\n" + "=" * 80)
print("CÁLCULO DE s0")
print("=" * 80)

print(f"Promedio de las determinaciones = {promedio_blanco:.6g}")
print(f"s0                              = {s0:.6g}")
print(f"GL                              = {gl}")

# ------------------------------------------------------------
# 7. nB — NÚMERO DE BLANCOS PROMEDIADOS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("CORRECCIÓN POR BLANCO")
print("=" * 80)

print(
    "\nEURACHEM utiliza nB como el número de observaciones de blanco "
    "que se promedian para la corrección del blanco."
)

while True:
    entrada = input(
        "\nIngrese nB (número de blancos que se promedian): "
    ).strip()

    try:
        nB = int(entrada)
        if nB < 1:
            print("nB debe ser un entero mayor o igual a 1.")
            continue
        break
    except ValueError:
        print("Ingrese un número entero válido.")

# ------------------------------------------------------------
# 8. s0' AJUSTADO
# ------------------------------------------------------------

s0_ajustado = s0 * np.sqrt((1 / n) + (1 / nB))

# ------------------------------------------------------------
# 9. VALOR CRÍTICO, LOD Y LCM
# ------------------------------------------------------------

CV = 1.645 * s0_ajustado
LOD = 3 * s0_ajustado

LCM_5 = 5 * s0_ajustado
LCM_6 = 6 * s0_ajustado
LCM_10 = 10 * s0_ajustado

# ------------------------------------------------------------
# 10. RESULTADOS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("RESULTADOS EURACHEM")
print("=" * 80)

print(f"\ns0                           = {s0:.6g}")
print(f"n                            = {n}")
print(f"nB                           = {nB}")
print(f"s0'                          = {s0_ajustado:.6g}")

print("\nLÍMITES")
print("-" * 80)
print(f"Valor crítico (CV)           = {CV:.6g}")
print(f"Límite de detección (LOD)    = {LOD:.6g}")
print(f"LCM — k = 5                  = {LCM_5:.6g}")
print(f"LCM — k = 6                  = {LCM_6:.6g}")
print(f"LCM — k = 10                 = {LCM_10:.6g}")

# ------------------------------------------------------------
# 11. COMPROBACIÓN DEL ORDEN
# ------------------------------------------------------------

orden_correcto = CV < LOD < LCM_5 < LCM_6 < LCM_10

print("\n" + "-" * 80)
print("COMPROBACIÓN DEL ORDEN")
print("-" * 80)

if orden_correcto:
    print("CV < LOD < LCM5 < LCM6 < LCM10  →  ORDEN CORRECTO")
else:
    print(
        "ADVERTENCIA: revise los resultados porque el orden "
        "esperado no se cumple."
    )

# ------------------------------------------------------------
# 12. TABLA RESUMEN
# ------------------------------------------------------------

resumen = pd.DataFrame({
    "Indicador": [
        "Determinaciones independientes (m)",
        "Réplicas por determinación (n)",
        "Grados de libertad",
        "Número de blancos (nB)",
        "Promedio de las determinaciones",
        "s0",
        "s0 ajustado (s0')",
        "Valor crítico (CV)",
        "LOD",
        "LCM (k=5)",
        "LCM (k=6)",
        "LCM (k=10)",
    ],
    "Resultado": [
        f"{m}",
        f"{n}",
        f"{gl}",
        f"{nB}",
        f"{promedio_blanco:.6g}",
        f"{s0:.6g}",
        f"{s0_ajustado:.6g}",
        f"{CV:.6g}",
        f"{LOD:.6g}",
        f"{LCM_5:.6g}",
        f"{LCM_6:.6g}",
        f"{LCM_10:.6g}",
    ]
})

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(resumen.to_string(index=False))

# ------------------------------------------------------------
# 13. GRÁFICA
# ------------------------------------------------------------
# Se muestran únicamente líneas horizontales.
# No se muestran los resultados experimentales.
# El eje X representa una escala visual de concentración.

fig, ax = plt.subplots(figsize=(13, 7))

# Línea base
ax.axhline(
    0,
    color="black",
    linewidth=1.5
)

# Límites
ax.axhline(
    CV,
    color="#2E8B57",
    linewidth=3,
    label=f"CV = {CV:.3g}"
)

ax.axhline(
    LOD,
    color="#1565C0",
    linewidth=3,
    label=f"LOD = {LOD:.3g}"
)

ax.axhline(
    LCM_5,
    color="#F9A825",
    linewidth=2.8,
    linestyle="--",
    label=f"LCM (k=5) = {LCM_5:.3g}"
)

ax.axhline(
    LCM_6,
    color="#EF6C00",
    linewidth=2.8,
    linestyle="--",
    label=f"LCM (k=6) = {LCM_6:.3g}"
)

ax.axhline(
    LCM_10,
    color="#C62828",
    linewidth=3,
    label=f"LCM (k=10) = {LCM_10:.3g}"
)

# Zonas visuales
ax.axhspan(
    0,
    CV,
    alpha=0.10,
    color="#81C784"
)

ax.axhspan(
    CV,
    LOD,
    alpha=0.10,
    color="#64B5F6"
)

ax.axhspan(
    LOD,
    LCM_10,
    alpha=0.08,
    color="#FFCC80"
)

# Etiquetas directas a la derecha
x_text = 0.985

ax.text(
    x_text, CV,
    f"CV = {CV:.3g}",
    transform=ax.get_yaxis_transform(),
    ha="right",
    va="bottom",
    fontsize=11,
    fontweight="bold",
    color="#2E8B57",
    bbox=dict(
        boxstyle="round,pad=0.25",
        facecolor="white",
        edgecolor="#2E8B57",
        alpha=0.9
    )
)

ax.text(
    x_text, LOD,
    f"LOD = {LOD:.3g}",
    transform=ax.get_yaxis_transform(),
    ha="right",
    va="bottom",
    fontsize=11,
    fontweight="bold",
    color="#1565C0",
    bbox=dict(
        boxstyle="round,pad=0.25",
        facecolor="white",
        edgecolor="#1565C0",
        alpha=0.9
    )
)

ax.text(
    x_text, LCM_5,
    f"LCM 5 = {LCM_5:.3g}",
    transform=ax.get_yaxis_transform(),
    ha="right",
    va="bottom",
    fontsize=10,
    fontweight="bold",
    color="#B26A00"
)

ax.text(
    x_text, LCM_6,
    f"LCM 6 = {LCM_6:.3g}",
    transform=ax.get_yaxis_transform(),
    ha="right",
    va="bottom",
    fontsize=10,
    fontweight="bold",
    color="#D35400"
)

ax.text(
    x_text, LCM_10,
    f"LCM 10 = {LCM_10:.3g}",
    transform=ax.get_yaxis_transform(),
    ha="right",
    va="bottom",
    fontsize=11,
    fontweight="bold",
    color="#C62828"
)

# Título
ax.set_title(
    "EURACHEM — Valor crítico, LOD y LCM",
    fontsize=18,
    fontweight="bold",
    pad=18
)

ax.text(
    0.5,
    1.01,
    f"m = {m} determinaciones  |  n = {n} réplicas  |  "
    f"GL = {gl}  |  nB = {nB}",
    transform=ax.transAxes,
    ha="center",
    fontsize=11
)

ax.set_xlabel(
    "Concentración →",
    fontsize=13,
    fontweight="bold"
)

ax.set_ylabel(
    "Nivel del límite",
    fontsize=13,
    fontweight="bold"
)

# El eje X es solamente conceptual; no representa resultados
ax.set_xlim(0, 10)

# Límite superior con margen
y_max = LCM_10 * 1.18 if LCM_10 > 0 else 1
ax.set_ylim(0, y_max)

# No mostramos ticks innecesarios en X
ax.set_xticks([])

ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

ax.legend(
    loc="upper left",
    frameon=True,
    fontsize=10
)

plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# FIN
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("ANÁLISIS FINALIZADO")
print("=" * 80)
