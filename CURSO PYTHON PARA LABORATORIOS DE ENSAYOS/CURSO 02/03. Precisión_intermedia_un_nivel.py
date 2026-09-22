# ============================================================
# PRECISIÓN INTERMEDIA - DISEÑO CRUZADO
# REPRODUCCIÓN DE MINITAB: TIPO I Y TIPO III
#
# Archivo:
# D:\Ciencia_de_Datos\Validación de métodos químicos\
# precision_intermedia.xlsx
#
# Hoja:
# hoja1
#
# Diseño:
# 3 Analistas × 3 Días × 3 réplicas = 27 observaciones
#
# Modelo:
# Resultado = μ + Analista + Día + Analista×Día + Error
#
# Analista y Día: factores ALEATORIOS
#
# El programa genera:
#   A. Información del diseño
#   B. ANOVA Tipo I - SC secuencial
#   C. Componentes de varianza Tipo I
#   D. ANOVA Tipo III - SC ajustada
#   E. Componentes de varianza Tipo III
#   F. Comparación Tipo I vs Tipo III
#   G. Resumen del modelo
#   H. Coeficientes y ecuación
#   I. Diagnóstico de residuos
#   J. Gráficas de residuos de alta resolución
#
# Nota:
# En este diseño balanceado las gráficas de residuos son las mismas
# para Tipo I y Tipo III porque ambos parten del mismo modelo ajustado.
# Se presentan dos figuras identificadas para poder compararlas
# visualmente con las dos salidas de Minitab.
# ============================================================


import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt

from scipy.stats import f, probplot
from statsmodels.formula.api import ols
from statsmodels.regression.mixed_linear_model import MixedLM
import statsmodels.api as sm


# ============================================================
# 1. ARCHIVO
# ============================================================

archivo = r"D:\Ciencia_de_Datos\Validación de métodos químicos\precision_intermedia.xlsx"

HOJA = "hoja1"


# ============================================================
# 2. LECTURA
# ============================================================

print("\nREPORTE TEXTUAL COMPLETO: TIPO I, TIPO III Y REML")
print("Las gráficas de residuos se muestran al final del análisis.")

df0 = pd.read_excel(
    archivo,
    sheet_name=HOJA
)

if df0.shape[1] < 3:
    raise ValueError(
        "La Hoja 1 debe contener por lo menos tres columnas: "
        "Analista, Día y Resultado."
    )

df = df0.iloc[:, :3].copy()
df.columns = ["Analista", "Dia", "Resultado"]

df["Analista"] = df["Analista"].astype(str).str.strip()
df["Dia"] = pd.to_numeric(df["Dia"], errors="raise")
df["Resultado"] = pd.to_numeric(df["Resultado"], errors="raise")

df["Analista"] = pd.Categorical(
    df["Analista"],
    categories=sorted(df["Analista"].unique())
)

df["Dia"] = pd.Categorical(
    df["Dia"],
    categories=sorted(df["Dia"].unique())
)

df["Orden"] = np.arange(1, len(df) + 1)


# ============================================================
# 3. INFORMACIÓN DEL DISEÑO — DETECCIÓN AUTOMÁTICA
# ============================================================
#
# El programa detecta automáticamente:
#   • número de analistas
#   • número de días
#   • réplicas por combinación Analista × Día
#   • celdas faltantes
#   • si el diseño está balanceado
#
# No está limitado a 3 × 3 × 3.
# ============================================================

analistas = list(df["Analista"].cat.categories)
dias = list(df["Dia"].cat.categories)

a = len(analistas)
b = len(dias)

conteos = (
    df.groupby(
        ["Analista", "Dia"],
        observed=True
    )
    .size()
)

celdas_esperadas = [
    (analista, dia)
    for analista in analistas
    for dia in dias
]

celdas_faltantes = [
    celda
    for celda in celdas_esperadas
    if celda not in conteos.index
]

# Si faltan celdas, no existe un diseño cruzado completo.
if celdas_faltantes:
    raise ValueError(
        "\nDISEÑO INCOMPLETO\n"
        "Faltan las siguientes combinaciones Analista × Día:\n"
        + "\n".join(
            f"  - {celda[0]} × Día {celda[1]}"
            for celda in celdas_faltantes
        )
    )

# Todas las celdas deben tener el mismo número de réplicas.
if conteos.nunique() != 1:
    print("\nADVERTENCIA: DISEÑO NO BALANCEADO")
    print("Número de réplicas por celda:")
    print(conteos.to_string())

    raise ValueError(
        "\nLas fórmulas ANOVA/EMS utilizadas en este módulo "
        "requieren un diseño cruzado balanceado.\n"
        "Para un diseño no balanceado, se debe trabajar "
        "directamente con un modelo general de componentes "
        "de varianza/REML."
    )

n = int(conteos.iloc[0])

print("\n")
print("=" * 75)
print("DIAGNÓSTICO AUTOMÁTICO DEL DISEÑO EXPERIMENTAL")
print("=" * 75)

print(
    f"Analistas detectados:        {a}"
)

print(
    f"Días detectados:             {b}"
)

print(
    f"Réplicas por celda:          {n}"
)

print(
    f"Observaciones:               {len(df)}"
)

print(
    f"Celdas Analista × Día:       {a*b}"
)

print(
    "Diseño cruzado completo:     SÍ"
)

print(
    "Diseño balanceado:           SÍ"
)

print("=" * 75)

# ============================================================
# 4. MODELO
# ============================================================

modelo = ols(
    "Resultado ~ Analista * Dia",
    data=df
).fit()


# ============================================================
# 5. ANOVA TIPO I Y TIPO III
# ============================================================
#
# Tipo I:
# Se calcula explícitamente para el diseño cruzado balanceado:
#
#   3 Analistas × 3 Días × 3 réplicas
#
# Esto reproduce las SC secuenciales de Minitab mediante:
#
#   SC Analista
#   SC Día
#   SC Analista×Día
#   SC Error
#
# Tipo III:
# Se obtiene mediante SC ajustada (statsmodels typ=3).
# ============================================================


# ------------------------------------------------------------
# 5.1 Tipo I - SC secuencial
# ------------------------------------------------------------

media_general = df["Resultado"].mean()

media_analista = (
    df.groupby(
        "Analista",
        observed=True
    )["Resultado"]
    .mean()
)

media_dia = (
    df.groupby(
        "Dia",
        observed=True
    )["Resultado"]
    .mean()
)

media_celda = (
    df.groupby(
        ["Analista", "Dia"],
        observed=True
    )["Resultado"]
    .mean()
)


# SC Analista
SC_A = (
    b * n *
    np.sum(
        (
            media_analista.values -
            media_general
        ) ** 2
    )
)


# SC Día
SC_D = (
    a * n *
    np.sum(
        (
            media_dia.values -
            media_general
        ) ** 2
    )
)


# SC Analista × Día
SC_AD = 0.0

for analista in df["Analista"].cat.categories:

    for dia in df["Dia"].cat.categories:

        media_ij = media_celda.loc[
            (analista, dia)
        ]

        efecto_interaccion = (
            media_ij
            - media_analista.loc[analista]
            - media_dia.loc[dia]
            + media_general
        )

        SC_AD += (
            n *
            efecto_interaccion ** 2
        )


# SC Error
SC_E = 0.0

for _, fila in df.iterrows():

    media_ij = media_celda.loc[
        (fila["Analista"], fila["Dia"])
    ]

    SC_E += (
        fila["Resultado"] -
        media_ij
    ) ** 2


tab_I = pd.DataFrame(
    {
        "GL": [
            a - 1,
            b - 1,
            (a - 1) * (b - 1),
            a * b * (n - 1)
        ],

        "SC": [
            SC_A,
            SC_D,
            SC_AD,
            SC_E
        ]
    },

    index=[
        "Analista",
        "Día",
        "Analista*Día",
        "Error"
    ]
)

tab_I["MC"] = (
    tab_I["SC"] /
    tab_I["GL"]
)


# ------------------------------------------------------------
# 5.2 Tipo III - SC ajustada
# ------------------------------------------------------------
#
# En este diseño:
#
#     3 Analistas × 3 Días × 3 réplicas
#
# el diseño es completamente balanceado y ortogonal.
#
# Por ello, las SC ajustadas (Tipo III) de Minitab coinciden
# con las SC secuenciales (Tipo I):
#
#     SC Tipo III = SC Tipo I
#
# No se utiliza aquí el typ=3 genérico de statsmodels porque
# su parametrización de contrastes puede producir una salida
# distinta de la parametrización que Minitab utiliza para este
# modelo factorial balanceado.
#
# Se reproduce directamente la solución de Minitab para este
# diseño específico.
# ------------------------------------------------------------

tab_III = tab_I.copy()

# ============================================================
# 6. PRUEBAS F PARA FACTORES ALEATORIOS
# ============================================================
#
# Analista       -> MS Analista / MS Analista×Día
# Día            -> MS Día / MS Analista×Día
# Analista×Día   -> MS Analista×Día / MS Error
#
# ============================================================

def agregar_pruebas(tabla):

    tabla = tabla.copy()

    tabla["F"] = np.nan
    tabla["p"] = np.nan

    ms_A = tabla.loc["Analista", "MC"]
    ms_D = tabla.loc["Día", "MC"]
    ms_AD = tabla.loc["Analista*Día", "MC"]
    ms_E = tabla.loc["Error", "MC"]

    gl_A = int(tabla.loc["Analista", "GL"])
    gl_D = int(tabla.loc["Día", "GL"])
    gl_AD = int(tabla.loc["Analista*Día", "GL"])
    gl_E = int(tabla.loc["Error", "GL"])

    F_A = ms_A / ms_AD
    F_D = ms_D / ms_AD
    F_AD = ms_AD / ms_E

    tabla.loc["Analista", "F"] = F_A
    tabla.loc["Analista", "p"] = f.sf(
        F_A,
        gl_A,
        gl_AD
    )

    tabla.loc["Día", "F"] = F_D
    tabla.loc["Día", "p"] = f.sf(
        F_D,
        gl_D,
        gl_AD
    )

    tabla.loc["Analista*Día", "F"] = F_AD
    tabla.loc["Analista*Día", "p"] = f.sf(
        F_AD,
        gl_AD,
        gl_E
    )

    return tabla


tab_I = agregar_pruebas(tab_I)
tab_III = agregar_pruebas(tab_III)


# ============================================================
# 7. COMPONENTES DE VARIANZA
# ============================================================

def componentes_varianza(tabla):

    MS_A = tabla.loc["Analista", "MC"]
    MS_D = tabla.loc["Día", "MC"]
    MS_AD = tabla.loc["Analista*Día", "MC"]
    MS_E = tabla.loc["Error", "MC"]

    # Componentes esperados para:
    # Y = μ + A + D + A×D + e

    var_A = (MS_A - MS_AD) / (b * n)
    var_D = (MS_D - MS_AD) / (a * n)
    var_AD = (MS_AD - MS_E) / n
    var_E = MS_E

    # Para % del total, Minitab no utiliza componentes
    # negativos como contribución.
    vA = max(var_A, 0)
    vD = max(var_D, 0)
    vAD = max(var_AD, 0)
    vE = max(var_E, 0)

    suma_pos = vA + vD + vAD + vE

    # Minitab utiliza cero para un componente negativo al
    # calcular la contribución total.
    #
    # Por tanto:
    # Varianza total = max(var_A,0) + max(var_D,0)
    #                + max(var_AD,0) + max(var_E,0)
    #
    # Esta es la varianza de precisión intermedia (SI).
    var_total = (
        vA +
        vD +
        vAD +
        vE
    )

    sd_A = np.sqrt(vA)
    sd_D = np.sqrt(vD)
    sd_AD = np.sqrt(vAD)
    sd_E = np.sqrt(vE)

    sd_total = np.sqrt(max(var_total, 0))

    resultado = pd.DataFrame({
        "Fuente": [
            "Analista",
            "Día",
            "Analista*Día",
            "Error",
            "Total"
        ],

        "Varianza": [
            var_A,
            var_D,
            var_AD,
            var_E,
            var_total
        ],

        "% del total": [
            100 * vA / suma_pos,
            100 * vD / suma_pos,
            100 * vAD / suma_pos,
            100 * vE / suma_pos,
            100.0
        ],

        "Desv.Est.": [
            sd_A,
            sd_D,
            sd_AD,
            sd_E,
            sd_total
        ],

        "% de SD total": [
            100 * sd_A / sd_total,
            100 * sd_D / sd_total,
            100 * sd_AD / sd_total,
            100 * sd_E / sd_total,
            100.0
        ]
    })

    return resultado


vc_I = componentes_varianza(tab_I)
vc_III = componentes_varianza(tab_III)


# ============================================================
# 8. FUNCIONES DE PRESENTACIÓN
# ============================================================

def mostrar_anova(tabla, titulo):

    print("\n")
    print("=" * 95)
    print(titulo)
    print("=" * 95)

    salida = tabla.copy()
    salida.index.name = "Fuente"

    print(
        salida[
            ["GL", "SC", "MC", "F", "p"]
        ].to_string(
            formatters={
                "GL": lambda x: f"{int(x)}",
                "SC": lambda x: f"{x:.9f}",
                "MC": lambda x: f"{x:.9f}",
                "F": lambda x: (
                    "" if pd.isna(x)
                    else f"{x:.3f}"
                ),
                "p": lambda x: (
                    "" if pd.isna(x)
                    else f"{x:.4f}"
                )
            }
        )
    )

    SC_total = salida["SC"].sum()
    GL_total = salida["GL"].sum()

    print(
        f"\nTotal: GL = {int(GL_total)}, "
        f"SC = {SC_total:.9f}"
    )


def mostrar_resumen_modelo():

    S = np.sqrt(tab_I.loc["Error", "MC"])

    R2 = modelo.rsquared * 100
    R2_adj = modelo.rsquared_adj * 100

    influence = modelo.get_influence()

    press = np.sum(
        influence.resid_press ** 2
    )

    sst = np.sum(
        (
            df["Resultado"] -
            df["Resultado"].mean()
        ) ** 2
    )

    R2_pred = (
        1 -
        press / sst
    ) * 100

    # Minitab muestra 0.00% cuando R2 pred resulta negativo.
    R2_pred = max(R2_pred, 0)

    print("\n")
    print("=" * 95)
    print("RESUMEN DEL MODELO")
    print("=" * 95)

    print(
        f"{'S':<18}"
        f"{'R-cuadrado':<18}"
        f"{'R-cuadrado(ajustado)':<25}"
        f"{'R-cuadrado (pred)':<20}"
    )

    print(
        f"{S:<18.7f}"
        f"{R2:<18.2f}%"
        f"{R2_adj:<25.2f}%"
        f"{R2_pred:<20.2f}%"
    )


def mostrar_ems():

    print("\n")
    print("=" * 95)
    print(
        "MEDIA DE CUADRADOS ESPERADA, "
        "UTILIZANDO SC SECUENCIAL"
    )
    print("=" * 95)

    print(
        f"{'Fuente':<20}"
        f"{'Media de cuadrados esperada':<50}"
    )

    print(
        f"{'1 Analista':<20}"
        f"(4) + {n:.4f} (3) + {b*n:.4f} (1)"
    )

    print(
        f"{'2 Día':<20}"
        f"(4) + {n:.4f} (3) + {a*n:.4f} (2)"
    )

    print(
        f"{'3 Analista*Día':<20}"
        f"(4) + {n:.4f} (3)"
    )

    print(
        f"{'4 Error':<20}"
        f"(4)"
    )


def mostrar_ems_ajustada():

    print("\n")
    print("=" * 95)
    print(
        "MEDIA DE CUADRADOS ESPERADA, "
        "UTILIZANDO SC AJUSTADA"
    )
    print("=" * 95)

    print(
        f"{'Fuente':<20}"
        f"{'Media de cuadrados esperada':<50}"
    )

    print(
        f"{'1 Analista':<20}"
        f"(4) + {n:.4f} (3) + {b*n:.4f} (1)"
    )

    print(
        f"{'2 Día':<20}"
        f"(4) + {n:.4f} (3) + {a*n:.4f} (2)"
    )

    print(
        f"{'3 Analista*Día':<20}"
        f"(4) + {n:.4f} (3)"
    )

    print(
        f"{'4 Error':<20}"
        f"(4)"
    )



def mostrar_terminos_error(tabla, titulo):

    print("\n")
    print("=" * 95)
    print(titulo)
    print("=" * 95)

    ms_ad = tabla.loc[
        "Analista*Día", "MC"
    ]

    ms_e = tabla.loc[
        "Error", "MC"
    ]

    gl_error_ad = (a - 1) * (b - 1)
    gl_error_e = a * b * (n - 1)

    print(
        f"{'Fuente':<22}"
        f"{'GL de error':>15}"
        f"{'MC de error':>18}"
        f"{'Síntesis de MC de error':>28}"
    )

    print(
        f"{'1 Analista':<22}"
        f"{gl_error_ad:>15.2f}"
        f"{ms_ad:>18.4f}"
        f"{'(3)':>28}"
    )

    print(
        f"{'2 Día':<22}"
        f"{gl_error_ad:>15.2f}"
        f"{ms_ad:>18.4f}"
        f"{'(3)':>28}"
    )

    print(
        f"{'3 Analista*Día':<22}"
        f"{gl_error_e:>15.2f}"
        f"{ms_e:>18.4f}"
        f"{'(4)':>28}"
    )



def mostrar_componentes(vc, titulo):

    print("\n")
    print("=" * 95)
    print(titulo)
    print("=" * 95)

    print(
        f"{'Fuente':<18}"
        f"{'Varianza':>16}"
        f"{'% del total':>15}"
        f"{'Desv.Est.':>16}"
        f"{'% del total':>15}"
    )

    for _, fila in vc.iterrows():

        print(
            f"{fila['Fuente']:<18}"
            f"{fila['Varianza']:>16.9f}"
            f"{fila['% del total']:>14.2f}%"
            f"{fila['Desv.Est.']:>16.7f}"
            f"{fila['% de SD total']:>14.2f}%"
        )

    negativos = vc[
        vc["Varianza"] < 0
    ]

    if len(negativos) > 0:

        print(
            "\n* El valor es negativo y se calcula "
            "dividiendo entre cero."
        )



# ============================================================
# 8B. GRÁFICAS DE RESIDUOS — ESTILO MINITAB
# ============================================================
#
# Las gráficas se basan en el mismo modelo lineal:
#
# Resultado = μ + Analista + Día + Analista×Día + Error
#
# Como Tipo I y Tipo III coinciden en este diseño balanceado y
# REML estima los componentes de varianza del mismo experimento,
# las gráficas diagnósticas del modelo lineal son las mismas.
#
# Se muestran las cuatro gráficas clásicas de Minitab:
#   1. Probabilidad normal
#   2. Residuos vs. ajustes
#   3. Histograma
#   4. Residuos vs. orden
# ============================================================

def mostrar_graficas_residuos():

    residuos = np.asarray(modelo.resid, dtype=float)
    ajustes = np.asarray(modelo.fittedvalues, dtype=float)
    orden = np.arange(1, len(residuos) + 1)

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(14, 9),
        dpi=180
    )

    fig.suptitle(
        "Gráficas de residuos para % Proteína",
        fontsize=18,
        fontweight="bold",
        y=0.98
    )

    # --------------------------------------------------------
    # 1. Gráfica de probabilidad normal
    # --------------------------------------------------------

    ax = axes[0, 0]

    (osm, osr), (slope, intercept, r) = probplot(
        residuos,
        dist="norm"
    )

    ax.scatter(
        osm,
        osr,
        s=42,
        alpha=0.9
    )

    x_line = np.linspace(
        np.min(osm),
        np.max(osm),
        100
    )

    ax.plot(
        x_line,
        slope * x_line + intercept,
        linewidth=1.8
    )

    ax.set_title(
        "Gráfica de probabilidad normal",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_xlabel("Residuo")
    ax.set_ylabel("Porcentaje")

    ax.grid(
        True,
        alpha=0.25
    )

    # --------------------------------------------------------
    # 2. Residuos vs. ajustes
    # --------------------------------------------------------

    ax = axes[0, 1]

    ax.scatter(
        ajustes,
        residuos,
        s=42,
        alpha=0.9
    )

    ax.axhline(
        0,
        linewidth=1.2,
        linestyle="--"
    )

    ax.set_title(
        "Residuos vs. ajustes",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_xlabel("Valor ajustado")
    ax.set_ylabel("Residuo")

    ax.grid(
        True,
        alpha=0.25
    )

    # --------------------------------------------------------
    # 3. Histograma
    # --------------------------------------------------------

    ax = axes[1, 0]

    ax.hist(
        residuos,
        bins="auto",
        edgecolor="black",
        alpha=0.75
    )

    ax.set_title(
        "Histograma",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_xlabel("Residuo")
    ax.set_ylabel("Frecuencia")

    ax.grid(
        True,
        axis="y",
        alpha=0.25
    )

    # --------------------------------------------------------
    # 4. Residuos vs. orden
    # --------------------------------------------------------

    ax = axes[1, 1]

    ax.plot(
        orden,
        residuos,
        marker="o",
        markersize=4.5,
        linewidth=1.2
    )

    ax.axhline(
        0,
        linewidth=1.2,
        linestyle="--"
    )

    ax.set_title(
        "vs. orden",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_xlabel("Orden de observación")
    ax.set_ylabel("Residuo")

    ax.set_xticks(
        np.arange(
            1,
            len(residuos) + 1,
            2
        )
    )

    ax.grid(
        True,
        alpha=0.25
    )

    plt.tight_layout(
        rect=[0, 0, 1, 0.95]
    )

    plt.show()


# ============================================================
# 9. REPORTE TIPO I
# ============================================================

print("\n\n")
print("#" * 95)
print("PRECISIÓN INTERMEDIA - MÉTODO TIPO I")
print("SC SECUENCIAL")
print("#" * 95)

print("\nINFORMACIÓN DEL FACTOR")
print(
    f"Analista: Aleatorio | {a} niveles | "
    f"{', '.join(map(str, df['Analista'].cat.categories))}"
)

print(
    f"Día: Aleatorio | {b} niveles | "
    f"{', '.join(map(str, df['Dia'].cat.categories))}"
)

print(f"Réplicas por celda: {n}")
print(f"Observaciones: {len(df)}")

mostrar_anova(
    tab_I,
    "ANÁLISIS DE VARIANZA - SC SECUENCIAL (TIPO I)"
)

mostrar_resumen_modelo()

mostrar_ems()

mostrar_terminos_error(
    tab_I,
    "TÉRMINOS DE ERROR PARA PRUEBAS, UTILIZANDO SC SECUENCIAL"
)

mostrar_componentes(
    vc_I,
    "COMPONENTES DE VARIANZA, UTILIZANDO SC SECUENCIAL"
)


# ============================================================
# 10. REPORTE TIPO III
# ============================================================

print("\n\n")
print("#" * 95)
print("PRECISIÓN INTERMEDIA - MÉTODO TIPO III")
print("SC AJUSTADA")
print("#" * 95)

print("\nINFORMACIÓN DEL FACTOR")
print(
    f"Analista: Aleatorio | {a} niveles | "
    f"{', '.join(map(str, df['Analista'].cat.categories))}"
)

print(
    f"Día: Aleatorio | {b} niveles | "
    f"{', '.join(map(str, df['Dia'].cat.categories))}"
)

print(f"Réplicas por celda: {n}")
print(f"Observaciones: {len(df)}")

mostrar_anova(
    tab_III,
    "ANÁLISIS DE VARIANZA - SC AJUSTADA (TIPO III)"
)

mostrar_resumen_modelo()

mostrar_ems_ajustada()

mostrar_terminos_error(
    tab_III,
    "TÉRMINOS DE ERROR PARA PRUEBAS, UTILIZANDO SC AJUSTADA"
)

mostrar_componentes(
    vc_III,
    "COMPONENTES DE VARIANZA, UTILIZANDO SC AJUSTADA"
)


# ============================================================
# 11. REML - ESTIMACIÓN DE COMPONENTES DE VARIANZA
# ============================================================
#
# REML = Restricted Maximum Likelihood
#
# En este diseño se modelan como efectos aleatorios:
#
#   Analista
#   Día
#   Analista × Día
#
# y el error residual.
#
# Como los factores Analista y Día están cruzados, se utiliza
# MixedLM con un único grupo global y componentes de varianza
# (variance components) para cada factor.
#
# IMPORTANTE:
# REML no es un "Tipo de SC" como Tipo I o Tipo III.
# Es un MÉTODO DE ESTIMACIÓN de los componentes de varianza.
# Aquí se presenta como un tercer método del análisis porque es
# precisamente el método que queremos comparar posteriormente
# con las estimaciones por ANOVA.
# ============================================================

df_reml = df.copy()

df_reml["Analista_Dia"] = (
    df_reml["Analista"].astype(str)
    + ":"
    + df_reml["Dia"].astype(str)
)


modelo_reml = MixedLM.from_formula(
    "Resultado ~ 1",
    groups=np.ones(len(df_reml)),
    re_formula="0",
    vc_formula={
        "Analista": "0 + Analista",
        "Dia": "0 + Dia",
        "Analista_Dia": "0 + Analista_Dia"
    },
    data=df_reml
)


with warnings.catch_warnings(record=True) as advertencias_reml:
    warnings.simplefilter("always")

    resultado_reml = modelo_reml.fit(
        reml=True,
        method="lbfgs",
        maxiter=2000,
        disp=False
    )

advertencias_reml_texto = [
    str(advertencia.message)
    for advertencia in advertencias_reml
]


# ------------------------------------------------------------
# Extraer componentes REML
# ------------------------------------------------------------

nombres_vc = resultado_reml.model.exog_vc.names
valores_vc = resultado_reml.vcomp

componentes_reml = dict(
    zip(
        nombres_vc,
        valores_vc
    )
)

var_A_reml = max(
    float(componentes_reml.get("Analista", 0.0)),
    0.0
)

var_D_reml = max(
    float(componentes_reml.get("Dia", 0.0)),
    0.0
)

var_AD_reml = max(
    float(componentes_reml.get("Analista_Dia", 0.0)),
    0.0
)

var_E_reml = max(
    float(resultado_reml.scale),
    0.0
)


var_total_reml = (
    var_A_reml
    + var_D_reml
    + var_AD_reml
    + var_E_reml
)

sd_A_reml = np.sqrt(var_A_reml)
sd_D_reml = np.sqrt(var_D_reml)
sd_AD_reml = np.sqrt(var_AD_reml)
sd_E_reml = np.sqrt(var_E_reml)
sd_total_reml = np.sqrt(var_total_reml)


vc_REML = pd.DataFrame({

    "Fuente": [
        "Analista",
        "Día",
        "Analista*Día",
        "Error",
        "Total"
    ],

    "Varianza": [
        var_A_reml,
        var_D_reml,
        var_AD_reml,
        var_E_reml,
        var_total_reml
    ],

    "% del total": [
        100 * var_A_reml / var_total_reml,
        100 * var_D_reml / var_total_reml,
        100 * var_AD_reml / var_total_reml
        if var_total_reml > 0 else 0.0,
        100 * var_E_reml / var_total_reml,
        100.0
    ],

    "Desv.Est.": [
        sd_A_reml,
        sd_D_reml,
        sd_AD_reml,
        sd_E_reml,
        sd_total_reml
    ],

    "% de SD total": [
        100 * sd_A_reml / sd_total_reml,
        100 * sd_D_reml / sd_total_reml,
        100 * sd_AD_reml / sd_total_reml,
        100 * sd_E_reml / sd_total_reml,
        100.0
    ]
})


# ------------------------------------------------------------
# Presentación REML
# ------------------------------------------------------------

print("\n\n")
print("#" * 95)
print("PRECISIÓN INTERMEDIA - MÉTODO REML")
print("RESTRICTED MAXIMUM LIKELIHOOD")
print("#" * 95)

print("\nMODELO REML")
print(
    "Resultado = μ + Analista + Día + "
    "Analista×Día + Error"
)

print("\nFactores aleatorios:")
print("  Analista")
print("  Día")
print("  Analista×Día")

print("\nRESUMEN DEL MODELO REML")
print("=" * 95)

print(
    f"Método de estimación       : REML"
)
print(
    f"Convergencia               : "
    f"{'Sí' if resultado_reml.converged else 'No'}"
)
print(
    f"Log-verosimilitud restringida: "
    f"{resultado_reml.llf:.6f}"
)
print(
    f"S (Error residual)         : "
    f"{sd_E_reml:.7f}"
)

if advertencias_reml_texto:
    print("\nADVERTENCIA DEL AJUSTE REML:")
    for mensaje in advertencias_reml_texto:
        print(f"  - {mensaje}")


mostrar_componentes(
    vc_REML,
    "COMPONENTES DE VARIANZA, MÉTODO REML"
)




# ============================================================
# GRÁFICAS DE RESIDUOS
# ============================================================

mostrar_graficas_residuos()


# ============================================================
# RESULTADO FINAL - PRECISIÓN INTERMEDIA (SI)
# ============================================================
#
# SI² = Varianza total de los componentes de varianza
# SI  = Desviación estándar de precisión intermedia
# ============================================================

varianza_SI_tipo_I = vc_I.loc[
    vc_I["Fuente"] == "Total",
    "Varianza"
].iloc[0]

SD_SI_tipo_I = vc_I.loc[
    vc_I["Fuente"] == "Total",
    "Desv.Est."
].iloc[0]

varianza_SI_tipo_III = vc_III.loc[
    vc_III["Fuente"] == "Total",
    "Varianza"
].iloc[0]

SD_SI_tipo_III = vc_III.loc[
    vc_III["Fuente"] == "Total",
    "Desv.Est."
].iloc[0]

varianza_SI_REML = vc_REML.loc[
    vc_REML["Fuente"] == "Total",
    "Varianza"
].iloc[0]

SD_SI_REML = vc_REML.loc[
    vc_REML["Fuente"] == "Total",
    "Desv.Est."
].iloc[0]


print("\n\n")
print("=" * 105)
print("RESULTADO FINAL — PRECISIÓN INTERMEDIA (SI)")
print("=" * 105)

print(
    f"{'Método':<22}"
    f"{'Varianza SI (SI²)':>28}"
    f"{'Desv. estándar SI':>28}"
)

print("-" * 105)

print(
    f"{'Tipo I — SC secuencial':<22}"
    f"{varianza_SI_tipo_I:>28.7f}"
    f"{SD_SI_tipo_I:>28.7f}"
)

print(
    f"{'Tipo III — SC ajustada':<22}"
    f"{varianza_SI_tipo_III:>28.7f}"
    f"{SD_SI_tipo_III:>28.7f}"
)

print(
    f"{'REML':<22}"
    f"{varianza_SI_REML:>28.7f}"
    f"{SD_SI_REML:>28.7f}"
)

print("=" * 105)

print(
    "\nNOTA: REML es un método de estimación de componentes de "
    "varianza; no corresponde a una suma de cuadrados Tipo I o Tipo III."
)

# ============================================================
# 12. EVALUACIÓN DE PRECISIÓN INTERMEDIA FRENTE A HORWITZ
# ============================================================
#
# Para PRECISIÓN INTERMEDIA se utiliza:
#
#     PRSD_intermedia = (2/3) × PRSDR
#
# donde:
#
#     PRSDR = 2 × C_muestra^(-0.15)
#
# La evaluación se realiza para UN SOLO NIVEL DE CONCENTRACIÓN.
#
# Para HorRat(r) se mantiene el criterio solicitado:
#
#     0.3 ≤ HorRat(r) ≤ 1.3
#
# IMPORTANTE:
# La variable C_muestra NO se llama C para no interferir con
# funciones/nombres utilizados por Patsy en fórmulas estadísticas.
# Además, el modelo anterior fue escrito sin C(...): las columnas
# Analista y Dia ya son categóricas, por lo que Patsy las trata
# como factores automáticamente.
# ============================================================

print("\n\n")
print("=" * 105)
print("EVALUACIÓN DE PRECISIÓN INTERMEDIA FRENTE A HORWITZ")
print("=" * 105)

print("\nSeleccione la estimación de precisión intermedia (SI) que desea evaluar:")
print("1. Tipo I  — SC secuencial")
print("2. Tipo III — SC ajustada")
print("3. REML")

opcion_SI = input("\nIngrese una opción (1, 2 o 3): ").strip()

if opcion_SI == "1":
    metodo_SI = "Tipo I — SC secuencial"
    varianza_SI = float(varianza_SI_tipo_I)
    SD_SI = float(SD_SI_tipo_I)
elif opcion_SI == "2":
    metodo_SI = "Tipo III — SC ajustada"
    varianza_SI = float(varianza_SI_tipo_III)
    SD_SI = float(SD_SI_tipo_III)
elif opcion_SI == "3":
    metodo_SI = "REML"
    varianza_SI = float(varianza_SI_REML)
    SD_SI = float(SD_SI_REML)
else:
    raise ValueError("Debe seleccionar 1, 2 o 3.")

print("\nEstimación seleccionada:", metodo_SI)
print(f"Desviación estándar de precisión intermedia (SI) = {SD_SI:.6f}")

# ------------------------------------------------------------
# 12.1 CONCENTRACIÓN DE EVALUACIÓN
# ------------------------------------------------------------

concentracion_muestra = float(
    input("\nIngrese la concentración del nivel de evaluación: ").replace(",", ".")
)

if concentracion_muestra <= 0:
    raise ValueError("La concentración debe ser mayor que cero.")

# ------------------------------------------------------------
# 12.2 UNIDAD
# ------------------------------------------------------------

print("\nSeleccione la unidad de concentración:")
print("1. ppm")
print("2. ppb")
print("3. %")

opcion_unidad = input("Ingrese una opción (1, 2 o 3): ").strip()

if opcion_unidad == "1":
    unidad = "ppm"
    factor_masico = 10 ** (-6)
elif opcion_unidad == "2":
    unidad = "ppb"
    factor_masico = 10 ** (-9)
elif opcion_unidad == "3":
    unidad = "%"
    factor_masico = 10 ** (-2)
else:
    raise ValueError("Debe seleccionar 1, 2 o 3.")

# ------------------------------------------------------------
# 12.3 CÁLCULO DE RSD EXPERIMENTAL
# ------------------------------------------------------------

RSD_SI = (
    SD_SI / concentracion_muestra
) * 100

# ------------------------------------------------------------
# 12.4 CONVERSIÓN A FRACCIÓN MÁSICA
# ------------------------------------------------------------
#
# NO utilizar una variable llamada C.
# Esto evita cualquier conflicto con nombres/factores de Patsy.
# ------------------------------------------------------------

C_muestra = (
    concentracion_muestra * factor_masico
)

if C_muestra <= 0:
    raise ValueError("La fracción másica de la concentración debe ser mayor que cero.")

# ------------------------------------------------------------
# 12.5 HORWITZ — REPRODUCIBILIDAD
# ------------------------------------------------------------

PRSDR = (
    2 * C_muestra ** (-0.15)
)

# ------------------------------------------------------------
# 12.6 PRECISIÓN INTERMEDIA
# ------------------------------------------------------------
#
# Para precisión intermedia:
#
#     PRSD_intermedia = (2/3) × PRSDR
# ------------------------------------------------------------

factor_intermedia = 2 / 3

PRSD_intermedia = (
    factor_intermedia * PRSDR
)

# ------------------------------------------------------------
# 12.7 HORRAT(r)
# ------------------------------------------------------------
#
# Se utiliza el mismo criterio solicitado para repetibilidad:
#
#     0.3 ≤ HorRat(r) ≤ 1.3
#
# El denominador es PRSDR.
# ------------------------------------------------------------

HorRat_r = (
    RSD_SI / PRSDR
)

if 0.3 <= HorRat_r <= 1.3:
    conclusion_HorRat = "CUMPLE"
else:
    conclusion_HorRat = "NO CUMPLE"

if RSD_SI <= PRSD_intermedia:
    conclusion_PRSD = "CUMPLE"
else:
    conclusion_PRSD = "NO CUMPLE"

# ------------------------------------------------------------
# 12.8 REPORTE FINAL
# ------------------------------------------------------------

print("\n")
print("=" * 105)
print("RESULTADO FINAL — PRECISIÓN INTERMEDIA")
print("=" * 105)

print(f"\nMétodo de estimación SI:       {metodo_SI}")
print(f"Varianza SI:                   {varianza_SI:.8f}")
print(f"Desviación estándar SI:        {SD_SI:.8f}")
print(f"Concentración evaluada:        {concentracion_muestra:.6g} {unidad}")
print(f"Fracción másica C_muestra:     {C_muestra:.6e}")
print(f"RSD experimental SI:           {RSD_SI:.6f} %")
print(f"PRSDR de Horwitz:              {PRSDR:.6f} %")
print(f"Factor para intermedia:        2/3 = {factor_intermedia:.6f}")
print(f"PRSD intermedia (2/3×PRSDR):   {PRSD_intermedia:.6f} %")
print(f"HorRat(r):                     {HorRat_r:.6f}")
print("Criterio HorRat(r):            0.3 ≤ HorRat(r) ≤ 1.3")
print(f"Resultado HorRat(r):            {conclusion_HorRat}")
print(f"Resultado frente a (2/3)×PRSDR: {conclusion_PRSD}")

print("\n" + "-" * 105)
print("TABLA RESUMEN")
print("-" * 105)

resumen_intermedia = pd.DataFrame({
    "Concepto": [
        "Método SI",
        "Concentración",
        "Unidad",
        "Desviación estándar SI",
        "%RSD experimental SI",
        "Fracción másica C_muestra",
        "PRSDR Horwitz",
        "Factor precisión intermedia",
        "PRSD intermedia",
        "HorRat(r)",
        "Criterio HorRat(r)",
        "Resultado HorRat(r)",
        "Resultado frente a (2/3)×PRSDR"
    ],
    "Resultado": [
        metodo_SI,
        f"{concentracion_muestra:.6g}",
        unidad,
        f"{SD_SI:.8f}",
        f"{RSD_SI:.6f} %",
        f"{C_muestra:.6e}",
        f"{PRSDR:.6f} %",
        "2/3",
        f"{PRSD_intermedia:.6f} %",
        f"{HorRat_r:.6f}",
        "0.3 ≤ HorRat(r) ≤ 1.3",
        conclusion_HorRat,
        conclusion_PRSD
    ]
})

display(resumen_intermedia)

print("\n")
print("NOTA:")
print("La evaluación de Horwitz y HorRat(r) se realizó únicamente")
print("para la concentración indicada por el usuario.")
print("Para precisión intermedia se utilizó el factor 2/3 de PRSDR.")
print("El criterio solicitado para HorRat(r) es 0.3 ≤ HorRat(r) ≤ 1.3.")
