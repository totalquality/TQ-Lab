# ============================================================
# VERACIDAD — CASO C.2
# Comparación entre diferentes muestras de un método candidato
# y el método de referencia
#
# FLUJO:
#   1. Detectar automáticamente todas las hojas/niveles.
#   2. En cada nivel identificar método candidato y referencia.
#   3. Calcular:
#          diferencias = candidato - referencia
#   4. Aplicar Anderson-Darling sobre las diferencias.
#   5. Si p-valor AD >= alpha:
#          diferencias normales -> t de Student pareada
#      Si p-valor AD < alpha:
#          diferencias no normales -> Wilcoxon
#   6. En ambas pruebas, el valor de referencia es 0:
#          H0: diferencia = 0
#          H1: diferencia != 0
#
# El análisis es independiente para cada nivel.
# ============================================================


# ============================================================
# 1. BIBLIOTECAS
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy import stats

try:
    from statsmodels.stats.diagnostic import normal_ad
    STATSmodels_AD = True
except ImportError:
    STATSmodels_AD = False


# ============================================================
# 2. CONFIGURACIÓN
# ============================================================

archivo = (
    r"D:\Ciencia_de_Datos\Validación de métodos químicos"
    r"\veracidad_dos_grupos.xlsx"
)

alpha = 0.05


# ============================================================
# 3. FUNCIÓN DE ANDERSON-DARLING
# ============================================================

def prueba_anderson_darling(diferencias):
    """
    Anderson-Darling para normalidad.

    Se utiliza statsmodels.normal_ad porque proporciona
    directamente:
        - estadístico AD
        - p-valor

    H0: las diferencias siguen una distribución normal.
    H1: las diferencias no siguen una distribución normal.

    Regla:
        p >= alpha -> se considera normal
        p < alpha  -> no normal
    """

    diferencias = pd.Series(diferencias).dropna().astype(float)

    if len(diferencias) < 3:
        raise ValueError(
            "No hay suficientes observaciones para evaluar "
            "la normalidad de las diferencias."
        )

    if STATSmodels_AD:
        estadistico_ad, p_valor = normal_ad(
            diferencias.to_numpy()
        )

        return (
            float(estadistico_ad),
            float(p_valor),
            "Anderson-Darling — statsmodels.normal_ad"
        )

    # --------------------------------------------------------
    # Respaldo si statsmodels no está disponible.
    # scipy.stats.anderson no entrega p-valor directamente.
    # En ese caso se devuelve el estadístico y se detiene
    # para evitar inventar un p-valor.
    # --------------------------------------------------------

    resultado = stats.anderson(
        diferencias.to_numpy(),
        dist="norm"
    )

    raise ImportError(
        "Para este script se requiere statsmodels porque "
        "el criterio de selección entre t pareada y Wilcoxon "
        "se basa en el p-valor de Anderson-Darling.\n\n"
        "Instale statsmodels en el entorno .venv con:\n"
        "python -m pip install statsmodels"
    )


# ============================================================
# 4. PREGUNTA VISIBLE PARA JUPYTER
# ============================================================

def seleccionar_columna(numero, nivel, mensaje, opciones):
    """
    Si existen más de dos columnas numéricas, permite
    seleccionar explícitamente candidato y referencia.
    """

    print("\n" + "=" * 90)
    print(f"NIVEL {numero} — {nivel}")
    print(mensaje)
    print("=" * 90)

    for i, nombre in enumerate(opciones, start=1):
        print(f"{i} → {nombre}")

    while True:
        try:
            respuesta = int(
                input(
                    "\nEscriba el número de la columna: "
                )
            )

            if 1 <= respuesta <= len(opciones):
                return opciones[respuesta - 1]

        except ValueError:
            pass

        print("Selección no válida.")


# ============================================================
# 5. GRÁFICA
# ============================================================

def grafica_c2(
    nombre_hoja,
    candidato,
    referencia,
    diferencias,
    prueba,
    estadistico_ad,
    p_ad,
    estadistico,
    p_prueba,
    media_diferencia,
    mediana_diferencia,
    ic_inferior=None,
    ic_superior=None
):

    fig = plt.figure(
        figsize=(15, 8.5),
        dpi=120
    )

    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[3.8, 1.7],
        wspace=0.10
    )

    ax = fig.add_subplot(gs[0])
    info = fig.add_subplot(gs[1])

    # --------------------------------------------------------
    # BOXPLOT DE LAS DIFERENCIAS
    # --------------------------------------------------------

    datos = diferencias.to_numpy()

    ax.boxplot(
        [datos],
        positions=[1],
        widths=0.48,
        patch_artist=True,
        medianprops={
            "linewidth": 2.4
        },
        whiskerprops={
            "linewidth": 1.6
        },
        capprops={
            "linewidth": 1.6
        },
        boxprops={
            "linewidth": 1.7
        }
    )

    # --------------------------------------------------------
    # OBSERVACIONES INDIVIDUALES
    # --------------------------------------------------------

    rng = np.random.default_rng(12345)

    jitter = rng.normal(
        0,
        0.045,
        size=len(datos)
    )

    ax.scatter(
        np.full(len(datos), 1) + jitter,
        datos,
        s=42,
        alpha=0.78,
        edgecolors="black",
        linewidths=0.45,
        zorder=3
    )

    # --------------------------------------------------------
    # LÍNEA DE REFERENCIA = 0
    # --------------------------------------------------------

    ax.axhline(
        0,
        linestyle="--",
        linewidth=2.2,
        label="Diferencia de referencia = 0"
    )

    # --------------------------------------------------------
    # MEDIA
    # --------------------------------------------------------

    ax.scatter(
        [1],
        [media_diferencia],
        marker="D",
        s=85,
        zorder=5,
        label="Media de las diferencias"
    )

    # --------------------------------------------------------
    # IC DE LA MEDIA SI SE UTILIZÓ t PAREADA
    # --------------------------------------------------------

    if (
        ic_inferior is not None
        and ic_superior is not None
    ):

        ax.plot(
            [1, 1],
            [ic_inferior, ic_superior],
            linewidth=4,
            solid_capstyle="round",
            label="IC 95 % de la diferencia"
        )

    # --------------------------------------------------------
    # FORMATO
    # --------------------------------------------------------

    ax.set_xticks([1])
    ax.set_xticklabels(
        ["Diferencias\nCandidato − Referencia"],
        fontsize=11,
        fontweight="bold"
    )

    ax.set_ylabel(
        "Diferencia",
        fontsize=12,
        fontweight="bold"
    )

    ax.set_title(
        "Distribución de las diferencias",
        fontsize=17,
        fontweight="bold",
        pad=14
    )

    ax.grid(
        axis="y",
        linestyle="--",
        linewidth=0.7,
        alpha=0.35
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(
        loc="best",
        fontsize=9.5,
        frameon=True
    )

    # --------------------------------------------------------
    # PANEL DE RESULTADOS
    # --------------------------------------------------------

    info.axis("off")

    normalidad = (
        "NORMAL"
        if p_ad >= alpha
        else
        "NO NORMAL"
    )

    resultado_final = (
        "NO SE EVIDENCIA\nDIFERENCIA"
        if p_prueba >= alpha
        else
        "SE EVIDENCIA\nDIFERENCIA"
    )

    info.text(
        0.05,
        0.96,
        "RESULTADO ESTADÍSTICO",
        fontsize=15,
        fontweight="bold",
        transform=info.transAxes,
        verticalalignment="top"
    )

    info.text(
        0.05,
        0.84,
        f"Prueba utilizada:\n{prueba}",
        fontsize=11.5,
        fontweight="bold",
        transform=info.transAxes,
        verticalalignment="top",
        linespacing=1.35
    )

    info.text(
        0.05,
        0.68,
        (
            "NORMALIDAD DE LAS DIFERENCIAS\n"
            f"AD = {estadistico_ad:.6f}\n"
            f"p-valor AD = {p_ad:.6f}\n"
            f"α = {alpha:.2f}\n"
            f"Resultado: {normalidad}"
        ),
        fontsize=10.5,
        transform=info.transAxes,
        verticalalignment="top",
        linespacing=1.35
    )

    info.text(
        0.05,
        0.44,
        (
            f"Estadístico = {estadistico:.6f}\n"
            f"p-valor = {p_prueba:.6f}\n"
            f"Referencia = 0\n"
            f"Media d = {media_diferencia:.6f}\n"
            f"Mediana d = {mediana_diferencia:.6f}"
        ),
        fontsize=10.5,
        transform=info.transAxes,
        verticalalignment="top",
        linespacing=1.35
    )

    info.text(
        0.05,
        0.20,
        resultado_final,
        fontsize=14,
        fontweight="bold",
        transform=info.transAxes,
        verticalalignment="top",
        bbox={
            "boxstyle": "round,pad=0.55",
            "alpha": 0.12
        }
    )

    fig.suptitle(
        f"VERACIDAD — C.2 — {nombre_hoja}",
        fontsize=20,
        fontweight="bold",
        y=0.97
    )

    fig.text(
        0.32,
        0.025,
        (
            "Diferencia = Método candidato − Método referencia"
            "   |   Valor de referencia = 0"
        ),
        ha="center",
        fontsize=9.5,
        style="italic"
    )

    plt.tight_layout(
        rect=[0, 0.04, 1, 0.94]
    )

    plt.show()


# ============================================================
# 6. ENCABEZADO
# ============================================================

print("\n" + "#" * 100)
print("VERACIDAD — CASO C.2")
print("COMPARACIÓN ENTRE DIFERENTES MUESTRAS")
print("MÉTODO CANDIDATO vs MÉTODO DE REFERENCIA")
print("#" * 100)

print(
    "\nRuta configurada:"
    f"\n{archivo}"
)

print(
    "\nFlujo estadístico:"
    "\n1. Diferencias = Candidato − Referencia"
    "\n2. Anderson-Darling sobre las diferencias"
    "\n3. p-valor AD >= α → t de Student pareada"
    "\n4. p-valor AD < α  → Wilcoxon"
    "\n5. Valor de referencia para las diferencias = 0"
)


# ============================================================
# 7. VERIFICAR ARCHIVO
# ============================================================

ruta = Path(archivo)

if not ruta.exists():

    print("\n" + "!" * 90)
    print("NO SE ENCONTRÓ EL ARCHIVO EN LA RUTA CONFIGURADA")
    print("!" * 90)

    raise FileNotFoundError(
        f"No se encontró:\n{archivo}\n\n"
        "Revise el nombre y la carpeta del Excel."
    )


# ============================================================
# 8. LEER TODAS LAS HOJAS
# ============================================================

datos_excel = pd.read_excel(
    archivo,
    sheet_name=None
)

print("\nHojas/niveles detectados:")

for i, nombre in enumerate(
    datos_excel.keys(),
    start=1
):
    print(f"{i} → {nombre}")


# ============================================================
# 9. PROCESAR CADA NIVEL
# ============================================================

resultados_finales = []

for numero, (nombre_hoja, hoja) in enumerate(
    datos_excel.items(),
    start=1
):

    print("\n\n")

    print("█" * 100)
    print(
        f"█   NIVEL {numero} — {nombre_hoja}"
    )
    print(
        "█   COMPARACIÓN CANDIDATO vs REFERENCIA"
    )
    print(
        "█   Las decisiones de este nivel son independientes."
    )
    print("█" * 100)

    # --------------------------------------------------------
    # IDENTIFICAR COLUMNAS NUMÉRICAS
    # --------------------------------------------------------

    columnas_numericas = (
        hoja
        .select_dtypes(include=np.number)
        .columns
        .tolist()
    )

    if len(columnas_numericas) < 2:

        raise ValueError(
            f"El nivel '{nombre_hoja}' no tiene al menos "
            "dos columnas numéricas."
        )

    print("\nColumnas numéricas detectadas:")

    for i, columna in enumerate(
        columnas_numericas,
        start=1
    ):
        print(
            f"{i} → {columna}"
        )

    # --------------------------------------------------------
    # SELECCIÓN DE COLUMNAS
    # --------------------------------------------------------

    if len(columnas_numericas) == 2:

        nombre_candidato = columnas_numericas[0]
        nombre_referencia = columnas_numericas[1]

        print(
            "\nSe detectaron exactamente dos columnas."
        )

        print(
            f"Método candidato   → {nombre_candidato}"
        )

        print(
            f"Método referencia  → {nombre_referencia}"
        )

    else:

        nombre_candidato = seleccionar_columna(
            numero,
            nombre_hoja,
            "Seleccione la columna del MÉTODO CANDIDATO:",
            columnas_numericas
        )

        columnas_restantes = [
            c
            for c in columnas_numericas
            if c != nombre_candidato
        ]

        nombre_referencia = seleccionar_columna(
            numero,
            nombre_hoja,
            "Seleccione la columna del MÉTODO DE REFERENCIA:",
            columnas_restantes
        )

    # --------------------------------------------------------
    # PREPARAR PARES
    # --------------------------------------------------------

    datos_pareados = hoja[
        [
            nombre_candidato,
            nombre_referencia
        ]
    ].copy()

    datos_pareados[
        nombre_candidato
    ] = pd.to_numeric(
        datos_pareados[
            nombre_candidato
        ],
        errors="coerce"
    )

    datos_pareados[
        nombre_referencia
    ] = pd.to_numeric(
        datos_pareados[
            nombre_referencia
        ],
        errors="coerce"
    )

    datos_pareados = (
        datos_pareados
        .dropna()
    )

    candidato = datos_pareados[
        nombre_candidato
    ]

    referencia = datos_pareados[
        nombre_referencia
    ]

    # --------------------------------------------------------
    # DIFERENCIAS
    # --------------------------------------------------------

    diferencias = (
        candidato
        -
        referencia
    )

    # --------------------------------------------------------
    # INFORMACIÓN BÁSICA
    # --------------------------------------------------------

    print("\n" + "-" * 90)
    print("CONSTRUCCIÓN DE LA VARIABLE DIFERENCIAS")
    print("-" * 90)

    print(
        f"Diferencias = {nombre_candidato} − "
        f"{nombre_referencia}"
    )

    print(
        f"N de pares = {len(diferencias)}"
    )

    print(
        f"Media de diferencias = "
        f"{diferencias.mean():.6f}"
    )

    print(
        f"Mediana de diferencias = "
        f"{diferencias.median():.6f}"
    )

    print(
        f"Desv. estándar = "
        f"{diferencias.std(ddof=1):.6f}"
    )

    # --------------------------------------------------------
    # NORMALIDAD — ANDERSON DARLING
    # --------------------------------------------------------

    print("\n" + "=" * 90)
    print("PASO 1 — NORMALIDAD DE LAS DIFERENCIAS")
    print("=" * 90)

    print(
        "\nH₀: Las diferencias siguen una distribución normal."
    )

    print(
        "H₁: Las diferencias no siguen una distribución normal."
    )

    estadistico_ad, p_ad, metodo_ad = (
        prueba_anderson_darling(
            diferencias
        )
    )

    es_normal = (
        p_ad >= alpha
    )

    print(
        f"\nMétodo: {metodo_ad}"
    )

    print(
        f"Estadístico AD = {estadistico_ad:.6f}"
    )

    print(
        f"p-valor AD = {p_ad:.6f}"
    )

    print(
        f"α = {alpha:.2f}"
    )

    if es_normal:

        print(
            "\nDECISIÓN AD: NO SE RECHAZA H₀"
        )

        print(
            "Las diferencias se consideran normales."
        )

        print(
            "→ Se utilizará t de Student pareada."
        )

    else:

        print(
            "\nDECISIÓN AD: SE RECHAZA H₀"
        )

        print(
            "Las diferencias no se consideran normales."
        )

        print(
            "→ Se utilizará Wilcoxon de rangos con signo."
        )

    # --------------------------------------------------------
    # PRUEBA SEGÚN NORMALIDAD
    # --------------------------------------------------------

    if es_normal:

        # ====================================================
        # t DE STUDENT PAREADA
        # ====================================================

        prueba = "t de Student pareada"

        print("\n" + "=" * 90)
        print("PASO 2 — t DE STUDENT PAREADA")
        print("=" * 90)

        print(
            "\nLa prueba se realiza sobre las diferencias."
        )

        print(
            "Valor de referencia = 0"
        )

        print(
            "\nH₀: μd = 0"
        )

        print(
            "H₁: μd ≠ 0"
        )

        estadistico, p_prueba = (
            stats.ttest_1samp(
                diferencias.to_numpy(),
                0
            )
        )

        gl = (
            len(diferencias) - 1
        )

        media_diferencia = (
            diferencias.mean()
        )

        sd_diferencia = (
            diferencias.std(ddof=1)
        )

        error_estandar = (
            sd_diferencia
            /
            np.sqrt(len(diferencias))
        )

        t_critico = stats.t.ppf(
            1 - alpha / 2,
            gl
        )

        margen = (
            t_critico
            *
            error_estandar
        )

        ic_inferior = (
            media_diferencia
            -
            margen
        )

        ic_superior = (
            media_diferencia
            +
            margen
        )

        print(
            f"\nt = {estadistico:.6f}"
        )

        print(
            f"gl = {gl}"
        )

        print(
            f"p-valor = {p_prueba:.6f}"
        )

        print(
            f"IC 95 % de la diferencia = "
            f"{ic_inferior:.6f} a "
            f"{ic_superior:.6f}"
        )

        if p_prueba < alpha:

            decision = (
                "SE RECHAZA H₀"
            )

            conclusion = (
                "Existe evidencia estadística de "
                "una diferencia entre el método "
                "candidato y el método de referencia."
            )

        else:

            decision = (
                "NO SE RECHAZA H₀"
            )

            conclusion = (
                "No existe evidencia estadística "
                "suficiente para afirmar una "
                "diferencia entre ambos métodos."
            )

    else:

        # ====================================================
        # WILCOXON
        # ====================================================

        prueba = (
            "Wilcoxon de rangos con signo"
        )

        print("\n" + "=" * 90)
        print("PASO 2 — WILCOXON")
        print("=" * 90)

        print(
            "\nLa prueba se realiza sobre las diferencias."
        )

        print(
            "Valor de referencia = 0"
        )

        print(
            "\nH₀: Mediana(d) = 0"
        )

        print(
            "H₁: Mediana(d) ≠ 0"
        )

        diferencias_no_cero = (
            diferencias[
                diferencias != 0
            ]
        )

        n_ceros = int(
            (
                diferencias == 0
            ).sum()
        )

        if len(diferencias_no_cero) == 0:

            raise ValueError(
                f"En el nivel '{nombre_hoja}', "
                "todas las diferencias son cero. "
                "Wilcoxon no puede realizarse."
            )

        valores_abs = np.abs(
            diferencias_no_cero.to_numpy()
        )

        rangos = stats.rankdata(
            valores_abs,
            method="average"
        )

        W_mas = (
            rangos[
                diferencias_no_cero.to_numpy() > 0
            ].sum()
        )

        W_menos = (
            rangos[
                diferencias_no_cero.to_numpy() < 0
            ].sum()
        )

        W_usado = min(
            W_mas,
            W_menos
        )

        _, frecuencias = np.unique(
            valores_abs,
            return_counts=True
        )

        hay_empates = bool(
            np.any(
                frecuencias > 1
            )
        )

        resultado_w = stats.wilcoxon(
            diferencias.to_numpy(),
            zero_method="wilcox",
            correction=True,
            alternative="two-sided",
            method="approx"
        )

        estadistico = (
            resultado_w.statistic
        )

        p_prueba = (
            resultado_w.pvalue
        )

        media_diferencia = (
            diferencias.mean()
        )

        mediana_diferencia = (
            diferencias.median()
        )

        ic_inferior = None
        ic_superior = None

        print(
            f"\nW+ = {W_mas:.6f}"
        )

        print(
            f"W− = {W_menos:.6f}"
        )

        print(
            f"W usado = {W_usado:.6f}"
        )

        print(
            f"N original = {len(diferencias)}"
        )

        print(
            f"N efectivo = {len(diferencias_no_cero)}"
        )

        print(
            f"Diferencias cero = {n_ceros}"
        )

        print(
            f"Empates reales = "
            f"{'SÍ' if hay_empates else 'NO'}"
        )

        print(
            "Corrección de continuidad = SÍ"
        )

        print(
            f"W = {estadistico:.6f}"
        )

        print(
            f"p-valor = {p_prueba:.6f}"
        )

        if p_prueba < alpha:

            decision = (
                "SE RECHAZA H₀"
            )

            conclusion = (
                "Existe evidencia estadística de "
                "que la mediana de las diferencias "
                "es diferente de cero."
            )

        else:

            decision = (
                "NO SE RECHAZA H₀"
            )

            conclusion = (
                "No existe evidencia estadística "
                "suficiente para afirmar que la "
                "mediana de las diferencias "
                "sea diferente de cero."
            )

    # --------------------------------------------------------
    # RESULTADO FINAL DEL NIVEL
    # --------------------------------------------------------

    media_diferencia = (
        diferencias.mean()
    )

    mediana_diferencia = (
        diferencias.median()
    )

    print("\n" + "=" * 90)
    print(f"RESULTADO FINAL — NIVEL {numero} — {nombre_hoja}")
    print("=" * 90)

    print(
        f"Método candidato  : {nombre_candidato}"
    )

    print(
        f"Método referencia : {nombre_referencia}"
    )

    print(
        f"Prueba utilizada  : {prueba}"
    )

    print(
        f"p-valor AD        : {p_ad:.6f}"
    )

    print(
        f"p-valor prueba    : {p_prueba:.6f}"
    )

    print(
        f"Referencia        : 0"
    )

    print(
        f"DECISIÓN          : {decision}"
    )

    print(
        f"CONCLUSIÓN        : {conclusion}"
    )

    # --------------------------------------------------------
    # GRÁFICA
    # --------------------------------------------------------

    grafica_c2(
        nombre_hoja,
        nombre_candidato,
        nombre_referencia,
        diferencias,
        prueba,
        estadistico_ad,
        p_ad,
        estadistico,
        p_prueba,
        media_diferencia,
        mediana_diferencia,
        ic_inferior,
        ic_superior
    )

    # --------------------------------------------------------
    # FIN DEL NIVEL
    # --------------------------------------------------------

    print("\n" + "─" * 100)
    print(
        f"FIN DEL NIVEL {numero} — {nombre_hoja}"
    )
    print("─" * 100)

    resultados_finales.append(
        {
            "Nivel": nombre_hoja,
            "Candidato": nombre_candidato,
            "Referencia": nombre_referencia,
            "N": len(diferencias),
            "AD": estadistico_ad,
            "p_AD": p_ad,
            "Normalidad": (
                "Normal"
                if es_normal
                else "No normal"
            ),
            "Prueba": prueba,
            "Estadístico": estadistico,
            "p_valor": p_prueba,
            "Media_d": media_diferencia,
            "Mediana_d": mediana_diferencia,
            "Decisión": decision
        }
    )


# ============================================================
# 10. RESUMEN FINAL
# ============================================================

print("\n\n")

print("#" * 110)
print("RESUMEN FINAL — VERACIDAD C.2")
print("#" * 110)

resumen = pd.DataFrame(
    resultados_finales
)

print(
    resumen.to_string(
        index=False,
        formatters={
            "N": lambda x: f"{int(x)}",
            "AD": lambda x: f"{x:.6f}",
            "p_AD": lambda x: f"{x:.6f}",
            "Estadístico": lambda x: f"{x:.6f}",
            "p_valor": lambda x: f"{x:.6f}",
            "Media_d": lambda x: f"{x:.6f}",
            "Mediana_d": lambda x: f"{x:.6f}"
        }
    )
)

print("\n" + "#" * 110)
print("ANÁLISIS C.2 TERMINADO")
print("#" * 110)

