# ============================================================
# AUTOMATIZACIÓN DE PRECISIÓN INTERMEDIA - VARIOS NIVELES
#
# Para cada nivel de concentración (cada hoja):
#   1. Detecta Analista × Día × Réplicas automáticamente
#   2. Calcula componentes de varianza Tipo I
#   3. Calcula componentes de varianza Tipo III
#   4. Calcula componentes de varianza mediante REML
#   5. Obtiene SI² y SI
#
# Luego:
#   6. Pregunta qué SI se desea utilizar:
#        Tipo I / Tipo III / REML
#   7. Calcula %RSD = SI / C × 100
#   8. Hace la regresión %RSD vs concentración
#   9. Compara modelos
#  10. Muestra gráficas
#  11. Permite selección manual del modelo
#  12. Estima SI para una concentración de muestra
#
# La lógica de regresión es la misma del script de repetibilidad
# proporcionado: únicamente se reemplaza Sr por SI.
# ============================================================


import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import f
from statsmodels.formula.api import ols
from statsmodels.regression.mixed_linear_model import MixedLM


# ============================================================
# 1. UBICACIÓN DEL ARCHIVO
# ============================================================

archivo_windows = r"D:\Ciencia_de_Datos\Validación de métodos químicos\precision_intermedia.xlsx"

# En el equipo del usuario se utilizará la ruta de Windows.
# El segundo camino sólo permite probar el script con el Excel adjunto
# cuando se ejecuta dentro de este entorno.
archivo = archivo_windows

if not pd.io.common.file_exists(archivo):
    archivo_adjunto = "/mnt/data/precision_intermedia(1).xlsx"
    if pd.io.common.file_exists(archivo_adjunto):
        archivo = archivo_adjunto

print(f"Archivo utilizado: {archivo}")


# ============================================================
# 2. FUNCIONES AUXILIARES
# ============================================================

def calcular_r2(y_real, y_pred):

    ss_res = np.sum(
        (y_real - y_pred) ** 2
    )

    ss_tot = np.sum(
        (y_real - np.mean(y_real)) ** 2
    )

    if ss_tot == 0:
        return np.nan

    return 1 - (
        ss_res / ss_tot
    )


def preparar_nivel(archivo, hoja):
    """
    Lee una hoja de un nivel.

    Se esperan las primeras tres columnas:
        Analista | Día | Resultado

    El número de analistas, días y réplicas NO está fijado.
    """

    datos = pd.read_excel(
        archivo,
        sheet_name=hoja
    )

    if datos.shape[1] < 3:
        raise ValueError(
            f"La hoja '{hoja}' debe tener al menos "
            "tres columnas: Analista, Día y Resultado."
        )

    df = datos.iloc[:, :3].copy()

    df.columns = [
        "Analista",
        "Dia",
        "Resultado"
    ]

    df["Analista"] = (
        df["Analista"]
        .astype(str)
        .str.strip()
    )

    df["Dia"] = pd.to_numeric(
        df["Dia"],
        errors="raise"
    )

    df["Resultado"] = pd.to_numeric(
        df["Resultado"],
        errors="raise"
    )

    df = df.dropna(
        subset=[
            "Analista",
            "Dia",
            "Resultado"
        ]
    ).copy()

    df["Analista"] = pd.Categorical(
        df["Analista"],
        categories=sorted(
            df["Analista"].unique()
        )
    )

    df["Dia"] = pd.Categorical(
        df["Dia"],
        categories=sorted(
            df["Dia"].unique()
        )
    )

    return df


def diagnosticar_diseno(df, hoja):

    analistas = list(
        df["Analista"].cat.categories
    )

    dias = list(
        df["Dia"].cat.categories
    )

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

    if celdas_faltantes:

        raise ValueError(
            f"\nNivel '{hoja}': diseño incompleto.\n"
            "Faltan combinaciones Analista × Día:\n"
            + "\n".join(
                f"  - {celda[0]} × Día {celda[1]}"
                for celda in celdas_faltantes
            )
        )

    if conteos.nunique() != 1:

        print(
            f"\nNivel '{hoja}': DISEÑO NO BALANCEADO"
        )

        print(
            conteos.to_string()
        )

        raise ValueError(
            f"\nEl nivel '{hoja}' no está balanceado.\n"
            "El procedimiento Tipo I/Tipo III de este script "
            "requiere un diseño cruzado completo y balanceado."
        )

    n = int(
        conteos.iloc[0]
    )

    return {
        "analistas": analistas,
        "dias": dias,
        "a": a,
        "b": b,
        "n": n,
        "observaciones": len(df)
    }


# ============================================================
# 3. ANOVA TIPO I
# ============================================================

def calcular_tipo_I(df, diseno):

    a = diseno["a"]
    b = diseno["b"]
    n = diseno["n"]

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

    SC_A = (
        b * n *
        np.sum(
            (
                media_analista.values
                - media_general
            ) ** 2
        )
    )

    SC_D = (
        a * n *
        np.sum(
            (
                media_dia.values
                - media_general
            ) ** 2
        )
    )

    SC_AD = 0.0

    for analista in df["Analista"].cat.categories:

        for dia in df["Dia"].cat.categories:

            media_ij = media_celda.loc[
                (analista, dia)
            ]

            efecto = (
                media_ij
                - media_analista.loc[analista]
                - media_dia.loc[dia]
                + media_general
            )

            SC_AD += (
                n * efecto ** 2
            )

    SC_E = 0.0

    for _, fila in df.iterrows():

        media_ij = media_celda.loc[
            (
                fila["Analista"],
                fila["Dia"]
            )
        ]

        SC_E += (
            fila["Resultado"]
            - media_ij
        ) ** 2

    tabla = pd.DataFrame(
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

    tabla["MC"] = (
        tabla["SC"]
        / tabla["GL"]
    )

    # Pruebas para diseño cruzado:
    # Analista y Día contra Analista×Día
    # Analista×Día contra Error.

    F_A = (
        tabla.loc["Analista", "MC"]
        / tabla.loc["Analista*Día", "MC"]
    )

    F_D = (
        tabla.loc["Día", "MC"]
        / tabla.loc["Analista*Día", "MC"]
    )

    F_AD = (
        tabla.loc["Analista*Día", "MC"]
        / tabla.loc["Error", "MC"]
    )

    tabla["F"] = np.nan
    tabla["p"] = np.nan

    tabla.loc["Analista", "F"] = F_A
    tabla.loc["Analista", "p"] = f.sf(
        F_A,
        a - 1,
        (a - 1) * (b - 1)
    )

    tabla.loc["Día", "F"] = F_D
    tabla.loc["Día", "p"] = f.sf(
        F_D,
        b - 1,
        (a - 1) * (b - 1)
    )

    tabla.loc["Analista*Día", "F"] = F_AD
    tabla.loc["Analista*Día", "p"] = f.sf(
        F_AD,
        (a - 1) * (b - 1),
        a * b * (n - 1)
    )

    return tabla


# ============================================================
# 4. COMPONENTES DE VARIANZA
# ============================================================

def calcular_componentes(tabla, diseno):

    a = diseno["a"]
    b = diseno["b"]
    n = diseno["n"]

    MS_A = tabla.loc[
        "Analista", "MC"
    ]

    MS_D = tabla.loc[
        "Día", "MC"
    ]

    MS_AD = tabla.loc[
        "Analista*Día", "MC"
    ]

    MS_E = tabla.loc[
        "Error", "MC"
    ]

    # Componentes del modelo:
    #
    # Y = μ + A + D + A×D + e

    var_A = (
        MS_A - MS_AD
    ) / (b * n)

    var_D = (
        MS_D - MS_AD
    ) / (a * n)

    var_AD = (
        MS_AD - MS_E
    ) / n

    var_E = MS_E

    # Para la contribución total, un componente negativo
    # aporta cero, siguiendo la salida de Minitab.

    vA = max(var_A, 0)
    vD = max(var_D, 0)
    vAD = max(var_AD, 0)
    vE = max(var_E, 0)

    var_total = (
        vA + vD + vAD + vE
    )

    sd_A = np.sqrt(vA)
    sd_D = np.sqrt(vD)
    sd_AD = np.sqrt(vAD)
    sd_E = np.sqrt(vE)

    SI = np.sqrt(
        max(var_total, 0)
    )

    if var_total > 0:

        pct_var = [
            100 * vA / var_total,
            100 * vD / var_total,
            100 * vAD / var_total,
            100 * vE / var_total,
            100
        ]

        pct_sd = [
            100 * sd_A / SI,
            100 * sd_D / SI,
            100 * sd_AD / SI,
            100 * sd_E / SI,
            100
        ]

    else:

        pct_var = [0, 0, 0, 0, 100]
        pct_sd = [0, 0, 0, 0, 100]

    tabla = pd.DataFrame(
        {
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

            "% del total": pct_var,

            "Desv.Est.": [
                sd_A,
                sd_D,
                sd_AD,
                sd_E,
                SI
            ],

            "% de SD total": pct_sd
        }
    )

    return tabla, var_total, SI


# ============================================================
# 5. REML
# ============================================================

def calcular_reml(df, diseno):

    df_reml = df.copy()

    df_reml["Analista_Dia"] = (
        df_reml["Analista"].astype(str)
        + ":"
        + df_reml["Dia"].astype(str)
    )

    modelo_reml = MixedLM.from_formula(
        "Resultado ~ 1",

        groups=np.ones(
            len(df_reml)
        ),

        re_formula="0",

        vc_formula={
            "Analista":
                "0 + Analista",

            "Dia":
                "0 + Dia",

            "Analista_Dia":
                "0 + Analista_Dia"
        },

        data=df_reml
    )

    # --------------------------------------------------------
    # REML robusto:
    # se prueban varios optimizadores si el primero falla.
    #
    # IMPORTANTE:
    # No usamos C(Analista), C(Dia), etc. en vc_formula.
    # En un notebook Jupyter, C puede haber quedado definido
    # como una variable numérica en una ejecución anterior y
    # Patsy podría intentar evaluar C(...) como si fuera una
    # función. Las columnas son categóricas, por lo que Patsy
    # puede codificarlas directamente.
    # --------------------------------------------------------

    metodos = [
        ("lbfgs", {"maxiter": 2000}),
        ("powell", {"maxiter": 2000}),
        ("cg", {"maxiter": 2000})
    ]

    resultado = None
    metodo_usado = None
    advertencias = []

    for metodo, opciones in metodos:

        try:

            with warnings.catch_warnings(
                record=True
            ) as avisos:

                warnings.simplefilter(
                    "always"
                )

                candidato = modelo_reml.fit(
                    reml=True,
                    method=metodo,
                    disp=False,
                    **opciones
                )

                advertencias.extend(
                    [str(a.message) for a in avisos]
                )

            # Algunos optimizadores pueden devolver un objeto
            # aunque no hayan convergido.
            if candidato is not None:

                resultado = candidato
                metodo_usado = metodo

                if resultado.converged:
                    break

        except Exception as error:

            advertencias.append(
                f"{metodo}: {error}"
            )

    # Si ningún método produjo resultado, devolver un estado
    # controlado en lugar de dejar resultado=None.
    if resultado is None:

        return (
            None,
            np.nan,
            np.nan,
            None,
            advertencias,
            None,
            False
        )

    nombres = (
        resultado.model.exog_vc.names
    )

    valores = resultado.vcomp

    componentes = dict(
        zip(
            nombres,
            valores
        )
    )

    var_A = max(
        float(
            componentes.get(
                "Analista",
                0
            )
        ),
        0
    )

    var_D = max(
        float(
            componentes.get(
                "Dia",
                0
            )
        ),
        0
    )

    var_AD = max(
        float(
            componentes.get(
                "Analista_Dia",
                0
            )
        ),
        0
    )

    var_E = max(
        float(
            resultado.scale
        ),
        0
    )

    var_total = (
        var_A
        + var_D
        + var_AD
        + var_E
    )

    SI = np.sqrt(
        var_total
    )

    sd_A = np.sqrt(var_A)
    sd_D = np.sqrt(var_D)
    sd_AD = np.sqrt(var_AD)
    sd_E = np.sqrt(var_E)

    if var_total > 0:

        pct_var = [
            100 * var_A / var_total,
            100 * var_D / var_total,
            100 * var_AD / var_total,
            100 * var_E / var_total,
            100
        ]

        pct_sd = [
            100 * sd_A / SI,
            100 * sd_D / SI,
            100 * sd_AD / SI,
            100 * sd_E / SI,
            100
        ]

    else:

        pct_var = [0, 0, 0, 0, 100]
        pct_sd = [0, 0, 0, 0, 100]

    tabla = pd.DataFrame(
        {
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

            "% del total": pct_var,

            "Desv.Est.": [
                sd_A,
                sd_D,
                sd_AD,
                sd_E,
                SI
            ],

            "% de SD total": pct_sd
        }
    )

    return (
        tabla,
        var_total,
        SI,
        resultado,
        advertencias,
        metodo_usado,
        bool(resultado.converged)
    )


# ============================================================
# 6. MOSTRAR RESULTADOS DE CADA NIVEL
# ============================================================

def mostrar_nivel(
    hoja,
    diseno,
    tab_I,
    vc_I,
    tab_III,
    vc_III,
    vc_REML,
    SI_REML,
    resultado_reml,
    metodo_reml,
    reml_ok
):

    print("\n\n")
    print("#" * 100)
    print(
        f"NIVEL DE CONCENTRACIÓN: {hoja}"
    )
    print("#" * 100)

    print("\nINFORMACIÓN DEL DISEÑO")

    print(
        f"Analistas: {diseno['a']} | "
        f"{', '.join(map(str, diseno['analistas']))}"
    )

    print(
        f"Días: {diseno['b']} | "
        f"{', '.join(map(str, diseno['dias']))}"
    )

    print(
        f"Réplicas por celda: {diseno['n']}"
    )

    print(
        f"Observaciones: {diseno['observaciones']}"
    )

    # --------------------------------------------------------
    # Tipo I
    # --------------------------------------------------------

    print("\nANOVA — TIPO I — SC SECUENCIAL")
    print(
        tab_I[
            ["GL", "SC", "MC", "F", "p"]
        ].to_string(
            formatters={
                "GL":
                    lambda x: f"{int(x)}",

                "SC":
                    lambda x: f"{x:.9f}",

                "MC":
                    lambda x: f"{x:.9f}",

                "F":
                    lambda x:
                    ""
                    if pd.isna(x)
                    else f"{x:.3f}",

                "p":
                    lambda x:
                    ""
                    if pd.isna(x)
                    else f"{x:.4f}"
            }
        )
    )

    print("\nCOMPONENTES DE VARIANZA — TIPO I")

    print(
        vc_I.to_string(
            index=False,
            formatters={
                "Varianza":
                    lambda x: f"{x:.9f}",

                "% del total":
                    lambda x: f"{x:.2f}%",

                "Desv.Est.":
                    lambda x: f"{x:.7f}",

                "% de SD total":
                    lambda x: f"{x:.2f}%"
            }
        )
    )

    # --------------------------------------------------------
    # Tipo III
    # --------------------------------------------------------

    print("\nANOVA — TIPO III — SC AJUSTADA")

    print(
        tab_III[
            ["GL", "SC", "MC", "F", "p"]
        ].to_string(
            formatters={
                "GL":
                    lambda x: f"{int(x)}",

                "SC":
                    lambda x: f"{x:.9f}",

                "MC":
                    lambda x: f"{x:.9f}",

                "F":
                    lambda x:
                    ""
                    if pd.isna(x)
                    else f"{x:.3f}",

                "p":
                    lambda x:
                    ""
                    if pd.isna(x)
                    else f"{x:.4f}"
            }
        )
    )

    print("\nCOMPONENTES DE VARIANZA — TIPO III")

    print(
        vc_III.to_string(
            index=False,
            formatters={
                "Varianza":
                    lambda x: f"{x:.9f}",

                "% del total":
                    lambda x: f"{x:.2f}%",

                "Desv.Est.":
                    lambda x: f"{x:.7f}",

                "% de SD total":
                    lambda x: f"{x:.2f}%"
            }
        )
    )

    # --------------------------------------------------------
    # REML
    # --------------------------------------------------------

    print("\nCOMPONENTES DE VARIANZA — REML")

    print(
        f"Convergencia REML: "
        f"{'Sí' if reml_ok else 'No'}"
    )

    if metodo_reml is not None:
        print(
            f"Optimizador utilizado: {metodo_reml}"
        )

    if not reml_ok:
        print(
            "REML no produjo una estimación válida "
            "para este nivel."
        )

    print(
        vc_REML.to_string(
            index=False,
            formatters={
                "Varianza":
                    lambda x: f"{x:.9f}",

                "% del total":
                    lambda x: f"{x:.2f}%",

                "Desv.Est.":
                    lambda x: f"{x:.7f}",

                "% de SD total":
                    lambda x: f"{x:.2f}%"
            }
        )
    )

    print("\nSI DEL NIVEL")

    print(
        f"Tipo I   → SI² = "
        f"{vc_I.loc[vc_I['Fuente']=='Total','Varianza'].iloc[0]:.9f}"
        f" | SI = "
        f"{vc_I.loc[vc_I['Fuente']=='Total','Desv.Est.'].iloc[0]:.7f}"
    )

    print(
        f"Tipo III → SI² = "
        f"{vc_III.loc[vc_III['Fuente']=='Total','Varianza'].iloc[0]:.9f}"
        f" | SI = "
        f"{vc_III.loc[vc_III['Fuente']=='Total','Desv.Est.'].iloc[0]:.7f}"
    )

    print(
        f"REML     → SI² = "
        f"{SI_REML**2:.9f}"
        f" | SI = "
        f"{SI_REML:.7f}"
    )


# ============================================================
# 7. PROCESAR TODAS LAS HOJAS / NIVELES
# ============================================================

excel = pd.ExcelFile(
    archivo
)

print("\n")
print("=" * 80)
print("HOJAS / NIVELES ENCONTRADOS")
print("=" * 80)

for hoja in excel.sheet_names:
    print("-", hoja)


resultados_niveles = []


for hoja in excel.sheet_names:

    df = preparar_nivel(
        archivo,
        hoja
    )

    diseno = diagnosticar_diseno(
        df,
        hoja
    )

    tab_I = calcular_tipo_I(
        df,
        diseno
    )

    # En un diseño cruzado completo y balanceado,
    # Tipo I y Tipo III coinciden.
    tab_III = tab_I.copy()

    vc_I, var_I, SI_I = (
        calcular_componentes(
            tab_I,
            diseno
        )
    )

    vc_III, var_III, SI_III = (
        calcular_componentes(
            tab_III,
            diseno
        )
    )

    (
        vc_REML,
        var_REML,
        SI_REML,
        resultado_reml,
        advertencias,
        metodo_reml,
        reml_ok
    ) = calcular_reml(
        df,
        diseno
    )

    if not reml_ok:

        print(
            f"\nADVERTENCIA: REML no convergió "
            f"en el nivel '{hoja}'."
        )

        if advertencias:

            print(
                "Detalle de los intentos:"
            )

            for aviso in advertencias[-6:]:
                print(
                    " -", aviso
                )

        vc_REML = pd.DataFrame(
            {
                "Fuente": [
                    "Analista",
                    "Día",
                    "Analista*Día",
                    "Error",
                    "Total"
                ],

                "Varianza": [
                    np.nan
                ] * 5,

                "% del total": [
                    np.nan
                ] * 5,

                "Desv.Est.": [
                    np.nan
                ] * 5,

                "% de SD total": [
                    np.nan
                ] * 5
            }
        )

        var_REML = np.nan
        SI_REML = np.nan
        resultado_reml = None

    # --------------------------------------------------------
    # Concentración del nivel
    # --------------------------------------------------------
    #
    # Igual que el script de repetibilidad:
    # promedio general de todos los resultados.
    # --------------------------------------------------------

    concentracion_nivel = (
        df["Resultado"]
        .mean()
    )

    mostrar_nivel(
        hoja,
        diseno,
        tab_I,
        vc_I,
        tab_III,
        vc_III,
        vc_REML,
        SI_REML,
        resultado_reml,
        metodo_reml,
        reml_ok
    )

    resultados_niveles.append(
        {
            "Nivel": hoja,
            "Concentración": concentracion_nivel,

            "SI Tipo I":
                SI_I,

            "SI Tipo III":
                SI_III,

            "SI REML":
                SI_REML,

            "SI² Tipo I":
                var_I,

            "SI² Tipo III":
                var_III,

            "SI² REML":
                var_REML,

            "REML convergió":
                reml_ok
        }
    )


# ============================================================
# 8. TABLA GENERAL DE LOS NIVELES
# ============================================================

tabla_niveles = pd.DataFrame(
    resultados_niveles
)

print("\n\n")
print("#" * 105)
print("RESUMEN DE PRECISIÓN INTERMEDIA POR NIVEL")
print("#" * 105)

display(
    tabla_niveles.style.format(
        {
            "Concentración":
                "{:.6f}",

            "SI Tipo I":
                "{:.7f}",

            "SI Tipo III":
                "{:.7f}",

            "SI REML":
                lambda x:
                ""
                if pd.isna(x)
                else f"{x:.7f}",

            "SI² Tipo I":
                "{:.9f}",

            "SI² Tipo III":
                "{:.9f}",

            "SI² REML":
                lambda x:
                ""
                if pd.isna(x)
                else f"{x:.9f}"
        }
    )
)


# ============================================================
# 9. SELECCIONAR QUÉ SI UTILIZAR PARA LA REGRESIÓN
# ============================================================
#
# AQUÍ se pregunta qué estimación de precisión intermedia
# se utilizará en la regresión:
#
#   1 = Tipo I
#   2 = Tipo III
#   3 = REML
#
# No se elige un SI individual de un nivel.
# Se elige el MÉTODO con el que se obtuvieron los SI de todos
# los niveles.
# ============================================================

print("\n")
print("=" * 85)
print("SELECCIÓN DE LA DESVIACIÓN ESTÁNDAR DE PRECISIÓN INTERMEDIA")
print("=" * 85)

print(
    "\nSeleccione qué estimación de SI desea utilizar "
    "para la regresión %RSD vs concentración:"
)

print(
    "\n1. Tipo I  — SC secuencial"
)

print(
    "2. Tipo III — SC ajustada"
)

print(
    "3. REML"
)

opcion_SI = int(
    input(
        "\nIngrese el número del método de SI seleccionado: "
    )
)

if opcion_SI not in [1, 2, 3]:

    raise ValueError(
        "La opción de SI no es válida."
    )


mapa_SI = {
    1: "SI Tipo I",
    2: "SI Tipo III",
    3: "SI REML"
}

metodo_SI = mapa_SI[
    opcion_SI
]

if (
    opcion_SI == 3
    and (
        tabla_niveles["SI REML"].isna().any()
        or ~tabla_niveles["REML convergió"]
    ).any()
):

    raise ValueError(
        "Se seleccionó REML, pero uno o más niveles "
        "no tienen una estimación REML válida."
    )


# ============================================================
# 10. PREPARAR DATOS PARA LA REGRESIÓN
# ============================================================

concentraciones = (
    tabla_niveles[
        "Concentración"
    ]
    .to_numpy(
        dtype=float
    )
)

SI_niveles = (
    tabla_niveles[
        metodo_SI
    ]
    .to_numpy(
        dtype=float
    )
)

# %RSD de precisión intermedia
#
# %RSD = SI / C × 100

RSD_niveles = (
    SI_niveles
    / concentraciones
) * 100

tabla_regresion = pd.DataFrame(
    {
        "Nivel":
            tabla_niveles["Nivel"],

        "Concentración":
            concentraciones,

        "SI":
            SI_niveles,

        "%RSD":
            RSD_niveles
    }
)

print("\n")
print("#" * 100)
print(
    f"DATOS PARA REGRESIÓN — {metodo_SI}"
)
print("#" * 100)

display(
    tabla_regresion.style.format(
        {
            "Concentración":
                "{:.6f}",

            "SI":
                "{:.7f}",

            "%RSD":
                "{:.6f}"
        }
    )
)


# ============================================================
# 11. DATOS X / Y
# ============================================================

x = np.array(
    concentraciones,
    dtype=float
)

y = np.array(
    RSD_niveles,
    dtype=float
)

if len(x) < 2:

    raise ValueError(
        "Se requieren al menos dos niveles "
        "para realizar una regresión."
    )

if np.any(x <= 0):

    raise ValueError(
        "La concentración debe ser > 0 para "
        "los modelos logarítmico y potencial."
    )

if np.any(y <= 0):

    raise ValueError(
        "%RSD debe ser > 0 para los modelos "
        "exponencial y potencial."
    )


# ============================================================
# 12. MODELOS DE REGRESIÓN
# ============================================================

resultados = []


# ------------------------------------------------------------
# 12.1 LINEAL
# ------------------------------------------------------------

coef = np.polyfit(
    x,
    y,
    1
)

b = coef[0]
a = coef[1]

pred = (
    a + b * x
)

r2 = calcular_r2(
    y,
    pred
)


def modelo_lineal(
    valor,
    a=a,
    b=b
):

    return (
        a + b * valor
    )


resultados.append(
    {
        "Modelo":
            "Lineal",

        "Ecuación":
            f"y = {a:.6f} + {b:.6f}x",

        "R²":
            r2,

        "Funcion":
            modelo_lineal
    }
)


# ------------------------------------------------------------
# 12.2 LOGARÍTMICO
# ------------------------------------------------------------

coef = np.polyfit(
    np.log(x),
    y,
    1
)

b = coef[0]
a = coef[1]

pred = (
    a + b * np.log(x)
)

r2 = calcular_r2(
    y,
    pred
)


def modelo_logaritmico(
    valor,
    a=a,
    b=b
):

    return (
        a + b * np.log(valor)
    )


resultados.append(
    {
        "Modelo":
            "Logarítmico",

        "Ecuación":
            f"y = {a:.6f} + {b:.6f} ln(x)",

        "R²":
            r2,

        "Funcion":
            modelo_logaritmico
    }
)


# ------------------------------------------------------------
# 12.3 EXPONENCIAL
# ------------------------------------------------------------

coef = np.polyfit(
    x,
    np.log(y),
    1
)

b = coef[0]

a = np.exp(
    coef[1]
)

pred = (
    a * np.exp(b * x)
)

r2 = calcular_r2(
    y,
    pred
)


def modelo_exponencial(
    valor,
    a=a,
    b=b
):

    return (
        a * np.exp(b * valor)
    )


resultados.append(
    {
        "Modelo":
            "Exponencial",

        "Ecuación":
            f"y = {a:.6f} e^({b:.6f}x)",

        "R²":
            r2,

        "Funcion":
            modelo_exponencial
    }
)


# ------------------------------------------------------------
# 12.4 POTENCIAL
# ------------------------------------------------------------

coef = np.polyfit(
    np.log(x),
    np.log(y),
    1
)

b = coef[0]

a = np.exp(
    coef[1]
)

pred = (
    a * x ** b
)

r2 = calcular_r2(
    y,
    pred
)


def modelo_potencial(
    valor,
    a=a,
    b=b
):

    return (
        a * valor ** b
    )


resultados.append(
    {
        "Modelo":
            "Potencial",

        "Ecuación":
            f"y = {a:.6f} x^{b:.6f}",

        "R²":
            r2,

        "Funcion":
            modelo_potencial
    }
)


# ------------------------------------------------------------
# 12.5 INVERSO
# ------------------------------------------------------------

coef = np.polyfit(
    1 / x,
    y,
    1
)

b = coef[0]
a = coef[1]

pred = (
    a + b / x
)

r2 = calcular_r2(
    y,
    pred
)


def modelo_inverso(
    valor,
    a=a,
    b=b
):

    return (
        a + b / valor
    )


resultados.append(
    {
        "Modelo":
            "Inverso",

        "Ecuación":
            f"y = {a:.6f} + {b:.6f}/x",

        "R²":
            r2,

        "Funcion":
            modelo_inverso
    }
)


# ------------------------------------------------------------
# 12.6 POLINÓMICO GRADO 2
# ------------------------------------------------------------

if len(x) >= 3:

    coef = np.polyfit(
        x,
        y,
        2
    )

    c = coef[0]
    b = coef[1]
    a = coef[2]

    pred = (
        a
        + b * x
        + c * x ** 2
    )

    r2 = calcular_r2(
        y,
        pred
    )


    def modelo_polinomico(
        valor,
        a=a,
        b=b,
        c=c
    ):

        return (
            a
            + b * valor
            + c * valor ** 2
        )


    resultados.append(
        {
            "Modelo":
                "Polinómico grado 2",

            "Ecuación":
                f"y = {a:.6f} + "
                f"{b:.6f}x + "
                f"{c:.6f}x²",

            "R²":
                r2,

            "Funcion":
                modelo_polinomico
        }
    )


# ============================================================
# 13. COMPARACIÓN DE MODELOS
# ============================================================

tabla_modelos = pd.DataFrame(
    {
        "Modelo": [
            r["Modelo"]
            for r in resultados
        ],

        "Ecuación": [
            r["Ecuación"]
            for r in resultados
        ],

        "R²": [
            r["R²"]
            for r in resultados
        ]
    }
)

print("\n")
print("#" * 100)
print("COMPARACIÓN DE MODELOS")
print("#" * 100)

display(
    tabla_modelos.style.format(
        {
            "R²":
                "{:.6f}"
        }
    )
)


# ============================================================
# 14. GRÁFICAS DE TODOS LOS MODELOS
# ============================================================

for resultado in resultados:

    nombre_modelo = (
        resultado["Modelo"]
    )

    ecuacion = (
        resultado["Ecuación"]
    )

    r2 = (
        resultado["R²"]
    )

    funcion = (
        resultado["Funcion"]
    )

    x_grafico = np.linspace(
        min(x),
        max(x),
        300
    )

    y_grafico = funcion(
        x_grafico
    )

    plt.figure(
        figsize=(9, 5.5),
        dpi=180
    )

    plt.scatter(
        x,
        y,
        s=70,
        label="Datos experimentales"
    )

    plt.plot(
        x_grafico,
        y_grafico,
        linewidth=2,
        label=nombre_modelo
    )

    texto = (
        f"{ecuacion}\n"
        f"R² = {r2:.6f}"
    )

    plt.text(
        0.05,
        0.95,
        texto,
        transform=plt.gca().transAxes,
        verticalalignment="top",
        bbox=dict(
            boxstyle="round",
            facecolor="white",
            alpha=0.9
        )
    )

    plt.xlabel(
        "Concentración"
    )

    plt.ylabel(
        "%RSD de precisión intermedia"
    )

    plt.title(
        f"Modelo {nombre_modelo}\n"
        f"{metodo_SI}"
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.legend()

    plt.tight_layout()

    plt.show()


# ============================================================
# 15. SELECCIÓN MANUAL DEL MODELO
# ============================================================

print("\n")
print("=" * 80)
print("SELECCIÓN DEL MODELO")
print("=" * 80)

for i, resultado in enumerate(
    resultados,
    start=1
):

    print(
        f"{i}. "
        f"{resultado['Modelo']} "
        f"(R² = {resultado['R²']:.6f})"
    )

print(
    "\nSeleccione el modelo que considere "
    "técnicamente apropiado según los resultados "
    "y gráficos."
)

opcion = int(
    input(
        "\nIngrese el número del modelo seleccionado: "
    )
)

if (
    opcion < 1
    or opcion > len(resultados)
):

    raise ValueError(
        "La opción seleccionada no es válida."
    )

seleccionado = resultados[
    opcion - 1
]


# ============================================================
# 16. MODELO SELECCIONADO
# ============================================================

print("\n")
print("=" * 80)
print("MODELO SELECCIONADO")
print("=" * 80)

print(
    f"Estimación utilizada: {metodo_SI}"
)

print(
    f"Modelo: "
    f"{seleccionado['Modelo']}"
)

print(
    f"Ecuación: "
    f"{seleccionado['Ecuación']}"
)

print(
    f"R²: "
    f"{seleccionado['R²']:.6f}"
)


# ============================================================
# 17. CONCENTRACIÓN DE LA MUESTRA
# ============================================================

print("\n")
print("=" * 80)
print(
    "CÁLCULO DE SI PARA UNA MUESTRA"
)
print("=" * 80)

concentracion_muestra = float(
    input(
        "\nIngrese la concentración de la muestra: "
    )
)


# ============================================================
# 18. %RSD ESTIMADO
# ============================================================

funcion = (
    seleccionado["Funcion"]
)

rsd_muestra = funcion(
    concentracion_muestra
)


# ============================================================
# 19. SI ESTIMADA
# ============================================================

SI_muestra = (
    rsd_muestra
    * concentracion_muestra
) / 100


SI2_muestra = (
    SI_muestra ** 2
)


# ============================================================
# 20. RESULTADO FINAL
# ============================================================

print("\n")
print("#" * 90)
print("RESULTADO FINAL — PRECISIÓN INTERMEDIA")
print("#" * 90)

print(
    f"Estimación utilizada: "
    f"{metodo_SI}"
)

print(
    f"Modelo seleccionado: "
    f"{seleccionado['Modelo']}"
)

print(
    f"Ecuación: "
    f"{seleccionado['Ecuación']}"
)

print(
    f"Concentración de la muestra: "
    f"{concentracion_muestra:.6f}"
)

print(
    f"%RSD de precisión intermedia estimado: "
    f"{rsd_muestra:.6f} %"
)

print(
    f"SI² estimada: "
    f"{SI2_muestra:.9f}"
)

print(
    f"SI estimada: "
    f"{SI_muestra:.7f}"
)

print("\n")
print("=" * 90)
print(
    "FIN DEL ANÁLISIS DE PRECISIÓN INTERMEDIA"
)
print("=" * 90)

