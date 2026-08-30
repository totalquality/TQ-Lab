# ============================================================
# RESUMEN ESTADÍSTICO AUTOMÁTICO
# Veracidad - Nivel 1
#
# El programa analiza automáticamente todas las columnas
# numéricas encontradas en el Excel.
#
# Para cada variable genera:
#
# 1. Histograma + distribución normal
# 2. Boxplot
# 3. Q-Q Plot
# 4. Estadística descriptiva
# 5. Intervalos de confianza
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
# 2. LECTURA DEL ARCHIVO
# ============================================================

archivo = "veracidad.xlsx"

hoja = "nivel1"

datos_excel = pd.read_excel(
    archivo,
    sheet_name=hoja
)


# ============================================================
# 3. IDENTIFICAR COLUMNAS NUMÉRICAS
# ============================================================

columnas_numericas = datos_excel.select_dtypes(
    include=np.number
).columns.tolist()


# ============================================================
# 4. FUNCIÓN PARA INTERVALO DE CONFIANZA DE LA MEDIA
# ============================================================

def ic_media(datos, confianza=0.95):

    n = len(datos)

    media = np.mean(datos)

    desv = np.std(
        datos,
        ddof=1
    )

    alpha = 1 - confianza

    error_estandar = desv / np.sqrt(n)

    t_critico = stats.t.ppf(
        1 - alpha / 2,
        df=n - 1
    )

    margen = (
        t_critico
        * error_estandar
    )

    inferior = media - margen

    superior = media + margen

    return inferior, superior


# ============================================================
# 5. FUNCIÓN PARA INTERVALO DE CONFIANZA DE LA MEDIANA
#    MÉTODO NLI
#    HETTMANSPERGER-SHEATHER
# ============================================================

def ic_mediana(datos, confianza=0.95):

    datos = np.sort(
        np.asarray(datos)
    )

    n = len(datos)

    gamma = confianza


    # --------------------------------------------------------
    # Determinar d
    # --------------------------------------------------------

    d = 0

    for candidato in range(
        1,
        n // 2 + 1
    ):

        prob = stats.binom.cdf(
            candidato - 1,
            n,
            0.5
        )

        if prob < (1 - gamma) / 2:

            d = candidato

        else:

            break


    # --------------------------------------------------------
    # Confianzas
    # --------------------------------------------------------

    gamma_d = (
        1
        -
        2 *
        stats.binom.cdf(
            d - 1,
            n,
            0.5
        )
    )

    gamma_d1 = (
        1
        -
        2 *
        stats.binom.cdf(
            d,
            n,
            0.5
        )
    )


    # --------------------------------------------------------
    # Interpolación
    # --------------------------------------------------------

    I = (
        gamma_d - gamma
    ) / (
        gamma_d - gamma_d1
    )

    lambda_nli = (
        (n - d) * I
    ) / (
        d + (n - 2 * d) * I
    )


    # --------------------------------------------------------
    # Límites
    # --------------------------------------------------------

    inferior = (
        datos[d - 1]
        +
        lambda_nli
        *
        (
            datos[d]
            -
            datos[d - 1]
        )
    )

    superior = (
        datos[n - d]
        -
        lambda_nli
        *
        (
            datos[n - d]
            -
            datos[n - d - 1]
        )
    )

    return inferior, superior


# ============================================================
# 6. RECORRER AUTOMÁTICAMENTE TODAS LAS COLUMNAS
# ============================================================

for nombre_columna in columnas_numericas:


    # ========================================================
    # CONVERTIR A NUMÉRICO
    # ========================================================

    datos = pd.to_numeric(
        datos_excel[nombre_columna],
        errors="coerce"
    ).dropna()


    # ========================================================
    # VERIFICAR CANTIDAD MÍNIMA DE DATOS
    # ========================================================

    if len(datos) < 2:

        print(
            f"Columna '{nombre_columna}' ignorada: "
            "no contiene suficientes datos numéricos."
        )

        continue


    # ========================================================
    # 7. ESTADÍSTICA DESCRIPTIVA
    # ========================================================

    n = len(datos)

    media = datos.mean()

    mediana = datos.median()

    minimo = datos.min()

    maximo = datos.max()

    rango = maximo - minimo

    desv = datos.std(
        ddof=1
    )

    varianza = datos.var(
        ddof=1
    )

    Q1 = datos.quantile(
        0.25
    )

    Q3 = datos.quantile(
        0.75
    )

    IQR = Q3 - Q1


    # ========================================================
    # 8. INTERVALOS DE CONFIANZA
    # ========================================================

    ic_media_inf, ic_media_sup = ic_media(
        datos
    )

    ic_mediana_inf, ic_mediana_sup = ic_mediana(
        datos
    )


    # ========================================================
    # 9. MOSTRAR RESULTADOS EN TERMINAL
    # ========================================================

    print("\n")

    print("=" * 60)

    print(
        f"RESUMEN ESTADÍSTICO - {nombre_columna}"
    )

    print("=" * 60)

    print(f"N:                  {n}")

    print(f"Media:              {media:.4f}")

    print(f"Mediana:            {mediana:.4f}")

    print(f"Mínimo:             {minimo:.4f}")

    print(f"Máximo:             {maximo:.4f}")

    print(f"Rango:              {rango:.4f}")

    print(f"Desv. estándar:     {desv:.4f}")

    print(f"Varianza:           {varianza:.4f}")

    print(f"Q1:                 {Q1:.4f}")

    print(f"Q3:                 {Q3:.4f}")

    print(f"IQR:                {IQR:.4f}")

    print()

    print(
        f"IC 95 % Media:      "
        f"{ic_media_inf:.4f} – {ic_media_sup:.4f}"
    )

    print(
        f"IC 95 % Mediana:    "
        f"{ic_mediana_inf:.4f} – {ic_mediana_sup:.4f}"
    )


    # ========================================================
    # 10. CREAR FIGURA
    # ========================================================

    fig = plt.figure(
        figsize=(16, 9)
    )


    fig.suptitle(
        f"Resumen estadístico — {nombre_columna}",
        fontsize=20,
        fontweight="bold",
        y=0.97
    )


    # ========================================================
    # 11. HISTOGRAMA
    # ========================================================

    ax1 = plt.subplot(
        2,
        3,
        1
    )


    limites = np.histogram_bin_edges(
        datos,
        bins="auto"
    )


    frecuencias, limites, _ = ax1.hist(
        datos,
        bins=limites,
        edgecolor="black",
        alpha=0.75
    )


    # --------------------------------------------------------
    # Curva normal
    # --------------------------------------------------------

    x = np.linspace(
        limites[0],
        limites[-1],
        500
    )


    densidad = stats.norm.pdf(
        x,
        media,
        desv
    )


    ancho = limites[1] - limites[0]


    curva = (
        densidad
        * n
        * ancho
    )


    ax1.plot(
        x,
        curva,
        color="red",
        linewidth=2.5,
        label="Distribución normal"
    )


    ax1.set_title(
        "Histograma + distribución normal",
        fontsize=13,
        fontweight="bold"
    )


    ax1.set_xlabel(
        "Resultado"
    )


    ax1.set_ylabel(
        "Frecuencia"
    )


    ax1.grid(
        True,
        alpha=0.20
    )


    ax1.legend()


    # ========================================================
    # 12. BOXPLOT
    # ========================================================

    ax2 = plt.subplot(
        2,
        3,
        2
    )


    ax2.boxplot(
        datos,
        vert=False,
        patch_artist=True
    )


    ax2.set_title(
        "Boxplot",
        fontsize=13,
        fontweight="bold"
    )


    ax2.set_xlabel(
        "Resultado"
    )


    ax2.set_yticks([])


    ax2.grid(
        True,
        axis="x",
        alpha=0.20
    )


    # ========================================================
    # 13. Q-Q PLOT
    # ========================================================

    ax3 = plt.subplot(
        2,
        3,
        3
    )


    stats.probplot(
        datos,
        dist="norm",
        plot=ax3
    )


    # --------------------------------------------------------
    # Recta de referencia en rojo
    # --------------------------------------------------------

    if len(ax3.lines) > 0:

        ax3.lines[0].set_color(
            "red"
        )

        ax3.lines[0].set_linewidth(
            2
        )


    ax3.set_title(
        "Q-Q Plot — Normal",
        fontsize=13,
        fontweight="bold"
    )


    ax3.set_xlabel(
        "Cuantiles teóricos"
    )


    ax3.set_ylabel(
        "Cuantiles observados"
    )


    ax3.grid(
        True,
        alpha=0.20
    )


    # ========================================================
    # 14. ESTADÍSTICA DESCRIPTIVA
    # ========================================================

    ax4 = plt.subplot(
        2,
        3,
        4
    )


    ax4.axis(
        "off"
    )


    # --------------------------------------------------------
    # AHORA INCLUIMOS TAMBIÉN LOS INTERVALOS DE CONFIANZA
    # --------------------------------------------------------

    texto = (

        f"N = {n}\n\n"

        f"Media = {media:.4f}\n"
        f"Mediana = {mediana:.4f}\n\n"

        f"Desv. estándar = {desv:.4f}\n"
        f"Varianza = {varianza:.4f}\n\n"

        f"Mínimo = {minimo:.4f}\n"
        f"Máximo = {maximo:.4f}\n"
        f"Rango = {rango:.4f}\n\n"

        f"Q1 = {Q1:.4f}\n"
        f"Q3 = {Q3:.4f}\n"
        f"IQR = {IQR:.4f}\n\n"

        f"IC 95 % Media\n"
        f"{ic_media_inf:.4f} – {ic_media_sup:.4f}\n\n"

        f"IC 95 % Mediana\n"
        f"{ic_mediana_inf:.4f} – {ic_mediana_sup:.4f}"
    )


    ax4.text(
        0.05,
        0.98,
        texto,
        transform=ax4.transAxes,
        fontsize=11.5,
        verticalalignment="top",
        bbox=dict(
            boxstyle="round,pad=0.8",
            alpha=0.08
        )
    )


    ax4.set_title(
        "Estadística descriptiva",
        fontsize=13,
        fontweight="bold"
    )


    # ========================================================
    # 15. INTERVALOS DE CONFIANZA
    # ========================================================

    ax5 = plt.subplot(
        2,
        3,
        5
    )


    # --------------------------------------------------------
    # MEDIA
    #
    # La colocamos ARRIBA.
    # --------------------------------------------------------

    ax5.errorbar(
        media,
        1,
        xerr=[
            [
                media - ic_media_inf
            ],
            [
                ic_media_sup - media
            ]
        ],
        fmt="o",
        markersize=8,
        capsize=7,
        linewidth=2,
        label="Media"
    )


    # --------------------------------------------------------
    # MEDIANA
    #
    # La colocamos ABAJO.
    # --------------------------------------------------------

    ax5.errorbar(
        mediana,
        0,
        xerr=[
            [
                mediana - ic_mediana_inf
            ],
            [
                ic_mediana_sup - mediana
            ]
        ],
        fmt="o",
        markersize=8,
        capsize=7,
        linewidth=2,
        label="Mediana"
    )


    # ========================================================
    # ETIQUETAS DEL EJE Y
    # ========================================================

    ax5.set_yticks(
        [0, 1]
    )


    ax5.set_yticklabels(
        [
            "Mediana",
            "Media"
        ]
    )


    ax5.set_xlabel(
        "Resultado"
    )


    ax5.set_title(
        "Intervalos de confianza del 95 %",
        fontsize=13,
        fontweight="bold"
    )


    ax5.grid(
        True,
        axis="x",
        alpha=0.20
    )


    # ========================================================
    # 16. AJUSTAR EL DISEÑO
    # ========================================================

    plt.tight_layout(
        rect=[
            0,
            0,
            1,
            0.94
        ]
    )


    # ========================================================
    # 17. MOSTRAR LA FIGURA
    # ========================================================

    plt.show()


# ============================================================
# FIN
# ============================================================

print("\n")

print("=" * 60)

print(
    "ANÁLISIS COMPLETADO"
)

print("=" * 60)

print(
    f"Variables analizadas: {len(columnas_numericas)}"
)
