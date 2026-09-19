# ============================================================
# AUTOMATIZACIÓN DE PRECISIÓN
# Sr por nivel
# %RSD por nivel
# Regresión %RSD vs concentración
# Comparación de modelos
# Gráficos
# Selección manual del modelo
# Estimación de Sr para una muestra
# ============================================================


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. UBICACIÓN DEL ARCHIVO
# ============================================================

archivo = r"D:\Ciencia_de_Datos\Validación de métodos químicos\precision.xlsx"


# ============================================================
# 2. DETECTAR AUTOMÁTICAMENTE TODAS LAS HOJAS
# ============================================================

excel = pd.ExcelFile(archivo)

print("\nHOJAS ENCONTRADAS")
print("=" * 40)

for hoja in excel.sheet_names:
    print("-", hoja)


# ============================================================
# 3. CALCULAR Sr Y %RSD DE CADA NIVEL
# ============================================================

niveles = []
concentraciones = []
srs = []
rsds = []


for hoja in excel.sheet_names:

    # Leer hoja
    datos = pd.read_excel(
        archivo,
        sheet_name=hoja
    )

    # Mantener solamente columnas numéricas
    datos = datos.select_dtypes(
        include="number"
    )

    # Eliminar columnas completamente vacías
    datos = datos.dropna(
        axis=1,
        how="all"
    )

    # --------------------------------------------------------
    # Desviación estándar de cada analista
    # --------------------------------------------------------

    s = datos.std()

    # Número de resultados de cada analista

    n = datos.count()

    # --------------------------------------------------------
    # Desviación estándar de repetibilidad
    #
    # Sr = raíz de:
    # sum((ni-1) Si²) / sum(ni-1)
    # --------------------------------------------------------

    Sr = np.sqrt(
        np.sum(
            (n - 1) * s**2
        )
        /
        np.sum(n - 1)
    )

    # --------------------------------------------------------
    # Promedio general del nivel
    # --------------------------------------------------------

    C = datos.mean().mean()

    # --------------------------------------------------------
    # %RSD
    # --------------------------------------------------------

    RSD = (
        Sr / C
    ) * 100


    # Guardar resultados

    niveles.append(hoja)

    concentraciones.append(C)

    srs.append(Sr)

    rsds.append(RSD)


# ============================================================
# 4. TABLA DE RESULTADOS DE CADA NIVEL
# ============================================================

tabla_datos = pd.DataFrame({

    "Nivel": niveles,

    "Sr": srs,

    "Concentración": concentraciones,

    "%RSD": rsds

})


print("\nRESULTADOS DE LOS NIVELES")
print("=" * 40)

display(
    tabla_datos
)


# ============================================================
# 5. DATOS PARA LA REGRESIÓN
# ============================================================

x = np.array(
    concentraciones,
    dtype=float
)

y = np.array(
    rsds,
    dtype=float
)


# ============================================================
# 6. FUNCIÓN PARA CALCULAR R²
# ============================================================

def calcular_r2(y_real, y_pred):

    ss_res = np.sum(
        (y_real - y_pred) ** 2
    )

    ss_tot = np.sum(
        (y_real - np.mean(y_real)) ** 2
    )

    return 1 - (
        ss_res / ss_tot
    )


# ============================================================
# 7. LISTA DE RESULTADOS
# ============================================================

resultados = []


# ============================================================
# 8. MODELO LINEAL
#
# y = a + bx
# ============================================================

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


def modelo_lineal(valor, a=a, b=b):

    return a + b * valor


ecuacion = (
    f"y = {a:.6f} + "
    f"{b:.6f}x"
)


resultados.append({

    "Modelo": "Lineal",

    "Ecuación": ecuacion,

    "R²": r2,

    "Funcion": modelo_lineal

})


# ============================================================
# 9. MODELO LOGARÍTMICO
#
# y = a + b ln(x)
# ============================================================

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


ecuacion = (
    f"y = {a:.6f} + "
    f"{b:.6f} ln(x)"
)


resultados.append({

    "Modelo": "Logarítmico",

    "Ecuación": ecuacion,

    "R²": r2,

    "Funcion": modelo_logaritmico

})


# ============================================================
# 10. MODELO EXPONENCIAL
#
# y = a e^(bx)
# ============================================================

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


ecuacion = (
    f"y = {a:.6f} "
    f"e^({b:.6f}x)"
)


resultados.append({

    "Modelo": "Exponencial",

    "Ecuación": ecuacion,

    "R²": r2,

    "Funcion": modelo_exponencial

})


# ============================================================
# 11. MODELO POTENCIAL
#
# y = a x^b
# ============================================================

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
    a * x**b
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
        a * valor**b
    )


ecuacion = (
    f"y = {a:.6f} "
    f"x^{b:.6f}"
)


resultados.append({

    "Modelo": "Potencial",

    "Ecuación": ecuacion,

    "R²": r2,

    "Funcion": modelo_potencial

})


# ============================================================
# 12. MODELO INVERSO
#
# y = a + b/x
# ============================================================

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


ecuacion = (
    f"y = {a:.6f} + "
    f"{b:.6f}/x"
)


resultados.append({

    "Modelo": "Inverso",

    "Ecuación": ecuacion,

    "R²": r2,

    "Funcion": modelo_inverso

})


# ============================================================
# 13. MODELO POLINÓMICO GRADO 2
#
# y = a + bx + cx²
#
# SE COLOCA COMO ÚLTIMA ALTERNATIVA
# ============================================================

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
    + c * x**2
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
        + c * valor**2
    )


ecuacion = (
    f"y = {a:.6f} + "
    f"{b:.6f}x + "
    f"{c:.6f}x²"
)


resultados.append({

    "Modelo": "Polinómico grado 2",

    "Ecuación": ecuacion,

    "R²": r2,

    "Funcion": modelo_polinomico

})


# ============================================================
# 14. TABLA COMPARATIVA DE MODELOS
# ============================================================

tabla_modelos = pd.DataFrame({

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

})


print("\nCOMPARACIÓN DE MODELOS")
print("=" * 40)

display(
    tabla_modelos.style.format({
        "R²": "{:.6f}"
    })
)


# ============================================================
# 15. GRAFICAR TODOS LOS MODELOS
# ============================================================

for resultado in resultados:

    modelo = resultado["Modelo"]

    ecuacion = resultado["Ecuación"]

    r2 = resultado["R²"]

    funcion = resultado["Funcion"]


    # Valores X para dibujar la curva

    x_grafico = np.linspace(
        min(x),
        max(x),
        300
    )


    # Valores Y del modelo

    y_grafico = funcion(
        x_grafico
    )


    # --------------------------------------------------------
    # Crear gráfico
    # --------------------------------------------------------

    plt.figure(
        figsize=(8, 5)
    )


    # Datos experimentales

    plt.scatter(
        x,
        y,
        s=60,
        label="Datos experimentales"
    )


    # Modelo

    plt.plot(
        x_grafico,
        y_grafico,
        label=modelo
    )


    # --------------------------------------------------------
    # Ecuación y R²
    # --------------------------------------------------------

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
            alpha=0.85
        )
    )


    plt.xlabel(
        "Concentración"
    )

    plt.ylabel(
        "%RSD"
    )

    plt.title(
        f"Modelo {modelo}"
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.legend()

    plt.tight_layout()

    plt.show()


# ============================================================
# 16. SELECCIÓN MANUAL DEL MODELO
# ============================================================

print("\nSELECCIÓN DEL MODELO")
print("=" * 40)

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
    "técnicamente apropiado según los "
    "resultados y gráficos."
)


opcion = int(
    input(
        "\nIngrese el número del modelo seleccionado: "
    )
)


# Validar selección

if opcion < 1 or opcion > len(resultados):

    raise ValueError(
        "La opción seleccionada no es válida."
    )


seleccionado = resultados[
    opcion - 1
]


# ============================================================
# 17. MOSTRAR MODELO SELECCIONADO
# ============================================================

print("\nMODELO SELECCIONADO")
print("=" * 40)

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
# 18. SOLICITAR CONCENTRACIÓN DE LA MUESTRA
# ============================================================

print("\nCÁLCULO DE Sr PARA UNA MUESTRA")
print("=" * 40)

concentracion_muestra = float(
    input(
        "\nIngrese la concentración de la muestra: "
    )
)


# ============================================================
# 19. CALCULAR %RSD DE LA MUESTRA
# ============================================================

funcion = seleccionado["Funcion"]

rsd_muestra = funcion(
    concentracion_muestra
)


# ============================================================
# 20. CALCULAR Sr DE LA MUESTRA
# ============================================================

Sr_muestra = (
    rsd_muestra
    * concentracion_muestra
) / 100


# ============================================================
# 21. MOSTRAR RESULTADO FINAL
# ============================================================

print("\nRESULTADO FINAL")
print("=" * 40)

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
    f"{concentracion_muestra:.4f}"
)

print(
    f"%RSD estimado: "
    f"{rsd_muestra:.6f} %"
)

print(
    f"Sr estimado: "
    f"{Sr_muestra:.6f}"
)
