# ============================================================
# PRUEBAS NO PARAMÉTRICAS
# ============================================================
#
# Este programa detecta automáticamente el número de
# columnas numéricas del Excel y selecciona la prueba
# no paramétrica correspondiente.
#
# ------------------------------------------------------------
# 1 COLUMNA
#     → Wilcoxon de rangos con signo
#
#     Compara una muestra contra un valor de referencia.
#
# ------------------------------------------------------------
# 2 COLUMNAS
#     → Mann-Whitney U
#
#     Compara dos grupos independientes.
#
# ------------------------------------------------------------
# 3 O MÁS COLUMNAS
#     → Kruskal-Wallis
#
#     Compara tres o más grupos independientes.
#
# ------------------------------------------------------------
#
# NIVEL DE SIGNIFICANCIA
#
# α = 0.05
#
# REGLA DE DECISIÓN
#
# p > α
#     No se rechaza H₀.
#
# p ≤ α
#     Se rechaza H₀.
#
# ============================================================


# ============================================================
# 1. BIBLIOTECAS
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy import stats


# ============================================================
# 2. CONFIGURACIÓN
# ============================================================

archivo = "centralidad.xlsx"

hoja = "hoja1"

alpha = 0.05


# ============================================================
# 3. LECTURA DEL EXCEL
# ============================================================
#
# Pandas lee la hoja seleccionada y posteriormente
# identificaremos automáticamente las columnas numéricas.
# ============================================================

datos_excel = pd.read_excel(
    archivo,
    sheet_name=hoja
)


# ============================================================
# 4. IDENTIFICAR COLUMNAS NUMÉRICAS
# ============================================================
#
# Esto permite que el programa trabaje automáticamente
# con A1, A2, A3, etc.
#
# No es necesario escribir manualmente los nombres.
# ============================================================

columnas_numericas = datos_excel.select_dtypes(
    include=np.number
).columns.tolist()


print("=" * 80)
print("PRUEBAS NO PARAMÉTRICAS")
print("=" * 80)

print()

print(f"Archivo : {archivo}")
print(f"Hoja    : {hoja}")

print()

print("Columnas numéricas encontradas:")

for i, columna in enumerate(
    columnas_numericas,
    start=1
):

    print(
        f"{i}. {columna}"
    )

print()


# ============================================================
# 5. COMPROBAR QUE EXISTAN DATOS
# ============================================================

numero_columnas = len(
    columnas_numericas
)

if numero_columnas == 0:

    raise ValueError(
        "No se encontraron columnas numéricas "
        "en la hoja seleccionada."
    )


# ============================================================
# 6. CONVERTIR LAS COLUMNAS A NUMÉRICAS
# ============================================================
#
# Los valores que no puedan convertirse se transforman
# en NaN y posteriormente se eliminan únicamente para
# el análisis correspondiente.
# ============================================================

grupos = {}

for columna in columnas_numericas:

    grupos[columna] = pd.to_numeric(
        datos_excel[columna],
        errors="coerce"
    ).dropna()


# ============================================================
# 7. FUNCIÓN DE ESTADÍSTICA DESCRIPTIVA
# ============================================================

def mostrar_descriptiva(
    nombre,
    datos
):

    print("-" * 70)

    print(
        f"Variable: {nombre}"
    )

    print("-" * 70)

    print(
        f"N              = {len(datos)}"
    )

    print(
        f"Media          = {datos.mean():.4f}"
    )

    print(
        f"Mediana        = {datos.median():.4f}"
    )

    print(
        f"Desv. estándar = {datos.std(ddof=1):.4f}"
    )

    print(
        f"Mínimo         = {datos.min():.4f}"
    )

    print(
        f"Máximo         = {datos.max():.4f}"
    )

    print(
        f"Q1             = {datos.quantile(0.25):.4f}"
    )

    print(
        f"Q3             = {datos.quantile(0.75):.4f}"
    )

    print(
        f"IQR            = "
        f"{datos.quantile(0.75) - datos.quantile(0.25):.4f}"
    )

    print()


# ============================================================
# 8. FUNCIÓN DE DECISIÓN
# ============================================================

def obtener_decision(
    p_valor
):

    if p_valor <= alpha:

        return (
            "SE RECHAZA H₀",
            "Existe evidencia estadística "
            "suficiente para afirmar que "
            "existe una diferencia."
        )

    else:

        return (
            "NO SE RECHAZA H₀",
            "No existe evidencia estadística "
            "suficiente para afirmar que "
            "exista una diferencia."
        )


# ============================================================
# 9. ESTADÍSTICA DESCRIPTIVA GENERAL
# ============================================================

print("=" * 80)
print("ESTADÍSTICA DESCRIPTIVA")
print("=" * 80)

print()

for nombre, datos in grupos.items():

    mostrar_descriptiva(
        nombre,
        datos
    )


# ============================================================
# ============================================================
# CASO 1 — UNA COLUMNA
# WILCOXON
# ============================================================
# ============================================================

if numero_columnas == 1:

    nombre = columnas_numericas[0]

    datos = grupos[
        nombre
    ]


    # ========================================================
    # VALOR DE REFERENCIA
    # ========================================================

    print("=" * 80)
    print("PRUEBA DE WILCOXON")
    print("=" * 80)

    print()

    print(
        f"Variable seleccionada: {nombre}"
    )

    print()

    print(
        "La prueba comparará la muestra "
        "contra un valor de referencia."
    )

    print()

    referencia = float(
        input(
            "¿Qué valor de referencia desea utilizar? "
        )
    )


    # ========================================================
    # CONSTRUIR DIFERENCIAS
    # ========================================================
    #
    # La prueba de Wilcoxon se realiza sobre:
    #
    # diferencia = resultado - referencia
    #
    # Los valores cuya diferencia es exactamente cero
    # no aportan información al cálculo de los rangos.
    # ========================================================

    diferencias = (
        datos - referencia
    )

    diferencias_no_cero = (
        diferencias[
            diferencias != 0
        ]
    )


    # ========================================================
    # HIPÓTESIS
    # ========================================================

    print()

    print(
        "H₀: La mediana de la muestra "
        "es igual al valor de referencia."
    )

    print(
        "H₁: La mediana de la muestra "
        "es diferente del valor de referencia."
    )

    print()


    # ========================================================
    # EMPATES
    # ========================================================
    #
    # Los empates aparecen cuando existen valores absolutos
    # de las diferencias que reciben el mismo rango.
    #
    # Calculamos un factor de corrección para mostrar
    # explícitamente al alumno que los empates fueron
    # considerados.
    # ========================================================

    valores_abs = np.abs(
        diferencias_no_cero.to_numpy()
    )

    rangos = stats.rankdata(
        valores_abs
    )

    factor_empates = stats.tiecorrect(
        rangos
    )

    # Un empate existe cuando dos o más diferencias
    # absolutas reciben el mismo rango.
    _, frecuencias = np.unique(
        valores_abs,
        return_counts=True
    )

    hay_empates = np.any(
        frecuencias > 1
    )

    # Rangos con signo:
    # W+ = suma de rangos de diferencias positivas
    # W- = suma de rangos de diferencias negativas
    W_mas = rangos[
        diferencias_no_cero.to_numpy() > 0
    ].sum()

    W_menos = rangos[
        diferencias_no_cero.to_numpy() < 0
    ].sum()

    W_min = min(W_mas, W_menos)
    W_max = max(W_mas, W_menos)

    # Los ceros respecto al valor de referencia se eliminan
    # del cálculo estándar de Wilcoxon (zero_method='wilcox').
    n_ceros = int(
        (diferencias == 0).sum()
    )


    # ========================================================
    # PRUEBA DE WILCOXON
    # ========================================================
    #
    # correction=True:
    #
    # incorpora la corrección de continuidad en la
    # aproximación normal.
    #
    # method="approx":
    #
    # utiliza la aproximación normal, apropiada cuando
    # necesitamos un p-valor aun cuando existen empates.
    # ========================================================

    resultado = stats.wilcoxon(
        diferencias,
        zero_method="wilcox",
        correction=True,
        alternative="two-sided",
        method="approx"
    )


    estadistico = resultado.statistic

    p_valor = resultado.pvalue


    # ========================================================
    # TAMAÑO DE MUESTRA EFECTIVO
    # ========================================================

    n_efectivo = len(
        diferencias_no_cero
    )


    # ========================================================
    # DECISIÓN
    # ========================================================

    decision, conclusion = (
        obtener_decision(
            p_valor
        )
    )


    # ========================================================
    # RESULTADOS
    # ========================================================

    print("=" * 80)
    print("RESULTADO — WILCOXON")
    print("=" * 80)

    print()

    print(
        f"Valor de referencia = "
        f"{referencia:.4f}"
    )

    print()

    print(
        f"N original = "
        f"{len(datos)}"
    )

    print(
        f"N efectivo = "
        f"{n_efectivo}"
    )

    print()

    print(
        f"Mediana = "
        f"{datos.median():.4f}"
    )

    print()

    print(
        f"W− (rangos negativos) = "
        f"{W_menos:.4f}"
    )

    print(
        f"W+ (rangos positivos) = "
        f"{W_mas:.4f}"
    )

    print(
        f"W usado para el contraste = "
        f"{estadistico:.4f}"
    )

    print()

    print(
        f"Factor de corrección por empates = "
        f"{factor_empates:.6f}"
    )

    print(
        f"Empates reales detectados = "
        f"{'SÍ' if hay_empates else 'NO'}"
    )

    print(
        f"Observaciones con diferencia cero = "
        f"{n_ceros}"
    )

    print()

    print(
        "Corrección de continuidad = SÍ"
    )

    print(
        f"Corrección por empates en p-valor = "
        f"{'SÍ' if hay_empates else 'NO NECESARIA'}"
    )

    print()

    print(
        f"p-valor = "
        f"{p_valor:.6f}"
    )

    print()

    print(
        f"α = {alpha:.2f}"
    )

    print()

    print(
        f"DECISIÓN: {decision}"
    )

    print()

    print(
        f"CONCLUSIÓN: {conclusion}"
    )

    print()


    # ========================================================
    # INTERPRETACIÓN DIDÁCTICA
    # ========================================================

    print("=" * 80)
    print("INTERPRETACIÓN DIDÁCTICA")
    print("=" * 80)

    print()

    print(
        "Wilcoxon no utiliza directamente la media."
    )

    print(
        "Trabaja con las diferencias respecto "
        "al valor de referencia y sus rangos."
    )

    print()

    if p_valor <= alpha:

        print(
            f"Como p = {p_valor:.6f} ≤ "
            f"α = {alpha}, se rechaza H₀."
        )

        print()

        print(
            "Existe evidencia estadística "
            "de que la mediana difiere "
            "del valor de referencia."
        )

    else:

        print(
            f"Como p = {p_valor:.6f} > "
            f"α = {alpha}, no se rechaza H₀."
        )

        print()

        print(
            "No existe evidencia estadística "
            "suficiente para afirmar que "
            "la mediana difiera del valor "
            "de referencia."
        )

    print()


    # ========================================================
    # GRÁFICA
    # ========================================================

    fig = plt.figure(
        figsize=(14, 7)
    )

    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[3.5, 1.5],
        wspace=0.08
    )

    ax = fig.add_subplot(
        gs[0]
    )

    ax_info = fig.add_subplot(
        gs[1]
    )


    # --------------------------------------------------------
    # BOXPLOT
    # --------------------------------------------------------

    ax.boxplot(
        datos,
        vert=False,
        widths=0.35,
        patch_artist=True
    )


    # --------------------------------------------------------
    # VALOR DE REFERENCIA
    # --------------------------------------------------------

    ax.axvline(
        referencia,
        linestyle="--",
        linewidth=2,
        color="red",
        label="Valor de referencia"
    )


    # --------------------------------------------------------
    # MEDIANA
    # --------------------------------------------------------

    ax.axvline(
        datos.median(),
        linestyle=":",
        linewidth=2,
        label="Mediana"
    )


    ax.set_yticks(
        [1]
    )

    ax.set_yticklabels(
        [nombre]
    )

    ax.set_xlabel(
        "Resultado",
        fontsize=12
    )

    ax.set_title(
        "Wilcoxon — comparación de la mediana",
        fontsize=14,
        fontweight="bold"
    )

    ax.grid(
        axis="x",
        alpha=0.20
    )

    ax.spines[
        "top"
    ].set_visible(False)

    ax.spines[
        "right"
    ].set_visible(False)

    ax.legend()


    # --------------------------------------------------------
    # PANEL DE RESULTADOS
    # --------------------------------------------------------

    ax_info.axis(
        "off"
    )

    ax_info.text(
        0.05,
        0.95,
        "RESULTADO ESTADÍSTICO",
        fontsize=15,
        fontweight="bold",
        transform=ax_info.transAxes,
        verticalalignment="top"
    )

    ax_info.text(
        0.05,
        0.82,
        (
            f"N original = {len(datos)}\n"
            f"N efectivo = {n_efectivo}\n\n"
            f"Mediana = {datos.median():.4f}\n\n"
            f"Referencia = {referencia:.4f}\n\n"
            f"W− = {W_menos:.4f}\n"
            f"W+ = {W_mas:.4f}\n"
            f"W usado = {estadistico:.4f}\n\n"
            f"p = {p_valor:.6f}\n\n"
            f"Empates reales = "
            f"{'SÍ' if hay_empates else 'NO'}\n"
            f"Continuidad = corregida\n"
            f"Corrección por empates = "
            f"{'SÍ' if hay_empates else 'NO NECESARIA'}\n\n"
            f"{decision}"
        ),
        fontsize=10.5,
        transform=ax_info.transAxes,
        verticalalignment="top",
        linespacing=1.20
    )


    fig.suptitle(
        f"Prueba de Wilcoxon — {nombre}",
        fontsize=21,
        fontweight="bold",
        y=0.97
    )

    fig.text(
        0.5,
        0.015,
        "La detección estadística de una diferencia "
        "no implica por sí sola que el resultado "
        "deba eliminarse o modificarse.",
        ha="center",
        fontsize=10,
        style="italic"
    )

    plt.tight_layout(
        rect=[0, 0.05, 1, 0.94]
    )

    plt.show()


# ============================================================
# ============================================================
# CASO 2 — DOS COLUMNAS
# MANN-WHITNEY U
# ============================================================
# ============================================================

elif numero_columnas == 2:

    nombre_1 = columnas_numericas[0]

    nombre_2 = columnas_numericas[1]

    datos_1 = grupos[
        nombre_1
    ]

    datos_2 = grupos[
        nombre_2
    ]


    # ========================================================
    # HIPÓTESIS
    # ========================================================

    print("=" * 80)
    print("PRUEBA DE MANN-WHITNEY U")
    print("=" * 80)

    print()

    print(
        f"Grupo 1: {nombre_1}"
    )

    print(
        f"Grupo 2: {nombre_2}"
    )

    print()

    print(
        "Esta prueba compara dos grupos "
        "INDEPENDIENTES."
    )

    print()

    print(
        "H₀: Las distribuciones de ambos grupos "
        "son iguales."
    )

    print(
        "H₁: Las distribuciones de ambos grupos "
        "son diferentes."
    )

    print()


    # ========================================================
    # COMBINAR DATOS PARA EVALUAR EMPATES
    # ========================================================

    datos_combinados = pd.concat(
        [
            datos_1,
            datos_2
        ],
        ignore_index=True
    )


    rangos_combinados = stats.rankdata(
        datos_combinados
    )

    factor_empates = stats.tiecorrect(
        rangos_combinados
    )

    # En Kruskal-Wallis los empates se evalúan sobre
    # todas las observaciones conjuntamente.
    _, frecuencias = np.unique(
        datos_combinados.to_numpy(),
        return_counts=True
    )

    hay_empates = np.any(
        frecuencias > 1
    )

    # Un empate real existe si un mismo valor aparece
    # más de una vez en los datos combinados.
    _, frecuencias = np.unique(
        datos_combinados.to_numpy(),
        return_counts=True
    )

    hay_empates = np.any(
        frecuencias > 1
    )

    n1 = len(datos_1)
    n2 = len(datos_2)

    # U1 y U2 son las dos formas equivalentes de expresar
    # la estadística de Mann-Whitney.
    R1 = rangos_combinados[:n1].sum()
    R2 = rangos_combinados[n1:].sum()

    U1 = R1 - n1 * (n1 + 1) / 2
    U2 = R2 - n2 * (n2 + 1) / 2

    U_min = min(U1, U2)
    U_max = max(U1, U2)


    # ========================================================
    # MANN-WHITNEY
    # ========================================================
    #
    # method="asymptotic":
    #
    # utiliza la aproximación asintótica.
    #
    # use_continuity=True:
    #
    # incorpora corrección de continuidad.
    #
    # La aproximación asintótica incorpora la corrección
    # necesaria por empates.
    # ========================================================

    resultado = stats.mannwhitneyu(
        datos_1,
        datos_2,
        alternative="two-sided",
        method="asymptotic",
        use_continuity=True
    )


    estadistico = resultado.statistic

    p_valor = resultado.pvalue


    # ========================================================
    # DECISIÓN
    # ========================================================

    decision, conclusion = (
        obtener_decision(
            p_valor
        )
    )


    # ========================================================
    # RESULTADOS
    # ========================================================

    print("=" * 80)
    print("RESULTADO — MANN-WHITNEY U")
    print("=" * 80)

    print()

    print(
        f"Mediana {nombre_1} = "
        f"{datos_1.median():.4f}"
    )

    print(
        f"Mediana {nombre_2} = "
        f"{datos_2.median():.4f}"
    )

    print()

    print(
        f"U₁ = {U1:.4f}"
    )

    print(
        f"U₂ = {U2:.4f}"
    )

    print(
        f"U mínimo = {U_min:.4f}"
    )

    print(
        f"U máximo = {U_max:.4f}"
    )

    print(
        f"U usado para el contraste = "
        f"{estadistico:.4f}"
    )

    print()

    print(
        f"Factor de corrección por empates = "
        f"{factor_empates:.6f}"
    )

    print(
        f"Empates reales detectados = "
        f"{'SÍ' if hay_empates else 'NO'}"
    )

    print()

    print(
        "Corrección de continuidad = SÍ"
    )

    print(
        f"Corrección por empates en p-valor = "
        f"{'SÍ' if hay_empates else 'NO NECESARIA'}"
    )

    print()

    print(
        f"p-valor = "
        f"{p_valor:.6f}"
    )

    print()

    print(
        f"α = {alpha:.2f}"
    )

    print()

    print(
        f"DECISIÓN: {decision}"
    )

    print()

    print(
        f"CONCLUSIÓN: {conclusion}"
    )

    print()


    # ========================================================
    # INTERPRETACIÓN
    # ========================================================

    print("=" * 80)
    print("INTERPRETACIÓN DIDÁCTICA")
    print("=" * 80)

    print()

    print(
        "Mann-Whitney utiliza los rangos de "
        "los resultados en lugar de asumir "
        "normalidad de los datos."
    )

    print()

    if p_valor <= alpha:

        print(
            f"Como p = {p_valor:.6f} ≤ "
            f"α = {alpha}, se rechaza H₀."
        )

        print()

        print(
            "Existe evidencia estadística "
            "de una diferencia entre "
            "los dos grupos."
        )

    else:

        print(
            f"Como p = {p_valor:.6f} > "
            f"α = {alpha}, no se rechaza H₀."
        )

        print()

        print(
            "No existe evidencia estadística "
            "suficiente para afirmar que "
            "los grupos sean diferentes."
        )

    print()


    # ========================================================
    # GRÁFICA
    # ========================================================

    fig = plt.figure(
        figsize=(14, 8)
    )

    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[3.5, 1.5],
        wspace=0.08
    )

    ax = fig.add_subplot(
        gs[0]
    )

    ax_info = fig.add_subplot(
        gs[1]
    )


    # --------------------------------------------------------
    # BOXPLOT
    # --------------------------------------------------------

    ax.boxplot(
        [
            datos_1,
            datos_2
        ],
        tick_labels=[
            nombre_1,
            nombre_2
        ],
        widths=0.45,
        patch_artist=True,
        showmeans=True
    )


    ax.set_ylabel(
        "Resultado",
        fontsize=12
    )

    ax.set_title(
        "Comparación de dos grupos independientes",
        fontsize=14,
        fontweight="bold"
    )

    ax.grid(
        axis="y",
        alpha=0.20
    )

    ax.spines[
        "top"
    ].set_visible(False)

    ax.spines[
        "right"
    ].set_visible(False)


    # --------------------------------------------------------
    # PANEL
    # --------------------------------------------------------

    ax_info.axis(
        "off"
    )

    ax_info.text(
        0.05,
        0.95,
        "RESULTADO ESTADÍSTICO",
        fontsize=15,
        fontweight="bold",
        transform=ax_info.transAxes,
        verticalalignment="top"
    )

    ax_info.text(
        0.05,
        0.82,
        (
            f"{nombre_1}\n"
            f"N = {len(datos_1)}\n"
            f"Mediana = {datos_1.median():.4f}\n\n"

            f"{nombre_2}\n"
            f"N = {len(datos_2)}\n"
            f"Mediana = {datos_2.median():.4f}\n\n"

            f"U₁ = {U1:.4f}\n"
            f"U₂ = {U2:.4f}\n"
            f"U mínimo = {U_min:.4f}\n"
            f"U máximo = {U_max:.4f}\n"
            f"U usado = {estadistico:.4f}\n\n"
            f"p = {p_valor:.6f}\n\n"

            f"Empates reales = "
            f"{'SÍ' if hay_empates else 'NO'}\n"
            f"Continuidad = corregida\n"
            f"Corrección por empates = "
            f"{'SÍ' if hay_empates else 'NO NECESARIA'}\n\n"

            f"{decision}"
        ),
        fontsize=11,
        transform=ax_info.transAxes,
        verticalalignment="top",
        linespacing=1.2
    )


    fig.suptitle(
        f"Mann-Whitney U — "
        f"{nombre_1} vs {nombre_2}",
        fontsize=21,
        fontweight="bold",
        y=0.97
    )

    fig.text(
        0.5,
        0.015,
        "La prueba permite comparar dos grupos "
        "independientes sin asumir normalidad.",
        ha="center",
        fontsize=10,
        style="italic"
    )

    plt.tight_layout(
        rect=[0, 0.05, 1, 0.94]
    )

    plt.show()


# ============================================================
# ============================================================
# CASO 3 — TRES O MÁS COLUMNAS
# KRUSKAL-WALLIS
# ============================================================
# ============================================================

else:

    nombres = columnas_numericas


    datos_grupos = [
        grupos[nombre]
        for nombre in nombres
    ]


    # ========================================================
    # HIPÓTESIS
    # ========================================================

    print("=" * 80)
    print("PRUEBA DE KRUSKAL-WALLIS")
    print("=" * 80)

    print()

    print(
        f"Se encontraron {numero_columnas} grupos."
    )

    print()

    print(
        "H₀: Las distribuciones de todos "
        "los grupos son iguales."
    )

    print(
        "H₁: Al menos uno de los grupos "
        "presenta una distribución diferente."
    )

    print()


    # ========================================================
    # COMBINAR LOS DATOS
    # ========================================================
    #
    # Kruskal-Wallis trabaja mediante rangos conjuntos.
    #
    # Por ello calculamos los rangos de todas las
    # observaciones conjuntamente.
    # ========================================================

    datos_combinados = pd.concat(
        datos_grupos,
        ignore_index=True
    )


    rangos_combinados = stats.rankdata(
        datos_combinados
    )


    # ========================================================
    # CORRECCIÓN POR EMPATES
    # ========================================================

    factor_empates = stats.tiecorrect(
        rangos_combinados
    )


    # ========================================================
    # KRUSKAL-WALLIS
    # ========================================================
    #
    # SciPy incorpora la corrección por empates
    # en el cálculo de la estadística H.
    #
    # No aplicamos una corrección de continuidad de 0.5,
    # porque ésta no corresponde al procedimiento estándar
    # de Kruskal-Wallis.
    # ========================================================

    resultado = stats.kruskal(
        *datos_grupos
    )


    estadistico = resultado.statistic

    p_valor = resultado.pvalue


    # ========================================================
    # DECISIÓN
    # ========================================================

    decision, conclusion = (
        obtener_decision(
            p_valor
        )
    )


    # ========================================================
    # RESULTADOS
    # ========================================================

    print("=" * 80)
    print("RESULTADO — KRUSKAL-WALLIS")
    print("=" * 80)

    print()

    for nombre, datos in zip(
        nombres,
        datos_grupos
    ):

        print(
            f"{nombre}: "
            f"N = {len(datos)}, "
            f"Mediana = {datos.median():.4f}"
        )

    print()

    print(
        f"H = "
        f"{estadistico:.4f}"
    )

    print()

    print(
        f"Factor de corrección por empates = "
        f"{factor_empates:.6f}"
    )

    print(
        f"Empates reales detectados = "
        f"{'SÍ' if hay_empates else 'NO'}"
    )

    print()

    print(
        f"Corrección por empates en p-valor = "
        f"{'SÍ' if hay_empates else 'NO NECESARIA'}"
    )

    print(
        "Corrección de continuidad = "
        "NO APLICA"
    )

    print()

    print(
        f"p-valor = "
        f"{p_valor:.6f}"
    )

    print()

    print(
        f"α = {alpha:.2f}"
    )

    print()

    print(
        f"DECISIÓN: {decision}"
    )

    print()

    print(
        f"CONCLUSIÓN: {conclusion}"
    )

    print()


    # ========================================================
    # INTERPRETACIÓN DIDÁCTICA
    # ========================================================

    print("=" * 80)
    print("INTERPRETACIÓN DIDÁCTICA")
    print("=" * 80)

    print()

    print(
        "Kruskal-Wallis permite comparar "
        "tres o más grupos independientes "
        "sin asumir normalidad."
    )

    print()

    if p_valor <= alpha:

        print(
            f"Como p = {p_valor:.6f} ≤ "
            f"α = {alpha}, se rechaza H₀."
        )

        print()

        print(
            "Existe evidencia estadística de "
            "que al menos uno de los grupos "
            "es diferente."
        )

        print()

        print(
            "IMPORTANTE:"
        )

        print(
            "Kruskal-Wallis por sí sola NO indica "
            "qué grupos son diferentes."
        )

        print(
            "Para identificar las diferencias "
            "entre pares se realizará posteriormente "
            "una prueba post-hoc."
        )

    else:

        print(
            f"Como p = {p_valor:.6f} > "
            f"α = {alpha}, no se rechaza H₀."
        )

        print()

        print(
            "No existe evidencia estadística "
            "suficiente para afirmar que "
            "alguno de los grupos sea diferente."
        )

    print()


    # ========================================================
    # GRÁFICA
    # ========================================================

    fig = plt.figure(
        figsize=(15, 8)
    )

    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[3.5, 1.5],
        wspace=0.08
    )

    ax = fig.add_subplot(
        gs[0]
    )

    ax_info = fig.add_subplot(
        gs[1]
    )


    # --------------------------------------------------------
    # BOXPLOT DE TODOS LOS GRUPOS
    # --------------------------------------------------------

    ax.boxplot(
        datos_grupos,
        tick_labels=nombres,
        widths=0.45,
        patch_artist=True,
        showmeans=True
    )


    ax.set_ylabel(
        "Resultado",
        fontsize=12
    )

    ax.set_title(
        "Comparación de múltiples grupos",
        fontsize=14,
        fontweight="bold"
    )

    ax.grid(
        axis="y",
        alpha=0.20
    )

    ax.spines[
        "top"
    ].set_visible(False)

    ax.spines[
        "right"
    ].set_visible(False)


    # --------------------------------------------------------
    # PANEL DE RESULTADOS
    # --------------------------------------------------------

    ax_info.axis(
        "off"
    )

    ax_info.text(
        0.05,
        0.95,
        "RESULTADO ESTADÍSTICO",
        fontsize=15,
        fontweight="bold",
        transform=ax_info.transAxes,
        verticalalignment="top"
    )


    resumen_grupos = ""

    for nombre, datos in zip(
        nombres,
        datos_grupos
    ):

        resumen_grupos += (
            f"{nombre}: "
            f"N={len(datos)}, "
            f"Mediana={datos.median():.4f}\n"
        )


    ax_info.text(
        0.05,
        0.82,
        (
            f"{resumen_grupos}\n"
            f"H = {estadistico:.4f}\n\n"
            f"p = {p_valor:.6f}\n\n"
            f"Empates reales = "
            f"{'SÍ' if hay_empates else 'NO'}\n"
            f"Corrección por empates = "
            f"{'SÍ' if hay_empates else 'NO NECESARIA'}\n"
            f"Continuidad = no aplica\n\n"
            f"{decision}"
        ),
        fontsize=10.5,
        transform=ax_info.transAxes,
        verticalalignment="top",
        linespacing=1.25
    )


    fig.suptitle(
        "Kruskal-Wallis — comparación de grupos",
        fontsize=21,
        fontweight="bold",
        y=0.97
    )


    fig.text(
        0.5,
        0.015,
        "Un resultado significativo indica que "
        "al menos un grupo difiere. "
        "La identificación de los grupos responsables "
        "requiere una prueba post-hoc.",
        ha="center",
        fontsize=10,
        style="italic"
    )


    plt.tight_layout(
        rect=[0, 0.05, 1, 0.94]
    )

    plt.show()


# ============================================================
# FIN DEL PROGRAMA
# ============================================================

print()

print("=" * 80)

print("ANÁLISIS NO PARAMÉTRICO COMPLETADO")

print("=" * 80)

print()

print(
    "Los resultados originales del Excel "
    "no fueron modificados."
)

print()

print(
    "La decisión estadística debe interpretarse "
    "considerando el diseño experimental y "
    "el contexto del laboratorio."
)
