# ============================================================
# REPETIBILIDAD PARA VARIOS NIVELES DE CONCENTRACIÓN
# REGRESIÓN %RSD vs CONCENTRACIÓN
# EVALUACIÓN DE UNA CONCENTRACIÓN DE MUESTRA
# HORWITZ + HORRAT(r)
#
# LÓGICA:
#   Cada hoja = un nivel experimental.
#
#   Nivel 1 -> Sr1 -> %RSD1
#   Nivel 2 -> Sr2 -> %RSD2
#   Nivel 3 -> Sr3 -> %RSD3
#                         |
#                         v
#              REGRESIÓN %RSD vs C
#                         |
#                 selección manual
#                         |
#              concentración de muestra
#                         |
#                  %RSD estimado
#                         |
#                      Sr estimado
#                         |
#                 HORWITZ + HORRAT
#
# Horwitz/HorRat NO se calculan para cada hoja.
# Se calculan únicamente para la concentración de evaluación
# proporcionada por el usuario.
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. ARCHIVO Y DETECCIÓN AUTOMÁTICA DE HOJAS
# ============================================================

archivo = r"D:\Ciencia_de_Datos\Validación de métodos químicos\precision.xlsx"

excel = pd.ExcelFile(archivo)
hojas = excel.sheet_names

print("\n" + "=" * 90)
print("NIVELES DE TRABAJO DETECTADOS")
print("=" * 90)

for i, hoja in enumerate(hojas, 1):
    print(f"{i}. {hoja}")

print(f"\nTotal de niveles detectados = {len(hojas)}")


# ============================================================
# 2. PROCESAR CADA NIVEL Y CALCULAR Sr
# ============================================================

resultados_niveles = []

for hoja in hojas:

    print("\n" + "#" * 90)
    print(f"NIVEL EXPERIMENTAL: {hoja}")
    print("#" * 90)

    datos = pd.read_excel(
        archivo,
        sheet_name=hoja
    )

    # Mantiene la lógica del script original:
    # cada columna numérica corresponde a los resultados
    # de un analista.
    datos_numericos = datos.select_dtypes(
        include="number"
    ).copy()

    if datos_numericos.shape[1] == 0:
        raise ValueError(
            f"La hoja '{hoja}' no contiene columnas numéricas."
        )

    # Desviación estándar de cada analista
    estadisticas = datos_numericos.describe()

    # Extraer las desviaciones estándar
    s = estadisticas.loc["std"]

    # Número de resultados de cada analista
    n = datos_numericos.count()

    # MISMA FÓRMULA DEL SCRIPT ORIGINAL
    Sr = np.sqrt(
        np.sum((n - 1) * s**2)
        /
        np.sum(n - 1)
    )

    # Concentración media del nivel
    concentracion = datos_numericos.mean().mean()

    if concentracion <= 0:
        raise ValueError(
            f"La concentración media de '{hoja}' debe ser > 0."
        )

    # %RSD experimental
    RSD = (Sr / concentracion) * 100

    print(f"Concentración media = {concentracion:.6g}")
    print(f"Sr                  = {Sr:.6g}")
    print(f"%RSD experimental    = {RSD:.4f} %")

    resultados_niveles.append({
        "Nivel": hoja,
        "Concentración": concentracion,
        "Sr": Sr,
        "%RSD": RSD
    })


# ============================================================
# 3. RESUMEN DE LOS NIVELES EXPERIMENTALES
# ============================================================

tabla_niveles = pd.DataFrame(resultados_niveles)

print("\n" + "=" * 100)
print("RESUMEN DE REPETIBILIDAD POR NIVEL")
print("=" * 100)

display(
    tabla_niveles.style.format({
        "Concentración": "{:.6g}",
        "Sr": "{:.6g}",
        "%RSD": "{:.4f} %"
    })
)


# ============================================================
# 4. PREPARAR REGRESIÓN
# ============================================================

x = tabla_niveles["Concentración"].to_numpy(dtype=float)
y = tabla_niveles["%RSD"].to_numpy(dtype=float)

if len(x) < 2:
    raise ValueError(
        "Se necesitan al menos dos niveles para realizar la regresión."
    )

if np.any(x <= 0):
    raise ValueError(
        "Todas las concentraciones deben ser > 0."
    )

if np.any(y <= 0):
    raise ValueError(
        "Todos los %RSD deben ser > 0."
    )


def calcular_r2(y_real, y_pred):
    ss_res = np.sum((y_real - y_pred) ** 2)
    ss_tot = np.sum((y_real - np.mean(y_real)) ** 2)

    if ss_tot == 0:
        return np.nan

    return 1 - ss_res / ss_tot


resultados_modelos = []


# ============================================================
# 5. MODELO LINEAL
# ============================================================

coef = np.polyfit(x, y, 1)
b = coef[0]
a = coef[1]

pred = a + b * x
r2 = calcular_r2(y, pred)


def modelo_lineal(valor, a=a, b=b):
    return a + b * valor


resultados_modelos.append({
    "Modelo": "Lineal",
    "Ecuación": f"y = {a:.6f} + {b:.6f}x",
    "R²": r2,
    "Funcion": modelo_lineal
})


# ============================================================
# 6. MODELO LOGARÍTMICO
# ============================================================

coef = np.polyfit(np.log(x), y, 1)
b = coef[0]
a = coef[1]

pred = a + b * np.log(x)
r2 = calcular_r2(y, pred)


def modelo_logaritmico(valor, a=a, b=b):
    return a + b * np.log(valor)


resultados_modelos.append({
    "Modelo": "Logarítmico",
    "Ecuación": f"y = {a:.6f} + {b:.6f} ln(x)",
    "R²": r2,
    "Funcion": modelo_logaritmico
})


# ============================================================
# 7. MODELO EXPONENCIAL
# ============================================================

coef = np.polyfit(x, np.log(y), 1)
b = coef[0]
a = np.exp(coef[1])

pred = a * np.exp(b * x)
r2 = calcular_r2(y, pred)


def modelo_exponencial(valor, a=a, b=b):
    return a * np.exp(b * valor)


resultados_modelos.append({
    "Modelo": "Exponencial",
    "Ecuación": f"y = {a:.6f} e^({b:.6f}x)",
    "R²": r2,
    "Funcion": modelo_exponencial
})


# ============================================================
# 8. MODELO POTENCIAL
# ============================================================

coef = np.polyfit(np.log(x), np.log(y), 1)
b = coef[0]
a = np.exp(coef[1])

pred = a * x**b
r2 = calcular_r2(y, pred)


def modelo_potencial(valor, a=a, b=b):
    return a * valor**b


resultados_modelos.append({
    "Modelo": "Potencial",
    "Ecuación": f"y = {a:.6f} x^{b:.6f}",
    "R²": r2,
    "Funcion": modelo_potencial
})


# ============================================================
# 9. MODELO INVERSO
# ============================================================

coef = np.polyfit(1 / x, y, 1)
b = coef[0]
a = coef[1]

pred = a + b / x
r2 = calcular_r2(y, pred)


def modelo_inverso(valor, a=a, b=b):
    return a + b / valor


resultados_modelos.append({
    "Modelo": "Inverso",
    "Ecuación": f"y = {a:.6f} + {b:.6f}/x",
    "R²": r2,
    "Funcion": modelo_inverso
})


# ============================================================
# 10. MODELO POLINÓMICO GRADO 2
# ============================================================

if len(x) >= 3:

    coef = np.polyfit(x, y, 2)

    c = coef[0]
    b = coef[1]
    a = coef[2]

    pred = a + b * x + c * x**2
    r2 = calcular_r2(y, pred)


    def modelo_polinomico(valor, a=a, b=b, c=c):
        return a + b * valor + c * valor**2


    resultados_modelos.append({
        "Modelo": "Polinómico grado 2",
        "Ecuación": (
            f"y = {a:.6f} + "
            f"{b:.6f}x + "
            f"{c:.6f}x²"
        ),
        "R²": r2,
        "Funcion": modelo_polinomico
    })


# ============================================================
# 11. COMPARACIÓN DE MODELOS
# ============================================================

tabla_modelos = pd.DataFrame({
    "Modelo": [
        r["Modelo"] for r in resultados_modelos
    ],
    "Ecuación": [
        r["Ecuación"] for r in resultados_modelos
    ],
    "R²": [
        r["R²"] for r in resultados_modelos
    ]
})

print("\n" + "=" * 100)
print("COMPARACIÓN DE MODELOS")
print("=" * 100)

display(
    tabla_modelos.style.format({
        "R²": "{:.6f}"
    })
)


# ============================================================
# 12. GRÁFICAS DE LOS MODELOS
# ============================================================

for resultado in resultados_modelos:

    funcion = resultado["Funcion"]

    x_grafico = np.linspace(
        np.min(x),
        np.max(x),
        300
    )

    y_grafico = funcion(x_grafico)

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
        label=resultado["Modelo"]
    )

    plt.text(
        0.05,
        0.95,
        (
            f"{resultado['Ecuación']}\n"
            f"R² = {resultado['R²']:.6f}"
        ),
        transform=plt.gca().transAxes,
        verticalalignment="top",
        bbox=dict(
            boxstyle="round",
            facecolor="white",
            alpha=0.9
        )
    )

    plt.xlabel("Concentración")
    plt.ylabel("%RSD experimental de repetibilidad")

    plt.title(
        f"Modelo {resultado['Modelo']} — Repetibilidad"
    )

    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ============================================================
# 13. SELECCIÓN MANUAL DEL MODELO
# ============================================================

print("\n" + "=" * 90)
print("SELECCIÓN DEL MODELO DE REPETIBILIDAD")
print("=" * 90)

for i, resultado in enumerate(resultados_modelos, 1):
    print(
        f"{i}. {resultado['Modelo']} "
        f"(R² = {resultado['R²']:.6f})"
    )

opcion_modelo = int(
    input(
        "\nIngrese el número del modelo seleccionado: "
    )
)

if not 1 <= opcion_modelo <= len(resultados_modelos):
    raise ValueError("La opción seleccionada no es válida.")

modelo_seleccionado = resultados_modelos[
    opcion_modelo - 1
]

print("\nMODELO SELECCIONADO")
print("-" * 80)
print(f"Modelo   = {modelo_seleccionado['Modelo']}")
print(f"Ecuación = {modelo_seleccionado['Ecuación']}")
print(f"R²       = {modelo_seleccionado['R²']:.6f}")


# ============================================================
# 14. CONCENTRACIÓN ÚNICA DE EVALUACIÓN
# ============================================================
#
# A partir de aquí NO se evalúan las hojas individualmente.
# Se evalúa solamente la concentración indicada por el usuario.
# ============================================================

print("\n" + "=" * 90)
print("CONCENTRACIÓN DE EVALUACIÓN")
print("=" * 90)

concentracion_muestra = float(
    input(
        "\nIngrese la concentración de evaluación: "
    )
)

if concentracion_muestra <= 0:
    raise ValueError(
        "La concentración de evaluación debe ser > 0."
    )


# ============================================================
# 15. %RSD DE REPETIBILIDAD ESTIMADO
# ============================================================

funcion_seleccionada = modelo_seleccionado["Funcion"]

RSD_muestra = funcion_seleccionada(
    concentracion_muestra
)

if RSD_muestra <= 0:
    raise ValueError(
        "El modelo seleccionado produjo un %RSD <= 0 "
        "para la concentración indicada."
    )


# ============================================================
# 16. Sr ESTIMADO EN LA CONCENTRACIÓN DE EVALUACIÓN
# ============================================================

Sr_muestra = (
    RSD_muestra
    *
    concentracion_muestra
    /
    100
)


# ============================================================
# 17. SELECCIÓN DE LA FRACCIÓN MÁSICA PARA HORWITZ
# ============================================================

print("\n" + "=" * 90)
print("SELECCIÓN DE LA FRACCIÓN MÁSICA PARA HORWITZ")
print("=" * 90)

print("\nSeleccione la unidad de concentración de la muestra:")

print("1. ppm  -> factor 10^-6")
print("2. ppb  -> factor 10^-9")
print("3. %    -> factor 10^-2")

opcion_unidad = input(
    "\nIngrese una opción (1, 2 o 3): "
).strip()

factores = {
    "1": (1e-6, "ppm"),
    "2": (1e-9, "ppb"),
    "3": (1e-2, "%")
}

if opcion_unidad not in factores:
    raise ValueError(
        "Opción no válida. Debe seleccionar 1, 2 o 3."
    )

factor_masico, unidad_concentracion = factores[
    opcion_unidad
]


# ============================================================
# 18. CONVERTIR CONCENTRACIÓN A FRACCIÓN MÁSICA
# ============================================================

C = concentracion_muestra * factor_masico

if C <= 0:
    raise ValueError(
        "La concentración convertida a fracción másica debe ser > 0."
    )


# ============================================================
# 19. HORWITZ - REPRODUCIBILIDAD
# ============================================================

PRSDR = 2 * C**(-0.15)


# ============================================================
# 20. HORWITZ - REPETIBILIDAD
# ============================================================

factor_repetibilidad = 0.5

PRSD_repetibilidad = (
    factor_repetibilidad
    *
    PRSDR
)


# ============================================================
# 21. HORRAT(r)
# ============================================================

HorRat_r = (
    RSD_muestra
    /
    PRSDR
)

if 0.3 <= HorRat_r <= 1.3:
    conclusion_horrat = "PASA"
else:
    conclusion_horrat = "NO PASA"


# ============================================================
# 22. COMPARACIÓN CON 0.5 × PRSDR
# ============================================================

if RSD_muestra <= PRSD_repetibilidad:
    conclusion_objetivo = "PASA"
else:
    conclusion_objetivo = "NO PASA"


# ============================================================
# 23. RESULTADO FINAL
# ============================================================

print("\n" + "#" * 100)
print("EVALUACIÓN FINAL DE REPETIBILIDAD")
print("#" * 100)

print("\nMODELO SELECCIONADO")
print(f"  Modelo   = {modelo_seleccionado['Modelo']}")
print(f"  Ecuación = {modelo_seleccionado['Ecuación']}")
print(f"  R²       = {modelo_seleccionado['R²']:.6f}")

print("\nCONCENTRACIÓN DE EVALUACIÓN")
print(f"  Concentración = {concentracion_muestra:.6g}")
print(f"  Unidad        = {unidad_concentracion}")

print("\nPRECISIÓN DE REPETIBILIDAD ESTIMADA")
print(f"  %RSD repetibilidad = {RSD_muestra:.6f} %")
print(f"  Sr estimado        = {Sr_muestra:.7f}")

print("\nHORWITZ")
print(f"  Fracción másica C = {C:.6e}")
print(
    f"  %RSD Horwitz - reproducibilidad "
    f"(PRSDR) = {PRSDR:.6f} %"
)
print(
    f"  Factor reproducibilidad -> repetibilidad = "
    f"{factor_repetibilidad:.2f}"
)
print(
    f"  %RSD Horwitz - repetibilidad "
    f"(0.5 x PRSDR) = {PRSD_repetibilidad:.6f} %"
)

print("\nHORRAT(r)")
print(f"  HorRat(r) = {HorRat_r:.6f}")
print("  Criterio de referencia: 0.3 <= HorRat(r) <= 1.3")
print(f"  Conclusión HorRat(r): {conclusion_horrat}")

print("\nCOMPARACIÓN CON EL OBJETIVO DE REPETIBILIDAD")
print(f"  %RSD estimado              = {RSD_muestra:.6f} %")
print(f"  %RSD objetivo 0.5 x PRSDR = {PRSD_repetibilidad:.6f} %")
print(f"  Conclusión                 = {conclusion_objetivo}")


# ============================================================
# 24. CONCLUSIÓN
# ============================================================

print("\n" + "=" * 100)
print("CONCLUSIÓN")
print("=" * 100)

if conclusion_horrat == "PASA":
    print(
        "Para la concentración de evaluación indicada, "
        "el HorRat(r) se encuentra dentro del intervalo "
        "de referencia 0.3–1.3."
    )
else:
    print(
        "Para la concentración de evaluación indicada, "
        "el HorRat(r) se encuentra fuera del intervalo "
        "de referencia 0.3–1.3."
    )

if conclusion_objetivo == "PASA":
    print(
        "El %RSD de repetibilidad estimado es menor o igual "
        "al objetivo definido como 0.5 × PRSDR."
    )
else:
    print(
        "El %RSD de repetibilidad estimado supera el objetivo "
        "definido como 0.5 × PRSDR."
    )


# ============================================================
# 25. RESUMEN FINAL
# ============================================================

resumen_final = pd.DataFrame({
    "Indicador": [
        "Modelo seleccionado",
        "Ecuación",
        "R²",
        "Concentración de evaluación",
        "Unidad",
        "Factor de conversión",
        "Fracción másica C",
        "%RSD repetibilidad estimado",
        "Sr estimado",
        "%RSD Horwitz - reproducibilidad",
        "%RSD Horwitz - repetibilidad",
        "HorRat(r)",
        "Criterio HorRat(r)",
        "Resultado HorRat(r)",
        "Resultado 0.5×PRSDR"
    ],
    "Resultado": [
        modelo_seleccionado["Modelo"],
        modelo_seleccionado["Ecuación"],
        f"{modelo_seleccionado['R²']:.6f}",
        f"{concentracion_muestra:.6g}",
        unidad_concentracion,
        f"{factor_masico:.0e}",
        f"{C:.6e}",
        f"{RSD_muestra:.6f} %",
        f"{Sr_muestra:.7f}",
        f"{PRSDR:.6f} %",
        f"{PRSD_repetibilidad:.6f} %",
        f"{HorRat_r:.6f}",
        "0.3 – 1.3",
        conclusion_horrat,
        conclusion_objetivo
    ]
})

print("\n" + "=" * 100)
print("RESUMEN FINAL DE LA EVALUACIÓN")
print("=" * 100)

display(resumen_final)
