# ============================================================
# Z-SCORE ROBUSTO
# CLASIFICACIÓN DE RESULTADOS
#
# Objetivo:
# Evaluar qué tan alejada se encuentra cada observación
# respecto de la MEDIANA utilizando una medida de dispersión
# ROBUSTA: el MAD.
#
# A diferencia del Z-score clásico:
#
#       Z clásico → Media + Desviación estándar
#
#       Z robusto  → Mediana + MAD
#
# Esto hace que el método sea menos sensible a valores
# extremos presentes en los propios datos.
#
#
# CRITERIO DE INTERPRETACIÓN UTILIZADO EN EL LABORATORIO
#
# |Z| ≤ 2       → SATISFACTORIO
# 2 < |Z| ≤ 3   → DUDOSO
# |Z| > 3       → INSATISFACTORIO
#
#
# IMPORTANTE:
#
# El Z-score robusto NO es una prueba de hipótesis clásica.
# Por ello, no se calcula un p-valor.
#
# Un resultado "insatisfactorio" NO significa que deba
# eliminarse automáticamente.
#
# El resultado debe investigarse conforme al procedimiento
# del laboratorio.
# ============================================================


# ============================================================
# 1. BIBLIOTECAS
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 2. CONFIGURACIÓN
# ============================================================

# Archivo Excel
archivo = "veracidad.xlsx"

# Hoja que vamos a analizar
hoja = "nivel1"


# ------------------------------------------------------------
# Límites de interpretación
# ------------------------------------------------------------

limite_satisfactorio = 2

limite_dudoso = 3


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

columnas_numericas = datos_excel.select_dtypes(
    include=np.number
).columns.tolist()


print("=" * 75)
print("Z-SCORE ROBUSTO")
print("CLASIFICACIÓN DE RESULTADOS")
print("=" * 75)

print()

print(f"Archivo analizado: {archivo}")
print(f"Hoja analizada: {hoja}")

print()

print("Criterio utilizado:")

print(
    f"|Z| ≤ {limite_satisfactorio} → SATISFACTORIO"
)

print(
    f"{limite_satisfactorio} < |Z| ≤ {limite_dudoso} → DUDOSO"
)

print(
    f"|Z| > {limite_dudoso} → INSATISFACTORIO"
)

print()

print("Variables numéricas encontradas:")

print(
    columnas_numericas
)

print()


# ============================================================
# 5. FUNCIÓN PARA CALCULAR EL Z-SCORE ROBUSTO
# ============================================================

def calcular_z_robusto(datos):

    """
    Calcula el Z-score robusto de cada observación.

    El cálculo utiliza:

        Mediana
        MAD (Median Absolute Deviation)

    Fórmula:

        Z robusto =
        0.6745 × (x - mediana) / MAD

    El signo indica la dirección:

        Z positivo → valor por encima de la mediana
        Z negativo → valor por debajo de la mediana

    Para clasificar se utiliza:

        |Z robusto|
    """


    # ========================================================
    # 6. CONVERTIR LOS DATOS A NUMPY
    # ========================================================

    datos = np.asarray(
        datos,
        dtype=float
    )


    # ========================================================
    # 7. ELIMINAR VALORES FALTANTES
    # ========================================================

    datos = datos[
        ~np.isnan(datos)
    ]


    # ========================================================
    # 8. TAMAÑO DE MUESTRA
    # ========================================================

    n = len(datos)


    if n < 3:

        raise ValueError(
            "Se requieren al menos 3 observaciones."
        )


    # ========================================================
    # 9. CALCULAR LA MEDIANA
    # ========================================================

    mediana = np.median(
        datos
    )


    # ========================================================
    # 10. CALCULAR EL MAD
    # ========================================================

    # Primero calculamos la distancia absoluta de cada
    # observación respecto de la mediana.

    desviaciones_absolutas = np.abs(
        datos - mediana
    )


    # Luego obtenemos la mediana de esas distancias.

    MAD = np.median(
        desviaciones_absolutas
    )


    # ========================================================
    # 11. COMPROBAR EL MAD
    # ========================================================

    if MAD == 0:

        raise ValueError(
            "El MAD es igual a cero. "
            "No es posible calcular el Z-score robusto "
            "con esta metodología."
        )


    # ========================================================
    # 12. CALCULAR EL Z-SCORE ROBUSTO
    # ========================================================

    z_robusto = (
        0.6745
        *
        (datos - mediana)
        /
        MAD
    )


    # ========================================================
    # 13. CALCULAR EL VALOR ABSOLUTO
    # ========================================================

    z_absoluto = np.abs(
        z_robusto
    )


    # ========================================================
    # 14. CLASIFICAR CADA OBSERVACIÓN
    # ========================================================

    clasificaciones = []


    for z in z_absoluto:

        if z <= limite_satisfactorio:

            clasificaciones.append(
                "SATISFACTORIO"
            )

        elif z <= limite_dudoso:

            clasificaciones.append(
                "DUDOSO"
            )

        else:

            clasificaciones.append(
                "INSATISFACTORIO"
            )


    # ========================================================
    # 15. IDENTIFICAR EXTREMOS BAJOS Y ALTOS
    # ========================================================

    extremos_bajos = (
        z_robusto < -limite_dudoso
    )


    extremos_altos = (
        z_robusto > limite_dudoso
    )


    # ========================================================
    # 16. CONTADORES
    # ========================================================

    cantidad_satisfactorios = sum(
        clasificacion == "SATISFACTORIO"
        for clasificacion in clasificaciones
    )


    cantidad_dudosos = sum(
        clasificacion == "DUDOSO"
        for clasificacion in clasificaciones
    )


    cantidad_insatisfactorios = sum(
        clasificacion == "INSATISFACTORIO"
        for clasificacion in clasificaciones
    )


    cantidad_extremos_bajos = np.sum(
        extremos_bajos
    )


    cantidad_extremos_altos = np.sum(
        extremos_altos
    )


    # ========================================================
    # 17. DECISIÓN GENERAL
    # ========================================================

    if cantidad_insatisfactorios > 0:

        decision = (
            "SE DETECTAN RESULTADOS "
            "INSATISFACTORIOS"
        )

        hay_insatisfactorios = True

    elif cantidad_dudosos > 0:

        decision = (
            "SE DETECTAN RESULTADOS DUDOSOS"
        )

        hay_insatisfactorios = False

    else:

        decision = (
            "TODOS LOS RESULTADOS SON SATISFACTORIOS"
        )

        hay_insatisfactorios = False


    # ========================================================
    # 18. DEVOLVER RESULTADOS
    # ========================================================

    return {

        "n": n,

        "mediana": mediana,

        "MAD": MAD,

        "z_robusto": z_robusto,

        "z_absoluto": z_absoluto,

        "clasificaciones": clasificaciones,

        "cantidad_satisfactorios":
            cantidad_satisfactorios,

        "cantidad_dudosos":
            cantidad_dudosos,

        "cantidad_insatisfactorios":
            cantidad_insatisfactorios,

        "cantidad_extremos_bajos":
            cantidad_extremos_bajos,

        "cantidad_extremos_altos":
            cantidad_extremos_altos,

        "extremos_bajos":
            extremos_bajos,

        "extremos_altos":
            extremos_altos,

        "decision":
            decision,

        "hay_insatisfactorios":
            hay_insatisfactorios
    }


# ============================================================
# 19. ANALIZAR AUTOMÁTICAMENTE TODAS LAS COLUMNAS
# ============================================================

for nombre_columna in columnas_numericas:


    print()

    print("=" * 75)

    print(
        f"ANÁLISIS Z-SCORE ROBUSTO — {nombre_columna}"
    )

    print("=" * 75)


    # ========================================================
    # 20. CONVERTIR LA COLUMNA A NUMÉRICO
    # ========================================================

    datos = pd.to_numeric(
        datos_excel[nombre_columna],
        errors="coerce"
    ).dropna()


    # ========================================================
    # 21. COMPROBAR TAMAÑO
    # ========================================================

    if len(datos) < 3:

        print()

        print(
            "⚠️ Variable omitida."
        )

        print(
            "Se requieren al menos 3 observaciones."
        )

        continue


    # ========================================================
    # 22. EJECUTAR EL ANÁLISIS
    # ========================================================

    try:

        resultado = calcular_z_robusto(
            datos
        )

    except ValueError as error:

        print()

        print(
            f"⚠️ {error}"
        )

        continue


    # ========================================================
    # 23. MOSTRAR RESULTADOS GENERALES
    # ========================================================

    print()

    print(
        f"N = {resultado['n']}"
    )

    print(
        f"Mediana = "
        f"{resultado['mediana']:.4f}"
    )

    print(
        f"MAD = "
        f"{resultado['MAD']:.4f}"
    )

    print()

    print(
        "Clasificación:"
    )

    print(
        f"Satisfactorios = "
        f"{resultado['cantidad_satisfactorios']}"
    )

    print(
        f"Dudosos = "
        f"{resultado['cantidad_dudosos']}"
    )

    print(
        f"Insatisfactorios = "
        f"{resultado['cantidad_insatisfactorios']}"
    )

    print()

    print(
        f"Extremos bajos (Z < -3) = "
        f"{resultado['cantidad_extremos_bajos']}"
    )

    print(
        f"Extremos altos (Z > +3) = "
        f"{resultado['cantidad_extremos_altos']}"
    )


    # ========================================================
    # 24. TABLA DETALLADA DE RESULTADOS
    # ========================================================

    tabla_resultados = pd.DataFrame({

        "Observación":
            np.arange(
                1,
                resultado["n"] + 1
            ),

        "Resultado":
            datos.values,

        "Z robusto":
            resultado["z_robusto"],

        "|Z|":
            resultado["z_absoluto"],

        "Clasificación":
            resultado["clasificaciones"]
    })


    print()

    print(
        "RESULTADOS INDIVIDUALES"
    )

    print()

    print(
        tabla_resultados.to_string(
            index=False,
            formatters={
                "Resultado":
                    lambda x: f"{x:.4f}",

                "Z robusto":
                    lambda x: f"{x:.4f}",

                "|Z|":
                    lambda x: f"{x:.4f}"
            }
        )
    )


    # ========================================================
    # 25. INTERPRETACIÓN
    # ========================================================

    print()

    print(
        "Interpretación:"
    )

    if resultado["cantidad_insatisfactorios"] > 0:

        print(
            "Se identificaron uno o más resultados "
            "con |Z| > 3."
        )

        print(
            "Estos resultados se clasifican como "
            "INSATISFACTORIOS."
        )

        print()

        print(
            "Debe investigarse la causa antes de "
            "tomar una decisión sobre el resultado."
        )

    elif resultado["cantidad_dudosos"] > 0:

        print(
            "Se identificaron uno o más resultados "
            "con 2 < |Z| ≤ 3."
        )

        print(
            "Estos resultados se clasifican como "
            "DUDOSOS."
        )

        print()

        print(
            "Se recomienda revisar el resultado y "
            "su posible causa."
        )

    else:

        print(
            "Todos los resultados presentan "
            "|Z| ≤ 2."
        )

        print(
            "Todos se clasifican como "
            "SATISFACTORIOS."
        )


    # ========================================================
    # 26. PREPARAR LA GRÁFICA
    # ========================================================

    posiciones = np.arange(
        1,
        resultado["n"] + 1
    )

    z = resultado[
        "z_robusto"
    ]


    # ========================================================
    # 27. CREAR FIGURA
    # ========================================================

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


    # ========================================================
    # 28. GRAFICAR TODOS LOS Z ROBUSTOS
    # ========================================================

    ax.scatter(
        posiciones,
        z,
        s=110,
        alpha=0.85,
        zorder=4
    )


    # ========================================================
    # 29. LÍNEA CENTRAL
    # ========================================================

    ax.axhline(
        0,
        linestyle="--",
        linewidth=2,
        zorder=1
    )


    # ========================================================
    # 30. LÍMITES DE SATISFACTORIO
    # ========================================================

    ax.axhline(
        +2,
        linestyle="--",
        linewidth=1.5,
        zorder=2
    )

    ax.axhline(
        -2,
        linestyle="--",
        linewidth=1.5,
        zorder=2
    )


    # ========================================================
    # 31. LÍMITES DE INSATISFACTORIO
    # ========================================================

    ax.axhline(
        +3,
        linestyle="-",
        linewidth=2,
        zorder=2
    )

    ax.axhline(
        -3,
        linestyle="-",
        linewidth=2,
        zorder=2
    )


    # ========================================================
    # 32. MARCAR RESULTADOS DUDOSOS
    # ========================================================

    mascara_dudosos = (
        (resultado["z_absoluto"] > 2)
        &
        (resultado["z_absoluto"] <= 3)
    )


    if np.any(mascara_dudosos):

        ax.scatter(
            posiciones[mascara_dudosos],
            z[mascara_dudosos],
            s=250,
            facecolors="none",
            edgecolors="orange",
            linewidths=3,
            zorder=6
        )


    # ========================================================
    # 33. MARCAR INSATISFACTORIOS
    # ========================================================

    mascara_insatisfactorios = (
        resultado["z_absoluto"] > 3
    )


    if np.any(mascara_insatisfactorios):

        ax.scatter(
            posiciones[
                mascara_insatisfactorios
            ],
            z[
                mascara_insatisfactorios
            ],
            s=300,
            facecolors="none",
            edgecolors="red",
            linewidths=3,
            zorder=7
        )


    # ========================================================
    # 34. ANOTAR RESULTADOS INSATISFACTORIOS
    # ========================================================

    indices_insatisfactorios = np.where(
        mascara_insatisfactorios
    )[0]


    for indice in indices_insatisfactorios:

        valor_z = z[indice]

        resultado_original = datos.iloc[
            indice
        ]


        if valor_z > 0:

            desplazamiento = (
                15,
                -55
            )

        else:

            desplazamiento = (
                15,
                35
            )


        ax.annotate(
            (
                f"Insatisfactorio\n"
                f"Resultado = "
                f"{resultado_original:.4f}\n"
                f"Z = {valor_z:.2f}"
            ),
            xy=(
                indice + 1,
                valor_z
            ),
            xytext=desplazamiento,
            textcoords="offset points",
            fontsize=10,
            fontweight="bold",
            color="red",
            arrowprops=dict(
                arrowstyle="->",
                linewidth=2,
                color="red"
            ),
            bbox=dict(
                boxstyle="round,pad=0.45",
                alpha=0.12
            )
        )


    # ========================================================
    # 35. TÍTULOS DE LOS EJES
    # ========================================================

    ax.set_xlabel(
        "Número de observación",
        fontsize=12
    )

    ax.set_ylabel(
        "Z-score robusto",
        fontsize=12
    )


    # ========================================================
    # 36. TÍTULO PRINCIPAL
    # ========================================================

    fig.suptitle(
        f"Z-score robusto — {nombre_columna}",
        fontsize=21,
        fontweight="bold",
        y=0.97
    )


    ax.set_title(
        "Clasificación de resultados según |Z|",
        fontsize=12,
        pad=12
    )


    # ========================================================
    # 37. ETIQUETAS DE LOS LÍMITES
    # ========================================================

    ax.text(
        resultado["n"] + 0.15,
        2,
        "+2",
        fontsize=10,
        va="center"
    )

    ax.text(
        resultado["n"] + 0.15,
        -2,
        "-2",
        fontsize=10,
        va="center"
    )

    ax.text(
        resultado["n"] + 0.15,
        3,
        "+3",
        fontsize=10,
        va="center"
    )

    ax.text(
        resultado["n"] + 0.15,
        -3,
        "-3",
        fontsize=10,
        va="center"
    )


    # ========================================================
    # 38. CUADRÍCULA
    # ========================================================

    ax.grid(
        axis="y",
        alpha=0.20,
        linestyle="-"
    )

    ax.grid(
        axis="x",
        alpha=0.08
    )


    # ========================================================
    # 39. BORDES
    # ========================================================

    ax.spines["top"].set_visible(
        False
    )

    ax.spines["right"].set_visible(
        False
    )


    # ========================================================
    # 40. PANEL ESTADÍSTICO
    # ========================================================

    ax_info.axis(
        "off"
    )


    # ========================================================
    # 41. TÍTULO DEL PANEL
    # ========================================================

    ax_info.text(
        0.05,
        0.94,
        "RESULTADO ESTADÍSTICO",
        fontsize=14,
        fontweight="bold",
        transform=ax_info.transAxes
    )


    # ========================================================
    # 42. INFORMACIÓN ESTADÍSTICA
    # ========================================================

    texto_estadistico = (

        f"N\n"
        f"{resultado['n']}\n\n"

        f"Mediana\n"
        f"{resultado['mediana']:.4f}\n\n"

        f"MAD\n"
        f"{resultado['MAD']:.4f}\n\n"

        f"Satisfactorios\n"
        f"{resultado['cantidad_satisfactorios']}\n\n"

        f"Dudosos\n"
        f"{resultado['cantidad_dudosos']}\n\n"

        f"Insatisfactorios\n"
        f"{resultado['cantidad_insatisfactorios']}"
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


    # ========================================================
    # 43. CAJA DE DECISIÓN
    # ========================================================

    if resultado["cantidad_insatisfactorios"] > 0:

        texto_decision = (
            "⚠ RESULTADOS\n"
            "INSATISFACTORIOS\n\n"
            "|Z| > 3\n\n"
            "Investigar antes de\n"
            "modificar los datos."
        )

    elif resultado["cantidad_dudosos"] > 0:

        texto_decision = (
            "⚠ RESULTADOS\n"
            "DUDOSOS\n\n"
            "2 < |Z| ≤ 3\n\n"
            "Revisar los resultados\n"
            "y su posible causa."
        )

    else:

        texto_decision = (
            "✓ RESULTADOS\n"
            "SATISFACTORIOS\n\n"
            "|Z| ≤ 2\n\n"
            "No se identifican\n"
            "resultados dudosos\n"
            "o insatisfactorios."
        )


    # ========================================================
    # 44. CAJA INFERIOR
    # ========================================================

    ax_info.text(
        0.05,
        0.015,
        texto_decision,
        fontsize=10.5,
        fontweight="bold",
        transform=ax_info.transAxes,
        verticalalignment="bottom",
        bbox=dict(
            boxstyle="round,pad=0.7",
            alpha=0.12
        )
    )


    # ========================================================
    # 45. NOTA INFERIOR
    # ========================================================

    fig.text(
        0.5,
        0.015,
        "⚠ Un resultado insatisfactorio no implica "
        "eliminarlo automáticamente. Investigar la causa "
        "antes de modificar los datos.",
        ha="center",
        fontsize=10,
        style="italic"
    )


    # ========================================================
    # 46. AJUSTAR Y MOSTRAR
    # ========================================================

    plt.tight_layout(
        rect=[0, 0.04, 1, 0.94]
    )

    plt.show()


# ============================================================
# 47. FINAL
# ============================================================

print()

print("=" * 75)

print(
    "ANÁLISIS Z-SCORE ROBUSTO COMPLETADO"
)

print("=" * 75)

print()

print(
    f"Variables analizadas: "
    f"{len(columnas_numericas)}"
)

print()

print(
    "Criterio de interpretación:"
)

print(
    f"|Z| ≤ {limite_satisfactorio} → SATISFACTORIO"
)

print(
    f"{limite_satisfactorio} < |Z| ≤ {limite_dudoso} → DUDOSO"
)

print(
    f"|Z| > {limite_dudoso} → INSATISFACTORIO"
)

print()

print(
    "IMPORTANTE:"
)

print(
    "El Z-score robusto es un método de clasificación "
    "basado en mediana y MAD."
)

print(
    "No es una prueba de hipótesis y no se calcula "
    "un p-valor."
)

print(
    "Ningún dato ha sido eliminado automáticamente."
)
