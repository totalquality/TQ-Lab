# ============================================================
# PRUEBA DE NORMALIDAD DE SHAPIRO-WILK
# Versión automática y didáctica para laboratorio
#
# OBJETIVO:
# Evaluar si los datos son compatibles con una
# distribución normal.
#
# El programa:
#
# 1. Lee el archivo Excel
# 2. Detecta automáticamente las columnas
# 3. Convierte los datos a formato numérico
# 4. Elimina valores vacíos/no numéricos
# 5. Calcula el estadístico W
# 6. Calcula el p-valor
# 7. Toma una decisión estadística
# 8. Genera una gráfica de probabilidad normal
# 9. Repite automáticamente el proceso para cada columna
# 10. Genera un resumen final
# ============================================================


# ============================================================
# 1. BIBLIOTECAS
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


# ============================================================
# 2. LEER LOS DATOS DE EXCEL
# ============================================================
#
# El archivo debe encontrarse en la misma carpeta
# donde estamos trabajando.
#
# Ejemplo:
#
#       veracidad.xlsx
#
# y utilizamos la hoja:
#
#       nivel1
# ============================================================

datos_excel = pd.read_excel(
    "veracidad.xlsx",
    sheet_name="nivel1"
)


# ============================================================
# 3. IDENTIFICAR AUTOMÁTICAMENTE LAS COLUMNAS
# ============================================================
#
# NO escribimos A1, A2, A3...
#
# Python obtiene directamente los nombres de las columnas
# existentes en el Excel.
# ============================================================

columnas = datos_excel.columns


print("==============================================")
print("COLUMNAS DETECTADAS EN EL ARCHIVO")
print("==============================================")

for columna in columnas:
    print("-", columna)


# ============================================================
# 4. CREAR LISTA PARA GUARDAR LOS RESULTADOS
# ============================================================

resultados_finales = []


# ============================================================
# 5. RECORRER AUTOMÁTICAMENTE CADA COLUMNA
# ============================================================
#
# Si tenemos:
#
# A1 | A2 | A3
#
# Python realizará automáticamente:
#
#       análisis de A1
#       análisis de A2
#       análisis de A3
#
# ============================================================

for nombre_columna in columnas:

    print("\n")
    print("==============================================")
    print(f"ANALIZANDO: {nombre_columna}")
    print("==============================================")


    # ========================================================
    # 6. CONVERTIR LOS DATOS A NUMÉRICO
    # ========================================================
    #
    # Los datos pueden contener:
    #
    # - números
    # - celdas vacías
    # - textos
    #
    # errors="coerce" convierte los valores no numéricos
    # en NaN.
    #
    # Después eliminamos esos valores.
    # ========================================================

    datos = pd.to_numeric(
        datos_excel[nombre_columna],
        errors="coerce"
    ).dropna()


    # ========================================================
    # 7. CONVERTIR A NUMPY
    # ========================================================

    datos = datos.to_numpy()


    # ========================================================
    # 8. TAMAÑO DE LA MUESTRA
    # ========================================================

    n = len(datos)


    print(f"Número de observaciones: {n}")


    # ========================================================
    # 9. COMPROBAR QUE EXISTAN SUFICIENTES DATOS
    # ========================================================
    #
    # Shapiro-Wilk requiere un número suficiente de
    # observaciones para realizar la prueba.
    #
    # En esta plantilla exigimos al menos 3 datos.
    # ========================================================

    if n < 3:

        print(
            f"⚠️ La columna {nombre_columna} "
            "no tiene suficientes datos."
        )

        continue


    # ========================================================
    # 10. ORDENAR LOS DATOS
    # ========================================================
    #
    # El ordenamiento no es necesario para llamar a
    # scipy.stats.shapiro(), pero lo mostramos porque
    # ayuda al alumno a comprender la lógica de las
    # pruebas de normalidad.
    # ========================================================

    x = np.sort(datos)


    print("\nDatos ordenados:")
    print(x)


    # ========================================================
    # 11. ESTADÍSTICA DESCRIPTIVA
    # ========================================================

    media = np.mean(x)

    desv_est = np.std(
        x,
        ddof=1
    )


    print("\nParámetros descriptivos:")
    print(f"Media = {media:.6f}")
    print(f"Desv. estándar = {desv_est:.6f}")


    # ========================================================
    # 12. PRUEBA DE SHAPIRO-WILK
    # ========================================================
    #
    # scipy.stats.shapiro() devuelve dos valores:
    #
    # W       → estadístico de Shapiro-Wilk
    #
    # p       → p-valor
    #
    # La hipótesis nula es:
    #
    # H₀: Los datos son compatibles con una
    #     distribución normal.
    #
    # La hipótesis alternativa es:
    #
    # H₁: Los datos no son compatibles con una
    #     distribución normal.
    # ========================================================

    W, p_valor = stats.shapiro(x)


    print("\nShapiro-Wilk:")
    print(f"W = {W:.6f}")
    print(f"p-valor = {p_valor:.6f}")


    # ========================================================
    # 13. NIVEL DE SIGNIFICANCIA
    # ========================================================

    alpha = 0.05


    print("\nNivel de significancia:")
    print(f"α = {alpha}")


    # ========================================================
    # 14. DECISIÓN ESTADÍSTICA
    # ========================================================
    #
    # Si:
    #
    # p ≤ α
    #
    # rechazamos H₀.
    #
    # Si:
    #
    # p > α
    #
    # no rechazamos H₀.
    # ========================================================

    if p_valor <= alpha:

        decision = "Rechazar H₀"

        interpretacion = (
            "Existe evidencia estadísticamente "
            "significativa contra la normalidad."
        )

    else:

        decision = "No rechazar H₀"

        interpretacion = (
            "No existe evidencia estadísticamente "
            "significativa contra la normalidad."
        )


    # ========================================================
    # 15. MOSTRAR LA DECISIÓN
    # ========================================================

    print("\n----------------------------------------------")
    print("DECISIÓN")
    print("----------------------------------------------")

    print(f"α = {alpha}")
    print(f"W = {W:.6f}")
    print(f"p = {p_valor:.6f}")
    print(f"Decisión: {decision}")

    print(
        f"\nInterpretación:\n{interpretacion}"
    )


    # ========================================================
    # 16. POSICIONES DE PLOTEO
    # ========================================================
    #
    # Para construir la gráfica de probabilidad normal
    # necesitamos asignar a cada observación una posición
    # porcentual acumulada.
    #
    # Utilizamos la fórmula:
    #
    #        i - 0.375
    # P = ------------
    #        n + 0.25
    #
    # ========================================================

    i = np.arange(
        1,
        n + 1
    )


    probabilidades = (
        (i - 0.375)
        /
        (n + 0.25)
    )


    # ========================================================
    # 17. TRANSFORMACIÓN A ESCALA NORMAL
    # ========================================================
    #
    # Convertimos las probabilidades acumuladas a valores
    # de la distribución normal estándar.
    #
    # El eje se mostrará al alumno como porcentajes.
    # ========================================================

    y_normal = stats.norm.ppf(
        probabilidades
    )


    # ========================================================
    # 18. LÍNEA DE REFERENCIA NORMAL
    # ========================================================
    #
    # Para una distribución normal:
    #
    # X = Media + Desv.Est. × Z
    #
    # Esta ecuación permite construir la recta de referencia.
    # ========================================================

    z_linea = np.linspace(
        y_normal.min(),
        y_normal.max(),
        200
    )


    x_linea = (
        media
        +
        desv_est * z_linea
    )


    # ========================================================
    # 19. CREAR LA FIGURA
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(11, 7)
    )


    # ========================================================
    # 20. GRAFICAR LOS DATOS
    # ========================================================

    ax.scatter(
        x,
        y_normal,
        s=65,
        alpha=0.90,
        zorder=3
    )


    # ========================================================
    # 21. GRAFICAR LA RECTA DE REFERENCIA
    # ========================================================
    #
    # La recta será roja.
    # ========================================================

    ax.plot(
        x_linea,
        z_linea,
        color="red",
        linewidth=1.8,
        zorder=2
    )


    # ========================================================
    # 22. ESCALA DEL EJE Y
    # ========================================================
    #
    # Mostramos porcentajes acumulados.
    # ========================================================

    porcentajes_eje = np.array([
        1,
        5,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        95,
        99
    ])


    posiciones_eje = stats.norm.ppf(
        porcentajes_eje / 100
    )


    ax.set_yticks(
        posiciones_eje
    )


    ax.set_yticklabels(
        porcentajes_eje
    )


    # ========================================================
    # 23. LIMITES DEL EJE Y
    # ========================================================

    ax.set_ylim(
        stats.norm.ppf(0.01),
        stats.norm.ppf(0.99)
    )


    # ========================================================
    # 24. TÍTULO
    # ========================================================
    #
    # nombre_columna contiene automáticamente:
    #
    # A1
    # A2
    # A3
    #
    # Por tanto, el título coincidirá automáticamente
    # con la variable analizada.
    # ========================================================

    ax.set_title(
        f"Gráfica de probabilidad de {nombre_columna}",
        fontsize=18,
        fontweight="bold",
        pad=28
    )


    # ========================================================
    # 25. SUBTÍTULO
    # ========================================================

    ax.text(
        0.5,
        1.015,
        "Normal",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=11
    )


    # ========================================================
    # 26. ETIQUETAS DE LOS EJES
    # ========================================================

    ax.set_xlabel(
        nombre_columna,
        fontsize=12
    )


    ax.set_ylabel(
        "Porcentaje acumulado",
        fontsize=12
    )


    # ========================================================
    # 27. CUADRÍCULA
    # ========================================================

    ax.grid(
        True,
        alpha=0.25
    )


    # ========================================================
    # 28. INFORMACIÓN ESTADÍSTICA EN LA GRÁFICA
    # ========================================================

    texto = (
        f"Media       {media:.4f}\n"
        f"Desv.Est.   {desv_est:.4f}\n"
        f"N           {n}\n"
        f"W           {W:.4f}\n"
        f"Valor p     {p_valor:.4f}"
    )


    ax.text(
        1.03,
        0.95,
        texto,
        transform=ax.transAxes,
        verticalalignment="top",
        fontsize=10
    )


    # ========================================================
    # 29. AJUSTAR LA FIGURA
    # ========================================================

    plt.tight_layout()


    # ========================================================
    # 30. MOSTRAR LA GRÁFICA
    # ========================================================

    plt.show()


    # ========================================================
    # 31. GUARDAR LOS RESULTADOS
    # ========================================================

    resultados_finales.append({

        "Variable": nombre_columna,

        "N": n,

        "Media": media,

        "Desv. estándar": desv_est,

        "W": W,

        "p-valor": p_valor,

        "α": alpha,

        "Decisión": decision

    })


# ============================================================
# 32. RESUMEN FINAL
# ============================================================
#
# Después de analizar todas las columnas, construimos
# una tabla resumen.
# ============================================================

resumen_Shapiro = pd.DataFrame(
    resultados_finales
)


print("\n")
print("======================================================")
print("RESUMEN GENERAL — SHAPIRO-WILK")
print("======================================================")


resumen_Shapiro
