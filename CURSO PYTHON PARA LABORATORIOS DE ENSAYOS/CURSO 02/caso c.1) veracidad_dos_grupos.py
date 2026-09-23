import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# ============================================================
# VERACIDAD — CASO C.1
# Comparación entre un método estandarizado (referencia)
# y el método a validar (candidato) en una misma muestra.
#
# Selección estadística:
# 1) Si AMBOS grupos tienen distribución normal:
#       - Varianzas homogéneas  -> t de Student de dos muestras
#       - Varianzas diferentes  -> t de Welch
# 2) Si AL MENOS UNO no tiene distribución normal:
#       -> U de Mann-Whitney
#
# El archivo puede contener una o varias hojas.
# Cada hoja se procesa como una comparación independiente.
# ============================================================

archivo = r"D:\Ciencia_de_Datos\Validación de métodos químicos\veracidad_dos_grupos.xlsx"
alpha = 0.05


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def pregunta_si_no(numero, nivel, pregunta):
    """
    Cada pregunta identifica claramente el nivel/comparación.
    La pregunta completa se coloca dentro de input() para que
    sea visible en Jupyter/VS Code.
    """
    while True:
        respuesta = input(
            f"\n[NIVEL {numero}: {nivel}] "
            f"{pregunta} [S = SÍ / N = NO] → "
        ).strip().lower()

        if respuesta in ("s", "si", "sí"):
            return True

        if respuesta in ("n", "no"):
            return False

        print(
            f"[NIVEL {numero}: {nivel}] "
            "Respuesta no válida. Escriba S o N."
        )



def preparar_datos(hoja, nombre_hoja):
    """
    Detecta las columnas numéricas de la hoja.

    Se esperan al menos dos columnas numéricas:
    - Método Candidato
    - Método de Referencia / Estandarizado

    Si existen exactamente dos, se utilizan automáticamente.
    Si existen más de dos, el usuario selecciona las dos.
    """
    columnas_numericas = hoja.select_dtypes(
        include=np.number
    ).columns.tolist()

    if len(columnas_numericas) < 2:
        raise ValueError(
            f"La hoja '{nombre_hoja}' debe contener al menos "
            f"dos columnas numéricas."
        )

    print("\nColumnas numéricas detectadas:")
    for i, columna in enumerate(columnas_numericas, start=1):
        print(f"  {i} → {columna}")

    if len(columnas_numericas) == 2:
        candidato = columnas_numericas[0]
        referencia = columnas_numericas[1]

        print("\nSe detectaron exactamente dos columnas numéricas.")
        print(f"Método Candidato  = {candidato}")
        print(f"Método Referencia  = {referencia}")

    else:
        print("\nSe detectaron más de dos columnas numéricas.")
        print("Seleccione las columnas que corresponden a cada método.")

        while True:
            try:
                op_candidato = int(
                    input("Número de columna del MÉTODO CANDIDATO: ")
                )
                if 1 <= op_candidato <= len(columnas_numericas):
                    break
            except ValueError:
                pass
            print("Selección no válida.")

        while True:
            try:
                op_referencia = int(
                    input("Número de columna del MÉTODO DE REFERENCIA: ")
                )
                if (
                    1 <= op_referencia <= len(columnas_numericas)
                    and op_referencia != op_candidato
                ):
                    break
            except ValueError:
                pass
            print("Selección no válida. Debe ser diferente de la del candidato.")

        candidato = columnas_numericas[op_candidato - 1]
        referencia = columnas_numericas[op_referencia - 1]

    x_candidato = pd.to_numeric(
        hoja[candidato], errors="coerce"
    ).dropna()

    x_referencia = pd.to_numeric(
        hoja[referencia], errors="coerce"
    ).dropna()

    if len(x_candidato) < 2 or len(x_referencia) < 2:
        raise ValueError(
            f"'{nombre_hoja}': cada método debe tener al menos 2 resultados válidos."
        )

    return candidato, referencia, x_candidato, x_referencia


# ============================================================
# ESTADÍSTICA DESCRIPTIVA
# ============================================================

def mostrar_descriptiva(nombre_hoja, candidato, referencia,
                        x_candidato, x_referencia):

    print("\n" + "=" * 90)
    print(f"ESTADÍSTICA DESCRIPTIVA — {nombre_hoja}")
    print("=" * 90)

    print(f"\nMétodo candidato: {candidato}")
    print(f"N        = {len(x_candidato)}")
    print(f"Media    = {x_candidato.mean():.6f}")
    print(f"Mediana  = {x_candidato.median():.6f}")
    print(f"SD       = {x_candidato.std(ddof=1):.6f}")

    print(f"\nMétodo de referencia: {referencia}")
    print(f"N        = {len(x_referencia)}")
    print(f"Media    = {x_referencia.mean():.6f}")
    print(f"Mediana  = {x_referencia.median():.6f}")
    print(f"SD       = {x_referencia.std(ddof=1):.6f}")


# ============================================================
# t DE STUDENT DE DOS MUESTRAS — VARIANZAS HOMOGÉNEAS
# ============================================================

def t_student_dos_muestras(nombre_hoja, x_candidato, x_referencia):

    resultado = stats.ttest_ind(
        x_candidato,
        x_referencia,
        equal_var=True,
        alternative="two-sided"
    )

    n1 = len(x_candidato)
    n2 = len(x_referencia)

    gl = n1 + n2 - 2

    s1 = x_candidato.std(ddof=1)
    s2 = x_referencia.std(ddof=1)

    sp2 = (
        ((n1 - 1) * s1**2) +
        ((n2 - 1) * s2**2)
    ) / gl

    sp = np.sqrt(sp2)

    se = sp * np.sqrt((1 / n1) + (1 / n2))

    diferencia = x_candidato.mean() - x_referencia.mean()

    t_critico = stats.t.ppf(
        1 - alpha / 2,
        gl
    )

    ic_inf = diferencia - t_critico * se
    ic_sup = diferencia + t_critico * se

    p = resultado.pvalue
    pasa = p >= alpha

    print("\n" + "=" * 90)
    print("PRUEBA t DE STUDENT — DOS MUESTRAS")
    print("Varianzas homogéneas")
    print("=" * 90)

    print("\nHIPÓTESIS")
    print("H₀: μ candidato = μ referencia")
    print("H₁: μ candidato ≠ μ referencia")

    print(f"\nt calculado = {resultado.statistic:.6f}")
    print(f"t crítico   = ±{t_critico:.6f}")
    print(f"gl          = {gl}")
    print(f"p-valor     = {p:.6f}")

    print(f"\nDiferencia de medias = {diferencia:.6f}")
    print(
        f"IC 95 % de la diferencia = "
        f"{ic_inf:.6f} a {ic_sup:.6f}"
    )

    print(f"\np ≥ α ({alpha}) = {'SÍ' if pasa else 'NO'}")

    if pasa:
        conclusion = (
            "No se evidencia diferencia estadísticamente significativa "
            "entre el método candidato y el método de referencia."
        )
    else:
        conclusion = (
            "Se evidencia una diferencia estadísticamente significativa "
            "entre el método candidato y el método de referencia."
        )

    print("\nCONCLUSIÓN")
    print(conclusion)

    return {
        "Prueba": "t de Student (varianzas homogéneas)",
        "estadistico": resultado.statistic,
        "p": p,
        "gl": gl,
        "diferencia": diferencia,
        "ic_inf": ic_inf,
        "ic_sup": ic_sup,
        "pasa": pasa,
        "conclusion": conclusion
    }


# ============================================================
# t DE WELCH — VARIANZAS DIFERENTES
# ============================================================

def t_welch(nombre_hoja, x_candidato, x_referencia):

    resultado = stats.ttest_ind(
        x_candidato,
        x_referencia,
        equal_var=False,
        alternative="two-sided"
    )

    n1 = len(x_candidato)
    n2 = len(x_referencia)

    s1 = x_candidato.var(ddof=1)
    s2 = x_referencia.var(ddof=1)

    se2 = (s1 / n1) + (s2 / n2)
    se = np.sqrt(se2)

    diferencia = x_candidato.mean() - x_referencia.mean()

    gl = (
        se2**2 /
        (
            ((s1 / n1)**2 / (n1 - 1)) +
            ((s2 / n2)**2 / (n2 - 1))
        )
    )

    t_critico = stats.t.ppf(
        1 - alpha / 2,
        gl
    )

    ic_inf = diferencia - t_critico * se
    ic_sup = diferencia + t_critico * se

    p = resultado.pvalue
    pasa = p >= alpha

    print("\n" + "=" * 90)
    print("PRUEBA t DE WELCH — DOS MUESTRAS")
    print("Varianzas diferentes")
    print("=" * 90)

    print("\nHIPÓTESIS")
    print("H₀: μ candidato = μ referencia")
    print("H₁: μ candidato ≠ μ referencia")

    print(f"\nt calculado = {resultado.statistic:.6f}")
    print(f"t crítico   = ±{t_critico:.6f}")
    print(f"gl          = {gl:.4f}")
    print(f"p-valor     = {p:.6f}")

    print(f"\nDiferencia de medias = {diferencia:.6f}")
    print(
        f"IC 95 % de la diferencia = "
        f"{ic_inf:.6f} a {ic_sup:.6f}"
    )

    print(f"\np ≥ α ({alpha}) = {'SÍ' if pasa else 'NO'}")

    if pasa:
        conclusion = (
            "No se evidencia diferencia estadísticamente significativa "
            "entre el método candidato y el método de referencia."
        )
    else:
        conclusion = (
            "Se evidencia una diferencia estadísticamente significativa "
            "entre el método candidato y el método de referencia."
        )

    print("\nCONCLUSIÓN")
    print(conclusion)

    return {
        "Prueba": "t de Welch (varianzas diferentes)",
        "estadistico": resultado.statistic,
        "p": p,
        "gl": gl,
        "diferencia": diferencia,
        "ic_inf": ic_inf,
        "ic_sup": ic_sup,
        "pasa": pasa,
        "conclusion": conclusion
    }


# ============================================================
# MANN-WHITNEY U
# ============================================================

def mann_whitney(nombre_hoja, x_candidato, x_referencia):

    resultado = stats.mannwhitneyu(
        x_candidato,
        x_referencia,
        alternative="two-sided",
        method="auto"
    )

    p = resultado.pvalue
    pasa = p >= alpha

    n1 = len(x_candidato)
    n2 = len(x_referencia)

    print("\n" + "=" * 90)
    print("PRUEBA U DE MANN-WHITNEY")
    print("=" * 90)

    print("\nHIPÓTESIS")
    print(
        "H₀: Las distribuciones de ambos métodos "
        "son iguales."
    )
    print(
        "H₁: Las distribuciones de ambos métodos "
        "son diferentes."
    )

    print(f"\nU calculado = {resultado.statistic:.6f}")
    print(f"N candidato = {n1}")
    print(f"N referencia = {n2}")
    print(f"p-valor     = {p:.6f}")

    print(f"\np ≥ α ({alpha}) = {'SÍ' if pasa else 'NO'}")

    if pasa:
        conclusion = (
            "No se evidencia una diferencia estadísticamente significativa "
            "entre las distribuciones de los dos métodos."
        )
    else:
        conclusion = (
            "Se evidencia una diferencia estadísticamente significativa "
            "entre las distribuciones de los dos métodos."
        )

    print("\nCONCLUSIÓN")
    print(conclusion)

    return {
        "Prueba": "U de Mann-Whitney",
        "estadistico": resultado.statistic,
        "p": p,
        "gl": np.nan,
        "diferencia": x_candidato.median() - x_referencia.median(),
        "ic_inf": np.nan,
        "ic_sup": np.nan,
        "pasa": pasa,
        "conclusion": conclusion
    }


# ============================================================
# GRÁFICA
# ============================================================

def grafica_comparacion(nombre_hoja, candidato, referencia,
                        x_candidato, x_referencia, resultado):

    # Gráfico científico, con estética tipo MATLAB:
    # boxplot + puntos individuales + media ± 1 SD + panel estadístico.

    fig = plt.figure(figsize=(15, 8.5), dpi=120)

    gs = fig.add_gridspec(
        1, 2,
        width_ratios=[3.8, 1.7],
        wspace=0.10
    )

    ax = fig.add_subplot(gs[0])
    info = fig.add_subplot(gs[1])

    datos = [
        x_candidato.to_numpy(),
        x_referencia.to_numpy()
    ]

    posiciones = [1, 2]

    ax.boxplot(
        datos,
        positions=posiciones,
        widths=0.48,
        patch_artist=True,
        showmeans=False,
        medianprops={"linewidth": 2.2},
        whiskerprops={"linewidth": 1.5},
        capprops={"linewidth": 1.5},
        boxprops={"linewidth": 1.6}
    )

    rng = np.random.default_rng(12345)

    for pos, valores in zip(posiciones, datos):
        jitter = rng.normal(0, 0.045, size=len(valores))

        ax.scatter(
            np.full(len(valores), pos) + jitter,
            valores,
            s=38,
            alpha=0.75,
            edgecolors="black",
            linewidths=0.45,
            zorder=3
        )

    medias = [
        x_candidato.mean(),
        x_referencia.mean()
    ]

    desv = [
        x_candidato.std(ddof=1),
        x_referencia.std(ddof=1)
    ]

    ax.errorbar(
        posiciones,
        medias,
        yerr=desv,
        fmt="D",
        markersize=7,
        markeredgewidth=1.2,
        capsize=7,
        capthick=1.6,
        linewidth=1.6,
        label="Media ± 1 SD",
        zorder=5
    )

    ax.set_xticks(posiciones)
    ax.set_xticklabels(
        ["Método candidato", "Método referencia"],
        fontsize=11,
        fontweight="bold"
    )

    ax.set_ylabel(
        "Resultado",
        fontsize=12,
        fontweight="bold"
    )

    ax.set_title(
        "Comparación de resultados",
        fontsize=17,
        fontweight="bold",
        pad=14
    )

    ax.grid(
        axis="y",
        linestyle="--",
        linewidth=0.7,
        alpha=0.35
    )

    ax.tick_params(axis="both", labelsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(
        loc="best",
        frameon=True,
        fontsize=10
    )

    info.axis("off")

    p = resultado["p"]

    estado = (
        "SIN DIFERENCIA\nSIGNIFICATIVA"
        if resultado["pasa"]
        else
        "DIFERENCIA\nSIGNIFICATIVA"
    )

    info.text(
        0.05, 0.95,
        "RESULTADO ESTADÍSTICO",
        fontsize=15,
        fontweight="bold",
        transform=info.transAxes,
        verticalalignment="top"
    )

    info.text(
        0.05, 0.84,
        resultado["Prueba"],
        fontsize=11.5,
        fontweight="bold",
        transform=info.transAxes,
        verticalalignment="top"
    )

    info.text(
        0.05, 0.72,
        f"p-valor = {p:.6f}\nα = {alpha:.2f}",
        fontsize=12,
        transform=info.transAxes,
        verticalalignment="top",
        linespacing=1.5
    )

    info.text(
        0.05, 0.54,
        estado,
        fontsize=15,
        fontweight="bold",
        transform=info.transAxes,
        verticalalignment="top",
        bbox=dict(
            boxstyle="round,pad=0.55",
            alpha=0.12
        )
    )

    info.text(
        0.05, 0.36,
        "Criterio:\np ≥ α → no se evidencia\ndiferencia significativa\n\n"
        "p < α → se evidencia\ndiferencia significativa",
        fontsize=10.5,
        transform=info.transAxes,
        verticalalignment="top",
        linespacing=1.35
    )

    info.text(
        0.05, 0.08,
        f"n candidato = {len(x_candidato)}\n"
        f"n referencia = {len(x_referencia)}",
        fontsize=10.5,
        transform=info.transAxes,
        verticalalignment="bottom"
    )

    fig.suptitle(
        f"VERACIDAD — C.1 — {nombre_hoja}",
        fontsize=20,
        fontweight="bold",
        y=0.97
    )

    fig.text(
        0.31, 0.025,
        "Puntos = resultados individuales   |   ♦ = media   |   barra = ±1 SD",
        ha="center",
        fontsize=9.5,
        style="italic"
    )

    plt.tight_layout(rect=[0, 0.04, 1, 0.94])
    plt.show()


# ============================================================
# PROCESAMIENTO DE CADA HOJA
# ============================================================

def procesar_nivel(nombre_hoja, hoja, numero):

    print("\n\n")
    print("█" * 100)
    print(f"█   NIVEL {numero} — {nombre_hoja}")
    print("█   COMPARACIÓN ENTRE MÉTODO CANDIDATO Y MÉTODO DE REFERENCIA")
    print("█" * 100)
    print("█   Todas las preguntas que siguen pertenecen EXCLUSIVAMENTE a este nivel.")
    print("█" * 100)

    candidato, referencia, x_candidato, x_referencia = preparar_datos(
        hoja,
        nombre_hoja
    )

    mostrar_descriptiva(
        nombre_hoja,
        candidato,
        referencia,
        x_candidato,
        x_referencia
    )

    # --------------------------------------------------------
    # PASO 1 — NORMALIDAD
    # --------------------------------------------------------

    print("\n" + "-" * 90)
    print("PASO 1 — DISTRIBUCIÓN NORMAL")
    print("-" * 90)
    print("IMPORTANTE: responda pensando en AMBOS métodos.")

    normalidad = pregunta_si_no(
        numero,
        nombre_hoja,
        "¿AMBOS métodos tienen distribución normal?"
    )

    # --------------------------------------------------------
    # SI AMBOS SON NORMALES
    # --------------------------------------------------------

    if normalidad:

        print("\n" + "-" * 90)
        print("PASO 2 — HOMOGENEIDAD DE VARIANZAS")
        print("-" * 90)
        print("IMPORTANTE: responda comparando las varianzas de ambos métodos.")

        homogeneidad = pregunta_si_no(
            numero,
            nombre_hoja,
            "¿Los dos métodos tienen homogeneidad de varianzas?"
        )

        if homogeneidad:

            resultado = t_student_dos_muestras(
                nombre_hoja,
                x_candidato,
                x_referencia
            )

        else:

            resultado = t_welch(
                nombre_hoja,
                x_candidato,
                x_referencia
            )

    # --------------------------------------------------------
    # SI AL MENOS UNO NO ES NORMAL
    # --------------------------------------------------------

    else:

        print("\n" + "-" * 90)
        print("DISTRIBUCIÓN NO NORMAL")
        print("-" * 90)

        print(
            "\nAl menos uno de los dos métodos no presenta "
            "distribución normal."
        )

        print(
            "Se utilizará la prueba no paramétrica "
            "U de Mann-Whitney."
        )

        resultado = mann_whitney(
            nombre_hoja,
            x_candidato,
            x_referencia
        )

    # --------------------------------------------------------
    # GRÁFICA
    # --------------------------------------------------------

    grafica_comparacion(
        nombre_hoja,
        candidato,
        referencia,
        x_candidato,
        x_referencia,
        resultado
    )

    print("\n" + "─" * 100)
    print(f"FIN DEL NIVEL {numero} — {nombre_hoja}")
    print("─" * 100)

    return {
        "Comparación": numero,
        "Nivel": nombre_hoja,
        "Método candidato": candidato,
        "Método referencia": referencia,
        "N candidato": len(x_candidato),
        "N referencia": len(x_referencia),
        "Normalidad ambos": "Sí" if normalidad else "No",
        "Prueba": resultado["Prueba"],
        "Estadístico": resultado["estadistico"],
        "p-valor": resultado["p"],
        "Resultado": (
            "NO se evidencia diferencia significativa"
            if resultado["pasa"]
            else
            "SE evidencia diferencia significativa"
        )
    }


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

print("\n" + "#" * 90)
print("VERACIDAD — CASO C.1")
print("COMPARACIÓN ENTRE MÉTODO ESTANDARIZADO Y MÉTODO CANDIDATO")
print("#" * 90)

print(f"\nArchivo configurado:")
print(archivo)

# ------------------------------------------------------------
# VERIFICACIÓN DEL ARCHIVO
# Si la ruta configurada no existe, se intenta localizar
# automáticamente un Excel relacionado con "veracidad".
# Si hay más de uno, se solicita seleccionar uno.
# ------------------------------------------------------------

from pathlib import Path

ruta_archivo = Path(archivo)

if not ruta_archivo.exists():

    print("\n" + "!" * 90)
    print("NO SE ENCONTRÓ EL ARCHIVO EN LA RUTA CONFIGURADA")
    print("!" * 90)
    print(f"Ruta buscada:\n{archivo}")

    # Buscar primero en la misma carpeta indicada.
    carpeta = ruta_archivo.parent

    candidatos = []
    if carpeta.exists():
        candidatos = sorted(
            list(carpeta.glob("*veracidad*.xlsx")) +
            list(carpeta.glob("*Veracidad*.xlsx")) +
            list(carpeta.glob("*VERACIDAD*.xlsx"))
        )

    # Eliminar duplicados manteniendo el orden.
    candidatos = list(dict.fromkeys(candidatos))

    if len(candidatos) == 1:
        archivo = str(candidatos[0])
        print(f"\nSe encontró automáticamente:")
        print(archivo)

    elif len(candidatos) > 1:
        print("\nSe encontraron varios archivos Excel relacionados:")
        for i, candidato in enumerate(candidatos, start=1):
            print(f"  {i} → {candidato.name}")

        while True:
            try:
                opcion_archivo = int(
                    input("\nSeleccione el número del archivo: ")
                )

                if 1 <= opcion_archivo <= len(candidatos):
                    archivo = str(candidatos[opcion_archivo - 1])
                    break

            except ValueError:
                pass

            print("Selección no válida.")

        print(f"\nArchivo seleccionado:")
        print(archivo)

    else:
        print("\nNo se encontró automáticamente ningún Excel.")
        print(
            "Revise el nombre del archivo y la carpeta. "
            "También puede modificar la variable 'archivo' al inicio del script."
        )
        raise FileNotFoundError(
            f"No se encontró el archivo Excel: {archivo}"
        )

print(f"\nNivel de significancia: α = {alpha}")

print("\n" + "=" * 90)
print("RUTA DE DECISIÓN ESTADÍSTICA — CASO C.1")
print("=" * 90)
print("1. ¿AMBOS métodos tienen distribución normal?")
print("      SÍ  → preguntar homogeneidad de varianzas")
print("            SÍ → t de Student")
print("            NO → t de Welch")
print("      NO  → Mann-Whitney")
print("=" * 90)


datos_excel = pd.read_excel(
    archivo,
    sheet_name=None
)

if not datos_excel:
    raise ValueError(
        "No se encontraron hojas en el archivo."
    )

print("\nHojas detectadas:")

for hoja in datos_excel:
    print(f"  - {hoja}")

resultados_finales = []

print("\n" + "#" * 100)
print("IMPORTANTE: EL PROGRAMA PROCESARÁ CADA NIVEL POR SEPARADO")
print("Primero terminará completamente el Nivel 1; luego continuará con el Nivel 2, etc.")
print("#" * 100)

for numero, (nombre_hoja, hoja) in enumerate(
    datos_excel.items(),
    start=1
):

    resultado = procesar_nivel(
        nombre_hoja,
        hoja,
        numero
    )

    resultados_finales.append(
        resultado
    )


# ============================================================
# RESUMEN FINAL
# ============================================================

print("\n" + "#" * 100)
print("RESUMEN FINAL — VERACIDAD C.1")
print("#" * 100)

tabla = pd.DataFrame(
    resultados_finales
)

print(
    tabla.to_string(
        index=False
    )
)

print("\n" + "=" * 100)
print("CRITERIO DE ACEPTACIÓN")
print("=" * 100)

print(
    "p ≥ α → no se evidencia una diferencia estadísticamente "
    "significativa entre los métodos."
)

print(
    "p < α → se evidencia una diferencia estadísticamente "
    "significativa entre los métodos."
)

print(
    "\nLa prueba utilizada depende de la normalidad y, cuando "
    "corresponde, de la homogeneidad de varianzas."
)

