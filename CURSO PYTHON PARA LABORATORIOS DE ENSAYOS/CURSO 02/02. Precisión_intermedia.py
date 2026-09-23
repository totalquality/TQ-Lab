# ============================================================
# PRECISIÓN INTERMEDIA — TODOS LOS NIVELES
#
# Cada hoja del Excel representa un nivel de trabajo.
#
# Para CADA NIVEL, de forma independiente:
#
#   1. Detecta Analista × Día × réplicas
#   2. Calcula componentes de varianza Tipo I
#   3. Calcula componentes de varianza Tipo III
#   4. Calcula componentes de varianza mediante REML
#   5. Obtiene SI² y SI para cada alternativa
#   6. Pregunta qué estimación SI se desea evaluar
#   7. Pregunta la concentración del nivel
#   8. Pregunta la unidad
#   9. Calcula %RSD de precisión intermedia
#  10. Calcula Horwitz
#  11. Calcula PRSD intermedia = (2/3) × PRSDR
#  12. Calcula HorRat(r)
#  13. Evalúa 0.3 ≤ HorRat(r) ≤ 1.3
#  14. Evalúa %RSD frente a (2/3) × PRSDR
#  15. Muestra resumen individual del nivel
#
# Finalmente:
#   16. Muestra un resumen general de TODOS los niveles.
#
# Criterios mantenidos del script original:
#   PRSDR = 2 × C^(-0.15)
#   PRSD_intermedia = (2/3) × PRSDR
#   HorRat(r) = %RSD_SI / PRSDR
#   0.3 ≤ HorRat(r) ≤ 1.3
#
# IMPORTANTE:
#   Tipo I y Tipo III se calculan para el diseño cruzado balanceado.
#   REML se utiliza como estimación de componentes de varianza.
# ============================================================


import warnings
from pathlib import Path

import pandas as pd
import numpy as np

from statsmodels.regression.mixed_linear_model import MixedLM


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

archivo = (
    r"D:\Ciencia_de_Datos\Validación de métodos químicos"
    r"\precision_intermedia.xlsx"
)


# ============================================================
# 2. FUNCIONES AUXILIARES
# ============================================================

def preparar_nivel(archivo, hoja):
    """
    Lee una hoja correspondiente a un nivel.

    Se utilizan las primeras tres columnas:
        Analista | Día | Resultado

    Las columnas adicionales se ignoran.
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
        errors="coerce"
    )

    df["Resultado"] = pd.to_numeric(
        df["Resultado"],
        errors="coerce"
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
            "Este script requiere un diseño cruzado "
            "completo y balanceado para los cálculos "
            "Tipo I y Tipo III."
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
# 3. COMPONENTES DE VARIANZA — TIPO I
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
        b * n
        *
        np.sum(
            (
                media_analista
                - media_general
            ) ** 2
        )
    )

    SC_D = (
        a * n
        *
        np.sum(
            (
                media_dia
                - media_general
            ) ** 2
        )
    )

    SC_AD = (
        n
        *
        np.sum(
            [
                (
                    media_celda.loc[
                        analista,
                        dia
                    ]
                    - media_analista.loc[analista]
                    - media_dia.loc[dia]
                    + media_general
                ) ** 2
                for analista in media_analista.index
                for dia in media_dia.index
            ]
        )
    )

    SC_E = np.sum(
        (
            df["Resultado"]
            -
            df.groupby(
                ["Analista", "Dia"],
                observed=True
            )["Resultado"]
            .transform("mean")
        ) ** 2
    )

    gl_A = a - 1
    gl_D = b - 1
    gl_AD = (a - 1) * (b - 1)
    gl_E = a * b * (n - 1)

    MS_A = SC_A / gl_A
    MS_D = SC_D / gl_D
    MS_AD = SC_AD / gl_AD
    MS_E = SC_E / gl_E

    # Componentes de varianza:
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

    var_A_pos = max(float(var_A), 0.0)
    var_D_pos = max(float(var_D), 0.0)
    var_AD_pos = max(float(var_AD), 0.0)
    var_E_pos = max(float(var_E), 0.0)

    var_total = (
        var_A_pos
        + var_D_pos
        + var_AD_pos
        + var_E_pos
    )

    SI = np.sqrt(
        var_total
    )

    anova = pd.DataFrame({
        "Fuente": [
            "Analista",
            "Día",
            "Analista × Día",
            "Error"
        ],
        "SC": [
            SC_A,
            SC_D,
            SC_AD,
            SC_E
        ],
        "GL": [
            gl_A,
            gl_D,
            gl_AD,
            gl_E
        ],
        "MC": [
            MS_A,
            MS_D,
            MS_AD,
            MS_E
        ]
    })

    componentes = pd.DataFrame({
        "Fuente": [
            "Analista",
            "Día",
            "Analista × Día",
            "Error",
            "Total"
        ],
        "Varianza": [
            var_A_pos,
            var_D_pos,
            var_AD_pos,
            var_E_pos,
            var_total
        ],
        "Desviación estándar": [
            np.sqrt(var_A_pos),
            np.sqrt(var_D_pos),
            np.sqrt(var_AD_pos),
            np.sqrt(var_E_pos),
            SI
        ]
    })

    return {
        "anova": anova,
        "componentes": componentes,
        "varianza_SI": var_total,
        "SI": SI
    }


# ============================================================
# 4. COMPONENTES DE VARIANZA — TIPO III
# ============================================================

def calcular_tipo_III(df, resultado_tipo_I):
    """
    En un diseño cruzado completo y balanceado, el diseño es
    ortogonal y las SC Tipo I y Tipo III coinciden.

    Se conserva esta lógica para mantener la equivalencia
    con el procedimiento utilizado previamente.
    """

    anova_I = resultado_tipo_I["anova"].copy()
    componentes_I = resultado_tipo_I["componentes"].copy()

    anova_III = anova_I.copy()

    componentes_III = componentes_I.copy()

    return {
        "anova": anova_III,
        "componentes": componentes_III,
        "varianza_SI": resultado_tipo_I["varianza_SI"],
        "SI": resultado_tipo_I["SI"]
    }


# ============================================================
# 5. COMPONENTES DE VARIANZA — REML
# ============================================================

def calcular_REML(df):

    datos_reml = df.copy()

    datos_reml["Analista_Dia"] = (
        datos_reml["Analista"]
        .astype(str)
        + ":"
        + datos_reml["Dia"]
        .astype(str)
    )

    modelo_reml = MixedLM.from_formula(
        "Resultado ~ 1",
        groups=np.ones(
            len(datos_reml)
        ),
        re_formula="0",
        vc_formula={
            "Analista": "0 + Analista",
            "Dia": "0 + Dia",
            "Analista_Dia": "0 + Analista_Dia"
        },
        data=datos_reml
    )

    with warnings.catch_warnings():

        warnings.simplefilter(
            "ignore"
        )

        try:

            resultado_reml = modelo_reml.fit(
                reml=True,
                method="lbfgs",
                maxiter=2000,
                disp=False
            )

        except Exception:

            resultado_reml = modelo_reml.fit(
                reml=True,
                method="powell",
                maxiter=2000,
                disp=False
            )

    var_A = max(
        float(
            resultado_reml.vcomp[
                0
            ]
        ),
        0.0
    )

    var_D = max(
        float(
            resultado_reml.vcomp[
                1
            ]
        ),
        0.0
    )

    var_AD = max(
        float(
            resultado_reml.vcomp[
                2
            ]
        ),
        0.0
    )

    var_E = max(
        float(
            resultado_reml.scale
        ),
        0.0
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

    componentes = pd.DataFrame({
        "Fuente": [
            "Analista",
            "Día",
            "Analista × Día",
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
        "Desviación estándar": [
            np.sqrt(var_A),
            np.sqrt(var_D),
            np.sqrt(var_AD),
            np.sqrt(var_E),
            SI
        ]
    })

    return {
        "modelo": resultado_reml,
        "componentes": componentes,
        "varianza_SI": var_total,
        "SI": SI
    }


# ============================================================
# 6. SELECCIÓN DE SI
# ============================================================

def seleccionar_SI(
    numero_nivel,
    nombre_nivel,
    tipo_I,
    tipo_III,
    reml
):

    print("\n" + "=" * 90)
    print(
        f"NIVEL {numero_nivel} — {nombre_nivel}"
    )
    print(
        "SELECCIÓN DE LA ESTIMACIÓN DE PRECISIÓN INTERMEDIA"
    )
    print("=" * 90)

    print(
        "\nSeleccione qué estimación de SI desea utilizar "
        "para la evaluación:"
    )

    print(
        "1. Tipo I   — SC secuencial"
    )

    print(
        "2. Tipo III — SC ajustada"
    )

    print(
        "3. REML"
    )

    while True:

        opcion = input(
            f"\n[NIVEL {numero_nivel}: {nombre_nivel}] "
            "Ingrese una opción (1, 2 o 3): "
        ).strip()

        if opcion == "1":

            return (
                "Tipo I — SC secuencial",
                tipo_I["varianza_SI"],
                tipo_I["SI"]
            )

        if opcion == "2":

            return (
                "Tipo III — SC ajustada",
                tipo_III["varianza_SI"],
                tipo_III["SI"]
            )

        if opcion == "3":

            return (
                "REML",
                reml["varianza_SI"],
                reml["SI"]
            )

        print(
            "Opción no válida. Debe seleccionar 1, 2 o 3."
        )


# ============================================================
# 7. SELECCIÓN DE UNIDAD
# ============================================================

def seleccionar_unidad(
    numero_nivel,
    nombre_nivel
):

    print(
        "\nSeleccione la unidad de concentración:"
    )

    print(
        "1. ppm"
    )

    print(
        "2. ppb"
    )

    print(
        "3. %"
    )

    while True:

        opcion = input(
            f"\n[NIVEL {numero_nivel}: {nombre_nivel}] "
            "Ingrese una opción (1, 2 o 3): "
        ).strip()

        if opcion == "1":

            return (
                "ppm",
                1e-6
            )

        if opcion == "2":

            return (
                "ppb",
                1e-9
            )

        if opcion == "3":

            return (
                "%",
                1e-2
            )

        print(
            "Opción no válida. Debe seleccionar 1, 2 o 3."
        )


# ============================================================
# 8. ENCABEZADO
# ============================================================

print("\n" + "#" * 110)
print(
    "PRECISIÓN INTERMEDIA — EVALUACIÓN PARA TODOS LOS NIVELES"
)
print(
    "TIPO I | TIPO III | REML | HORWITZ | HORRAT(r)"
)
print("#" * 110)

print(
    "\nArchivo:"
)

print(
    archivo
)


# ============================================================
# 9. VERIFICAR ARCHIVO
# ============================================================

ruta = Path(
    archivo
)

if not ruta.exists():

    # Permite probar el archivo adjunto dentro del entorno
    # de ejecución. En el equipo del usuario se utiliza
    # siempre la ruta de Windows anterior.

    archivo_adjunto = (
        Path("/mnt/data/files/precision_intermedia.xlsx")
    )

    if not archivo_adjunto.exists():

        archivo_adjunto = (
            Path("/mnt/data/precision_intermedia(1).xlsx")
        )

    if archivo_adjunto.exists():

        archivo = str(
            archivo_adjunto
        )

        print(
            "\nNo se encontró la ruta de Windows."
        )

        print(
            "Se utilizará el archivo adjunto disponible:"
        )

        print(
            archivo
        )

    else:

        raise FileNotFoundError(
            "No se encontró el archivo "
            "precision_intermedia.xlsx."
        )


# ============================================================
# 10. DETECTAR TODOS LOS NIVELES
# ============================================================

datos_excel = pd.read_excel(
    archivo,
    sheet_name=None
)

nombres_niveles = list(
    datos_excel.keys()
)

print("\n" + "=" * 90)
print(
    "NIVELES DETECTADOS"
)
print("=" * 90)

for numero, nombre in enumerate(
    nombres_niveles,
    start=1
):

    print(
        f"{numero} → {nombre}"
    )


# ============================================================
# 11. RESULTADOS GENERALES
# ============================================================

resultados_finales = []


# ============================================================
# 12. PROCESAMIENTO DE CADA NIVEL
# ============================================================

for numero_nivel, nombre_nivel in enumerate(
    nombres_niveles,
    start=1
):

    print("\n\n")

    print(
        "█" * 110
    )

    print(
        f"█  NIVEL {numero_nivel} — {nombre_nivel}"
    )

    print(
        "█  PRECISIÓN INTERMEDIA"
    )

    print(
        "█  El análisis de este nivel es independiente "
        "de los demás niveles."
    )

    print(
        "█" * 110
    )


    # ========================================================
    # 12.1 PREPARAR DATOS
    # ========================================================

    df = preparar_nivel(
        archivo,
        nombre_nivel
    )

    diseno = diagnosticar_diseno(
        df,
        nombre_nivel
    )

    print("\nDISEÑO DETECTADO")

    print(
        f"Analistas       = {diseno['a']}"
    )

    print(
        f"Días            = {diseno['b']}"
    )

    print(
        f"Réplicas/celda  = {diseno['n']}"
    )

    print(
        f"Observaciones   = {diseno['observaciones']}"
    )

    print(
        f"Analistas       = {diseno['analistas']}"
    )

    print(
        f"Días            = {diseno['dias']}"
    )


    # ========================================================
    # 12.2 TIPO I
    # ========================================================

    resultado_tipo_I = calcular_tipo_I(
        df,
        diseno
    )

    print("\n" + "-" * 90)
    print(
        "COMPONENTES DE VARIANZA — TIPO I"
    )
    print("-" * 90)

    display(
        resultado_tipo_I["componentes"]
    )

    print(
        f"\nSI² Tipo I = "
        f"{resultado_tipo_I['varianza_SI']:.9f}"
    )

    print(
        f"SI Tipo I = "
        f"{resultado_tipo_I['SI']:.7f}"
    )


    # ========================================================
    # 12.3 TIPO III
    # ========================================================

    resultado_tipo_III = calcular_tipo_III(
        df,
        resultado_tipo_I
    )

    print("\n" + "-" * 90)
    print(
        "COMPONENTES DE VARIANZA — TIPO III"
    )
    print("-" * 90)

    display(
        resultado_tipo_III["componentes"]
    )

    print(
        f"\nSI² Tipo III = "
        f"{resultado_tipo_III['varianza_SI']:.9f}"
    )

    print(
        f"SI Tipo III = "
        f"{resultado_tipo_III['SI']:.7f}"
    )


    # ========================================================
    # 12.4 REML
    # ========================================================

    resultado_REML = calcular_REML(
        df
    )

    print("\n" + "-" * 90)
    print(
        "COMPONENTES DE VARIANZA — REML"
    )
    print("-" * 90)

    display(
        resultado_REML["componentes"]
    )

    print(
        f"\nSI² REML = "
        f"{resultado_REML['varianza_SI']:.9f}"
    )

    print(
        f"SI REML = "
        f"{resultado_REML['SI']:.7f}"
    )


    # ========================================================
    # 12.5 RESUMEN DE LAS TRES ESTIMACIONES
    # ========================================================

    comparacion_SI = pd.DataFrame({

        "N°": [
            1,
            2,
            3
        ],

        "Estimación": [
            "Tipo I — SC secuencial",
            "Tipo III — SC ajustada",
            "REML"
        ],

        "SI²": [
            resultado_tipo_I["varianza_SI"],
            resultado_tipo_III["varianza_SI"],
            resultado_REML["varianza_SI"]
        ],

        "SI": [
            resultado_tipo_I["SI"],
            resultado_tipo_III["SI"],
            resultado_REML["SI"]
        ]
    })

    # Reiniciar el índice para evitar que aparezca 0, 1, 2
    # como numeración automática de pandas.
    comparacion_SI.index = [1, 2, 3]

    print("\n" + "=" * 90)
    print(
        f"COMPARACIÓN DE SI — {nombre_nivel}"
    )
    print("=" * 90)

    display(
        comparacion_SI.style.hide(axis="index")
    )


    # ========================================================
    # 12.6 SELECCIONAR SI PARA EVALUACIÓN
    # ========================================================

    metodo_SI, varianza_SI, SD_SI = seleccionar_SI(
        numero_nivel,
        nombre_nivel,
        resultado_tipo_I,
        resultado_tipo_III,
        resultado_REML
    )

    print(
        "\nEstimación seleccionada:"
    )

    print(
        metodo_SI
    )

    print(
        f"Desviación estándar de precisión intermedia "
        f"(SI) = {SD_SI:.7f}"
    )


    # ========================================================
    # 12.7 CONCENTRACIÓN DEL NIVEL
    # ========================================================

    print("\n" + "-" * 90)

    print(
        f"NIVEL {numero_nivel} — {nombre_nivel}"
    )

    print(
        "INGRESO DE LA CONCENTRACIÓN"
    )

    print("-" * 90)

    while True:

        try:

            concentracion_nivel = float(
                input(
                    f"[NIVEL {numero_nivel}: {nombre_nivel}] "
                    "Ingrese la concentración del nivel: "
                )
                .replace(",", ".")
            )

            if concentracion_nivel > 0:
                break

            print(
                "La concentración debe ser mayor que cero."
            )

        except ValueError:

            print(
                "Ingrese un valor numérico válido."
            )


    # ========================================================
    # 12.8 UNIDAD
    # ========================================================

    unidad, factor_masico = seleccionar_unidad(
        numero_nivel,
        nombre_nivel
    )


    # ========================================================
    # 12.9 %RSD DE PRECISIÓN INTERMEDIA
    # ========================================================

    RSD_SI = (
        SD_SI
        /
        concentracion_nivel
    ) * 100


    # ========================================================
    # 12.10 FRACCIÓN MÁSICA
    # ========================================================

    # Se evita utilizar el nombre "C" para no interferir
    # con nombres utilizados por Patsy/statsmodels.

    C_nivel = (
        concentracion_nivel
        *
        factor_masico
    )

    if C_nivel <= 0:

        raise ValueError(
            "La fracción másica de la concentración "
            "debe ser mayor que cero."
        )


    # ========================================================
    # 12.11 HORWITZ — REPRODUCIBILIDAD
    # ========================================================

    PRSDR = (
        2
        *
        (
            C_nivel ** (-0.15)
        )
    )


    # ========================================================
    # 12.12 PRECISIÓN INTERMEDIA — HORWITZ
    # ========================================================
    #
    # PRSD_intermedia = (2/3) × PRSDR
    # ========================================================

    factor_intermedia = (
        2 / 3
    )

    PRSD_intermedia = (
        factor_intermedia
        *
        PRSDR
    )


    # ========================================================
    # 12.13 HORRAT(r)
    # ========================================================

    HorRat_r = (
        RSD_SI
        /
        PRSDR
    )


    if (
        0.3
        <= HorRat_r
        <= 1.3
    ):

        conclusion_horrat = (
            "PASA"
        )

    else:

        conclusion_horrat = (
            "NO PASA"
        )


    # ========================================================
    # 12.14 COMPARACIÓN CONTRA OBJETIVO INTERMEDIO
    # ========================================================

    if (
        RSD_SI
        <=
        PRSD_intermedia
    ):

        conclusion_objetivo = (
            "PASA"
        )

    else:

        conclusion_objetivo = (
            "NO PASA"
        )


    # ========================================================
    # 12.15 RESULTADOS HORWITZ
    # ========================================================

    print("\n" + "=" * 90)

    print(
        f"EVALUACIÓN DE PRECISIÓN INTERMEDIA FRENTE "
        f"A HORWITZ — {nombre_nivel}"
    )

    print("=" * 90)

    print(
        f"Estimación utilizada              = "
        f"{metodo_SI}"
    )

    print(
        f"Concentración del nivel           = "
        f"{concentracion_nivel:.6g} {unidad}"
    )

    print(
        f"SI                                 = "
        f"{SD_SI:.7f}"
    )

    print(
        f"%RSD precisión intermedia         = "
        f"{RSD_SI:.4f} %"
    )

    print(
        f"Fracción másica C                  = "
        f"{C_nivel:.6e}"
    )

    print(
        f"%RSD Horwitz — reproducibilidad   = "
        f"{PRSDR:.4f} %"
    )

    print(
        f"Factor intermedia                 = "
        f"{factor_intermedia:.6f} (2/3)"
    )

    print(
        f"%RSD Horwitz — precisión intermedia "
        f"= {PRSD_intermedia:.4f} %"
    )

    print(
        f"HorRat(r)                          = "
        f"{HorRat_r:.4f}"
    )

    print(
        "Criterio HorRat(r)                = "
        "0.3 ≤ HorRat(r) ≤ 1.3"
    )

    print(
        f"Conclusión HorRat(r)              = "
        f"{conclusion_horrat}"
    )

    print(
        f"Conclusión frente a (2/3)×PRSDR   = "
        f"{conclusion_objetivo}"
    )


    # ========================================================
    # 12.16 CONCLUSIÓN
    # ========================================================

    print("\nCONCLUSIÓN")
    print("-" * 90)

    if conclusion_horrat == "PASA":

        print(
            "El %RSD de precisión intermedia se encuentra "
            "dentro del intervalo de referencia establecido "
            "para HorRat(r) (0.3–1.3)."
        )

    else:

        print(
            "El %RSD de precisión intermedia se encuentra "
            "fuera del intervalo de referencia establecido "
            "para HorRat(r) (0.3–1.3)."
        )


    if conclusion_objetivo == "PASA":

        print(
            "Además, el %RSD de precisión intermedia es "
            "menor o igual al objetivo definido como "
            "(2/3) × PRSDR."
        )

    else:

        print(
            "Además, el %RSD de precisión intermedia supera "
            "el objetivo definido como (2/3) × PRSDR."
        )


    # ========================================================
    # 12.17 RESUMEN DEL NIVEL
    # ========================================================

    resumen_nivel = pd.DataFrame({

        "Indicador": [

            "Nivel",

            "Estimación SI utilizada",

            "Concentración",

            "Unidad",

            "Factor de conversión",

            "Fracción másica C",

            "Varianza SI (SI²)",

            "SI",

            "%RSD precisión intermedia",

            "%RSD Horwitz — reproducibilidad",

            "%RSD Horwitz — intermedia (2/3×PRSDR)",

            "HorRat(r)",

            "Criterio HorRat(r)",

            "Resultado HorRat(r)",

            "Resultado frente a (2/3)×PRSDR"
        ],

        "Resultado": [

            nombre_nivel,

            metodo_SI,

            f"{concentracion_nivel:.6g}",

            unidad,

            f"{factor_masico:.0e}",

            f"{C_nivel:.6e}",

            f"{varianza_SI:.9f}",

            f"{SD_SI:.7f}",

            f"{RSD_SI:.4f} %",

            f"{PRSDR:.4f} %",

            f"{PRSD_intermedia:.4f} %",

            f"{HorRat_r:.4f}",

            "0.3 – 1.3",

            conclusion_horrat,

            conclusion_objetivo
        ]
    })


    print("\n" + "=" * 90)

    print(
        f"RESUMEN DE PRECISIÓN INTERMEDIA — "
        f"{nombre_nivel}"
    )

    print("=" * 90)

    display(
        resumen_nivel
    )


    # ========================================================
    # 12.18 GUARDAR EN RESUMEN GENERAL
    # ========================================================

    resultados_finales.append({

        "Nivel":
            nombre_nivel,

        "Analistas":
            diseno["a"],

        "Días":
            diseno["b"],

        "Réplicas/celda":
            diseno["n"],

        "SI utilizada":
            metodo_SI,

        "Concentración":
            concentracion_nivel,

        "Unidad":
            unidad,

        "SI²":
            varianza_SI,

        "SI":
            SD_SI,

        "%RSD intermedia":
            RSD_SI,

        "PRSDR Horwitz":
            PRSDR,

        "PRSD intermedia (2/3)":
            PRSD_intermedia,

        "HorRat(r)":
            HorRat_r,

        "Resultado HorRat(r)":
            conclusion_horrat,

        "Resultado (2/3)×PRSDR":
            conclusion_objetivo
    })


    # ========================================================
    # 12.19 FIN DEL NIVEL
    # ========================================================

    print("\n" + "─" * 110)

    print(
        f"FIN DEL NIVEL {numero_nivel} — {nombre_nivel}"
    )

    print("─" * 110)


# ============================================================
# 13. RESUMEN GENERAL DE TODOS LOS NIVELES
# ============================================================

print("\n\n")

print(
    "#" * 120
)

print(
    "RESUMEN FINAL — PRECISIÓN INTERMEDIA PARA TODOS LOS NIVELES"
)

print(
    "#" * 120
)


if resultados_finales:

    resumen_general = pd.DataFrame(
        resultados_finales
    )

    display(
        resumen_general
    )

else:

    print(
        "No se obtuvieron resultados para ningún nivel."
    )


# ============================================================
# 14. FIN
# ============================================================

print("\n" + "#" * 120)

print(
    "ANÁLISIS DE PRECISIÓN INTERMEDIA PARA TODOS "
    "LOS NIVELES TERMINADO"
)

print("#" * 120)
