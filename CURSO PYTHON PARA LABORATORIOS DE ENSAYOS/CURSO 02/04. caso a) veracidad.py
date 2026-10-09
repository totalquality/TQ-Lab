# ============================================================
# VERACIDAD — MÉTODO A: MATERIAL DE REFERENCIA CERTIFICADO
#
# Flujo:
# 1. Lee automáticamente todas las hojas del Excel.
# 2. Cada hoja representa un nivel de concentración.
# 3. Pregunta qué prueba utilizar:
#       1 -> t de Student de una muestra
#       2 -> T de Wilcoxon de una muestra
# 4. Para cada nivel solicita el valor de referencia del MRC.
# 5. Realiza la prueba estadística.
# 6. Aplica el criterio de aceptación de la presentación:
#       p >= alfa -> se acepta H0 -> método veraz
#       p <  alfa -> se rechaza H0 -> método no veraz
# 7. Genera una gráfica para cada nivel.
#
#
# ============================================================

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy import stats


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

archivo = (
    r"D:\Ciencia_de_Datos\Validación de métodos químicos"
    r"\veracidad.xlsx"
)

alpha = 0.05


# ============================================================
# 2. FUNCIONES GENERALES
# ============================================================

def obtener_decision(p_valor):
    """
    Criterio indicado en la presentación:

        p >= alpha -> se acepta H0
        p <  alpha -> se rechaza H0
    """

    if p_valor >= alpha:
        return (
            "SE ACEPTA H₀",
            "El método es veraz; "
            "no se evidencian diferencias significativas."
        )

    return (
        "SE RECHAZA H₀",
        "El método no es veraz; "
        "se evidencian diferencias significativas."
    )


def leer_valor_referencia(nombre_nivel):
    """
    Solicita el valor certificado/asignado del MRC
    para el nivel que se está evaluando.
    """

    while True:
        try:
            return float(
                input(
                    f"\nIngrese el valor de referencia del MRC "
                    f"para {nombre_nivel}: "
                )
            )
        except ValueError:
            print("Ingrese un valor numérico válido.")


def preparar_datos(hoja):
    """
    Convierte todas las columnas numéricas de una hoja
    en un único vector de resultados.

    Ejemplo:
        A1, A2, A3
        10 resultados por columna

    Resultado:
        30 observaciones para el nivel.
    """

    columnas_numericas = (
        hoja.select_dtypes(
            include=np.number
        ).columns.tolist()
    )

    if len(columnas_numericas) == 0:
        raise ValueError(
            "La hoja no contiene columnas numéricas."
        )

    grupos = []

    for columna in columnas_numericas:

        datos_columna = pd.to_numeric(
            hoja[columna],
            errors="coerce"
        ).dropna()

        if len(datos_columna) > 0:
            grupos.append(datos_columna)

    if len(grupos) == 0:
        raise ValueError(
            "No existen resultados numéricos válidos "
            "en la hoja."
        )

    datos = pd.concat(
        grupos,
        ignore_index=True
    )

    return columnas_numericas, datos


def mostrar_descriptiva(
    nombre_nivel,
    datos,
    referencia
):

    print()
    print("=" * 80)
    print(
        f"ESTADÍSTICA DESCRIPTIVA — {nombre_nivel}"
    )
    print("=" * 80)

    print()

    print(f"N                  = {len(datos)}")
    print(f"Media              = {datos.mean():.6f}")
    print(f"Mediana            = {datos.median():.6f}")
    print(
        f"Desv. estándar     = "
        f"{datos.std(ddof=1):.6f}"
    )
    print(f"Mínimo             = {datos.min():.6f}")
    print(f"Máximo             = {datos.max():.6f}")
    print(
        f"Valor de referencia = "
        f"{referencia:.6f}"
    )

    print()


# ============================================================
# 3. GRÁFICA — t DE STUDENT DE UNA MUESTRA
# ============================================================

def grafica_t_student(
    nombre_nivel,
    datos,
    referencia,
    t_calculado,
    t_critico,
    p_valor,
    decision,
    conclusion
):

    n = len(datos)

    media = datos.mean()

    sd = datos.std(
        ddof=1
    )

    gl = n - 1

    error_estandar = (
        sd / np.sqrt(n)
    )

    margen_error = (
        t_critico
        * error_estandar
    )

    ic_inferior = (
        media - margen_error
    )

    ic_superior = (
        media + margen_error
    )

    fig = plt.figure(
        figsize=(14, 7)
    )

    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[3.5, 1.5],
        wspace=0.08
    )

    ax = fig.add_subplot(gs[0])
    ax_info = fig.add_subplot(gs[1])

    # IC 95 % de la media
    ax.errorbar(
        media,
        0,
        xerr=[
            [media - ic_inferior],
            [ic_superior - media]
        ],
        fmt="o",
        markersize=10,
        capsize=7,
        linewidth=2.5
    )

    # Valor de referencia
    ax.axvline(
        referencia,
        linestyle="--",
        linewidth=2,
        color="red",
        label="Valor de referencia (MRC)"
    )

    # Media
    ax.axvline(
        media,
        linestyle=":",
        linewidth=2,
        label="Media experimental"
    )

    ax.set_yticks([0])

    ax.set_yticklabels(
        [nombre_nivel]
    )

    ax.set_xlabel(
        "Resultado",
        fontsize=12
    )

    ax.set_title(
        "IC 95 % de la media vs. valor de referencia",
        fontsize=14,
        fontweight="bold"
    )

    ax.grid(
        axis="x",
        alpha=0.20
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend()

    # Panel de resultados
    ax_info.axis("off")

    ax_info.text(
        0.05,
        0.95,
        "RESULTADO ESTADÍSTICO",
        fontsize=15,
        fontweight="bold",
        transform=ax_info.transAxes,
        verticalalignment="top"
    )

    ax_info.text(
        0.05,
        0.82,
        (
            f"N = {n}\n"
            f"gl = {gl}\n\n"
            f"Media = {media:.6f}\n"
            f"Referencia = {referencia:.6f}\n\n"
            f"IC 95 %\n"
            f"{ic_inferior:.6f} – "
            f"{ic_superior:.6f}\n\n"
            f"t calculado = {t_calculado:.6f}\n"
            f"t crítico = {t_critico:.6f}\n\n"
            f"p = {p_valor:.6f}\n\n"
            f"{decision}"
        ),
        fontsize=10.5,
        transform=ax_info.transAxes,
        verticalalignment="top",
        linespacing=1.20
    )

    fig.suptitle(
        f"Veracidad — {nombre_nivel} — t de una muestra",
        fontsize=21,
        fontweight="bold",
        y=0.97
    )

    fig.text(
        0.5,
        0.015,
        conclusion,
        ha="center",
        fontsize=10,
        style="italic"
    )

    plt.tight_layout(
        rect=[0, 0.05, 1, 0.94]
    )

    plt.show()


# ============================================================
# 4. GRÁFICA — WILCOXON DE UNA MUESTRA
# ============================================================

def grafica_wilcoxon(
    nombre_nivel,
    datos,
    referencia,
    W_menos,
    W_mas,
    W_usado,
    p_valor,
    decision,
    conclusion,
    n_efectivo,
    n_ceros,
    hay_empates
):

    fig = plt.figure(
        figsize=(14, 7)
    )

    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[3.5, 1.5],
        wspace=0.08
    )

    ax = fig.add_subplot(gs[0])
    ax_info = fig.add_subplot(gs[1])

    # Boxplot
    ax.boxplot(
        datos,
        vert=False,
        widths=0.35,
        patch_artist=True
    )

    # Valor de referencia
    ax.axvline(
        referencia,
        linestyle="--",
        linewidth=2,
        color="red",
        label="Valor de referencia (MRC)"
    )

    # Mediana
    mediana = datos.median()

    ax.axvline(
        mediana,
        linestyle=":",
        linewidth=2,
        label="Mediana experimental"
    )

    ax.set_yticks([1])

    ax.set_yticklabels(
        [nombre_nivel]
    )

    ax.set_xlabel(
        "Resultado",
        fontsize=12
    )

    ax.set_title(
        "Wilcoxon — comparación de la posición central",
        fontsize=14,
        fontweight="bold"
    )

    ax.grid(
        axis="x",
        alpha=0.20
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend()

    # Panel de resultados
    ax_info.axis("off")

    ax_info.text(
        0.05,
        0.95,
        "RESULTADO ESTADÍSTICO",
        fontsize=15,
        fontweight="bold",
        transform=ax_info.transAxes,
        verticalalignment="top"
    )

    ax_info.text(
        0.05,
        0.82,
        (
            f"N original = {len(datos)}\n"
            f"N efectivo = {n_efectivo}\n\n"
            f"Mediana = {mediana:.6f}\n"
            f"Referencia = {referencia:.6f}\n\n"
            f"W− = {W_menos:.4f}\n"
            f"W+ = {W_mas:.4f}\n"
            f"W usado = {W_usado:.4f}\n\n"
            f"p = {p_valor:.6f}\n\n"
            f"Empates reales = "
            f"{'SÍ' if hay_empates else 'NO'}\n"
            f"Ceros eliminados = {n_ceros}\n\n"
            f"{decision}"
        ),
        fontsize=10.5,
        transform=ax_info.transAxes,
        verticalalignment="top",
        linespacing=1.20
    )

    fig.suptitle(
        f"Veracidad — {nombre_nivel} — Wilcoxon de una muestra",
        fontsize=21,
        fontweight="bold",
        y=0.97
    )

    fig.text(
        0.5,
        0.015,
        conclusion,
        ha="center",
        fontsize=10,
        style="italic"
    )

    plt.tight_layout(
        rect=[0, 0.05, 1, 0.94]
    )

    plt.show()


# ============================================================
# 5. ANÁLISIS t DE STUDENT
# ============================================================

def analizar_t_student(
    nombre_nivel,
    datos,
    referencia
):

    n = len(datos)

    if n < 2:
        raise ValueError(
            f"{nombre_nivel}: se necesitan al menos "
            "2 resultados para la prueba t."
        )

    media = datos.mean()

    sd = datos.std(
        ddof=1
    )

    gl = n - 1

    if sd == 0:
        raise ValueError(
            f"{nombre_nivel}: la desviación estándar es "
            "cero; no es posible calcular la prueba t."
        )

    error_estandar = (
        sd / np.sqrt(n)
    )

    # t calculado
    t_calculado = (
        (media - referencia)
        / error_estandar
    )

    # p-valor bilateral
    p_valor = (
        2
        * stats.t.sf(
            abs(t_calculado),
            gl
        )
    )

    # t crítico
    t_critico = stats.t.ppf(
        1 - alpha / 2,
        gl
    )

    # IC 95 % de la media
    margen_error = (
        t_critico
        * error_estandar
    )

    ic_inferior = (
        media - margen_error
    )

    ic_superior = (
        media + margen_error
    )

    # Decisión
    decision, conclusion = obtener_decision(
        p_valor
    )

    criterio_t = (
        abs(t_calculado)
        <= t_critico
    )

    print()
    print("=" * 80)
    print(
        f"RESULTADO — t DE STUDENT DE UNA MUESTRA — "
        f"{nombre_nivel}"
    )
    print("=" * 80)

    print()

    print(
        f"Valor de referencia = {referencia:.6f}"
    )

    print(
        f"Media = {media:.6f}"
    )

    print(
        f"Desv. estándar = {sd:.6f}"
    )

    print(
        f"N = {n}"
    )

    print(
        f"gl = {gl}"
    )

    print()

    print(
        f"t calculado = {t_calculado:.6f}"
    )

    print(
        f"t crítico = {t_critico:.6f}"
    )

    print(
        f"|t calculado| <= t crítico = "
        f"{'SÍ' if criterio_t else 'NO'}"
    )

    print()

    print(
        f"p-valor = {p_valor:.6f}"
    )

    print(
        f"α = {alpha:.2f}"
    )

    print()

    print(
        f"IC 95 % de la media = "
        f"{ic_inferior:.6f} – {ic_superior:.6f}"
    )

    print()

    print(
        f"DECISIÓN: {decision}"
    )

    print()

    print(
        f"CONCLUSIÓN: {conclusion}"
    )

    grafica_t_student(
        nombre_nivel,
        datos,
        referencia,
        t_calculado,
        t_critico,
        p_valor,
        decision,
        conclusion
    )

    return {
        "Nivel": nombre_nivel,
        "N": n,
        "Referencia": referencia,
        "Media": media,
        "Desv. estándar": sd,
        "t calculado": t_calculado,
        "t crítico": t_critico,
        "p-valor": p_valor,
        "Decisión": decision
    }


# ============================================================
# 6. ANÁLISIS WILCOXON
# ============================================================

def analizar_wilcoxon(
    nombre_nivel,
    datos,
    referencia
):

    diferencias = (
        datos - referencia
    )

    # Diferencias iguales a cero
    diferencias_no_cero = (
        diferencias[
            diferencias != 0
        ]
    )

    n_efectivo = len(
        diferencias_no_cero
    )

    n_ceros = (
        len(datos)
        - n_efectivo
    )

    if n_efectivo == 0:
        raise ValueError(
            f"{nombre_nivel}: todas las observaciones "
            "son exactamente iguales al valor de referencia."
        )

    # Rangos de los valores absolutos
    valores_abs = np.abs(
        diferencias_no_cero.to_numpy()
    )

    rangos = stats.rankdata(
        valores_abs,
        method="average"
    )

    # Detección de empates
    _, frecuencias = np.unique(
        valores_abs,
        return_counts=True
    )

    hay_empates = bool(
        np.any(
            frecuencias > 1
        )
    )

    # Suma de rangos
    W_mas = rangos[
        diferencias_no_cero.to_numpy() > 0
    ].sum()

    W_menos = rangos[
        diferencias_no_cero.to_numpy() < 0
    ].sum()

    W_usado = min(
        W_mas,
        W_menos
    )

    # Wilcoxon
    estadistico, p_valor = stats.wilcoxon(
        diferencias_no_cero,
        zero_method="wilcox",
        correction=True,
        alternative="two-sided",
        method="approx"
    )

    # Decisión
    decision, conclusion = obtener_decision(
        p_valor
    )

    print()
    print("=" * 80)
    print(
        f"RESULTADO — WILCOXON DE UNA MUESTRA — "
        f"{nombre_nivel}"
    )
    print("=" * 80)

    print()

    print(
        f"Valor de referencia = {referencia:.6f}"
    )

    print(
        f"Mediana = {datos.median():.6f}"
    )

    print(
        f"N original = {len(datos)}"
    )

    print(
        f"N efectivo = {n_efectivo}"
    )

    print(
        f"Observaciones con diferencia cero = "
        f"{n_ceros}"
    )

    print()

    print(
        f"W− (rangos negativos) = "
        f"{W_menos:.4f}"
    )

    print(
        f"W+ (rangos positivos) = "
        f"{W_mas:.4f}"
    )

    print(
        f"W usado para el contraste = "
        f"{W_usado:.4f}"
    )

    print()

    print(
        f"Empates reales detectados = "
        f"{'SÍ' if hay_empates else 'NO'}"
    )

    print(
        "Corrección de continuidad = SÍ"
    )

    print()

    print(
        f"p-valor = {p_valor:.6f}"
    )

    print(
        f"α = {alpha:.2f}"
    )

    print()

    print(
        f"DECISIÓN: {decision}"
    )

    print()

    print(
        f"CONCLUSIÓN: {conclusion}"
    )

    grafica_wilcoxon(
        nombre_nivel,
        datos,
        referencia,
        W_menos,
        W_mas,
        W_usado,
        p_valor,
        decision,
        conclusion,
        n_efectivo,
        n_ceros,
        hay_empates
    )

    return {
        "Nivel": nombre_nivel,
        "N": len(datos),
        "Referencia": referencia,
        "Mediana": datos.median(),
        "W usado": W_usado,
        "p-valor": p_valor,
        "Decisión": decision
    }


# ============================================================
# 7. CARGAR TODAS LAS HOJAS
# ============================================================

print()
print("#" * 90)
print("VERACIDAD — MATERIAL DE REFERENCIA CERTIFICADO (MRC)")
print("#" * 90)

print()

print(
    f"Archivo: {archivo}"
)

print(
    f"Nivel de significancia: α = {alpha}"
)

print()

print(
    "La presentación indica que, para el MRC, "
    "la veracidad puede determinarse mediante:"
)

print(
    "1. t de Student de una muestra"
)

print(
    "2. T de Wilcoxon de una muestra"
)

print()

datos_excel = pd.read_excel(
    archivo,
    sheet_name=None
)

if len(datos_excel) == 0:
    raise ValueError(
        "No se encontraron hojas en el archivo."
    )


# ============================================================
# 8. ANALIZAR CADA NIVEL Y SELECCIONAR PRUEBA INDIVIDUAL
# ============================================================

resultados = []

for nombre_nivel, hoja in datos_excel.items():

    print()
    print("#" * 90)
    print(
        f"NIVEL EN EVALUACIÓN: {nombre_nivel}"
    )
    print("#" * 90)

    print()

    # La prueba estadística se selecciona de forma independiente
    # para cada nivel. Se mantiene intacta la lógica de los cálculos.
    print("SELECCIÓN DE LA PRUEBA ESTADÍSTICA")
    print(f"Nivel actual: {nombre_nivel}")
    print("1 → t de Student de una muestra")
    print("2 → T de Wilcoxon de una muestra")

    while True:
        opcion = input(
            f"[Nivel: {nombre_nivel}] Escriba 1 para t de Student "
            "o 2 para Wilcoxon: "
        ).strip()

        if opcion in ("1", "2"):
            break

        print("Opción no válida. Para este nivel, escriba 1 o 2.")

    prueba_seleccionada = (
        "t de Student de una muestra" if opcion == "1"
        else "T de Wilcoxon de una muestra"
    )

    (
        columnas_numericas,
        datos
    ) = preparar_datos(
        hoja
    )

    print(
        "Columnas numéricas detectadas: "
        f"{', '.join(columnas_numericas)}"
    )

    print(
        f"Resultados utilizados: {len(datos)}"
    )

    referencia = leer_valor_referencia(
        nombre_nivel
    )

    mostrar_descriptiva(
        nombre_nivel,
        datos,
        referencia
    )

    if opcion == "1":

        resultado = analizar_t_student(
            nombre_nivel,
            datos,
            referencia
        )

    else:

        resultado = analizar_wilcoxon(
            nombre_nivel,
            datos,
            referencia
        )

    # Guardar la prueba utilizada en este nivel para que el resumen
    # y el JSON reflejen la selección individual de cada hoja.
    resultado["Prueba estadística"] = prueba_seleccionada

    resultados.append(
        resultado
    )


# ============================================================
# 10. RESUMEN FINAL
# ============================================================

tabla_resumen = pd.DataFrame(
    resultados
)

print()
print("#" * 90)
print("RESUMEN FINAL — VERACIDAD")
print("#" * 90)

print()

print(
    tabla_resumen.to_string(
        index=False
    )
)

print()

print(
    "Criterio de aceptación utilizado:"
)

print(
    f"p >= α ({alpha}) → SE ACEPTA H₀ → método veraz."
)

print(
    f"p < α ({alpha}) → SE RECHAZA H₀ → método no veraz."
)

print()

print(
    "Fin del análisis."
)


# ============================================================
# 11. EXPORTACIÓN JSON PARA INFORME GENERAL
#     Se conservan los cálculos y decisiones del script original.
#     No se registran fechas ni horas.
# ============================================================

import json

def convertir_json(obj):
    """Convierte tipos NumPy/Pandas a tipos compatibles con JSON."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        valor = float(obj)
        return valor if np.isfinite(valor) else None
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if pd.isna(obj):
        return None
    raise TypeError(f"Tipo no serializable en JSON: {type(obj).__name__}")

resultados_json = []

for resultado in resultados:
    resultado_json = dict(resultado)
    resultado_json["prueba_estadistica"] = resultado.get("Prueba estadística")
    resultado_json["Alfa"] = alpha
    resultado_json["Criterio de decisión"] = (
        "p-valor >= alfa: se acepta H0; p-valor < alfa: se rechaza H0"
    )
    p = resultado_json.get("p-valor")
    if p is not None:
        resultado_json["Estado"] = (
            "CUMPLE" if p >= alpha else "NO CUMPLE"
        )
        resultado_json["Conclusión"] = (
            "No se evidencian diferencias estadísticamente significativas "
            "respecto al valor de referencia del MRC."
            if p >= alpha else
            "Se evidencian diferencias estadísticamente significativas "
            "respecto al valor de referencia del MRC."
        )
    resultados_json.append(resultado_json)

salida_json = Path(archivo).with_name("resultados_veracidad_mrc.json")

contenido_json = {
    "schema_version": "1.0",
    "parametro": "Veracidad - Método A: Material de Referencia Certificado (MRC)",
    "archivo_datos": str(archivo),
    "seleccion_prueba": "Individual por nivel; consultar el campo prueba_estadistica de cada nivel.",
    "pruebas_disponibles": ["t de Student de una muestra", "T de Wilcoxon de una muestra"],
    "nivel_significancia": alpha,
    "criterio_decision": {
        "si_p_mayor_o_igual_alfa": "Se acepta H0",
        "si_p_menor_alfa": "Se rechaza H0"
    },
    "numero_niveles_evaluados": len(resultados_json),
    "estado_global": (
        "CUMPLE"
        if resultados_json and all(r.get("Estado") == "CUMPLE" for r in resultados_json)
        else "NO CUMPLE"
        if any(r.get("Estado") == "NO CUMPLE" for r in resultados_json)
        else "EVALUACIÓN INCOMPLETA"
    ),
    "niveles": resultados_json
}

with open(salida_json, "w", encoding="utf-8") as archivo_json:
    json.dump(
        contenido_json,
        archivo_json,
        ensure_ascii=False,
        indent=4,
        default=convertir_json
    )

print(f"\nJSON exportado correctamente: {salida_json}")
