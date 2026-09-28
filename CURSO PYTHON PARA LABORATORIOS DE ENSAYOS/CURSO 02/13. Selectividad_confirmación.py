# ============================================================
# SELECTIVIDAD — MÉTODO COMPARATIVO CON MÉTODO DE REFERENCIA
# Evaluación global de las diferencias:
# Anderson-Darling → t-Student / Wilcoxon
# Incluye únicamente la gráfica estadística final:
#   Intervalo de confianza de las diferencias
# ============================================================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.diagnostic import normal_ad


# ============================================================
# CONFIGURACIÓN
# ============================================================

ARCHIVO = r"D:\Ciencia_de_Datos\Validación de métodos químicos\Selectividad_confirmación.xlsx"

ALPHA = 0.05
NOMBRE_HOJA = 0

# Semilla para que el IC bootstrap de Wilcoxon sea reproducible
RANDOM_STATE = 12345


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def buscar_columna(df, palabras):
    """
    Busca una columna cuyo nombre contenga alguna de las palabras
    indicadas. Devuelve None si no encuentra coincidencia.
    """
    for col in df.columns:
        nombre = str(col).strip().lower()
        if all(p.lower() in nombre for p in palabras):
            return col

    for col in df.columns:
        nombre = str(col).strip().lower()
        if any(p.lower() in nombre for p in palabras):
            return col

    return None


def pedir_columnas(df):
    """
    Detecta automáticamente Nivel, Método A y Método B.
    Si no encuentra alguna, permite seleccionarla manualmente.
    """
    columnas = list(df.columns)

    col_nivel = buscar_columna(df, ["nivel"])
    col_a = buscar_columna(df, ["método", "a"])
    if col_a is None:
        col_a = buscar_columna(df, ["metodo", "a"])
    col_b = buscar_columna(df, ["método", "b"])
    if col_b is None:
        col_b = buscar_columna(df, ["metodo", "b"])

    # Evitar seleccionar la misma columna para A y B
    if col_a == col_b:
        col_b = None

    print("\nColumnas detectadas:")
    print(f"  Nivel   : {col_nivel}")
    print(f"  Método A : {col_a}")
    print(f"  Método B : {col_b}")

    if col_a is None or col_b is None:
        print("\nNo se pudieron identificar automáticamente las columnas.")
        print("Columnas disponibles:")
        for i, c in enumerate(columnas, start=1):
            print(f"  {i}. {c}")

        if col_a is None:
            opcion = int(input("\nSeleccione la columna del MÉTODO A: "))
            col_a = columnas[opcion - 1]

        if col_b is None:
            opcion = int(input("Seleccione la columna del MÉTODO B: "))
            col_b = columnas[opcion - 1]

    return col_nivel, col_a, col_b


def bootstrap_ic_mediana(x, confianza=0.95, n_boot=10000, random_state=12345):
    """
    Intervalo de confianza bootstrap percentil para la mediana.

    Se utiliza únicamente para la representación gráfica cuando
    corresponde el análisis no paramétrico de Wilcoxon.
    """
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]

    rng = np.random.default_rng(random_state)

    muestras = rng.choice(
        x,
        size=(n_boot, len(x)),
        replace=True
    )

    medianas = np.median(muestras, axis=1)

    alfa = 1 - confianza
    li = np.percentile(medianas, 100 * alfa / 2)
    ls = np.percentile(medianas, 100 * (1 - alfa / 2))

    return np.median(x), li, ls


def grafica_comparacion_y_diferencias(df, col_a, col_b, diferencias,
                                      media_diferencias):
    """
    Genera las dos gráficas originales:
      1. Comparación global A vs B
      2. Diferencias globales A-B
    """
    x = np.arange(1, len(df) + 1)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # --------------------------------------------------------
    # GRÁFICA 1: comparación global
    # --------------------------------------------------------
    axes[0].plot(
        x,
        df[col_a],
        marker="o",
        linewidth=2,
        label="Método A — UV-Vis"
    )

    axes[0].plot(
        x,
        df[col_b],
        marker="s",
        linewidth=2,
        label="Método B — HPLC"
    )

    axes[0].set_title("Comparación global de los métodos",
                      fontweight="bold")
    axes[0].set_xlabel("Observación")
    axes[0].set_ylabel("Resultado")
    axes[0].grid(alpha=0.25)
    axes[0].legend()

    # --------------------------------------------------------
    # GRÁFICA 2: diferencias globales
    # --------------------------------------------------------
    axes[1].plot(
        x,
        diferencias,
        marker="o",
        linewidth=1.5,
        alpha=0.75
    )

    axes[1].scatter(
        x,
        diferencias,
        s=60,
        zorder=3,
        label="Diferencias A − B"
    )

    axes[1].axhline(
        0,
        linestyle="--",
        linewidth=2,
        label="Diferencia = 0"
    )

    axes[1].axhline(
        media_diferencias,
        linestyle=":",
        linewidth=2,
        label=f"Media diferencias = {media_diferencias:.4f}"
    )

    axes[1].set_title("Diferencias globales",
                      fontweight="bold")
    axes[1].set_xlabel("Observación")
    axes[1].set_ylabel("Diferencia: Método A − Método B")
    axes[1].grid(alpha=0.25)
    axes[1].legend()

    plt.tight_layout()
    plt.show()


def grafica_intervalo_tstudent(diferencias, alpha=0.05):
    """
    Gráfica 3 para t-Student:
    media de las diferencias + IC bilateral del 95 %.
    """
    n = len(diferencias)
    media = np.mean(diferencias)
    sd = np.std(diferencias, ddof=1)
    gl = n - 1
    se = sd / np.sqrt(n)

    tcrit = stats.t.ppf(1 - alpha / 2, gl)

    li = media - tcrit * se
    ls = media + tcrit * se

    incluye_cero = li <= 0 <= ls

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.axvline(
        0,
        linestyle="--",
        linewidth=2,
        label="Diferencia = 0"
    )

    ax.errorbar(
        media,
        0,
        xerr=[[media - li], [ls - media]],
        fmt="o",
        markersize=10,
        capsize=8,
        linewidth=3,
        label="Media ± IC 95 %"
    )

    ax.text(
        media,
        0.12,
        f"Media = {media:.4f}\nIC 95 % = [{li:.4f}; {ls:.4f}]",
        ha="center",
        va="bottom",
        fontsize=10
    )

    if incluye_cero:
        interpretacion = "El IC incluye 0"
    else:
        interpretacion = "El IC no incluye 0"

    ax.text(
        0.02,
        0.95,
        interpretacion,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontweight="bold"
    )

    ax.set_yticks([])
    ax.set_xlabel("Diferencia: Método A − Método B")
    ax.set_title(
        "Intervalo de confianza de las diferencias — t-Student",
        fontweight="bold"
    )
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="lower right")

    plt.tight_layout()
    plt.show()

    return li, ls


def grafica_intervalo_wilcoxon(diferencias, alpha=0.05):
    """
    Gráfica 3 para Wilcoxon:
    mediana de las diferencias + IC bootstrap del 95 %.

    El bootstrap se utiliza para representar gráficamente la
    incertidumbre alrededor de la mediana. La prueba inferencial
    sigue siendo Wilcoxon.
    """
    mediana, li, ls = bootstrap_ic_mediana(
        diferencias,
        confianza=1 - alpha,
        n_boot=10000,
        random_state=RANDOM_STATE
    )

    incluye_cero = li <= 0 <= ls

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.axvline(
        0,
        linestyle="--",
        linewidth=2,
        label="Diferencia = 0"
    )

    ax.errorbar(
        mediana,
        0,
        xerr=[[mediana - li], [ls - mediana]],
        fmt="o",
        markersize=10,
        capsize=8,
        linewidth=3,
        label="Mediana ± IC bootstrap 95 %"
    )

    ax.text(
        mediana,
        0.12,
        f"Mediana = {mediana:.4f}\nIC bootstrap 95 % = [{li:.4f}; {ls:.4f}]",
        ha="center",
        va="bottom",
        fontsize=10
    )

    if incluye_cero:
        interpretacion = "El IC incluye 0"
    else:
        interpretacion = "El IC no incluye 0"

    ax.text(
        0.02,
        0.95,
        interpretacion,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontweight="bold"
    )

    ax.set_yticks([])
    ax.set_xlabel("Diferencia: Método A − Método B")
    ax.set_title(
        "Intervalo de confianza de las diferencias — Wilcoxon",
        fontweight="bold"
    )
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="lower right")

    plt.tight_layout()
    plt.show()

    return li, ls


# ============================================================
# LECTURA DEL ARCHIVO
# ============================================================

if not os.path.exists(ARCHIVO):
    print("\nERROR: No se encontró el archivo:")
    print(ARCHIVO)
    print("\nModifique la variable ARCHIVO al inicio del programa.")
    input("\nPresione ENTER para salir...")
    raise SystemExit

df_original = pd.read_excel(
    ARCHIVO,
    sheet_name=NOMBRE_HOJA
)

col_nivel, col_a, col_b = pedir_columnas(df_original)

df = df_original.copy()

# Convertir métodos a numérico
df[col_a] = pd.to_numeric(df[col_a], errors="coerce")
df[col_b] = pd.to_numeric(df[col_b], errors="coerce")

# Conservar solamente observaciones donde ambos métodos tengan resultado
df = df.dropna(subset=[col_a, col_b]).copy()

if len(df) < 3:
    print("\nERROR: Se necesitan al menos 3 observaciones.")
    input("\nPresione ENTER para salir...")
    raise SystemExit


# ============================================================
# DIFERENCIAS GLOBALES
# ============================================================

# IMPORTANTE:
# Todas las observaciones se agrupan en un solo vector.
# No se realiza normalidad por nivel.
diferencias = (df[col_a] - df[col_b]).to_numpy(dtype=float)

df["Diferencia_A_B"] = diferencias

n = len(diferencias)

media_a = df[col_a].mean()
media_b = df[col_b].mean()

media_diferencias = np.mean(diferencias)
mediana_diferencias = np.median(diferencias)
sd_diferencias = np.std(diferencias, ddof=1)


# ============================================================
# ANDERSON-DARLING SOBRE TODAS LAS DIFERENCIAS
# ============================================================

AD, p_AD = normal_ad(diferencias)

normal = p_AD >= ALPHA

print("\n" + "=" * 72)
print("SELECTIVIDAD — MÉTODO COMPARATIVO CON REFERENCIA")
print("=" * 72)

print("\nANÁLISIS GLOBAL DE LAS DIFERENCIAS")
print("-" * 72)
print(f"N total                         : {n}")
print(f"Media Método A                  : {media_a:.6f}")
print(f"Media Método B                  : {media_b:.6f}")
print(f"Media de diferencias A − B     : {media_diferencias:.6f}")
print(f"Mediana de diferencias         : {mediana_diferencias:.6f}")
print(f"Desv. estándar diferencias     : {sd_diferencias:.6f}")

print("\nNORMALIDAD DE LAS DIFERENCIAS")
print("-" * 72)
print(f"Anderson-Darling                : {AD:.6f}")
print(f"p-valor                         : {p_AD:.6f}")

if normal:
    print("Resultado                       : Compatible con normalidad")
    print("Prueba seleccionada            : t-Student de una muestra")
else:
    print("Resultado                       : No compatible con normalidad")
    print("Prueba seleccionada            : Wilcoxon de rangos con signo")


# ============================================================
# PRUEBA ESTADÍSTICA
# ============================================================

estadistico = np.nan
p_valor = np.nan
gl = np.nan
nombre_prueba = ""

if normal:

    # --------------------------------------------------------
    # t-STUDENT DE UNA MUESTRA SOBRE LAS DIFERENCIAS
    # H0: μd = 0
    # H1: μd ≠ 0
    # --------------------------------------------------------
    nombre_prueba = "t-Student de una muestra sobre las diferencias"

    resultado = stats.ttest_1samp(
        diferencias,
        popmean=0
    )

    estadistico = resultado.statistic
    p_valor = resultado.pvalue
    gl = n - 1

    if p_valor >= ALPHA:
        decision = "NO SE RECHAZA H₀"
        conclusion = (
            "No se evidencia una diferencia estadísticamente "
            "significativa entre el método candidato y el método de referencia."
        )
    else:
        decision = "SE RECHAZA H₀"
        conclusion = (
            "Se evidencia una diferencia estadísticamente significativa "
            "entre el método candidato y el método de referencia."
        )

else:

    # --------------------------------------------------------
    # WILCOXON SOBRE LAS DIFERENCIAS
    # H0: mediana de las diferencias = 0
    # H1: mediana de las diferencias ≠ 0
    # --------------------------------------------------------
    nombre_prueba = "Wilcoxon de rangos con signo"

    resultado = stats.wilcoxon(
        diferencias,
        zero_method="wilcox",
        alternative="two-sided",
        method="auto"
    )

    estadistico = resultado.statistic
    p_valor = resultado.pvalue

    if p_valor >= ALPHA:
        decision = "NO SE RECHAZA H₀"
        conclusion = (
            "No se evidencia una diferencia estadísticamente "
            "significativa entre el método candidato y el método de referencia."
        )
    else:
        decision = "SE RECHAZA H₀"
        conclusion = (
            "Se evidencia una diferencia estadísticamente significativa "
            "entre el método candidato y el método de referencia."
        )


# ============================================================
# RESULTADOS DE LA PRUEBA
# ============================================================

print("\n" + "=" * 72)
print("RESULTADO DE LA PRUEBA")
print("=" * 72)

print(f"\nPrueba                           : {nombre_prueba}")
print(f"Estadístico                     : {estadistico:.6f}")

if not np.isnan(gl):
    print(f"Grados de libertad              : {int(gl)}")

print(f"p-valor                         : {p_valor:.6f}")
print(f"Alpha                           : {ALPHA:.2f}")
print(f"Decisión                        : {decision}")
print(f"Conclusión                      : {conclusion}")


# ============================================================
# GRÁFICA 3 — INTERVALO DE CONFIANZA
# ============================================================

print("\n" + "=" * 72)
print("INTERVALO DE CONFIANZA DE LAS DIFERENCIAS")
print("=" * 72)

if normal:

    li, ls = grafica_intervalo_tstudent(
        diferencias,
        alpha=ALPHA
    )

    print(f"\nIC 95 % de la media de diferencias: [{li:.6f}; {ls:.6f}]")

else:

    li, ls = grafica_intervalo_wilcoxon(
        diferencias,
        alpha=ALPHA
    )

    print(
        f"\nIC bootstrap 95 % de la mediana de diferencias: "
        f"[{li:.6f}; {ls:.6f}]"
    )

incluye_cero = li <= 0 <= ls

if incluye_cero:
    print("Interpretación gráfica           : El intervalo incluye 0.")
else:
    print("Interpretación gráfica           : El intervalo NO incluye 0.")


# ============================================================
# TABLA RESUMEN
# ============================================================

resumen = pd.DataFrame({
    "N": [n],
    "Media Método A": [media_a],
    "Media Método B": [media_b],
    "Media diferencias": [media_diferencias],
    "Mediana diferencias": [mediana_diferencias],
    "Anderson-Darling": [AD],
    "p AD": [p_AD],
    "Normalidad": ["Sí" if normal else "No"],
    "Prueba": [nombre_prueba],
    "Estadístico": [estadistico],
    "gl": [gl],
    "p-valor": [p_valor],
    "Decisión": [decision],
    "IC inferior": [li],
    "IC superior": [ls],
    "IC incluye 0": ["Sí" if incluye_cero else "No"],
    "Conclusión": [conclusion]
})

print("\n" + "=" * 72)
print("TABLA RESUMEN")
print("=" * 72)
print(resumen.to_string(index=False))


# ============================================================
# EXPORTACIÓN AUTOMÁTICA
# ============================================================

# Se guarda automáticamente el resumen y las diferencias,
# sin preguntar al usuario.

carpeta = os.path.dirname(ARCHIVO)

archivo_salida = os.path.join(
    carpeta,
    "Resultado_Selectividad_Comparativo.xlsx"
)

with pd.ExcelWriter(archivo_salida, engine="openpyxl") as writer:

    resumen.to_excel(
        writer,
        sheet_name="Resumen",
        index=False
    )

    df.to_excel(
        writer,
        sheet_name="Diferencias",
        index=False
    )

print(f"\nArchivo Excel guardado automáticamente en:")
print(archivo_salida)

print("\nProceso finalizado.")
input("\nPresione ENTER para salir...")
