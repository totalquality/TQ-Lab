# ============================================================
# COMPARACIÓN DE MEDIAS
#
# El programa detecta automáticamente cuántas columnas
# numéricas existen en el Excel.
#
#
# SI HAY 1 COLUMNA:
#
#     → t de una muestra
#     → El programa solicita un valor de referencia.
#
#
# SI HAY 2 COLUMNAS:
#
#     → El programa pregunta:
#
#       1 = t de dos muestras independientes
#       2 = t pareada
#
#
#     SI SE ELIGE t DE DOS MUESTRAS:
#
#       → Pregunta si existe homogeneidad de varianzas.
#
#       Sí → t de Student con varianzas iguales
#       No → t de Welch
#
#
# ============================================================
#
# OBJETIVO
#
# Evaluar si una media, o una diferencia de medias,
# presenta evidencia estadística de ser diferente de
# un valor de referencia o de otra media.
#
#
# NIVEL DE SIGNIFICANCIA
#
# α = 0.05
#
#
# REGLA GENERAL
#
# p > α
#     No se rechaza H0.
#
# p ≤ α
#     Se rechaza H0.
#
#
# IMPORTANTE
#
# La prueba estadística no demuestra que dos valores sean
# "exactamente iguales".
#
# Permite determinar si existe evidencia estadística
# suficiente para afirmar que son diferentes.
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

hoja = "hoja2"

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
#
# Cada columna numérica será considerada una variable
# que puede participar en el análisis.
#
# Esto permite que el programa trabaje automáticamente
# con A1, A2, A3, etc., sin tener que escribir sus nombres.
# ============================================================

columnas_numericas = datos_excel.select_dtypes(
    include=np.number
).columns.tolist()


print("=" * 80)
print("COMPARACIÓN DE MEDIAS")
print("=" * 80)

print()

print(f"Archivo: {archivo}")
print(f"Hoja: {hoja}")

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
# 5. COMPROBAR CANTIDAD DE COLUMNAS
# ============================================================

numero_columnas = len(
    columnas_numericas
)


if numero_columnas == 0:

    raise ValueError(
        "No se encontraron columnas numéricas."
    )


if numero_columnas > 2:

    raise ValueError(
        "Este script está diseñado para 1 o 2 "
        "columnas numéricas."
        "\n\nPara 3 o más grupos utilizaremos posteriormente "
        "ANOVA y pruebas no paramétricas."
    )


# ============================================================
# 6. PREPARAR LOS DATOS
# ============================================================

grupos = {}


for columna in columnas_numericas:

    datos = pd.to_numeric(
        datos_excel[columna],
        errors="coerce"
    ).dropna()

    grupos[columna] = datos


# ============================================================
# 7. FUNCIÓN PARA MOSTRAR ESTADÍSTICA DESCRIPTIVA
# ============================================================

def mostrar_descriptiva(nombre, datos):

    print("-" * 70)

    print(
        f"Variable: {nombre}"
    )

    print("-" * 70)

    print(
        f"N                 = {len(datos)}"
    )

    print(
        f"Media             = {datos.mean():.4f}"
    )

    print(
        f"Mediana           = {datos.median():.4f}"
    )

    print(
        f"Desv. estándar    = {datos.std(ddof=1):.4f}"
    )

    print(
        f"Varianza          = {datos.var(ddof=1):.4f}"
    )

    print(
        f"Mínimo            = {datos.min():.4f}"
    )

    print(
        f"Máximo            = {datos.max():.4f}"
    )

    print(
        f"Rango             = "
        f"{datos.max() - datos.min():.4f}"
    )

    print()


# ============================================================
# 8. MOSTRAR DESCRIPTIVA
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
# 9. FUNCIÓN PARA CONSTRUIR CONCLUSIÓN
# ============================================================

def obtener_conclusion(
    p_valor,
    alpha
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
# 10. FUNCIÓN PARA CREAR EL PANEL DE RESULTADOS
# ============================================================

def panel_resultados(
    ax,
    titulo,
    estadistico,
    gl,
    p_valor,
    texto_extra=""
):

    ax.axis("off")

    ax.text(
        0.05,
        0.95,
        "RESULTADO ESTADÍSTICO",
        fontsize=15,
        fontweight="bold",
        transform=ax.transAxes,
        verticalalignment="top"
    )

    texto = (

        f"{titulo}\n\n"

        f"Estadístico t\n"
        f"{estadistico:.4f}\n\n"

        f"Grados de libertad\n"
        f"{gl:.4f}\n\n"

        f"p-valor\n"
        f"{p_valor:.4f}\n\n"

        f"α = {alpha:.2f}\n\n"

        f"{texto_extra}"
    )

    ax.text(
        0.05,
        0.82,
        texto,
        fontsize=11,
        transform=ax.transAxes,
        verticalalignment="top",
        linespacing=1.2
    )


# ============================================================
# ============================================================
# CASO 1 — UNA COLUMNA
# t DE UNA MUESTRA
# ============================================================
# ============================================================

if numero_columnas == 1:

    nombre = columnas_numericas[0]

    datos = grupos[nombre]


    # ========================================================
    # SOLICITAR VALOR DE REFERENCIA
    # ========================================================

    print("=" * 80)

    print("t DE UNA MUESTRA")

    print("=" * 80)

    print()

    print(
        f"Variable seleccionada: {nombre}"
    )

    print()

    print(
        "Ingrese el valor de referencia "
        "contra el cual desea comparar la media."
    )

    print()

    referencia = float(
        input(
            "\n¿QUÉ VALOR DE REFERENCIA DESEA UTILIZAR PARA COMPARAR LA MEDIA?\n"
            "Escriba el valor de referencia: "
        )
    )


    # ========================================================
    # HIPÓTESIS
    # ========================================================

    print()

    print(
        "H₀: μ = valor de referencia"
    )

    print(
        "H₁: μ ≠ valor de referencia"
    )

    print()


    # ========================================================
    # PRUEBA t
    # ========================================================

    t_estadistico, p_valor = stats.ttest_1samp(
        datos,
        referencia
    )


    # ========================================================
    # GRADOS DE LIBERTAD
    # ========================================================

    gl = len(datos) - 1


    # ========================================================
    # INTERVALO DE CONFIANZA PARA LA MEDIA
    # ========================================================

    n = len(datos)

    media = datos.mean()

    sd = datos.std(
        ddof=1
    )

    error_estandar = (
        sd / np.sqrt(n)
    )

    t_critico = stats.t.ppf(
        1 - alpha / 2,
        gl
    )

    margen_error = (
        t_critico
        *
        error_estandar
    )

    ic_inferior = (
        media - margen_error
    )

    ic_superior = (
        media + margen_error
    )


    # ========================================================
    # CONCLUSIÓN
    # ========================================================

    decision, conclusion = (
        obtener_conclusion(
            p_valor,
            alpha
        )
    )


    # ========================================================
    # MOSTRAR RESULTADOS
    # ========================================================

    print("=" * 80)

    print("RESULTADO — t DE UNA MUESTRA")

    print("=" * 80)

    print()

    print(
        f"Valor de referencia = "
        f"{referencia:.4f}"
    )

    print()

    print(
        f"Media = {media:.4f}"
    )

    print(
        f"IC 95 % de la media = "
        f"{ic_inferior:.4f} – "
        f"{ic_superior:.4f}"
    )

    print()

    print(
        f"t = {t_estadistico:.4f}"
    )

    print(
        f"gl = {gl}"
    )

    print(
        f"p-valor = {p_valor:.4f}"
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

    if p_valor <= alpha:

        print(
            f"Como p = {p_valor:.4f} ≤ "
            f"α = {alpha}, se rechaza H₀."
        )

        print()

        print(
            "Existe evidencia estadística de que "
            "la media es diferente del valor "
            "de referencia."
        )

    else:

        print(
            f"Como p = {p_valor:.4f} > "
            f"α = {alpha}, no se rechaza H₀."
        )

        print()

        print(
            "No existe evidencia estadística "
            "suficiente para afirmar que la "
            "media sea diferente del valor "
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


    ax.errorbar(
        media,
        0,
        xerr=[
            [media - ic_inferior],
            [ic_superior - media]
        ],
        fmt="o",
        markersize=10,
        capsize=7,
        linewidth=2.5
    )


    ax.axvline(
        referencia,
        linestyle="--",
        linewidth=2,
        label="Valor de referencia"
    )


    ax.axvline(
        media,
        linestyle=":",
        linewidth=1.5,
        alpha=0.7
    )


    ax.set_yticks(
        [0]
    )

    ax.set_yticklabels(
        [nombre]
    )

    ax.set_xlabel(
        "Valor",
        fontsize=12
    )

    ax.set_title(
        "IC 95 % de la media vs. valor de referencia",
        fontsize=13,
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


    panel_resultados(
        ax_info,
        "t de una muestra",
        t_estadistico,
        gl,
        p_valor,
        (
            f"Media = {media:.4f}\n"
            f"Referencia = {referencia:.4f}\n\n"
            f"IC 95 %\n"
            f"{ic_inferior:.4f} – "
            f"{ic_superior:.4f}"
        )
    )


    fig.suptitle(
        f"Comparación de medias — {nombre}",
        fontsize=21,
        fontweight="bold",
        y=0.97
    )

    fig.text(
        0.5,
        0.015,
        "La prueba evalúa si la media poblacional "
        "es estadísticamente diferente del valor "
        "de referencia.",
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
# ============================================================
# ============================================================

elif numero_columnas == 2:

    nombre_1 = columnas_numericas[0]

    nombre_2 = columnas_numericas[1]


    print("=" * 80)

    print("DOS COLUMNAS DETECTADAS")

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
        "Seleccione el tipo de comparación:"
    )

    print()

    print(
        "1 → t de dos muestras independientes"
    )

    print(
        "2 → t pareada"
    )

    print()


    opcion = input(
        "\n¿QUÉ TIPO DE COMPARACIÓN DE MEDIAS DESEA REALIZAR?\n"
        "1 → t de dos muestras independientes\n"
        "2 → t pareada (o de las diferencias)\n"
        "\nEscriba el número de la opción elegida (1 o 2): "
    ).strip()


    # ========================================================
    # CASO 2A — t DE DOS MUESTRAS INDEPENDIENTES
    # ========================================================

    if opcion == "1":

        datos_1 = grupos[
            nombre_1
        ]

        datos_2 = grupos[
            nombre_2
        ]


        # ====================================================
        # HIPÓTESIS
        # ====================================================

        print()

        print("=" * 80)

        print("t DE DOS MUESTRAS INDEPENDIENTES")

        print("=" * 80)

        print()

        print(
            "H₀: μ₁ = μ₂"
        )

        print(
            "H₁: μ₁ ≠ μ₂"
        )

        print()


        # ====================================================
        # HOMOGENEIDAD DE VARIANZAS
        # ====================================================
        #
        # Esta decisión debe provenir de una prueba de
        # homogeneidad realizada previamente.
        #
        # Por ejemplo:
        #
        # 2 grupos:
        #     Fisher
        #
        # También pueden utilizarse pruebas robustas como
        # Levene-Brown-Forsythe.
        #
        # El usuario introduce el resultado obtenido
        # previamente.
        # ====================================================

        print("=" * 80)

        print("HOMOGENEIDAD DE VARIANZAS")

        print("=" * 80)

        print()

        print(
            "Antes de aplicar la t de dos muestras "
            "debemos conocer si las varianzas pueden "
            "considerarse homogéneas."
        )

        print()

        print(
            "Recuerde:"
        )

        print(
            "p > α  →  No se rechaza igualdad de varianzas"
        )

        print(
            "p ≤ α  →  Se rechaza igualdad de varianzas"
        )

        print()

        print(
            "¿Existe homogeneidad de varianzas?"
        )

        print()

        print(
            "S → Sí, las varianzas son homogéneas"
        )

        print(
            "N → No, las varianzas no son homogéneas"
        )

        print()

        homogeneidad = input(
            "\n¿LAS VARIANZAS DE LOS DOS GRUPOS PUEDEN CONSIDERARSE HOMOGÉNEAS?\n"
            "S → Sí, las varianzas son homogéneas\n"
            "N → No, las varianzas no son homogéneas\n"
            "\nEscriba S para Sí o N para No: "
        ).strip().upper()


        if homogeneidad not in ["S", "N"]:

            raise ValueError(
                "Debe ingresar S para Sí o N para No."
            )


        # ====================================================
        # CASO A — VARIANZAS HOMOGÉNEAS
        # ====================================================

        if homogeneidad == "S":

            print()

            print(
                "Se utilizará la t de Student "
                "con varianzas iguales."
            )

            print()

            print(
                "Las dos muestras utilizan una "
                "varianza combinada (pooled)."
            )

            print()


            # ------------------------------------------------
            # t DE STUDENT CON VARIANZAS IGUALES
            # ------------------------------------------------

            t_estadistico, p_valor = (
                stats.ttest_ind(
                    datos_1,
                    datos_2,
                    equal_var=True
                )
            )


            # ------------------------------------------------
            # TAMAÑOS MUESTRALES
            # ------------------------------------------------

            n1 = len(datos_1)

            n2 = len(datos_2)


            # ------------------------------------------------
            # VARIANZAS
            # ------------------------------------------------

            var1 = datos_1.var(
                ddof=1
            )

            var2 = datos_2.var(
                ddof=1
            )


            # ------------------------------------------------
            # VARIANZA COMBINADA
            #
            # Sp² =
            #
            # [(n1-1)S1² + (n2-1)S2²]
            # -------------------------
            #       n1+n2-2
            # ------------------------------------------------

            varianza_combinada = (

                (
                    (n1 - 1) * var1
                    +
                    (n2 - 1) * var2
                )

                /

                (
                    n1 + n2 - 2
                )
            )


            # ------------------------------------------------
            # DESVIACIÓN ESTÁNDAR COMBINADA
            # ------------------------------------------------

            sp = np.sqrt(
                varianza_combinada
            )


            # ------------------------------------------------
            # GRADOS DE LIBERTAD
            #
            # gl = n1 + n2 - 2
            # ------------------------------------------------

            gl = (
                n1
                +
                n2
                -
                2
            )


            # ------------------------------------------------
            # DIFERENCIA DE MEDIAS
            # ------------------------------------------------

            media_1 = datos_1.mean()

            media_2 = datos_2.mean()

            diferencia = (
                media_1
                -
                media_2
            )


            # ------------------------------------------------
            # ERROR ESTÁNDAR
            # ------------------------------------------------

            error_diferencia = (
                sp
                *
                np.sqrt(
                    (1 / n1)
                    +
                    (1 / n2)
                )
            )


            metodo = (
                "t de Student — "
                "varianzas iguales"
            )


        # ====================================================
        # CASO B — VARIANZAS NO HOMOGÉNEAS
        # ====================================================

        else:

            print()

            print(
                "Se utilizará la t de Welch."
            )

            print()

            print(
                "Welch no requiere asumir igualdad "
                "de varianzas."
            )

            print()


            # ------------------------------------------------
            # TAMAÑOS MUESTRALES
            # ------------------------------------------------

            n1 = len(datos_1)

            n2 = len(datos_2)


            # ------------------------------------------------
            # VARIANZAS
            # ------------------------------------------------

            var1 = datos_1.var(
                ddof=1
            )

            var2 = datos_2.var(
                ddof=1
            )


            # ------------------------------------------------
            # t DE WELCH
            # ------------------------------------------------

            t_estadistico, p_valor = (
                stats.ttest_ind(
                    datos_1,
                    datos_2,
                    equal_var=False
                )
            )


            # ------------------------------------------------
            # GRADOS DE LIBERTAD DE WELCH
            # ------------------------------------------------

            gl = (

                (
                    var1 / n1
                    +
                    var2 / n2
                ) ** 2

                /

                (
                    (
                        (var1 / n1) ** 2
                        /
                        (n1 - 1)
                    )

                    +

                    (
                        (var2 / n2) ** 2
                        /
                        (n2 - 1)
                    )
                )
            )


            # ------------------------------------------------
            # DIFERENCIA DE MEDIAS
            # ------------------------------------------------

            media_1 = datos_1.mean()

            media_2 = datos_2.mean()

            diferencia = (
                media_1
                -
                media_2
            )


            # ------------------------------------------------
            # ERROR ESTÁNDAR DE WELCH
            # ------------------------------------------------

            error_diferencia = np.sqrt(
                (
                    var1 / n1
                )
                +
                (
                    var2 / n2
                )
            )


            metodo = "t de Welch"


        # ====================================================
        # INTERVALO DE CONFIANZA DE LA DIFERENCIA
        # ====================================================

        t_critico = stats.t.ppf(
            1 - alpha / 2,
            gl
        )


        margen_error = (
            t_critico
            *
            error_diferencia
        )


        ic_inferior = (
            diferencia
            -
            margen_error
        )

        ic_superior = (
            diferencia
            +
            margen_error
        )


        # ====================================================
        # CONCLUSIÓN
        # ====================================================

        decision, conclusion = (
            obtener_conclusion(
                p_valor,
                alpha
            )
        )


        # ====================================================
        # RESULTADOS
        # ====================================================

        print("=" * 80)

        print("RESULTADO — t DE DOS MUESTRAS")

        print("=" * 80)

        print()

        print(
            f"Método utilizado: {metodo}"
        )

        print()

        print(
            f"Media {nombre_1} = "
            f"{media_1:.4f}"
        )

        print(
            f"Media {nombre_2} = "
            f"{media_2:.4f}"
        )

        print()

        print(
            f"Diferencia de medias "
            f"({nombre_1} - {nombre_2}) = "
            f"{diferencia:.4f}"
        )

        print()

        print(
            f"IC 95 % de la diferencia = "
            f"{ic_inferior:.4f} – "
            f"{ic_superior:.4f}"
        )

        print()

        print(
            f"t = {t_estadistico:.4f}"
        )

        print(
            f"gl = {gl:.4f}"
        )

        print(
            f"p-valor = {p_valor:.4f}"
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


        # ====================================================
        # INTERPRETACIÓN DIDÁCTICA
        # ====================================================

        print("=" * 80)

        print("INTERPRETACIÓN DIDÁCTICA")

        print("=" * 80)

        print()

        if homogeneidad == "S":

            print(
                "Las varianzas fueron consideradas "
                "homogéneas según la evaluación "
                "realizada previamente."
            )

            print()

            print(
                "Por ello se utilizó la t de Student "
                "con varianzas iguales."
            )

            print()

            print(
                f"Grados de libertad = "
                f"n₁ + n₂ − 2 = {gl:.0f}"
            )

        else:

            print(
                "Las varianzas no fueron consideradas "
                "homogéneas según la evaluación "
                "realizada previamente."
            )

            print()

            print(
                "Por ello se utilizó la t de Welch."
            )

            print()

            print(
                "Los grados de libertad se ajustan "
                "mediante el método de Welch-Satterthwaite."
            )

        print()

        if p_valor <= alpha:

            print(
                f"Como p = {p_valor:.4f} ≤ "
                f"α = {alpha}, se rechaza H₀."
            )

            print()

            print(
                "Existe evidencia estadística de "
                "una diferencia entre las medias."
            )

        else:

            print(
                f"Como p = {p_valor:.4f} > "
                f"α = {alpha}, no se rechaza H₀."
            )

            print()

            print(
                "No existe evidencia estadística "
                "suficiente para afirmar que "
                "las medias sean diferentes."
            )

        print()


        # ====================================================
        # GRÁFICA
        # ====================================================

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


        # ----------------------------------------------------
        # IC DE CADA MEDIA
        # ----------------------------------------------------

        nombres = [
            nombre_1,
            nombre_2
        ]

        posiciones = [
            0,
            1
        ]


        for posicion, nombre, datos in zip(
            posiciones,
            nombres,
            [datos_1, datos_2]
        ):

            n = len(datos)

            media = datos.mean()

            sd = datos.std(
                ddof=1
            )

            gl_individual = n - 1

            se = (
                sd
                /
                np.sqrt(n)
            )

            tc = stats.t.ppf(
                1 - alpha / 2,
                gl_individual
            )

            margen = (
                tc * se
            )

            inferior = (
                media - margen
            )

            superior = (
                media + margen
            )


            ax.errorbar(
                media,
                posicion,
                xerr=[
                    [media - inferior],
                    [superior - media]
                ],
                fmt="o",
                markersize=10,
                capsize=7,
                linewidth=2.5
            )


        ax.set_yticks(
            posiciones
        )

        ax.set_yticklabels(
            nombres
        )


        ax.set_xlabel(
            "Media",
            fontsize=12
        )


        ax.set_title(
            "Comparación visual de las medias",
            fontsize=13,
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


        # ----------------------------------------------------
        # PANEL DE RESULTADOS
        # ----------------------------------------------------

        panel_resultados(
            ax_info,
            metodo,
            t_estadistico,
            gl,
            p_valor,
            (
                f"Media {nombre_1} = "
                f"{media_1:.4f}\n\n"

                f"Media {nombre_2} = "
                f"{media_2:.4f}\n\n"

                f"Diferencia = "
                f"{diferencia:.4f}\n\n"

                f"IC 95 % diferencia\n"
                f"{ic_inferior:.4f} – "
                f"{ic_superior:.4f}"
            )
        )


        fig.suptitle(
            f"Comparación de medias — "
            f"{nombre_1} vs {nombre_2}",
            fontsize=21,
            fontweight="bold",
            y=0.97
        )


        fig.text(
            0.5,
            0.015,
            "IC de la diferencia: si incluye 0, "
            "no existe evidencia estadística suficiente "
            "de una diferencia entre las medias.",
            ha="center",
            fontsize=10,
            style="italic"
        )


        plt.tight_layout(
            rect=[0, 0.05, 1, 0.94]
        )

        plt.show()


    # ========================================================
    # CASO 2B — t PAREADA
    # ========================================================

    elif opcion == "2":


        # ====================================================
        # IMPORTANTE
        #
        # En una prueba pareada cada fila representa
        # una pareja.
        #
        # La homogeneidad de varianzas NO es un supuesto
        # que tengamos que evaluar para esta prueba.
        #
        # La prueba se realiza sobre las diferencias.
        # ====================================================

        datos_pareados = datos_excel[
            [nombre_1, nombre_2]
        ].copy()


        datos_pareados[
            nombre_1
        ] = pd.to_numeric(
            datos_pareados[
                nombre_1
            ],
            errors="coerce"
        )


        datos_pareados[
            nombre_2
        ] = pd.to_numeric(
            datos_pareados[
                nombre_2
            ],
            errors="coerce"
        )


        # ----------------------------------------------------
        # ELIMINAR PAREJAS INCOMPLETAS
        # ----------------------------------------------------

        datos_pareados = (
            datos_pareados
            .dropna()
        )


        datos_1 = datos_pareados[
            nombre_1
        ]

        datos_2 = datos_pareados[
            nombre_2
        ]


        # ====================================================
        # CALCULAR DIFERENCIAS
        #
        # Diferencia = Grupo 1 - Grupo 2
        # ====================================================

        diferencias = (
            datos_1
            -
            datos_2
        )


        # ====================================================
        # HIPÓTESIS
        # ====================================================

        print()

        print("=" * 80)

        print("t PAREADA")

        print("=" * 80)

        print()

        print(
            "Cada fila representa una pareja."
        )

        print()

        print(
            f"Diferencia = "
            f"{nombre_1} - {nombre_2}"
        )

        print()

        print(
            "H₀: μd = 0"
        )

        print(
            "H₁: μd ≠ 0"
        )

        print()

        print(
            "Nota: para una t pareada no se requiere "
            "la prueba de homogeneidad de varianzas."
        )

        print()


        # ====================================================
        # PRUEBA t PAREADA
        # ====================================================

        t_estadistico, p_valor = (
            stats.ttest_rel(
                datos_1,
                datos_2
            )
        )


        # ====================================================
        # ESTADÍSTICAS DE LAS DIFERENCIAS
        # ====================================================

        n = len(
            diferencias
        )

        media_diferencia = (
            diferencias.mean()
        )

        sd_diferencia = (
            diferencias.std(
                ddof=1
            )
        )

        gl = n - 1


        # ====================================================
        # IC 95 % DE LA DIFERENCIA
        # ====================================================

        error_estandar = (
            sd_diferencia
            /
            np.sqrt(n)
        )


        t_critico = stats.t.ppf(
            1 - alpha / 2,
            gl
        )


        margen_error = (
            t_critico
            *
            error_estandar
        )


        ic_inferior = (
            media_diferencia
            -
            margen_error
        )


        ic_superior = (
            media_diferencia
            +
            margen_error
        )


        # ====================================================
        # CONCLUSIÓN
        # ====================================================

        decision, conclusion = (
            obtener_conclusion(
                p_valor,
                alpha
            )
        )


        # ====================================================
        # RESULTADOS
        # ====================================================

        print("=" * 80)

        print("RESULTADO — t PAREADA")

        print("=" * 80)

        print()

        print(
            f"N de parejas = {n}"
        )

        print()

        print(
            f"Media {nombre_1} = "
            f"{datos_1.mean():.4f}"
        )

        print(
            f"Media {nombre_2} = "
            f"{datos_2.mean():.4f}"
        )

        print()

        print(
            f"Media de las diferencias = "
            f"{media_diferencia:.4f}"
        )

        print()

        print(
            f"IC 95 % de la diferencia = "
            f"{ic_inferior:.4f} – "
            f"{ic_superior:.4f}"
        )

        print()

        print(
            f"t = {t_estadistico:.4f}"
        )

        print(
            f"gl = {gl}"
        )

        print(
            f"p-valor = {p_valor:.4f}"
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


        # ====================================================
        # INTERPRETACIÓN DIDÁCTICA
        # ====================================================

        print("=" * 80)

        print("INTERPRETACIÓN DIDÁCTICA")

        print("=" * 80)

        print()

        print(
            "La prueba se realizó sobre las "
            "DIFERENCIAS de cada pareja."
        )

        print()

        print(
            f"Como p = {p_valor:.4f}"
        )

        if p_valor <= alpha:

            print(
                f"p ≤ α = {alpha}, por lo tanto "
                "se rechaza H₀."
            )

            print()

            print(
                "Existe evidencia estadística "
                "de una diferencia entre "
                "las mediciones pareadas."
            )

        else:

            print(
                f"p > α = {alpha}, por lo tanto "
                "no se rechaza H₀."
            )

            print()

            print(
                "No existe evidencia estadística "
                "suficiente para afirmar que "
                "exista una diferencia entre "
                "las mediciones pareadas."
            )

        print()


        # ====================================================
        # GRÁFICA
        # ====================================================

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


        # ----------------------------------------------------
        # LÍNEA DE AUSENCIA DE DIFERENCIA
        # ----------------------------------------------------

        ax.axvline(
            0,
            linestyle="--",
            linewidth=2,
            alpha=0.7
        )


        # ----------------------------------------------------
        # IC DE LA DIFERENCIA MEDIA
        # ----------------------------------------------------

        ax.errorbar(
            media_diferencia,
            0,
            xerr=[
                [
                    media_diferencia
                    -
                    ic_inferior
                ],

                [
                    ic_superior
                    -
                    media_diferencia
                ]
            ],
            fmt="o",
            markersize=11,
            capsize=8,
            linewidth=3
        )


        ax.set_yticks(
            [0]
        )

        ax.set_yticklabels(
            ["Diferencia"]
        )

        ax.set_xlabel(
            f"{nombre_1} − {nombre_2}",
            fontsize=12
        )

        ax.set_title(
            "IC 95 % de la diferencia media",
            fontsize=13,
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


        # ----------------------------------------------------
        # PANEL
        # ----------------------------------------------------

        panel_resultados(
            ax_info,
            "t pareada",
            t_estadistico,
            gl,
            p_valor,
            (
                f"N = {n}\n\n"

                f"Media diferencia = "
                f"{media_diferencia:.4f}\n\n"

                f"IC 95 %\n"
                f"{ic_inferior:.4f} – "
                f"{ic_superior:.4f}"
            )
        )


        fig.suptitle(
            f"Comparación pareada — "
            f"{nombre_1} vs {nombre_2}",
            fontsize=21,
            fontweight="bold",
            y=0.97
        )


        fig.text(
            0.5,
            0.015,
            "La línea vertical en 0 representa ausencia "
            "de diferencia. Si el IC 95 % incluye 0, "
            "no existe evidencia estadística suficiente "
            "de una diferencia.",
            ha="center",
            fontsize=10,
            style="italic"
        )


        plt.tight_layout(
            rect=[0, 0.05, 1, 0.94]
        )

        plt.show()


    # ========================================================
    # OPCIÓN NO VÁLIDA
    # ========================================================

    else:

        raise ValueError(
            "Debe seleccionar 1 o 2."
        )


# ============================================================
# FIN DEL PROGRAMA
# ============================================================

print()

print("=" * 80)

print("ANÁLISIS COMPLETADO")

print("=" * 80)

print()

print(
    "No se modificaron ni eliminaron "
    "resultados originales del Excel."
)

print()

print(
    "La interpretación estadística debe "
    "considerarse junto con el contexto "
    "experimental del laboratorio."
)
