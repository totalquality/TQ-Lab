# ============================================================
# ANOVA DE UN FACTOR + DIAGNÓSTICO DE SUPUESTOS
# ============================================================
#
# ESTE PROGRAMA:
#
# 1. Lee automáticamente las columnas numéricas del Excel.
#
# 2. Pregunta si previamente se ha determinado que las
#    varianzas son iguales o diferentes.
#
# 3. Si las varianzas son iguales:
#       → ANOVA clásico
#       → IC 95 % de las medias
#       → Tukey
#
# 4. Si las varianzas son diferentes:
#       → ANOVA de Welch
#       → IC 95 % de las medias
#       → Games-Howell
#
# 5. Evalúa los supuestos mediante los RESIDUALES:
#
#       → Normalidad:
#          Anderson-Darling
#          Histograma de residuales
#          Gráfica Q-Q
#
#       → Homogeneidad:
#          Residuales vs. valores ajustados
#
#       → Independencia:
#          Residuales vs. orden de observación
#
# 6. Presenta:
#
#       → Estadística descriptiva
#       → Resumen del modelo
#       → ANOVA / Welch
#       → IC 95 % de cada grupo
#       → Post-hoc correspondiente
#       → Conclusión estadística
#
# ============================================================


# ============================================================
# 1. IMPORTAR LIBRERÍAS
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import stats

from statsmodels.stats.diagnostic import normal_ad
from statsmodels.formula.api import ols
import statsmodels.api as sm


# ============================================================
# 2. CONFIGURACIÓN DEL ARCHIVO
# ============================================================

archivo = "centralidad.xlsx"
hoja = "hoja3"


# ============================================================
# 3. LEER EL EXCEL
# ============================================================

print("=" * 80)
print("ANOVA DE UN FACTOR")
print("=" * 80)

print()
print("Leyendo archivo...")
print(f"Archivo : {archivo}")
print(f"Hoja    : {hoja}")

datos = pd.read_excel(
    archivo,
    sheet_name=hoja
)


# ============================================================
# 4. IDENTIFICAR AUTOMÁTICAMENTE LAS COLUMNAS NUMÉRICAS
# ============================================================

columnas_numericas = datos.select_dtypes(
    include=np.number
).columns.tolist()


if len(columnas_numericas) < 2:

    raise ValueError(
        "Se necesitan al menos 2 columnas numéricas "
        "para realizar un ANOVA."
    )


print()
print("Columnas numéricas encontradas:")

for i, columna in enumerate(
    columnas_numericas,
    start=1
):

    print(f"{i}. {columna}")


# ============================================================
# 5. PREPARAR LOS DATOS
# ============================================================
#
# Cada columna representa un grupo independiente.
#
# Ejemplo:
#
# A1 → Grupo 1
# A2 → Grupo 2
# A3 → Grupo 3
#
# ============================================================

datos_largos = []

for columna in columnas_numericas:

    valores = pd.to_numeric(
        datos[columna],
        errors="coerce"
    ).dropna()

    for valor in valores:

        datos_largos.append(
            {
                "Grupo": columna,
                "Resultado": valor
            }
        )


datos_largos = pd.DataFrame(
    datos_largos
)


# ============================================================
# 6. PREGUNTAR POR LA IGUALDAD DE VARIANZAS
# ============================================================
#
# IMPORTANTE:
#
# La prueba de igualdad de varianzas NO se vuelve a realizar
# aquí.
#
# Esa evaluación ya fue realizada previamente.
#
# Aquí simplemente indicamos al programa cuál fue el resultado
# para seleccionar el procedimiento correcto.
#
# ============================================================

print()
print("=" * 80)
print("SELECCIÓN DEL MÉTODO")
print("=" * 80)

print()
print(
    "La prueba de homogeneidad de varianzas ya debe "
    "haberse realizado previamente."
)

print()
print("Si la prueba previa indicó:")
print()
print("S → Varianzas iguales")
print("N → Varianzas diferentes")

print()

respuesta = input(
    "¿Las varianzas son iguales? [S/N]: "
).strip().upper()


if respuesta not in ["S", "N"]:

    raise ValueError(
        "Respuesta no válida. Debe ingresar S o N."
    )


varianzas_iguales = (
    respuesta == "S"
)


# ============================================================
# 7. ESTADÍSTICA DESCRIPTIVA
# ============================================================
#
# Antes del ANOVA observamos cómo se comporta cada grupo.
#
# ============================================================

print()
print("=" * 80)
print("ESTADÍSTICA DESCRIPTIVA")
print("=" * 80)


resumen = datos_largos.groupby(
    "Grupo"
)["Resultado"].agg(
    N="count",
    Media="mean",
    Mediana="median",
    Desv_Estandar="std",
    Varianza="var",
    Minimo="min",
    Maximo="max"
)


resumen["Rango"] = (
    resumen["Maximo"]
    -
    resumen["Minimo"]
)


print()
print(
    resumen.round(4)
)


# ============================================================
# 8. AJUSTAR EL MODELO
# ============================================================
#
# El modelo de un factor es:
#
# Resultado = Grupo + Error
#
# Los residuales son:
#
# Residual = Observado - Ajustado
#
# Estos residuales serán utilizados para evaluar los
# supuestos del ANOVA.
#
# ============================================================

modelo = ols(
    "Resultado ~ C(Grupo)",
    data=datos_largos
).fit()


datos_largos["Ajustado"] = (
    modelo.fittedvalues
)


datos_largos["Residual"] = (
    modelo.resid
)


residuales = datos_largos[
    "Residual"
].values


ajustados = datos_largos[
    "Ajustado"
].values


# ============================================================
# 9. NORMALIDAD DE LOS RESIDUALES
# ============================================================
#
# En ANOVA nos interesa evaluar la normalidad de los
# RESIDUALES del modelo.
#
# Prueba:
# Anderson-Darling
#
# H0:
# Los residuales siguen una distribución normal.
#
# p > 0.05:
# No se rechaza H0.
#
# p <= 0.05:
# Se rechaza H0.
#
# ============================================================

AD, p_AD = normal_ad(
    residuales
)


print()
print("=" * 80)
print("SUPUESTO 1 — NORMALIDAD DE LOS RESIDUALES")
print("=" * 80)

print()
print("Prueba de Anderson-Darling")

print()
print(f"AD       = {AD:.4f}")
print(f"p-valor  = {p_AD:.6f}")


if p_AD > 0.05:

    print()
    print("Conclusión:")
    print("NO se rechaza H0.")

    print(
        "No existe evidencia estadística suficiente "
        "para considerar no normales los residuales."
    )

else:

    print()
    print("Conclusión:")
    print("SE RECHAZA H0.")

    print(
        "Existe evidencia estadística de "
        "no normalidad en los residuales."
    )


# ============================================================
# 10. HISTOGRAMA DE RESIDUALES
# ============================================================

fig, ax = plt.subplots(
    figsize=(10, 6)
)


ax.hist(
    residuales,
    bins="auto",
    density=True,
    alpha=0.65,
    edgecolor="black"
)


# Curva normal de referencia

media_res = np.mean(
    residuales
)

sd_res = np.std(
    residuales,
    ddof=1
)


x = np.linspace(
    residuales.min(),
    residuales.max(),
    300
)


y = stats.norm.pdf(
    x,
    media_res,
    sd_res
)


ax.plot(
    x,
    y,
    linewidth=2
)


ax.axvline(
    0,
    linestyle="--",
    linewidth=1.5
)


ax.set_title(
    "Normalidad de los residuales — Histograma",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel(
    "Residual"
)

ax.set_ylabel(
    "Densidad"
)


ax.text(
    0.97,
    0.95,
    (
        f"AD = {AD:.4f}\n"
        f"p = {p_AD:.6f}\n"
        f"N = {len(residuales)}"
    ),
    transform=ax.transAxes,
    ha="right",
    va="top",
    fontsize=11
)


ax.grid(
    alpha=0.2
)


plt.tight_layout()
plt.show()


# ============================================================
# 11. GRÁFICA Q-Q DE LOS RESIDUALES
# ============================================================
#
# Los puntos deberían aproximarse a la recta.
#
# Esta gráfica complementa la prueba de Anderson-Darling.
#
# ============================================================

fig, ax = plt.subplots(
    figsize=(10, 6)
)


sm.qqplot(
    residuales,
    line="45",
    ax=ax,
    marker="o"
)


ax.set_title(
    "Gráfica Q-Q normal — Residuales",
    fontsize=16,
    fontweight="bold"
)


ax.set_xlabel(
    "Cuantiles teóricos"
)

ax.set_ylabel(
    "Cuantiles observados"
)


ax.grid(
    alpha=0.2
)


plt.tight_layout()
plt.show()


# ============================================================
# 12. HOMOGENEIDAD DE LOS RESIDUALES
# ============================================================
#
# AQUÍ NO volvemos a realizar la prueba de igualdad de
# varianzas entre A1, A2, A3.
#
# Ya fue realizada previamente.
#
# Ahora evaluamos si la variabilidad de los RESIDUALES
# permanece aproximadamente constante a lo largo de los
# valores ajustados.
#
# Esperamos:
#
# → nube aleatoria
# → dispersión aproximadamente constante
# → sin forma de embudo
# → sin patrones sistemáticos
#
# ============================================================

print()
print("=" * 80)
print("SUPUESTO 2 — HOMOGENEIDAD DE LOS RESIDUALES")
print("=" * 80)

print()
print(
    "Se analizará la gráfica de residuales "
    "vs. valores ajustados."
)

print()
print(
    "No debería observarse una forma de embudo "
    "ni un patrón sistemático."
)


fig, ax = plt.subplots(
    figsize=(10, 6)
)


ax.scatter(
    ajustados,
    residuales,
    s=55
)


ax.axhline(
    0,
    linestyle="--",
    linewidth=1.5
)


ax.set_title(
    "Residuales vs. valores ajustados",
    fontsize=16,
    fontweight="bold"
)


ax.set_xlabel(
    "Valor ajustado"
)

ax.set_ylabel(
    "Residual"
)


ax.grid(
    alpha=0.2
)


plt.tight_layout()
plt.show()


# ============================================================
# 13. INDEPENDENCIA DE LOS RESIDUALES
# ============================================================
#
# Evaluamos los residuales respecto al orden de observación.
#
# Buscamos:
#
# → ausencia de tendencia
# → ausencia de ciclos
# → ausencia de agrupamientos
#
# IMPORTANTE:
#
# Esta gráfica es un diagnóstico.
#
# La independencia depende principalmente de cómo se
# realizaron y ordenaron experimentalmente las mediciones.
#
# ============================================================

print()
print("=" * 80)
print("SUPUESTO 3 — INDEPENDENCIA")
print("=" * 80)

print()
print(
    "Se analizará la gráfica de residuales "
    "vs. orden de observación."
)


orden = np.arange(
    1,
    len(residuales) + 1
)


fig, ax = plt.subplots(
    figsize=(11, 5.5)
)


ax.plot(
    orden,
    residuales,
    marker="o",
    linewidth=1.3
)


ax.axhline(
    0,
    linestyle="--",
    linewidth=1.5
)


ax.set_title(
    "Residuales vs. orden de observación",
    fontsize=16,
    fontweight="bold"
)


ax.set_xlabel(
    "Orden de observación"
)

ax.set_ylabel(
    "Residual"
)


ax.grid(
    alpha=0.2
)


plt.tight_layout()
plt.show()


# ============================================================
# 14. RESUMEN DEL MODELO
# ============================================================
#
# Aquí presentamos información adicional que resulta muy
# útil para explicar el ANOVA.
#
# S:
# Desviación estándar residual / error estándar del modelo.
#
# R²:
# Proporción de variabilidad explicada por el factor.
#
# R² ajustado:
# Versión ajustada por el número de grupos y observaciones.
#
# ============================================================

S = np.sqrt(
    modelo.mse_resid
)


R2 = modelo.rsquared


R2_ajustado = (
    modelo.rsquared_adj
)


print()
print("=" * 80)
print("RESUMEN DEL MODELO")
print("=" * 80)

print()
print(f"S              = {S:.4f}")
print(f"R²             = {R2 * 100:.2f}%")
print(f"R² ajustado    = {R2_ajustado * 100:.2f}%")


# ============================================================
# 15. INTERVALOS DE CONFIANZA DEL 95 % PARA CADA MEDIA
# ============================================================
#
# Se presentan:
#
# Grupo
# N
# Media
# Desv. estándar
# IC 95 % inferior
# IC 95 % superior
#
# Para ANOVA clásico utilizamos el error agrupado.
#
# Para Welch utilizamos la incertidumbre de cada grupo
# individualmente.
#
# ============================================================

print()
print("=" * 80)
print("INTERVALOS DE CONFIANZA DEL 95 % PARA LAS MEDIAS")
print("=" * 80)


filas_ic = []


if varianzas_iguales:

    # --------------------------------------------------------
    # ANOVA CLÁSICO
    # --------------------------------------------------------

    mse = modelo.mse_resid

    gl_error = modelo.df_resid

    t_critico = stats.t.ppf(
        0.975,
        gl_error
    )


    for grupo in columnas_numericas:

        valores = datos_largos.loc[
            datos_largos["Grupo"] == grupo,
            "Resultado"
        ].values


        n = len(
            valores
        )

        media = np.mean(
            valores
        )


        error = np.sqrt(
            mse / n
        )


        margen = (
            t_critico
            *
            error
        )


        filas_ic.append(
            {
                "Grupo": grupo,
                "N": n,
                "Media": media,
                "Desv.Est.": np.std(
                    valores,
                    ddof=1
                ),
                "IC inferior": media - margen,
                "IC superior": media + margen
            }
        )


else:

    # --------------------------------------------------------
    # WELCH
    # --------------------------------------------------------
    #
    # Para cada grupo se utiliza su propia desviación estándar
    # y sus propios grados de libertad.
    # --------------------------------------------------------

    for grupo in columnas_numericas:

        valores = datos_largos.loc[
            datos_largos["Grupo"] == grupo,
            "Resultado"
        ].values


        n = len(
            valores
        )

        media = np.mean(
            valores
        )

        sd = np.std(
            valores,
            ddof=1
        )


        gl = n - 1


        t_critico = stats.t.ppf(
            0.975,
            gl
        )


        error = (
            sd /
            np.sqrt(n)
        )


        margen = (
            t_critico
            *
            error
        )


        filas_ic.append(
            {
                "Grupo": grupo,
                "N": n,
                "Media": media,
                "Desv.Est.": sd,
                "IC inferior": media - margen,
                "IC superior": media + margen
            }
        )


tabla_ic = pd.DataFrame(
    filas_ic
)


print()

print(
    tabla_ic.round(4).to_string(
        index=False
    )
)


# ============================================================
# 16. GRÁFICA DE INTERVALOS DE CONFIANZA
# ============================================================

fig, ax = plt.subplots(
    figsize=(10, 6)
)


posiciones = np.arange(
    len(tabla_ic)
)


medias_graf = tabla_ic[
    "Media"
].values


errores_inferiores = (
    medias_graf
    -
    tabla_ic[
        "IC inferior"
    ].values
)


errores_superiores = (
    tabla_ic[
        "IC superior"
    ].values
    -
    medias_graf
)


ax.errorbar(
    posiciones,
    medias_graf,
    yerr=[
        errores_inferiores,
        errores_superiores
    ],
    fmt="o",
    capsize=7,
    markersize=8,
    linewidth=2
)


ax.set_xticks(
    posiciones
)

ax.set_xticklabels(
    tabla_ic["Grupo"]
)


ax.set_title(
    "Intervalos de confianza del 95 % para las medias",
    fontsize=16,
    fontweight="bold"
)


ax.set_xlabel(
    "Grupo"
)

ax.set_ylabel(
    "Media del resultado"
)


ax.grid(
    axis="y",
    alpha=0.2
)


plt.tight_layout()
plt.show()


# ============================================================
# 17. ANOVA CLÁSICO O WELCH
# ============================================================

print()
print("=" * 80)
print("ANÁLISIS INFERENCIAL")
print("=" * 80)


if varianzas_iguales:

    # ========================================================
    # ANOVA CLÁSICO
    # ========================================================

    print()
    print(
        "Método seleccionado:"
    )

    print(
        "ANOVA de un factor — varianzas iguales"
    )


    tabla_anova = sm.stats.anova_lm(
        modelo,
        typ=2
    )


    print()
    print(
        tabla_anova.round(4)
    )


    F = tabla_anova.loc[
        "C(Grupo)",
        "F"
    ]


    p_anova = tabla_anova.loc[
        "C(Grupo)",
        "PR(>F)"
    ]


    gl1 = tabla_anova.loc[
        "C(Grupo)",
        "df"
    ]


    gl2 = tabla_anova.loc[
        "Residual",
        "df"
    ]


    print()
    print(
        f"F = {F:.4f}"
    )

    print(
        f"gl = ({gl1:.0f}, {gl2:.0f})"
    )

    print(
        f"p-valor = {p_anova:.6f}"
    )


else:

    # ========================================================
    # ANOVA DE WELCH
    # ========================================================

    print()
    print(
        "Método seleccionado:"
    )

    print(
        "ANOVA de Welch — varianzas diferentes"
    )


    grupos_datos = [
        datos_largos.loc[
            datos_largos["Grupo"] == grupo,
            "Resultado"
        ].values
        for grupo in columnas_numericas
    ]


    medias = np.array([
        np.mean(x)
        for x in grupos_datos
    ])


    varianzas = np.array([
        np.var(
            x,
            ddof=1
        )
        for x in grupos_datos
    ])


    ns = np.array([
        len(x)
        for x in grupos_datos
    ])


    k = len(
        grupos_datos
    )


    pesos = (
        ns /
        varianzas
    )


    media_ponderada = (
        np.sum(
            pesos * medias
        )
        /
        np.sum(
            pesos
        )
    )


    numerador = (
        np.sum(
            pesos
            *
            (
                medias
                -
                media_ponderada
            ) ** 2
        )
        /
        (k - 1)
    )


    termino = np.sum(
        (
            1
            -
            pesos /
            np.sum(pesos)
        ) ** 2
        /
        (ns - 1)
    )


    denominador = (
        1
        +
        (
            2 * (k - 2)
            /
            (k**2 - 1)
        )
        *
        termino
    )


    F_welch = (
        numerador
        /
        denominador
    )


    gl1_welch = (
        k - 1
    )


    gl2_welch = (
        (k**2 - 1)
        /
        (
            3 * termino
        )
    )


    p_welch = stats.f.sf(
        F_welch,
        gl1_welch,
        gl2_welch
    )


    F = F_welch

    p_anova = p_welch


    print()
    print(
        f"F de Welch = {F_welch:.4f}"
    )

    print(
        f"gl numerador = {gl1_welch:.4f}"
    )

    print(
        f"gl denominador = {gl2_welch:.4f}"
    )

    print(
        f"p-valor = {p_welch:.6f}"
    )


# ============================================================
# 18. CONCLUSIÓN DEL ANOVA
# ============================================================

print()
print("=" * 80)
print("CONCLUSIÓN DEL ANÁLISIS")
print("=" * 80)


if p_anova > 0.05:

    print()
    print(
        f"Como p = {p_anova:.6f} > 0.05, "
        "NO se rechaza H0."
    )

    print()
    print(
        "No existe evidencia estadística suficiente "
        "para afirmar que las medias de los grupos sean diferentes."
    )


else:

    print()
    print(
        f"Como p = {p_anova:.6f} ≤ 0.05, "
        "SE RECHAZA H0."
    )

    print()
    print(
        "Existe evidencia estadística de que "
        "al menos una de las medias es diferente."
    )


# ============================================================
# 19. PRUEBAS POST-HOC
# ============================================================
#
# IMPORTANTE:
#
# El ANOVA solamente nos dice:
#
# "Existe al menos una diferencia".
#
# No nos dice ENTRE QUÉ grupos está esa diferencia.
#
# Por eso necesitamos una comparación posterior.
#
# ------------------------------------------------------------
#
# VARIANZAS IGUALES:
#
#       → TUKEY
#
# VARIANZAS DIFERENTES:
#
#       → GAMES-HOWELL
#
# ============================================================


if p_anova <= 0.05:

    print()
    print("=" * 80)
    print("PRUEBAS POST-HOC")
    print("=" * 80)


    # ========================================================
    # TUKEY
    # ========================================================

    if varianzas_iguales:

        print()
        print(
            "Se utilizará Tukey HSD."
        )

        print()
        print(
            "Tukey permite identificar específicamente "
            "qué grupos presentan diferencias significativas."
        )


        from statsmodels.stats.multicomp import (
            pairwise_tukeyhsd
        )


        tukey = pairwise_tukeyhsd(
            endog=datos_largos[
                "Resultado"
            ],
            groups=datos_largos[
                "Grupo"
            ],
            alpha=0.05
        )


        print()
        print(tukey)


    # ========================================================
    # GAMES-HOWELL
    # ========================================================

    else:

        print()
        print(
            "Se utilizará Games-Howell."
        )

        print()
        print(
            "Games-Howell es apropiado cuando "
            "las varianzas no pueden considerarse iguales."
        )


        # ----------------------------------------------------
        # IMPLEMENTACIÓN DE GAMES-HOWELL
        # ----------------------------------------------------

        resultados_gh = []


        for i in range(
            len(columnas_numericas)
        ):

            for j in range(
                i + 1,
                len(columnas_numericas)
            ):

                grupo1 = columnas_numericas[i]
                grupo2 = columnas_numericas[j]


                x1 = datos_largos.loc[
                    datos_largos["Grupo"] == grupo1,
                    "Resultado"
                ].values


                x2 = datos_largos.loc[
                    datos_largos["Grupo"] == grupo2,
                    "Resultado"
                ].values


                n1 = len(x1)
                n2 = len(x2)


                m1 = np.mean(x1)
                m2 = np.mean(x2)


                s1 = np.var(
                    x1,
                    ddof=1
                )

                s2 = np.var(
                    x2,
                    ddof=1
                )


                diferencia = (
                    m1 - m2
                )


                error = np.sqrt(
                    (
                        s1 / n1
                    )
                    +
                    (
                        s2 / n2
                    )
                )


                # Estadístico q

                q = abs(
                    diferencia
                ) / (
                    error / np.sqrt(2)
                )


                # Grados de libertad de Welch

                numerador_gl = (
                    (
                        s1 / n1
                    )
                    +
                    (
                        s2 / n2
                    )
                ) ** 2


                denominador_gl = (
                    (
                        (
                            s1 / n1
                        ) ** 2
                        /
                        (n1 - 1)
                    )
                    +
                    (
                        (
                            s2 / n2
                        ) ** 2
                        /
                        (n2 - 1)
                    )
                )


                gl = (
                    numerador_gl
                    /
                    denominador_gl
                )


                # p-valor de Games-Howell

                p = stats.studentized_range.sf(
                    q,
                    len(columnas_numericas),
                    gl
                )


                # IC aproximado para la diferencia

                q_critico = stats.studentized_range.ppf(
                    0.95,
                    len(columnas_numericas),
                    gl
                )


                margen = (
                    q_critico
                    *
                    error
                    /
                    np.sqrt(2)
                )


                resultados_gh.append(
                    {
                        "Comparación":
                            f"{grupo1} - {grupo2}",

                        "Diferencia":
                            diferencia,

                        "IC inferior":
                            diferencia - margen,

                        "IC superior":
                            diferencia + margen,

                        "gl":
                            gl,

                        "p-valor":
                            p,

                        "Significativo":
                            "Sí"
                            if p <= 0.05
                            else "No"
                    }
                )


        tabla_gh = pd.DataFrame(
            resultados_gh
        )


        print()

        print(
            tabla_gh.round(5).to_string(
                index=False
            )
        )


else:

    print()
    print("=" * 80)
    print("PRUEBAS POST-HOC")
    print("=" * 80)

    print()
    print(
        "No se ejecutan comparaciones post-hoc porque "
        "el ANOVA no resultó significativo."
    )

    print(
        "No existe evidencia suficiente para afirmar "
        "diferencias globales entre las medias."
    )


# ============================================================
# 20. GRÁFICA DE COMPARACIONES POST-HOC
# ============================================================
#
# Cuando existen diferencias significativas, esta sección
# muestra las diferencias entre pares.
#
# ============================================================


if p_anova <= 0.05:

    if varianzas_iguales:

        # ----------------------------------------------------
        # EXTRAER RESULTADOS DE TUKEY
        # ----------------------------------------------------

        tabla_tukey = pd.DataFrame(
            data=tukey._results_table.data[1:],
            columns=tukey._results_table.data[0]
        )


        comparaciones = []

        for _, fila in tabla_tukey.iterrows():

            comparaciones.append(
                {
                    "Comparación":
                        f"{fila['group1']} - {fila['group2']}",

                    "Diferencia":
                        float(fila["meandiff"]),

                    "IC inferior":
                        float(fila["lower"]),

                    "IC superior":
                        float(fila["upper"]),

                    "p-valor":
                        float(fila["p-adj"]),

                    "Significativo":
                        "Sí"
                        if fila["reject"]
                        else "No"
                }
            )


        tabla_posthoc = pd.DataFrame(
            comparaciones
        )


    else:

        tabla_posthoc = tabla_gh


    # --------------------------------------------------------
    # GRÁFICA DE INTERVALOS DE LAS DIFERENCIAS
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )


    posiciones = np.arange(
        len(tabla_posthoc)
    )


    for i, (_, fila) in enumerate(
        tabla_posthoc.iterrows()
    ):

        inferior = fila[
            "IC inferior"
        ]

        superior = fila[
            "IC superior"
        ]

        diferencia = fila[
            "Diferencia"
        ]


        ax.plot(
            [inferior, superior],
            [i, i],
            linewidth=2
        )


        ax.plot(
            diferencia,
            i,
            marker="o",
            markersize=7
        )


    ax.axvline(
        0,
        linestyle="--",
        linewidth=1.5
    )


    ax.set_yticks(
        posiciones
    )


    ax.set_yticklabels(
        tabla_posthoc[
            "Comparación"
        ]
    )


    ax.set_title(
        "Comparaciones múltiples — Intervalos del 95 %",
        fontsize=16,
        fontweight="bold"
    )


    ax.set_xlabel(
        "Diferencia entre medias"
    )


    ax.set_ylabel(
        "Comparación"
    )


    ax.grid(
        axis="x",
        alpha=0.2
    )


    plt.tight_layout()
    plt.show()


# ============================================================
# 21. RESUMEN FINAL PARA EL ALUMNO
# ============================================================

print()
print("=" * 80)
print("RESUMEN FINAL")
print("=" * 80)

print()

print(
    f"Número de grupos = "
    f"{len(columnas_numericas)}"
)


print(
    f"Normalidad AD = "
    f"{AD:.4f}"
)


print(
    f"p normalidad = "
    f"{p_AD:.6f}"
)


if varianzas_iguales:

    print(
        "Método = ANOVA clásico"
    )

    print(
        "Post-hoc = Tukey"
    )

else:

    print(
        "Método = ANOVA de Welch"
    )

    print(
        "Post-hoc = Games-Howell"
    )


print(
    f"Estadístico = "
    f"{F:.4f}"
)


print(
    f"p-valor = "
    f"{p_anova:.6f}"
)


print()

if p_anova > 0.05:

    print(
        "Resultado: no se detectaron diferencias "
        "estadísticamente significativas entre las medias."
    )

else:

    print(
        "Resultado: se detectó evidencia de diferencias "
        "entre las medias."
    )


print()
print(
    "IMPORTANTE:"
)

print(
    "La significancia estadística no implica por sí sola "
    "importancia práctica o técnica."
)

print(
    "La decisión final debe considerar el contexto "
    "experimental y los criterios del laboratorio."
)


print()
print("=" * 80)
print("ANÁLISIS COMPLETADO")
print("=" * 80)
