# ============================================================
# PRUEBA DE NORMALIDAD DE ANDERSON-DARLING
# Versión automática y didáctica para laboratorio
#
# OBJETIVO:
# Evaluar automáticamente todas las columnas numéricas
# de una hoja de Excel para determinar si los datos son
# compatibles con una distribución normal.
#
# El programa:
#
# 1. Lee el archivo Excel
# 2. Detecta automáticamente las columnas
# 3. Convierte los datos a formato numérico
# 4. Ordena los datos
# 5. Calcula media y desviación estándar
# 6. Calcula el estadístico Anderson-Darling A²
# 7. Calcula el A² ajustado
# 8. Calcula el p-valor
# 9. Calcula el valor crítico (CV)
# 10. Toma una decisión estadística
# 11. Genera una gráfica de probabilidad normal
# 12. Repite automáticamente el proceso para cada columna
# 13. Genera un resumen final de todos los resultados
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
# En este ejemplo:
#
#        veracidad.xlsx
#
# y utilizamos la hoja:
#
#        nivel1
# ============================================================

datos_excel = pd.read_excel(
    "veracidad.xlsx",
    sheet_name="nivel1"
)


# ============================================================
# 3. IDENTIFICAR AUTOMÁTICAMENTE LAS COLUMNAS
# ============================================================
#
# Aquí NO escribimos A1, A2, A3...
#
# Python obtiene directamente los nombres de las
# columnas existentes en el Excel.
#
# Por ejemplo:
#
# A1 | A2 | A3
#
# Python detectará:
#
# ["A1", "A2", "A3"]
# ============================================================

columnas = datos_excel.columns


print("==============================================")
print("COLUMNAS DETECTADAS EN EL ARCHIVO")
print("==============================================")

for columna in columnas:
    print("-", columna)


# ============================================================
# 4. CREAR UNA LISTA PARA GUARDAR LOS RESULTADOS
# ============================================================
#
# Cada columna analizada generará un conjunto de
# resultados estadísticos.
#
# Al final construiremos una tabla resumen.
# ============================================================

resultados_finales = []


# ============================================================
# 5. RECORRER AUTOMÁTICAMENTE CADA COLUMNA
# ============================================================
#
# Esta es una de las partes más importantes del programa.
#
# Si el Excel tiene:
#
# A1
# A2
# A3
#
# el programa realizará automáticamente:
#
#       análisis de A1
#       análisis de A2
#       análisis de A3
#
# sin modificar el código.
# ============================================================

for nombre_columna in columnas:

    print("\n")
    print("==============================================")
    print(f"ANALIZANDO: {nombre_columna}")
    print("==============================================")


    # ========================================================
    # 6. CONVERTIR LA COLUMNA A NUMÉRICO
    # ========================================================
    #
    # Esto es importante porque los datos provenientes
    # de Excel pueden contener:
    #
    # - números
    # - celdas vacías
    # - textos
    # - símbolos
    #
    # errors="coerce" convierte los valores que no puedan
    # interpretarse como números en NaN.
    #
    # Después eliminamos los NaN.
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
    # 8. COMPROBAR EL TAMAÑO DE LA MUESTRA
    # ========================================================

    n = len(datos)


    print(f"Número de observaciones: {n}")


    # ========================================================
    # 9. COMPROBAR QUE EXISTAN SUFICIENTES DATOS
    # ========================================================
    #
    # Para realizar correctamente este análisis necesitamos
    # más de una observación.
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
    # Anderson-Darling trabaja con los datos ordenados:
    #
    # x(1) ≤ x(2) ≤ ... ≤ x(n)
    # ========================================================

    x = np.sort(datos)


    # ========================================================
    # 11. ESTIMAR LOS PARÁMETROS DE LA DISTRIBUCIÓN NORMAL
    # ========================================================
    #
    # Calculamos:
    #
    # Media
    # Desviación estándar muestral
    #
    # ddof=1 indica que calculamos la desviación estándar
    # muestral.
    # ========================================================

    media = np.mean(x)

    desv_est = np.std(
        x,
        ddof=1
    )


    print("\nParámetros estimados:")
    print(f"Media = {media:.6f}")
    print(f"Desv. estándar = {desv_est:.6f}")


    # ========================================================
    # 12. COMPROBAR DESVIACIÓN ESTÁNDAR
    # ========================================================
    #
    # Si todos los valores son iguales, la desviación
    # estándar será cero y no podremos estandarizar.
    # ========================================================

    if desv_est == 0:

        print(
            f"⚠️ La columna {nombre_columna} "
            "tiene desviación estándar igual a cero."
        )

        continue


    # ========================================================
    # 13. ESTANDARIZAR LOS DATOS
    # ========================================================
    #
    # Transformamos cada observación:
    #
    #              x - media
    # Z = ---------------------------
    #          desviación estándar
    #
    # De esta manera obtenemos los valores Z.
    # ========================================================

    z = (
        x - media
    ) / desv_est


    # ========================================================
    # 14. CALCULAR F(Z)
    # ========================================================
    #
    # F(Z) representa la probabilidad acumulada de una
    # distribución normal estándar:
    #
    # P(Z ≤ z)
    # ========================================================

    F = stats.norm.cdf(z)


    # ========================================================
    # 15. EVITAR PROBLEMAS CON log(0)
    # ========================================================
    #
    # Anderson-Darling utiliza logaritmos.
    #
    # Para evitar:
    #
    # log(0)
    #
    # limitamos los valores extremos.
    # ========================================================

    F = np.clip(
        F,
        1e-15,
        1 - 1e-15
    )


    # ========================================================
    # 16. CALCULAR LOS TÉRMINOS DE ANDERSON-DARLING
    # ========================================================
    #
    # Fórmula:
    #
    # A² = -N - (1/N) Σ (2i-1)
    #
    #      [ln(F(Zi)) +
    #       ln(1-F(Zn+1-i))]
    # ========================================================

    i = np.arange(
        1,
        n + 1
    )


    terminos = (
        (2 * i - 1)
        *
        (
            np.log(F)
            +
            np.log(
                1 - F[::-1]
            )
        )
    )


    # ========================================================
    # 17. CALCULAR EL ESTADÍSTICO A²
    # ========================================================

    AD = (
        -n
        -
        np.sum(terminos) / n
    )


    print("\nAnderson-Darling:")
    print(f"A² = {AD:.6f}")


    # ========================================================
    # 18. CORRECCIÓN POR TAMAÑO DE MUESTRA
    # ========================================================
    #
    # Aplicamos la corrección:
    #
    # A'² = A² ×
    #
    #       (1 + 0.75/N + 2.25/N²)
    #
    # Esta cantidad se utiliza para el cálculo del p-valor.
    # ========================================================

    AD_ajustado = (
        AD
        *
        (
            1
            +
            0.75 / n
            +
            2.25 / n**2
        )
    )


    print(
        f"A'² ajustado = {AD_ajustado:.6f}"
    )


    # ========================================================
    # 19. CALCULAR EL P-VALOR
    # ========================================================
    #
    # Utilizamos las aproximaciones correspondientes
    # al estadístico A'².
    # ========================================================

    if AD_ajustado < 0.200:

        p_valor = (
            1
            -
            np.exp(
                -13.436
                +
                101.14 * AD_ajustado
                -
                223.73 * AD_ajustado**2
            )
        )

    elif AD_ajustado < 0.340:

        p_valor = (
            1
            -
            np.exp(
                -8.318
                +
                42.796 * AD_ajustado
                -
                59.938 * AD_ajustado**2
            )
        )

    elif AD_ajustado < 0.600:

        p_valor = np.exp(
            0.9177
            -
            4.279 * AD_ajustado
            -
            1.38 * AD_ajustado**2
        )

    elif AD_ajustado <= 13:

        p_valor = np.exp(
            1.2937
            -
            5.709 * AD_ajustado
            +
            0.0186 * AD_ajustado**2
        )

    else:

        p_valor = 0.0


    # Evitamos valores fuera del intervalo [0,1]

    p_valor = np.clip(
        p_valor,
        0,
        1
    )


    print(
        f"p-valor = {p_valor:.6f}"
    )


    # ========================================================
    # 20. CALCULAR EL VALOR CRÍTICO
    # ========================================================
    #
    # Para α = 0.05:
    #
    # CV =
    #
    #       0.752
    # ---------------------------
    # 1 + 0.75/N + 2.25/N²
    # ========================================================

    CV = (
        0.752
        /
        (
            1
            +
            0.75 / n
            +
            2.25 / n**2
        )
    )


    print(
        f"Valor crítico (CV) = {CV:.6f}"
    )


    # ========================================================
    # 21. DECISIÓN MEDIANTE AD vs CV
    # ========================================================

    alpha = 0.05


    if AD > CV:

        decision_cv = "Rechazar H₀"

    else:

        decision_cv = "No rechazar H₀"


    # ========================================================
    # 22. DECISIÓN MEDIANTE P-VALOR
    # ========================================================

    if p_valor <= alpha:

        decision_p = "Rechazar H₀"

    else:

        decision_p = "No rechazar H₀"


    # ========================================================
    # 23. MOSTRAR DECISIONES
    # ========================================================

    print("\n----------------------------------------------")
    print("DECISIÓN")
    print("----------------------------------------------")

    print(f"α = {alpha}")
    print(f"AD = {AD:.6f}")
    print(f"CV = {CV:.6f}")
    print(f"p = {p_valor:.6f}")

    print(
        f"\nAD vs CV → {decision_cv}"
    )

    print(
        f"p-valor → {decision_p}"
    )


    # ========================================================
    # 24. POSICIONES DE PLOTEO
    # ========================================================
    #
    # Para construir la gráfica de probabilidad normal
    # utilizamos:
    #
    #        i - 0.375
    # P = ------------
    #        n + 0.25
    #
    # Esta fórmula permite obtener las posiciones de
    # probabilidad acumulada.
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


    porcentajes = (
        probabilidades * 100
    )


    # ========================================================
    # 25. TRANSFORMAR A ESCALA NORMAL
    # ========================================================
    #
    # El eje Y será mostrado al alumno como:
    #
    # 1, 5, 10, 20, 30, ..., 95, 99 %
    #
    # pero internamente utilizaremos los valores Z.
    # ========================================================

    y_normal = stats.norm.ppf(
        probabilidades
    )


    # ========================================================
    # 26. CONSTRUIR LA RECTA DE REFERENCIA NORMAL
    # ========================================================
    #
    # Si los datos siguen una distribución normal:
    #
    # X = Media + Desv.Est. × Z
    #
    # Esta será nuestra recta de referencia.
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
    # 27. CREAR LA FIGURA
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(11, 7)
    )


    # ========================================================
    # 28. GRAFICAR LOS DATOS
    # ========================================================

    ax.scatter(
        x,
        y_normal,
        s=65,
        alpha=0.90,
        zorder=3
    )


    # ========================================================
    # 29. GRAFICAR LA RECTA DE REFERENCIA
    # ========================================================
    #
    # La línea será roja para facilitar la comparación
    # visual con Minitab.
    # ========================================================

    ax.plot(
        x_linea,
        z_linea,
        color="red",
        linewidth=1.8,
        zorder=2
    )


    # ========================================================
    # 30. ESCALA DEL EJE Y
    # ========================================================
    #
    # Estos valores representan los porcentajes
    # acumulados de una distribución normal.
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
    # 31. LIMITES DEL EJE Y
    # ========================================================

    ax.set_ylim(
        stats.norm.ppf(0.01),
        stats.norm.ppf(0.99)
    )


    # ========================================================
    # 32. TÍTULO
    # ========================================================
    #
    # IMPORTANTE:
    #
    # nombre_columna contiene automáticamente:
    #
    # A1
    # A2
    # A3
    #
    # Por eso nunca tendremos que escribir el nombre
    # manualmente.
    # ========================================================

    ax.set_title(
        f"Gráfica de probabilidad de {nombre_columna}",
        fontsize=18,
        fontweight="bold",
        pad=28
    )


    # ========================================================
    # 33. SUBTÍTULO
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
    # 34. ETIQUETAS DE LOS EJES
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
    # 35. CUADRÍCULA
    # ========================================================

    ax.grid(
        True,
        alpha=0.25
    )


    # ========================================================
    # 36. INFORMACIÓN ESTADÍSTICA
    # ========================================================

    texto = (
        f"Media       {media:.4f}\n"
        f"Desv.Est.   {desv_est:.4f}\n"
        f"N           {n}\n"
        f"AD          {AD:.3f}\n"
        f"Valor p     {p_valor:.3f}\n"
        f"CV          {CV:.3f}"
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
    # 37. AJUSTAR LA FIGURA
    # ========================================================

    plt.tight_layout()


    # ========================================================
    # 38. MOSTRAR LA GRÁFICA
    # ========================================================

    plt.show()


    # ========================================================
    # 39. GUARDAR LOS RESULTADOS
    # ========================================================
    #
    # Guardamos los resultados de esta columna para
    # construir posteriormente una tabla resumen.
    # ========================================================

    resultados_finales.append({

        "Variable": nombre_columna,

        "N": n,

        "Media": media,

        "Desv. estándar": desv_est,

        "AD": AD,

        "AD ajustado": AD_ajustado,

        "p-valor": p_valor,

        "CV": CV,

        "Decisión AD-CV": decision_cv,

        "Decisión p-valor": decision_p

    })


# ============================================================
# 40. RESUMEN FINAL
# ============================================================
#
# Una vez analizadas todas las columnas, mostramos
# una tabla general.
# ============================================================

resumen_AD = pd.DataFrame(
    resultados_finales
)


print("\n")
print("======================================================")
print("RESUMEN GENERAL — ANDERSON-DARLING")
print("======================================================")


resumen_AD
