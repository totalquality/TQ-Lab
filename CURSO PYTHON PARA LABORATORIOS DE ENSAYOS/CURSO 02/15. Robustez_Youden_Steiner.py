# -*- coding: utf-8 -*-
"""
ROBUSTEZ — DISEÑO DE YOUDEN–STEINER / FACTORIAL FRACCIONADO
============================================================

Archivo de entrada:
D:\Ciencia_de_Datos\Validación de métodos químicos\Robustez_Youden_Steiner.xlsx

Estructura esperada:
- Cada hoja = un nivel de concentración.
- Una columna "Ensayo".
- Varias columnas "Factor 1", "Factor 2", ... con niveles + / -.
- Una columna "Resultado".
- Puede haber cualquier número de factores y réplicas según el diseño.

Para cada nivel, el programa solicita:
1. Concentración (solo informativa).
2. Sr de repetibilidad (se utiliza para el criterio de robustez).

Criterio:
    Efecto crítico = 2.24 × Sr

Efecto relativo FAO (ecuación 7.29):
    E_relativo(%) = [(sum(Y+) - sum(Y-)) / sum(Y+)] × 100
    Para la gráfica se muestra |E_relativo| (%).

    Si |Efecto| > Efecto crítico:
        Efecto potencialmente significativo.
    Si |Efecto| <= Efecto crítico:
        Efecto no significativo.

Gráficas generadas por cada nivel:
1. Efectos principales.
2. Pareto de efectos con línea de efecto crítico.
4. Efecto relativo (%) según FAO, ecuación 7.29.

No se genera ANOVA para estos diseños no replicados/saturados,
porque el diseño no proporciona una estimación independiente
del error experimental.

Tampoco se generan gráficos de interacciones como si fueran
estimables independientemente: en estos diseños las interacciones
están aliadas/confundidas.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURACIÓN
# ============================================================

archivo = Path(
    r"D:\Ciencia_de_Datos\Validación de métodos químicos\Robustez_Youden_Steiner.xlsx"
)

ALPHA = 0.05
FACTOR_CRITICO = 2.24

# Paleta para las gráficas
COLORES = [
    "#C62828", "#1565C0", "#2E7D32", "#EF6C00",
    "#6A1B9A", "#00838F", "#AD1457", "#4E342E",
    "#283593", "#558B2F", "#D84315", "#4527A0"
]


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def solicitar_numero(mensaje, permitir_cero=False):
    """Solicita un número al usuario y valida la entrada."""
    while True:
        try:
            valor = float(input(mensaje))
            if not permitir_cero and valor <= 0:
                print("  ⚠ Ingrese un valor mayor que cero.")
                continue
            if permitir_cero and valor < 0:
                print("  ⚠ Ingrese un valor igual o mayor que cero.")
                continue
            return valor
        except ValueError:
            print("  ⚠ Entrada no válida. Escriba un número.")


def detectar_columnas(df):
    """
    Detecta automáticamente:
    - columna de ensayo
    - columnas de factores
    - columna de resultado
    """
    columnas = list(df.columns)

    # Columna de resultado
    resultado = None
    for col in columnas:
        nombre = str(col).strip().lower()
        if nombre in ["resultado", "respuesta", "response", "y"]:
            resultado = col
            break

    if resultado is None:
        # Busca una columna que no sea ensayo ni factor
        candidatas = []
        for col in columnas:
            nombre = str(col).strip().lower()
            if "resultado" in nombre or "respuesta" in nombre:
                candidatas.append(col)
        if candidatas:
            resultado = candidatas[0]

    if resultado is None:
        raise ValueError(
            "No se encontró la columna 'Resultado'. "
            "Renómbrela como 'Resultado'."
        )

    # Columna Ensayo
    ensayo = None
    for col in columnas:
        nombre = str(col).strip().lower()
        if nombre in ["ensayo", "run", "corrida", "experimento"]:
            ensayo = col
            break

    # Factores = columnas que no son ensayo ni resultado
    factores = [
        col for col in columnas
        if col != resultado and col != ensayo
    ]

    if len(factores) < 2:
        raise ValueError(
            "No se detectaron suficientes columnas de factores."
        )

    return ensayo, factores, resultado


def validar_niveles_factor(df, factores):
    """Verifica que los factores estén codificados como + y -."""
    for factor in factores:
        valores = (
            df[factor]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        permitidos = set(valores.dropna().unique())

        # Aceptar +1/-1 además de +/- por comodidad
        permitidos_normalizados = set()
        for v in permitidos:
            if v in {"+", "+1", "1", "ALTO", "HIGH"}:
                permitidos_normalizados.add("+")
            elif v in {"-", "-1", "BAJO", "LOW"}:
                permitidos_normalizados.add("-")

        if not permitidos_normalizados.issubset({"+", "-"}):
            raise ValueError(
                f"El factor '{factor}' contiene niveles no reconocidos: "
                f"{sorted(permitidos)}. Use '+' y '-'."
            )


def normalizar_factor(serie):
    """Convierte diferentes formas de codificación a + / -."""
    salida = []

    for valor in serie:
        v = str(valor).strip().upper()

        if v in {"+", "+1", "1", "ALTO", "HIGH"}:
            salida.append("+")
        elif v in {"-", "-1", "BAJO", "LOW"}:
            salida.append("-")
        else:
            salida.append(np.nan)

    return np.array(salida)


def calcular_efectos(df, factores, resultado):
    """
    Calcula el efecto absoluto y el efecto relativo de cada factor.

    Efecto absoluto (FAO 7.26 / 7.28):
        E = (sum(Y+) - sum(Y-)) / n

    Efecto relativo (FAO 7.29):
        E_rel(%) = [(sum(Y+) - sum(Y-)) / sum(Y+)] * 100

    El denominador del efecto relativo es el resultado del nivel original (+).
    """
    efectos = []
    y = pd.to_numeric(df[resultado], errors="coerce").to_numpy()

    for factor in factores:
        niveles = normalizar_factor(df[factor])
        mask_plus = niveles == "+"
        mask_minus = niveles == "-"
        y_plus = y[mask_plus]
        y_minus = y[mask_minus]

        if len(y_plus) == 0 or len(y_minus) == 0:
            raise ValueError(f"El factor '{factor}' no contiene ambos niveles + y -.")
        if len(y_plus) != len(y_minus):
            raise ValueError(
                f"El factor '{factor}' no está balanceado: + = {len(y_plus)}, - = {len(y_minus)}."
            )

        n = len(y_plus)
        suma_plus = np.sum(y_plus)
        suma_minus = np.sum(y_minus)
        media_plus = np.mean(y_plus)
        media_minus = np.mean(y_minus)

        efecto = (suma_plus - suma_minus) / n

        if np.isclose(suma_plus, 0):
            efecto_relativo = np.nan
        else:
            efecto_relativo = ((suma_plus - suma_minus) / suma_plus) * 100

        efectos.append({
            "Factor": str(factor),
            "Media (+)": media_plus,
            "Media (-)": media_minus,
            "Suma Y+": suma_plus,
            "Suma Y-": suma_minus,
            "Efecto": efecto,
            "|Efecto|": abs(efecto),
            "Efecto relativo (%)": efecto_relativo,
            "|Efecto relativo| (%)": abs(efecto_relativo) if np.isfinite(efecto_relativo) else np.nan
        })

    return pd.DataFrame(efectos)

def grafico_efectos_principales(
    resultados,
    nivel_nombre,
    concentracion,
    efecto_critico
):
    """Gráfico de efectos principales."""
    factores = resultados["Factor"].tolist()
    medias_plus = resultados["Media (+)"].to_numpy()
    medias_minus = resultados["Media (-)"].to_numpy()

    x = np.arange(len(factores))
    ancho = 0.36

    fig, ax = plt.subplots(figsize=(12, 6.5))

    ax.bar(
        x - ancho / 2,
        medias_minus,
        width=ancho,
        label="Nivel −",
        color="#90CAF9",
        edgecolor="black"
    )

    ax.bar(
        x + ancho / 2,
        medias_plus,
        width=ancho,
        label="Nivel +",
        color="#EF5350",
        edgecolor="black"
    )

    ax.set_xticks(x)
    ax.set_xticklabels(factores, rotation=30, ha="right")
    ax.set_ylabel("Respuesta")
    ax.set_xlabel("Factor")
    ax.set_title(
        f"Efectos principales — {nivel_nombre}\n"
        f"Concentración: {concentracion:g}"
    )

    ax.legend()
    ax.grid(axis="y", alpha=0.25)

    # Texto de criterio en la parte inferior
    ax.text(
        0.99,
        0.02,
        f"Criterio: |Efecto| ≤ {efecto_critico:.4g}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
        bbox=dict(
            boxstyle="round,pad=0.35",
            facecolor="white",
            edgecolor="#777777"
        )
    )

    plt.tight_layout()
    plt.show()


def grafico_pareto(
    resultados,
    nivel_nombre,
    concentracion,
    efecto_critico
):
    """Gráfico de Pareto de los efectos absolutos."""
    orden = resultados.sort_values(
        "|Efecto|",
        ascending=True
    ).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(11, 6.5))

    colores = []
    for valor in orden["|Efecto|"]:
        if valor > efecto_critico:
            colores.append("#C62828")
        else:
            colores.append("#1565C0")

    ax.barh(
        orden["Factor"],
        orden["|Efecto|"],
        color=colores,
        edgecolor="black"
    )

    ax.axvline(
        efecto_critico,
        color="#D4A017",
        linewidth=2.5,
        linestyle="--",
        label=f"Efecto crítico = {efecto_critico:.4g}"
    )

    for i, valor in enumerate(orden["|Efecto|"]):
        ax.text(
            valor,
            i,
            f"  {valor:.4g}",
            va="center",
            fontsize=9
        )

    ax.set_xlabel("|Efecto|")
    ax.set_ylabel("Factor")
    ax.set_title(
        f"Diagrama de Pareto de efectos — {nivel_nombre}\n"
        f"Concentración: {concentracion:g}"
    )

    ax.legend()
    ax.grid(axis="x", alpha=0.25)

    plt.tight_layout()
    plt.show()



# ============================================================
# INICIO
# ============================================================

print("\n" + "=" * 78)
print("             ROBUSTEZ — YOUDEN–STEINER / DOE")
print("=" * 78)

print("\nArchivo:")
print(archivo)

if not archivo.exists():
    raise FileNotFoundError(
        "\nNo se encontró el archivo Excel.\n"
        "Verifique que exista en:\n"
        f"{archivo}"
    )

excel = pd.ExcelFile(archivo)
hojas = excel.sheet_names

print("\nHojas detectadas:")
for i, hoja in enumerate(hojas, start=1):
    print(f"  Nivel {i}: {hoja}")

print("\n" + "-" * 78)
print("CRITERIO DE EVALUACIÓN")
print("-" * 78)
print("Efecto crítico = 2.24 × Sr")
print("Si |Efecto| > efecto crítico → efecto potencialmente significativo")
print("Si |Efecto| ≤ efecto crítico → efecto no significativo")
print("-" * 78)

# ============================================================
# SOLICITUD DE DATOS POR NIVEL
# ============================================================

datos_niveles = []

print("\n")
print("╔" + "═" * 74 + "╗")
print("║" + "          DATOS A INGRESAR POR CADA NIVEL".center(74) + "║")
print("╠" + "═" * 74 + "╣")

for i, hoja in enumerate(hojas, start=1):
    print(
        "║" +
        f" Nivel {i} ({hoja}) → Concentración + Sr de repetibilidad".ljust(74)
        + "║"
    )

print("╚" + "═" * 74 + "╝")

for i, hoja in enumerate(hojas, start=1):

    nivel_nombre = f"Nivel {i}"

    print("\n" + "#" * 78)
    print(f"{nivel_nombre.upper()} | HOJA: {hoja}")
    print("#" * 78)

    print(f"\n[{nivel_nombre}] Concentración")
    print("  ℹ Este valor es únicamente informativo.")
    concentracion = solicitar_numero(
        f"  [{nivel_nombre}] Ingrese la concentración: "
    )

    print(f"\n[{nivel_nombre}] Sr de repetibilidad")
    print("  ℹ Este valor se utilizará para calcular el efecto crítico.")
    sr = solicitar_numero(
        f"  [{nivel_nombre}] Ingrese Sr: "
    )

    datos_niveles.append({
        "hoja": hoja,
        "nivel": nivel_nombre,
        "concentracion": concentracion,
        "Sr": sr
    })


def grafico_efecto_relativo(resultados, nivel_nombre, concentracion):
    """Gráfico del efecto relativo absoluto (%) según FAO 7.29."""
    orden = resultados.sort_values("|Efecto relativo| (%)", ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    valores = orden["|Efecto relativo| (%)"]
    colores = ["#C62828" if np.isfinite(v) and v > 0 else "#9E9E9E" for v in valores]

    ax.barh(orden["Factor"], valores, color=colores, edgecolor="black", alpha=0.88)

    for i, valor in enumerate(valores):
        if np.isfinite(valor):
            ax.text(valor, i, f"  {valor:.3f}%", va="center", fontsize=9)

    ax.set_xlabel("|Efecto relativo| (%)")
    ax.set_ylabel("Factor")
    ax.set_title(
        f"Efecto relativo de los factores — {nivel_nombre}\n"
        f"Concentración: {concentracion:g}\n"
        f"FAO, ecuación 7.29",
        fontweight="bold"
    )
    ax.grid(axis="x", alpha=0.25)
    ax.text(
        0.99, 0.02,
        "Referencia: nivel original (+) de cada factor",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#777777")
    )
    plt.tight_layout()
    plt.show()


# ============================================================
# PROCESAMIENTO
# ============================================================

resultados_globales = []

for datos_nivel in datos_niveles:

    hoja = datos_nivel["hoja"]
    nivel_nombre = datos_nivel["nivel"]
    concentracion = datos_nivel["concentracion"]
    sr = datos_nivel["Sr"]

    print("\n\n" + "=" * 78)
    print(f"ANÁLISIS: {nivel_nombre} | HOJA: {hoja}")
    print(f"Concentración: {concentracion:g}")
    print(f"Sr: {sr:g}")
    print("=" * 78)

    df = pd.read_excel(archivo, sheet_name=hoja)

    ensayo, factores, resultado = detectar_columnas(df)

    # Limpiar resultado
    df[resultado] = pd.to_numeric(
        df[resultado],
        errors="coerce"
    )

    df = df.dropna(
        subset=[resultado]
    ).copy()

    validar_niveles_factor(df, factores)

    n_experimentos = len(df)

    print(f"\nExperimentos detectados: {n_experimentos}")
    print(f"Factores detectados: {len(factores)}")
    print("Factores:", ", ".join(str(f) for f in factores))

    # Cálculo del efecto crítico
    efecto_critico = FACTOR_CRITICO * sr

    print(f"\nEfecto crítico = 2.24 × {sr:g} = {efecto_critico:.6g}")

    # Calcular efectos
    resultados = calcular_efectos(
        df,
        factores,
        resultado
    )

    resultados["Efecto crítico"] = efecto_critico
    resultados["Cumple"] = (
        resultados["|Efecto|"] <= efecto_critico
    )
    resultados["Nivel"] = nivel_nombre
    resultados["Hoja"] = hoja
    resultados["Concentración"] = concentracion
    resultados["Sr"] = sr

    # Mostrar resultados
    print("\n" + "-" * 78)
    print("RESULTADOS DE LOS EFECTOS")
    print("-" * 78)

    for _, fila in resultados.iterrows():

        estado = (
            "NO SIGNIFICATIVO"
            if fila["Cumple"]
            else
            "POTENCIALMENTE SIGNIFICATIVO"
        )

        print(
            f"\n{fila['Factor']}"
            f"\n  Media (+)  = {fila['Media (+)']:.6g}"
            f"\n  Media (-)  = {fila['Media (-)']:.6g}"
            f"\n  Efecto     = {fila['Efecto']:.6g}"
            f"\n  |Efecto|   = {fila['|Efecto|']:.6g}"
            f"\n  Efecto relativo = {fila['Efecto relativo (%)']:.6g}%"
            f"\n  |Efecto relativo| = {fila['|Efecto relativo| (%)']:.6g}%"
            f"\n  Criterio   = {efecto_critico:.6g}"
            f"\n  Evaluación = {estado}"
        )

        resultados_globales.append({
            "Nivel": nivel_nombre,
            "Hoja": hoja,
            "Concentración": concentracion,
            "Sr": sr,
            "Factor": fila["Factor"],
            "Media (+)": fila["Media (+)"],
            "Media (-)": fila["Media (-)"],
            "Efecto": fila["Efecto"],
            "|Efecto|": fila["|Efecto|"],
            "Efecto relativo (%)": fila["Efecto relativo (%)"],
            "|Efecto relativo| (%)": fila["|Efecto relativo| (%)"],
            "Efecto crítico": efecto_critico,
            "Evaluación": estado
        })

    # ========================================================
    # GRÁFICAS POR NIVEL
    # ========================================================

    print("\nGenerando gráficas del nivel...")

    grafico_efectos_principales(
        resultados,
        nivel_nombre,
        concentracion,
        efecto_critico
    )

    grafico_pareto(
        resultados,
        nivel_nombre,
        concentracion,
        efecto_critico
    )
grafico_efecto_relativo(
        resultados,
        nivel_nombre,
        concentracion
    )


# ============================================================
# RESUMEN FINAL
# ============================================================

df_global = pd.DataFrame(resultados_globales)

print("\n\n" + "=" * 90)
print("                         RESUMEN FINAL DE ROBUSTEZ")
print("=" * 90)

for nivel in df_global["Nivel"].unique():

    bloque = df_global[
        df_global["Nivel"] == nivel
    ]

    concentracion = bloque["Concentración"].iloc[0]

    print(
        f"\n{nivel} | Concentración = {concentracion:g}"
    )

    for _, fila in bloque.iterrows():

        simbolo = "✓" if "NO SIGNIFICATIVO" in fila["Evaluación"] else "✗"

        print(
            f"  {fila['Factor']:<15} "
            f"Efecto = {fila['Efecto']:>10.5g} | "
            f"|Efecto| = {fila['|Efecto|']:>10.5g} | "
            f"Efecto rel. = {fila['Efecto relativo (%)']:>9.4g}% | "
            f"Criterio = {fila['Efecto crítico']:>10.5g} | "
            f"{simbolo} {fila['Evaluación']}"
        )

print("\n" + "=" * 90)
print("INTERPRETACIÓN GENERAL")
print("=" * 90)

factores_significativos = df_global[
    ~df_global["Evaluación"].str.contains("NO SIGNIFICATIVO")
]

if factores_significativos.empty:
    print(
        "\n✓ No se identificaron efectos que superen el criterio "
        "2.24 × Sr en los niveles evaluados."
    )
else:
    print(
        "\n⚠ Se identificaron factores cuyos efectos superan el criterio "
        "2.24 × Sr:"
    )

    for _, fila in factores_significativos.iterrows():
        print(
            f"  - {fila['Nivel']} | {fila['Factor']} | "
            f"|Efecto| = {fila['|Efecto|']:.5g} > "
            f"{fila['Efecto crítico']:.5g}"
        )

print("\n" + "=" * 90)
print("Análisis terminado.")
print("=" * 90)
