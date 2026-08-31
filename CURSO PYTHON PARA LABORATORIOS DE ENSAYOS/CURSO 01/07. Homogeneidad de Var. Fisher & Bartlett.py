# ============================================================
# HOMOGENEIDAD DE VARIANZAS
#
# Objetivo:
# Determinar si las poblaciones presentan varianzas iguales.
#
# El programa selecciona automáticamente la prueba según
# el número de columnas numéricas:
#
#     2 columnas       → F de Fisher
#     3 o más columnas → Bartlett
#
# SUPUESTO IMPORTANTE:
#
# Ambas pruebas se utilizan bajo el supuesto de NORMALIDAD
# de los datos.
#
# Hipótesis:
#
# H0: Todas las varianzas son iguales.
#
# H1: Al menos una varianza es diferente.
#
# Nivel de significancia:
#
# α = 0.05
#
# Regla de decisión:
#
# p > α  → No se rechaza H0
#          No hay evidencia de diferencias entre varianzas.
#
# p ≤ α → Se rechaza H0
#          Existe evidencia de que las varianzas no son iguales.
#
# IMPORTANTE:
#
# Detectar varianzas diferentes NO significa que exista un
# error en los datos. Debe investigarse la causa.
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

archivo = "precision.xlsx"

hoja = "Nivel 1"

alpha = 0.05


# ============================================================
# 3. LECTURA DEL EXCEL
# ============================================================

datos_excel = pd.read_excel(
    archivo,
    sheet_name=hoja
)


# ============================================================
# 4. IDENTIFICAR COLUMNAS NUMÉRICAS
# ============================================================

columnas_numericas = datos_excel.select_dtypes(
    include=np.number
).columns.tolist()


print("=" * 80)
print("HOMOGENEIDAD DE VARIANZAS")
print("=" * 80)

print()

print(f"Archivo: {archivo}")
print(f"Hoja: {hoja}")

print()

print("Variables numéricas encontradas:")

print(
    columnas_numericas
)

print()


# ============================================================
# 5. COMPROBAR CANTIDAD DE COLUMNAS
# ============================================================

numero_columnas = len(
    columnas_numericas
)


if numero_columnas < 2:

    raise ValueError(
        "Se necesitan al menos 2 columnas numéricas "
        "para evaluar la homogeneidad de varianzas."
    )


# ============================================================
# 6. PREPARAR LOS DATOS
# ============================================================

grupos = {}

for columna in columnas_numericas:

    # Convertimos explícitamente a numérico.
    # Los valores que no puedan convertirse se convierten
    # en NaN y posteriormente se eliminan.

    datos = pd.to_numeric(
        datos_excel[columna],
        errors="coerce"
    ).dropna()

    grupos[columna] = datos


# ============================================================
# 7. INFORMACIÓN DESCRIPTIVA
# ============================================================

resumen = []


for nombre, datos in grupos.items():

    resumen.append({

        "Variable": nombre,

        "N": len(datos),

        "Media": datos.mean(),

        "Desv. estándar": datos.std(ddof=1),

        "Varianza": datos.var(ddof=1),

        "Mínimo": datos.min(),

        "Máximo": datos.max()
    })


resumen_df = pd.DataFrame(
    resumen
)


print("=" * 80)
print("ESTADÍSTICA DESCRIPTIVA")
print("=" * 80)

print()

print(
    resumen_df.to_string(
        index=False,
        formatters={
            "Media":
                lambda x: f"{x:.4f}",

            "Desv. estándar":
                lambda x: f"{x:.4f}",

            "Varianza":
                lambda x: f"{x:.4f}",

            "Mínimo":
                lambda x: f"{x:.4f}",

            "Máximo":
                lambda x: f"{x:.4f}"
        }
    )
)

print()


# ============================================================
# 8. INTERVALOS DE CONFIANZA BONFERRONI
#    PARA LAS DESVIACIONES ESTÁNDAR
#
# Esto reproduce la lógica del informe de Minitab.
#
# Si tenemos k grupos:
#
#     confianza individual =
#     1 - α/k
#
# Para 3 grupos y α=0.05:
#
#     1 - 0.05/3 = 98.3333 %
#
# Para 2 grupos:
#
#     1 - 0.05/2 = 97.5 %
#
# Los intervalos se calculan utilizando la distribución
# Chi-cuadrado.
# ============================================================


k = numero_columnas

alpha_individual = alpha / k

confianza_individual = (
    1 - alpha_individual
)


intervalos = []


for nombre, datos in grupos.items():

    n = len(datos)

    s = datos.std(
        ddof=1
    )

    df = n - 1

    # --------------------------------------------------------
    # Intervalo para la VARIANZA
    # --------------------------------------------------------

    limite_inferior_var = (
        df * s**2
        /
        stats.chi2.ppf(
            1 - alpha_individual / 2,
            df
        )
    )

    limite_superior_var = (
        df * s**2
        /
        stats.chi2.ppf(
            alpha_individual / 2,
            df
        )
    )


    # --------------------------------------------------------
    # Convertimos de varianza a desviación estándar
    # --------------------------------------------------------

    limite_inferior_sd = np.sqrt(
        limite_inferior_var
    )

    limite_superior_sd = np.sqrt(
        limite_superior_var
    )


    intervalos.append({

        "Variable": nombre,

        "N": n,

        "Desv. estándar": s,

        "IC inferior": limite_inferior_sd,

        "IC superior": limite_superior_sd
    })


intervalos_df = pd.DataFrame(
    intervalos
)


print("=" * 80)
print("INTERVALOS DE CONFIANZA BONFERRONI")
print("PARA DESVIACIONES ESTÁNDAR")
print("=" * 80)

print()

print(
    f"Nivel de confianza familiar = "
    f"{(1-alpha)*100:.2f}%"
)

print(
    f"Nivel de confianza individual = "
    f"{confianza_individual*100:.4f}%"
)

print()

print(
    intervalos_df.to_string(
        index=False,
        formatters={
            "Desv. estándar":
                lambda x: f"{x:.4f}",

            "IC inferior":
                lambda x: f"{x:.4f}",

            "IC superior":
                lambda x: f"{x:.4f}"
        }
    )
)

print()


# ============================================================
# 9. SELECCIÓN AUTOMÁTICA DE LA PRUEBA
# ============================================================

if numero_columnas == 2:

    # ========================================================
    # PRUEBA F DE FISHER
    # ========================================================

    nombre_1 = columnas_numericas[0]

    nombre_2 = columnas_numericas[1]

    datos_1 = grupos[nombre_1]

    datos_2 = grupos[nombre_2]


    # --------------------------------------------------------
    # Varianzas muestrales
    # --------------------------------------------------------

    var_1 = datos_1.var(
        ddof=1
    )

    var_2 = datos_2.var(
        ddof=1
    )


    # --------------------------------------------------------
    # Estadístico F
    #
    # Se mantiene el orden de las columnas:
    #
    # F = Var(A1) / Var(A2)
    #
    # Esto permite comparar directamente con Minitab.
    # --------------------------------------------------------

    F = var_1 / var_2


    df1 = len(datos_1) - 1

    df2 = len(datos_2) - 1


    # --------------------------------------------------------
    # p-valor bilateral
    # --------------------------------------------------------

    p_izquierda = stats.f.cdf(
        F,
        df1,
        df2
    )

    p_derecha = stats.f.sf(
        F,
        df1,
        df2
    )


    p_valor = 2 * min(
        p_izquierda,
        p_derecha
    )


    # --------------------------------------------------------
    # Limitar p a 1
    # --------------------------------------------------------

    p_valor = min(
        p_valor,
        1.0
    )


    nombre_prueba = (
        "F de Fisher"
    )


    estadistico = F


    texto_estadistico = "F"


    grados_libertad = (
        f"gl₁ = {df1}, gl₂ = {df2}"
    )


    # --------------------------------------------------------
    # Razón de desviaciones estándar
    # --------------------------------------------------------

    razon_sd = (
        datos_1.std(ddof=1)
        /
        datos_2.std(ddof=1)
    )


    # --------------------------------------------------------
    # Razón de varianzas
    # --------------------------------------------------------

    razon_varianzas = (
        var_1 / var_2
    )


else:

    # ========================================================
    # PRUEBA DE BARTLETT
    # ========================================================

    muestras = [
        grupos[columna]
        for columna in columnas_numericas
    ]


    estadistico, p_valor = (
        stats.bartlett(
            *muestras
        )
    )


    nombre_prueba = (
        "Bartlett"
    )


    texto_estadistico = (
        "χ²"
    )


    grados_libertad = (
        f"gl = {numero_columnas - 1}"
    )


    # --------------------------------------------------------
    # Para varias muestras calculamos también:
    #
    # mayor / menor desviación estándar
    # mayor / menor varianza
    #
    # como información adicional.
    # --------------------------------------------------------

    desviaciones = resumen_df[
        "Desv. estándar"
    ]

    varianzas = resumen_df[
        "Varianza"
    ]


    razon_sd = (
        desviaciones.max()
        /
        desviaciones.min()
    )


    razon_varianzas = (
        varianzas.max()
        /
        varianzas.min()
    )


# ============================================================
# 10. DECISIÓN ESTADÍSTICA
# ============================================================

if p_valor > alpha:

    decision = (
        "NO SE RECHAZA H₀"
    )

    conclusion = (
        "No existe evidencia estadística suficiente "
        "para afirmar que las varianzas sean diferentes."
    )

    estado = (
        "VARIANZAS HOMOGÉNEAS"
    )

else:

    decision = (
        "SE RECHAZA H₀"
    )

    conclusion = (
        "Existe evidencia estadística de que "
        "al menos una varianza es diferente."
    )

    estado = (
        "VARIANZAS NO HOMOGÉNEAS"
    )


# ============================================================
# 11. MOSTRAR RESULTADO DE LA PRUEBA
# ============================================================

print("=" * 80)

print(
    f"PRUEBA DE HOMOGENEIDAD — {nombre_prueba}"
)

print("=" * 80)

print()

print(
    "H₀: Todas las varianzas son iguales."
)

print(
    "H₁: Al menos una varianza es diferente."
)

print()

print(
    f"Nivel de significancia α = {alpha}"
)

print()

print(
    f"{texto_estadistico} = "
    f"{estadistico:.4f}"
)

print(
    f"{grados_libertad}"
)

print(
    f"p-valor = "
    f"{p_valor:.4f}"
)

print()

print(
    f"Razón de varianzas "
    f"(máxima / mínima) = "
    f"{razon_varianzas:.4f}"
)

print(
    f"Razón de desviaciones estándar "
    f"(máxima / mínima) = "
    f"{razon_sd:.4f}"
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


# ============================================================
# 12. INTERPRETACIÓN DIDÁCTICA
# ============================================================

print("=" * 80)
print("INTERPRETACIÓN")
print("=" * 80)

print()

if p_valor > alpha:

    print(
        f"Como p = {p_valor:.4f} > α = {alpha}, "
        "no se rechaza H₀."
    )

    print()

    print(
        "Los datos no proporcionan evidencia estadística "
        "suficiente para considerar diferentes las varianzas."
    )

    print()

    print(
        "En términos prácticos, las muestras pueden "
        "considerarse compatibles con una varianza común."
    )

else:

    print(
        f"Como p = {p_valor:.4f} ≤ α = {alpha}, "
        "se rechaza H₀."
    )

    print()

    print(
        "Existe evidencia estadística de diferencias "
        "entre las varianzas."
    )

    print()

    print(
        "Debe investigarse qué grupo presenta la "
        "mayor variabilidad y cuál puede ser la causa."
    )


print()

print(
    "IMPORTANTE: una prueba estadística no determina "
    "por sí sola la causa de una diferencia de varianzas."
)

print()


# ============================================================
# 13. PREPARAR GRÁFICA
#
# La gráfica reproduce la idea visual de Minitab:
#
#     • Un punto = desviación estándar
#     • Barra = IC Bonferroni
#
# Además:
#
#     • Línea vertical = referencia de la menor DE
#     • Panel estadístico = prueba y p-valor
# ============================================================


fig = plt.figure(
    figsize=(14, 8)
)


gs = fig.add_gridspec(
    1,
    2,
    width_ratios=[3.6, 1.4],
    wspace=0.08
)


ax = fig.add_subplot(
    gs[0]
)


ax_info = fig.add_subplot(
    gs[1]
)


# ============================================================
# 14. POSICIONES
# ============================================================

posiciones = np.arange(
    len(intervalos_df)
)


# ============================================================
# 15. INTERVALOS DE CONFIANZA
# ============================================================

for i, fila in intervalos_df.iterrows():

    sd = fila[
        "Desv. estándar"
    ]

    inferior = fila[
        "IC inferior"
    ]

    superior = fila[
        "IC superior"
    ]


    # --------------------------------------------------------
    # Barra horizontal
    # --------------------------------------------------------

    ax.plot(
        [inferior, superior],
        [i, i],
        linewidth=3
    )


    # --------------------------------------------------------
    # Extremo izquierdo
    # --------------------------------------------------------

    ax.plot(
        [inferior, inferior],
        [i - 0.10, i + 0.10],
        linewidth=2
    )


    # --------------------------------------------------------
    # Extremo derecho
    # --------------------------------------------------------

    ax.plot(
        [superior, superior],
        [i - 0.10, i + 0.10],
        linewidth=2
    )


    # --------------------------------------------------------
    # Punto = desviación estándar
    # --------------------------------------------------------

    ax.scatter(
        sd,
        i,
        s=100,
        zorder=4
    )


# ============================================================
# 16. LÍNEA DE REFERENCIA
# ============================================================

menor_sd = intervalos_df[
    "Desv. estándar"
].min()


ax.axvline(
    menor_sd,
    linestyle="--",
    linewidth=1.5,
    alpha=0.6
)


# ============================================================
# 17. CONFIGURACIÓN DE EJES
# ============================================================

ax.set_yticks(
    posiciones
)

ax.set_yticklabels(
    intervalos_df["Variable"]
)


ax.set_xlabel(
    "Desviación estándar",
    fontsize=12
)


ax.set_ylabel(
    "Muestra",
    fontsize=12
)


# ============================================================
# 18. TÍTULOS
# ============================================================

fig.suptitle(
    f"Homogeneidad de varianzas — "
    f"{nombre_prueba}",
    fontsize=21,
    fontweight="bold",
    y=0.97
)


ax.set_title(
    "Intervalos de confianza Bonferroni del 95 % "
    "para la desviación estándar",
    fontsize=12,
    pad=12
)


# ============================================================
# 19. CUADRÍCULA
# ============================================================

ax.grid(
    axis="x",
    alpha=0.20
)

ax.grid(
    axis="y",
    alpha=0.08
)


# ============================================================
# 20. BORDES
# ============================================================

ax.spines[
    "top"
].set_visible(False)

ax.spines[
    "right"
].set_visible(False)


# ============================================================
# 21. PANEL DERECHO
# ============================================================

ax_info.axis(
    "off"
)


ax_info.text(
    0.05,
    0.94,
    "RESULTADO ESTADÍSTICO",
    fontsize=14,
    fontweight="bold",
    transform=ax_info.transAxes
)


# ============================================================
# 22. INFORMACIÓN
# ============================================================

texto_estadistico = (

    f"Prueba\n"
    f"{nombre_prueba}\n\n"

    f"{texto_estadistico}\n"
    f"{estadistico:.4f}\n\n"

    f"p-valor\n"
    f"{p_valor:.4f}\n\n"

    f"α\n"
    f"{alpha:.2f}\n\n"

    f"Razón de varianzas\n"
    f"{razon_varianzas:.4f}\n\n"

    f"Razón de DE\n"
    f"{razon_sd:.4f}"
)


ax_info.text(
    0.05,
    0.87,
    texto_estadistico,
    fontsize=10.5,
    transform=ax_info.transAxes,
    verticalalignment="top",
    linespacing=1.05
)


# ============================================================
# 23. CAJA DE CONCLUSIÓN
# ============================================================

if p_valor > alpha:

    texto_conclusion = (

        "✓ VARIANZAS\n"
        "HOMOGÉNEAS\n\n"

        f"p = {p_valor:.4f} > α\n\n"

        "No existe evidencia\n"
        "suficiente de diferencias\n"
        "entre las varianzas."
    )

else:

    texto_conclusion = (

        "⚠ VARIANZAS\n"
        "NO HOMOGÉNEAS\n\n"

        f"p = {p_valor:.4f} ≤ α\n\n"

        "Al menos una varianza\n"
        "presenta evidencia de\n"
        "ser diferente."
    )


# ------------------------------------------------------------
# La caja queda abajo para evitar solapamientos.
# ------------------------------------------------------------

ax_info.text(
    0.05,
    0.015,
    texto_conclusion,
    fontsize=10.5,
    fontweight="bold",
    transform=ax_info.transAxes,
    verticalalignment="bottom",
    bbox=dict(
        boxstyle="round,pad=0.7",
        alpha=0.12
    )
)


# ============================================================
# 24. NOTA INFERIOR
# ============================================================

fig.text(
    0.5,
    0.015,
    "⚠ La homogeneidad de varianzas debe evaluarse "
    "considerando el supuesto de normalidad. "
    "Una diferencia estadística no implica por sí sola "
    "un error en los datos.",
    ha="center",
    fontsize=10,
    style="italic"
)


# ============================================================
# 25. MOSTRAR
# ============================================================

plt.tight_layout(
    rect=[0, 0.05, 1, 0.94]
)

plt.show()


# ============================================================
# 26. RESUMEN FINAL
# ============================================================

print()

print("=" * 80)

print(
    "ANÁLISIS DE HOMOGENEIDAD COMPLETADO"
)

print("=" * 80)

print()

print(
    f"Cantidad de grupos analizados: "
    f"{numero_columnas}"
)

print(
    f"Prueba seleccionada automáticamente: "
    f"{nombre_prueba}"
)

print(
    f"p-valor = {p_valor:.4f}"
)

print()

if p_valor > alpha:

    print(
        "RESULTADO: VARIANZAS HOMOGÉNEAS"
    )

else:

    print(
        "RESULTADO: VARIANZAS NO HOMOGÉNEAS"
    )

print()

print(
    "No se modificaron ni eliminaron datos."
)

print(
    "La decisión sobre los resultados debe considerar "
    "el contexto experimental del laboratorio."
)
