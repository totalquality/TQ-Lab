# ============================================================
# PRUEBA DE GRUBBS PARA DETECCIÓN DE VALORES ATÍPICOS
#
# Objetivo:
# Detectar si existe evidencia estadística de que el valor
# más pequeño o el más grande de una muestra es un valor
# atípico.
#
# El programa analiza automáticamente todas las columnas
# numéricas encontradas en el archivo Excel.
#
# IMPORTANTE:
# Grubbs está diseñado para detectar un posible valor
# atípico extremo.
#
# NO elimina ningún dato automáticamente.
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

# Archivo Excel
archivo = "veracidad.xlsx"

# Hoja que vamos a analizar
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

columnas_numericas = datos_excel.select_dtypes(
    include=np.number
).columns.tolist()


print("=" * 75)
print("PRUEBA DE GRUBBS - DETECCIÓN DE VALORES ATÍPICOS")
print("=" * 75)

print()

print(f"Archivo analizado: {archivo}")
print(f"Hoja analizada: {hoja}")
print(f"Nivel de significancia α = {alpha}")

print()

print("Variables numéricas encontradas:")
print(columnas_numericas)

print()


# ============================================================
# 5. FUNCIÓN DE GRUBBS
# ============================================================

def prueba_grubbs(datos, alpha=0.05):

    """
    Realiza la prueba bilateral de Grubbs.

    Objetivo:
    Detectar si existe evidencia de un único valor
    atípico extremo, ya sea el mínimo o el máximo.

    Devuelve:

        N
        media
        desviación estándar
        mínimo
        máximo
        G
        G crítico
        p-valor
        valor candidato
        tipo de extremo
        posición del candidato
        decisión
    """


    # --------------------------------------------------------
    # Convertir los datos a NumPy
    # --------------------------------------------------------

    datos = np.asarray(
        datos,
        dtype=float
    )


    # --------------------------------------------------------
    # Eliminar valores faltantes
    # --------------------------------------------------------

    datos = datos[
        ~np.isnan(datos)
    ]


    # --------------------------------------------------------
    # Tamaño de muestra
    # --------------------------------------------------------

    n = len(datos)


    # --------------------------------------------------------
    # Comprobar tamaño mínimo
    # --------------------------------------------------------

    if n < 3:

        raise ValueError(
            "La prueba de Grubbs requiere al menos "
            "3 observaciones."
        )


    # --------------------------------------------------------
    # Media
    # --------------------------------------------------------

    media = np.mean(
        datos
    )


    # --------------------------------------------------------
    # Desviación estándar MUESTRAL
    #
    # ddof=1:
    # utiliza la desviación estándar muestral.
    # --------------------------------------------------------

    desviacion = np.std(
        datos,
        ddof=1
    )


    # --------------------------------------------------------
    # Comprobar variabilidad
    # --------------------------------------------------------

    if desviacion == 0:

        raise ValueError(
            "No se puede realizar Grubbs porque todos "
            "los valores son iguales."
        )


    # ========================================================
    # 6. IDENTIFICAR EL VALOR MÁS EXTREMO
    # ========================================================

    # Calculamos la distancia absoluta de cada observación
    # respecto de la media.

    distancias = np.abs(
        datos - media
    )


    # Índice del valor más alejado

    indice_candidato = np.argmax(
        distancias
    )


    # Valor candidato

    valor_candidato = datos[
        indice_candidato
    ]


    # --------------------------------------------------------
    # Determinar si el candidato es mínimo o máximo
    # --------------------------------------------------------

    if valor_candidato == np.min(datos):

        tipo_extremo = "Mínimo"

    elif valor_candidato == np.max(datos):

        tipo_extremo = "Máximo"

    else:

        tipo_extremo = "Extremo"


    # ========================================================
    # 7. ESTADÍSTICO DE GRUBBS
    # ========================================================

    # G representa la distancia del valor extremo
    # respecto de la media, expresada en desviaciones
    # estándar.

    G = (
        np.abs(
            valor_candidato - media
        )
        /
        desviacion
    )


    # ========================================================
    # 8. VALOR CRÍTICO DE GRUBBS
    # ========================================================

    # Prueba bilateral:
    #
    # α / (2n)
    #
    # grados de libertad = n - 2

    t_critico = stats.t.ppf(
        1 - alpha / (2 * n),
        df=n - 2
    )


    G_critico = (
        (n - 1)
        /
        np.sqrt(n)
        *
        np.sqrt(
            t_critico**2
            /
            (
                n - 2
                +
                t_critico**2
            )
        )
    )


    # ========================================================
    # 9. CÁLCULO DEL P-VALOR
    # ========================================================

    # Transformación del estadístico G a una estadística
    # con distribución t.
    #
    # Esta es la formulación bilateral utilizada para
    # obtener el p-valor de Grubbs.

    t_grubbs = np.sqrt(
        (
            n
            * (n - 2)
            * G**2
        )
        /
        (
            (n - 1)**2
            -
            n * G**2
        )
    )


    # --------------------------------------------------------
    # p-valor bilateral
    # --------------------------------------------------------

    p_valor = (
        2
        * n
        *
        stats.t.sf(
            t_grubbs,
            df=n - 2
        )
    )


    # --------------------------------------------------------
    # El p-valor debe estar entre 0 y 1
    # --------------------------------------------------------

    p_valor = min(
        p_valor,
        1.0
    )


    # ========================================================
    # 10. DECISIÓN ESTADÍSTICA
    # ========================================================

    if p_valor <= alpha:

        decision = (
            "SE DETECTA UN POSIBLE VALOR ATÍPICO"
        )

        atipico = True

    else:

        decision = (
            "NO SE DETECTA UN VALOR ATÍPICO"
        )

        atipico = False


    # ========================================================
    # 11. DEVOLVER RESULTADOS
    # ========================================================

    return {

        "n": n,

        "media": media,

        "desviacion": desviacion,

        "minimo": np.min(datos),

        "maximo": np.max(datos),

        "G": G,

        "G_critico": G_critico,

        "p_valor": p_valor,

        "valor_candidato": valor_candidato,

        "tipo_extremo": tipo_extremo,

        "indice_candidato": indice_candidato,

        "atipico": atipico,

        "decision": decision
    }


# ============================================================
# 12. ANALIZAR AUTOMÁTICAMENTE TODAS LAS VARIABLES
# ============================================================

for nombre_columna in columnas_numericas:


    print()

    print("=" * 75)

    print(
        f"ANÁLISIS DE GRUBBS — {nombre_columna}"
    )

    print("=" * 75)


    # ========================================================
    # 13. CONVERTIR LA COLUMNA A NUMÉRICO
    # ========================================================

    datos = pd.to_numeric(
        datos_excel[nombre_columna],
        errors="coerce"
    ).dropna()


    # ========================================================
    # 14. COMPROBAR CANTIDAD DE DATOS
    # ========================================================

    if len(datos) < 3:

        print()

        print(
            "⚠️ Variable omitida."
        )

        print(
            "Grubbs requiere al menos 3 observaciones."
        )

        continue


    # ========================================================
    # 15. EJECUTAR LA PRUEBA
    # ========================================================

    resultado = prueba_grubbs(
        datos,
        alpha
    )


    # ========================================================
    # 16. MOSTRAR RESULTADOS EN TERMINAL
    # ========================================================

    print()

    print(
        f"N = {resultado['n']}"
    )

    print(
        f"Media = {resultado['media']:.4f}"
    )

    print(
        f"Desv. estándar = "
        f"{resultado['desviacion']:.4f}"
    )

    print()

    print(
        f"Mínimo = {resultado['minimo']:.4f}"
    )

    print(
        f"Máximo = {resultado['maximo']:.4f}"
    )

    print()

    print(
        f"Extremo evaluado = "
        f"{resultado['tipo_extremo']}"
    )

    print(
        f"Valor candidato = "
        f"{resultado['valor_candidato']:.4f}"
    )

    print()

    print(
        f"G = {resultado['G']:.4f}"
    )

    print(
        f"G crítico = "
        f"{resultado['G_critico']:.4f}"
    )

    print(
        f"p-valor = "
        f"{resultado['p_valor']:.4f}"
    )

    print()

    print(
        f"α = {alpha}"
    )

    print()

    print(
        resultado["decision"]
    )


    # ========================================================
    # 17. INTERPRETACIÓN
    # ========================================================

    print()

    print("Interpretación:")

    if resultado["atipico"]:

        print(
            "Existe evidencia estadística para considerar "
            f"el {resultado['tipo_extremo'].lower()} "
            f"({resultado['valor_candidato']:.4f}) "
            "como un posible valor atípico."
        )

        print()

        print(
            "⚠️ El resultado NO debe eliminarse automáticamente."
        )

        print(
            "Debe investigarse la causa del resultado."
        )

    else:

        print(
            "No existe evidencia estadística suficiente "
            "para considerar el extremo evaluado como "
            "un valor atípico."
        )


    # ========================================================
    # 18. PREPARAR DATOS PARA LA GRÁFICA
    # ========================================================

    valores = datos.values

    posiciones = np.arange(
        1,
        len(valores) + 1
    )


    # ========================================================
    # 19. CREAR FIGURA
    # ========================================================

    fig = plt.figure(
        figsize=(14, 8)
    )


    # --------------------------------------------------------
    # Crear dos áreas:
    #
    # izquierda → gráfica
    # derecha   → información estadística
    # --------------------------------------------------------

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
    # 20. GRÁFICA PRINCIPAL
    # ========================================================

    ax.scatter(
        posiciones,
        valores,
        s=110,
        alpha=0.85,
        zorder=3,
        label="Resultados"
    )


    # ========================================================
    # 21. LÍNEA DE LA MEDIA
    # ========================================================

    ax.axhline(
        resultado["media"],
        linestyle="--",
        linewidth=2,
        label="Media",
        zorder=1
    )


    # ========================================================
    # 22. POSICIÓN DEL MÍNIMO
    # ========================================================

    posicion_minimo = np.where(
        valores == resultado["minimo"]
    )[0][0] + 1


    # ========================================================
    # 23. POSICIÓN DEL MÁXIMO
    # ========================================================

    posicion_maximo = np.where(
        valores == resultado["maximo"]
    )[0][0] + 1


    # ========================================================
    # 24. MARCAR MÍNIMO
    # ========================================================

    ax.scatter(
        posicion_minimo,
        resultado["minimo"],
        s=160,
        marker="v",
        zorder=4,
        label="Mínimo"
    )


    # ========================================================
    # 25. MARCAR MÁXIMO
    # ========================================================

    ax.scatter(
        posicion_maximo,
        resultado["maximo"],
        s=160,
        marker="^",
        zorder=4,
        label="Máximo"
    )


    # ========================================================
    # 26. MARCAR CANDIDATO DE GRUBBS
    # ========================================================

    ax.scatter(
        resultado["indice_candidato"] + 1,
        resultado["valor_candidato"],
        s=320,
        facecolors="none",
        edgecolors="red",
        linewidths=3,
        zorder=6
    )


    # ========================================================
    # 27. ANOTACIÓN DEL CANDIDATO
    # ========================================================

    # Si el candidato es el mínimo, colocamos la etiqueta
    # hacia arriba y a la derecha.
    #
    # Si es el máximo, la colocamos hacia abajo y a la derecha
    # para evitar que salga de la figura.

    if resultado["tipo_extremo"] == "Mínimo":

        desplazamiento = (20, 35)

    else:

        desplazamiento = (20, -55)


    ax.annotate(
        (
            f"Candidato Grubbs\n"
            f"{resultado['valor_candidato']:.4f}"
        ),
        xy=(
            resultado["indice_candidato"] + 1,
            resultado["valor_candidato"]
        ),
        xytext=desplazamiento,
        textcoords="offset points",
        fontsize=11,
        fontweight="bold",
        color="red",
        arrowprops=dict(
            arrowstyle="->",
            linewidth=2,
            color="red"
        ),
        bbox=dict(
            boxstyle="round,pad=0.5",
            alpha=0.12
        )
    )


    # ========================================================
    # 28. TÍTULOS DE LOS EJES
    # ========================================================

    ax.set_xlabel(
        "Número de observación",
        fontsize=12
    )

    ax.set_ylabel(
        "Resultado",
        fontsize=12
    )


    # ========================================================
    # 29. TÍTULO PRINCIPAL
    # ========================================================

    fig.suptitle(
        f"Prueba de Grubbs — {nombre_columna}",
        fontsize=21,
        fontweight="bold",
        y=0.97
    )


    # Subtítulo

    ax.set_title(
        "Detección de un posible valor atípico extremo",
        fontsize=12,
        pad=12
    )


    # ========================================================
    # 30. CUADRÍCULA
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
    # 31. ELIMINAR BORDES SUPERIORES Y DERECHOS
    # ========================================================

    ax.spines["top"].set_visible(
        False
    )

    ax.spines["right"].set_visible(
        False
    )


    # ========================================================
    # 32. LEYENDA
    # ========================================================

    ax.legend(
        loc="upper right",
        frameon=True
    )


    # ========================================================
    # 33. PANEL ESTADÍSTICO
    # ========================================================

    ax_info.axis(
        "off"
    )


    # --------------------------------------------------------
    # Título del panel
    # --------------------------------------------------------

    ax_info.text(
        0.05,
        0.94,
        "RESULTADO ESTADÍSTICO",
        fontsize=14,
        fontweight="bold",
        transform=ax_info.transAxes
    )


    # --------------------------------------------------------
    # Información estadística
    # --------------------------------------------------------

    texto_estadistico = (

        f"N\n"
        f"{resultado['n']}\n\n"

        f"Media\n"
        f"{resultado['media']:.4f}\n\n"

        f"Desv. estándar\n"
        f"{resultado['desviacion']:.4f}\n\n"

        f"Mínimo\n"
        f"{resultado['minimo']:.4f}\n\n"

        f"Máximo\n"
        f"{resultado['maximo']:.4f}\n\n"

        f"G\n"
        f"{resultado['G']:.4f}\n\n"

        f"G crítico\n"
        f"{resultado['G_critico']:.4f}\n\n"

        f"p-valor\n"
        f"{resultado['p_valor']:.4f}"
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
    # 34. CAJA DE DECISIÓN
    # ========================================================

    if resultado["atipico"]:

        texto_decision = (
            "⚠ POSIBLE VALOR ATÍPICO\n\n"
            "p ≤ α\n\n"
            "Investigar antes de tomar\n"
            "cualquier decisión."
        )

    else:

        texto_decision = (
            "✓ NO SE DETECTA\n"
            "VALOR ATÍPICO\n\n"
            "p > α\n\n"
            "No existe evidencia\n"
            "estadística suficiente."
        )


    # ========================================================
    # 34. CAJA DE DECISIÓN
    # ========================================================

    if resultado["atipico"]:

        texto_decision = (
            "⚠ POSIBLE VALOR ATÍPICO\n\n"
            "p ≤ α\n\n"
            "Investigar antes de tomar\n"
            "cualquier decisión."
        )

    else:

        texto_decision = (
            "✓ NO SE DETECTA\n"
            "VALOR ATÍPICO\n\n"
            "p > α\n\n"
            "No existe evidencia\n"
            "estadística suficiente."
        )


    # --------------------------------------------------------
    # Caja de decisión
    # Colocada en la parte inferior del panel para evitar
    # cualquier solapamiento con los resultados estadísticos.
    # --------------------------------------------------------

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
    # 35. NOTA INFERIOR
    # ========================================================

    fig.text(
        0.5,
        0.015,
        "⚠ Detección estadística ≠ eliminación del resultado. "
        "Investigar la causa antes de modificar los datos.",
        ha="center",
        fontsize=10,
        style="italic"
    )


    # ========================================================
    # 36. AJUSTAR Y MOSTRAR
    # ========================================================

    plt.tight_layout(
        rect=[0, 0.04, 1, 0.94]
    )

    plt.show()


# ============================================================
# 37. FINAL DEL ANÁLISIS
# ============================================================

print()

print("=" * 75)

print(
    "ANÁLISIS DE GRUBBS COMPLETADO"
)

print("=" * 75)

print()

print(
    f"Variables analizadas: "
    f"{len(columnas_numericas)}"
)

print()

print(
    "IMPORTANTE:"
)

print(
    "La prueba identifica posibles valores atípicos."
)

print(
    "Ningún dato ha sido eliminado automáticamente."
)

print(
    "Toda observación potencialmente atípica debe ser "
    "investigada antes de tomar una decisión."
)
