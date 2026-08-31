# ============================================================
# PRUEBA DE NORMALIDAD DE LILLIEFORS
# Versión automática y didáctica para laboratorio
#
# OBJETIVO:
# Evaluar si los datos son compatibles con una
# distribución normal cuando la media y la desviación
# estándar se estiman a partir de la propia muestra.
#
# El programa:
#
# 1. Lee el archivo Excel
# 2. Detecta automáticamente las columnas
# 3. Convierte los datos a formato numérico
# 4. Elimina valores vacíos/no numéricos
# 5. Calcula estadística descriptiva
# 6. Calcula el estadístico D de Lilliefors
# 7. Calcula el p-valor
# 8. Toma una decisión estadística
# 9. Genera una gráfica de probabilidad normal
# 10. Repite automáticamente el proceso para cada columna
# 11. Genera un resumen final
# ============================================================


# ============================================================
# 1. BIBLIOTECAS
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import stats

from statsmodels.stats.diagnostic import lilliefors


# ============================================================
# 2. LEER LOS DATOS DE EXCEL
# ============================================================
#
# El archivo debe encontrarse en la misma carpeta
# donde estamos trabajando.
#
# En este ejemplo:
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
# Python obtiene directamente los nombres de las columnas.
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
# Si el Excel contiene:
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
    # errors="coerce":
    #
    # Convierte los valores que no puedan interpretarse
    # como números en NaN.
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
    # 8. TAMAÑO DE LA MUESTRA
    # ========================================================

    n = len(datos)


    print(f"Número de observaciones: {n}")


    # ========================================================
    # 9. COMPROBAR QUE EXISTAN SUFICIENTES DATOS
    # ========================================================

    if n < 5:

        print(
            f"⚠️ La columna {nombre_columna} "
            "tiene muy pocos datos para realizar "
            "esta evaluación de manera apropiada."
        )

        continue


    # ========================================================
    # 10. ORDENAR LOS DATOS
    # ========================================================
    #
    # Ordenamos los datos de menor a mayor.
    #
    # Esto también nos ayuda a comprender visualmente
    # cómo funcionan las pruebas de distribución.
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

    print(
        f"Media = {media:.6f}"
    )

    print(
        f"Desv. estándar = {desv_est:.6f}"
    )


    # ========================================================
    # 12. COMPROBAR DESVIACIÓN ESTÁNDAR
    # ========================================================

    if desv_est == 0:

        print(
            f"⚠️ La columna {nombre_columna} "
            "tiene desviación estándar igual a cero."
        )

        continue


    # ========================================================
    # 13. PRUEBA DE LILLIEFORS
    # ========================================================
    #
    # Lilliefors evalúa la diferencia máxima entre:
    #
    #   Distribución acumulada empírica
    #
    # y
    #
    #   Distribución normal estimada
    #
    # La función devuelve:
    #
    # D       → estadístico de Lilliefors
    #
    # p       → p-valor
    #
    # Usamos dist="norm" porque queremos evaluar
    # normalidad.
    # ========================================================

    D, p_valor = lilliefors(
        x,
        dist="norm"
    )


    print("\nLilliefors:")

    print(
        f"D = {D:.6f}"
    )

    print(
        f"p-valor = {p_valor:.6f}"
    )


    # ========================================================
    # 14. NIVEL DE SIGNIFICANCIA
    # ========================================================

    alpha = 0.05


    print("\nNivel de significancia:")

    print(
        f"α = {alpha}"
    )


    # ========================================================
    # 15. HIPÓTESIS
    # ========================================================
    #
    # H₀:
    #
    # Los datos son compatibles con una distribución normal.
    #
    # H₁:
    #
    # Los datos no son compatibles con una distribución
    # normal.
    # ========================================================

    print("\nHipótesis:")

    print(
        "H₀: Los datos son compatibles "
        "con una distribución normal."
    )

    print(
        "H₁: Los datos no son compatibles "
        "con una distribución normal."
    )


    # ========================================================
    # 16. DECISIÓN ESTADÍSTICA
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
    # 17. MOSTRAR LA DECISIÓN
    # ========================================================

    print("\n----------------------------------------------")
    print("DECISIÓN")
    print("----------------------------------------------")

    print(
        f"α = {alpha}"
    )

    print(
        f"D = {D:.6f}"
    )

    print(
        f"p = {p_valor:.6f}"
    )

    print(
        f"Decisión: {decision}"
    )

    print(
        f"\nInterpretación:\n{interpretacion}"
    )


    # ========================================================
    # 18. POSICIONES DE PLOTEO
    # ========================================================
    #
    # Para construir la gráfica de probabilidad normal
    # asignamos a cada observación una posición porcentual.
    #
    # Fórmula de Bernard:
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
    # 19. TRANSFORMACIÓN A ESCALA NORMAL
    # ========================================================
    #
    # Convertimos las probabilidades acumuladas a
    # puntuaciones Z.
    #
    # El alumno verá porcentajes en el eje Y.
    # ========================================================

    y_normal = stats.norm.ppf(
        probabilidades
    )


    # ========================================================
    # 20. LÍNEA DE REFERENCIA NORMAL
    # ========================================================
    #
    # Si los datos siguen aproximadamente una normal:
    #
    # X = Media + Desv.Est. × Z
    #
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
    # 21. CREAR LA FIGURA
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(11, 7)
    )


    # ========================================================
    # 22. GRAFICAR LOS DATOS
    # ========================================================

    ax.scatter(
        x,
        y_normal,
        s=65,
        alpha=0.90,
        zorder=3
    )


    # ========================================================
    # 23. GRAFICAR LA RECTA DE REFERENCIA
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
    # 24. ESCALA DEL EJE Y
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
    # 25. LIMITES DEL EJE Y
    # ========================================================

    ax.set_ylim(
        stats.norm.ppf(0.01),
        stats.norm.ppf(0.99)
    )


    # ========================================================
    # 26. TÍTULO
    # ========================================================
    #
    # El nombre de la variable procede directamente
    # del encabezado del Excel.
    #
    # Por ejemplo:
    #
    # A1 → Gráfica de probabilidad de A1
    #
    # A2 → Gráfica de probabilidad de A2
    #
    # A3 → Gráfica de probabilidad de A3
    # ========================================================

    ax.set_title(
        f"Gráfica de probabilidad de {nombre_columna}",
        fontsize=18,
        fontweight="bold",
        pad=28
    )


    # ========================================================
    # 27. SUBTÍTULO
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
    # 28. ETIQUETAS DE LOS EJES
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
    # 29. CUADRÍCULA
    # ========================================================

    ax.grid(
        True,
        alpha=0.25
    )


    # ========================================================
    # 30. INFORMACIÓN ESTADÍSTICA
    # ========================================================

    texto = (
        f"Media       {media:.4f}\n"
        f"Desv.Est.   {desv_est:.4f}\n"
        f"N           {n}\n"
        f"D           {D:.4f}\n"
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
    # 31. AJUSTAR LA FIGURA
    # ========================================================

    plt.tight_layout()


    # ========================================================
    # 32. MOSTRAR LA GRÁFICA
    # ========================================================

    plt.show()


    # ========================================================
    # 33. GUARDAR LOS RESULTADOS
    # ========================================================

    resultados_finales.append({

        "Variable": nombre_columna,

        "N": n,

        "Media": media,

        "Desv. estándar": desv_est,

        "D": D,

        "p-valor": p_valor,

        "α": alpha,

        "Decisión": decision

    })


# ============================================================
# 34. RESUMEN FINAL
# ============================================================
#
# Una vez analizadas todas las columnas, mostramos
# una tabla resumen.
# ============================================================

resumen_Lilliefors = pd.DataFrame(
    resultados_finales
)


print("\n")
print("======================================================")
print("RESUMEN GENERAL — LILLIEFORS")
print("======================================================")


resumen_Lilliefors
