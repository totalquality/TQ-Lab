# ============================================================
# PRUEBA DE LEVENE–BROWN–FORSYTHE
# HOMOGENEIDAD DE VARIANZAS
#
# Objetivo:
# Determinar si las poblaciones presentan varianzas iguales.
#
# Esta prueba puede utilizarse con:
#
#     2 grupos
#     3 grupos
#     4 grupos
#     ...
#
# El programa detectará automáticamente todas las columnas
# numéricas del Excel y las utilizará como grupos.
#
#
# ============================================================
# HIPÓTESIS
# ============================================================
#
# H0: Todas las varianzas son iguales.
#
# H1: Al menos una varianza es diferente.
#
#
# ============================================================
# NIVEL DE SIGNIFICANCIA
# ============================================================
#
# α = 0.05
#
#
# ============================================================
# REGLA DE DECISIÓN
# ============================================================
#
# p > α
#     No se rechaza H0.
#     No existe evidencia suficiente para afirmar
#     que las varianzas sean diferentes.
#
# p ≤ α
#     Se rechaza H0.
#     Existe evidencia de que al menos una varianza
#     es diferente.
#
#
# ============================================================
# IMPORTANTE
# ============================================================
#
# Esta implementación utiliza la MEDIANA como medida central:
#
#     center="median"
#
# Por ello corresponde a la modificación de Brown–Forsythe
# de la prueba de Levene.
#
# Es más robusta frente a desviaciones de normalidad que
# la versión original de Levene basada en la media.
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

# Nombre del archivo Excel

archivo = "veracidad.xlsx"


# Nombre de la hoja

hoja = "nivel1"


# Nivel de significancia

alpha = 0.05


# ============================================================
# 3. LECTURA DEL ARCHIVO EXCEL
# ============================================================

datos_excel = pd.read_excel(
    archivo,
    sheet_name=hoja
)


# ============================================================
# 4. IDENTIFICAR AUTOMÁTICAMENTE LAS COLUMNAS NUMÉRICAS
# ============================================================
#
# Cada columna numérica será considerada un grupo.
#
# Por ejemplo:
#
# A1   A2
#
# → 2 grupos
#
#
# A1   A2   A3
#
# → 3 grupos
#
#
# A1   A2   A3   A4
#
# → 4 grupos
#
# No es necesario modificar el código.
# ============================================================

columnas_numericas = datos_excel.select_dtypes(
    include=np.number
).columns.tolist()


print("=" * 80)
print("PRUEBA DE LEVENE–BROWN–FORSYTHE")
print("HOMOGENEIDAD DE VARIANZAS")
print("=" * 80)

print()

print(f"Archivo analizado: {archivo}")

print(f"Hoja analizada: {hoja}")

print()

print("Columnas numéricas encontradas:")

print(columnas_numericas)

print()


# ============================================================
# 5. COMPROBAR CANTIDAD DE GRUPOS
# ============================================================

numero_grupos = len(
    columnas_numericas
)


if numero_grupos < 2:

    raise ValueError(
        "Se necesitan al menos 2 grupos "
        "para realizar la prueba de "
        "Levene–Brown–Forsythe."
    )


print(
    f"Cantidad de grupos analizados: "
    f"{numero_grupos}"
)

print()


# ============================================================
# 6. PREPARAR LOS DATOS
# ============================================================
#
# Convertimos cada columna a numérico.
#
# Si existe algún valor que no pueda convertirse,
# se transforma en NaN.
#
# Posteriormente se eliminan solamente los valores
# no numéricos de esa columna para realizar el análisis.
# ============================================================

grupos = {}


for columna in columnas_numericas:

    datos = pd.to_numeric(
        datos_excel[columna],
        errors="coerce"
    )


    datos = datos.dropna()


    grupos[columna] = datos


# ============================================================
# 7. ESTADÍSTICA DESCRIPTIVA
# ============================================================
#
# Antes de realizar una prueba estadística es conveniente
# conocer el comportamiento básico de cada grupo.
# ============================================================

resumen = []


for nombre, datos in grupos.items():

    resumen.append({

        "Variable": nombre,

        "N": len(datos),

        "Media": datos.mean(),

        "Mediana": datos.median(),

        "Desv. estándar": datos.std(
            ddof=1
        ),

        "Varianza": datos.var(
            ddof=1
        ),

        "Mínimo": datos.min(),

        "Máximo": datos.max(),

        "Rango": (
            datos.max()
            -
            datos.min()
        )
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

            "Mediana":
                lambda x: f"{x:.4f}",

            "Desv. estándar":
                lambda x: f"{x:.4f}",

            "Varianza":
                lambda x: f"{x:.4f}",

            "Mínimo":
                lambda x: f"{x:.4f}",

            "Máximo":
                lambda x: f"{x:.4f}",

            "Rango":
                lambda x: f"{x:.4f}"
        }
    )
)

print()


# ============================================================
# 8. INTERVALOS DE CONFIANZA BONFERRONI
#    PARA LAS DESVIACIONES ESTÁNDAR
# ============================================================
#
# Estos intervalos permiten visualizar la incertidumbre
# asociada a la desviación estándar de cada grupo.
#
# No sustituyen la prueba de Levene.
#
# Son información complementaria.
# ============================================================

k = numero_grupos


# Corrección de Bonferroni

alpha_individual = (
    alpha / k
)


confianza_individual = (
    1 - alpha_individual
)


intervalos = []


for nombre, datos in grupos.items():

    n = len(datos)

    df = n - 1

    sd = datos.std(
        ddof=1
    )


    # --------------------------------------------------------
    # Intervalo de confianza para la VARIANZA
    # --------------------------------------------------------

    limite_inferior_var = (

        df * sd**2

        /

        stats.chi2.ppf(
            1 - alpha_individual / 2,
            df
        )
    )


    limite_superior_var = (

        df * sd**2

        /

        stats.chi2.ppf(
            alpha_individual / 2,
            df
        )
    )


    # --------------------------------------------------------
    # Convertir de varianza a desviación estándar
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

        "Desv. estándar": sd,

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
# 9. PREPARAR LAS MUESTRAS
# ============================================================

muestras = [

    grupos[columna]

    for columna in columnas_numericas
]


# ============================================================
# 10. PRUEBA DE LEVENE–BROWN–FORSYTHE
# ============================================================
#
# center="median"
#
# Esta es la parte fundamental del procedimiento.
#
# La prueba utiliza la MEDIANA como medida central.
#
# Esto corresponde a la modificación de Brown–Forsythe
# de la prueba de Levene.
# ============================================================

estadistico, p_valor = stats.levene(
    *muestras,
    center="median"
)


# ============================================================
# 11. GRADOS DE LIBERTAD
# ============================================================

grados_libertad_1 = (
    numero_grupos - 1
)


grados_libertad_2 = (
    sum(
        len(datos)
        for datos in muestras
    )
    -
    numero_grupos
)


# ============================================================
# 12. DECISIÓN ESTADÍSTICA
# ============================================================

if p_valor > alpha:

    decision = (
        "NO SE RECHAZA H₀"
    )

    estado = (
        "VARIANZAS HOMOGÉNEAS"
    )

    conclusion = (
        "No existe evidencia estadística suficiente "
        "para afirmar que las varianzas sean diferentes."
    )

else:

    decision = (
        "SE RECHAZA H₀"
    )

    estado = (
        "VARIANZAS NO HOMOGÉNEAS"
    )

    conclusion = (
        "Existe evidencia estadística de que "
        "al menos una varianza es diferente."
    )


# ============================================================
# 13. INFORMACIÓN ADICIONAL
# ============================================================
#
# Calculamos la razón entre la mayor y menor varianza.
#
# Esto NO reemplaza el p-valor.
#
# Sirve para dimensionar la diferencia observada.
# ============================================================

varianza_maxima = resumen_df[
    "Varianza"
].max()


varianza_minima = resumen_df[
    "Varianza"
].min()


desv_maxima = resumen_df[
    "Desv. estándar"
].max()


desv_minima = resumen_df[
    "Desv. estándar"
].min()


razon_varianzas = (
    varianza_maxima
    /
    varianza_minima
)


razon_desviaciones = (
    desv_maxima
    /
    desv_minima
)


# ============================================================
# 14. MOSTRAR RESULTADOS
# ============================================================

print("=" * 80)
print("RESULTADO DE LEVENE–BROWN–FORSYTHE")
print("=" * 80)

print()

print(
    "Hipótesis nula (H₀): "
    "Todas las varianzas son iguales."
)

print()

print(
    "Hipótesis alternativa (H₁): "
    "Al menos una varianza es diferente."
)

print()

print(
    f"Nivel de significancia α = {alpha}"
)

print()

print(
    f"Estadístico = "
    f"{estadistico:.4f}"
)

print(
    f"gl₁ = {grados_libertad_1}"
)

print(
    f"gl₂ = {grados_libertad_2}"
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
    f"{razon_desviaciones:.4f}"
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
# 15. INTERPRETACIÓN DIDÁCTICA
# ============================================================

print("=" * 80)
print("INTERPRETACIÓN DIDÁCTICA")
print("=" * 80)

print()

if p_valor > alpha:

    print(
        f"Como p = {p_valor:.4f} > "
        f"α = {alpha}, no se rechaza H₀."
    )

    print()

    print(
        "No existe evidencia estadística suficiente "
        "para afirmar que las varianzas sean diferentes."
    )

    print()

    print(
        "Los grupos pueden considerarse compatibles "
        "con una variabilidad común."
    )

else:

    print(
        f"Como p = {p_valor:.4f} ≤ "
        f"α = {alpha}, se rechaza H₀."
    )

    print()

    print(
        "Existe evidencia estadística de que "
        "al menos una varianza es diferente."
    )

    print()

    print(
        "Se recomienda investigar qué grupo presenta "
        "mayor variabilidad y cuál puede ser la causa."
    )


print()

print(
    "IMPORTANTE:"
)

print(
    "La prueba de Levene–Brown–Forsythe evalúa "
    "la igualdad de las varianzas."
)

print(
    "Una diferencia estadística no significa "
    "automáticamente que exista un error en los datos."
)

print(
    "Debe evaluarse el contexto experimental."
)

print()


# ============================================================
# 16. CREAR GRÁFICA
# ============================================================
#
# La gráfica permite visualizar:
#
#     • Desviación estándar de cada grupo.
#     • Intervalo de confianza Bonferroni.
#     • Diferencias de magnitud entre grupos.
#
# La gráfica complementa, pero NO reemplaza,
# la prueba estadística.
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
# 17. POSICIONES DE LOS GRUPOS
# ============================================================

posiciones = np.arange(
    len(intervalos_df)
)


# ============================================================
# 18. GRAFICAR INTERVALOS
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
    # Línea horizontal del intervalo
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
    # Punto central = desviación estándar
    # --------------------------------------------------------

    ax.scatter(
        sd,
        i,
        s=110,
        zorder=5
    )


# ============================================================
# 19. LÍNEA DE REFERENCIA
# ============================================================

ax.axvline(
    desv_minima,
    linestyle="--",
    linewidth=1.5,
    alpha=0.6
)


# ============================================================
# 20. CONFIGURACIÓN DE EJES
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
    "Grupo",
    fontsize=12
)


# ============================================================
# 21. TÍTULOS
# ============================================================

fig.suptitle(
    "Prueba de Levene–Brown–Forsythe",
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
# 22. CUADRÍCULA
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
# 23. BORDES
# ============================================================

ax.spines[
    "top"
].set_visible(False)

ax.spines[
    "right"
].set_visible(False)


# ============================================================
# 24. PANEL DERECHO
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
# 25. INFORMACIÓN ESTADÍSTICA
# ============================================================

texto_estadistico = (

    f"Prueba\n"
    f"Levene–Brown–Forsythe\n\n"

    f"Estadístico\n"
    f"{estadistico:.4f}\n\n"

    f"gl₁\n"
    f"{grados_libertad_1}\n\n"

    f"gl₂\n"
    f"{grados_libertad_2}\n\n"

    f"p-valor\n"
    f"{p_valor:.4f}\n\n"

    f"α\n"
    f"{alpha:.2f}\n\n"

    f"Razón de varianzas\n"
    f"{razon_varianzas:.4f}\n\n"

    f"Razón de DE\n"
    f"{razon_desviaciones:.4f}"
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
# 26. CAJA DE CONCLUSIÓN
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


# ============================================================
# 27. COLOCAR CONCLUSIÓN EN LA PARTE INFERIOR
# ============================================================

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
# 28. NOTA INFERIOR
# ============================================================

fig.text(
    0.5,
    0.015,
    "⚠ La prueba evalúa la igualdad de varianzas. "
    "No se eliminaron ni modificaron resultados.",
    ha="center",
    fontsize=10,
    style="italic"
)


# ============================================================
# 29. MOSTRAR GRÁFICA
# ============================================================

plt.tight_layout(
    rect=[0, 0.05, 1, 0.94]
)


plt.show()


# ============================================================
# 30. RESUMEN FINAL
# ============================================================

print()

print("=" * 80)
print("ANÁLISIS COMPLETADO")
print("=" * 80)

print()

print(
    f"Grupos analizados: {numero_grupos}"
)

print(
    "Prueba utilizada: "
    "Levene–Brown–Forsythe"
)

print(
    "Medida central utilizada: MEDIANA"
)

print(
    f"Estadístico = {estadistico:.4f}"
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
    "La decisión final debe considerar "
    "el contexto experimental del laboratorio."
)
