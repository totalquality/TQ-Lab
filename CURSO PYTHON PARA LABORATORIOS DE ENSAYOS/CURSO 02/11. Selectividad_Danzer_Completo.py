# -*- coding: utf-8 -*-
"""
SELECTIVIDAD – MÉTODO DE DÄNZER
Versión con detección automática de réplicas por columnas

Estructura esperada del Excel
-----------------------------
Método completo:
    Hoja "Analito"       -> Concentracion | R1 | R2 | R3 | ...
    Hoja "Interferente"  -> Concentracion | R1 | R2 | R3 | ...

Cada fila representa un nivel de concentración y las columnas R1, R2, R3...
son las réplicas de respuesta para ese nivel.

Método simplificado:
    Hoja "Analito"       -> Concentracion | R1 | R2 | R3 | ...
    Hoja "Interferente"  -> Concentracion | R1 | R2 | R3 | ...

Se utiliza un único nivel de concentración, con las réplicas en columnas.

El programa detecta automáticamente:
- La columna de concentración.
- Todas las columnas numéricas de respuesta (réplicas).
- Filas/niveles válidos.
- Réplicas faltantes (NaN) sin detener el análisis.

En el método completo:
1. Calcula la media de las réplicas de cada nivel.
2. Ajusta la regresión Respuesta media vs Concentración.
3. Obtiene KA y KI a partir de las pendientes.
4. Calcula Ks = KI / KA.
5. Criterio Dänzer: Ks <= 0.30.

En el método simplificado:
1. Calcula la media de las réplicas.
2. KA = media respuesta del analito / concentración del analito.
3. KI = media respuesta del interferente / concentración del interferente.
4. Ks = KI / KA.
5. Criterio Dänzer: Ks <= 0.30.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ============================================================
# CONFIGURACIÓN
# ============================================================

CARPETA = r"D:\Ciencia_de_Datos\Validación de métodos químicos"
ARCHIVO_POR_DEFECTO = "Selectividad_Danzer_completo.xlsx"
CRITERIO_KS = 0.30


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def buscar_columna_concentracion(df):
    """Busca automáticamente la columna de concentración."""
    palabras = [
        "concentracion", "concentración",
        "concentr", "nivel",
        "mg/l", "mg/kg", "ug/l", "µg/l", "ppm", "ppb"
    ]

    for col in df.columns:
        nombre = str(col).strip().lower()
        if any(p in nombre for p in palabras):
            return col

    # Si no la encuentra por nombre, usa la primera columna numérica
    for col in df.columns:
        serie = pd.to_numeric(df[col], errors="coerce")
        if serie.notna().sum() > 0:
            return col

    raise ValueError("No se pudo identificar la columna de concentración.")


def detectar_replicas(df, columna_concentracion):
    """
    Detecta todas las columnas numéricas distintas de concentración.
    Cada columna numérica se considera una réplica de respuesta.
    """
    replicas = []

    for col in df.columns:
        if col == columna_concentracion:
            continue

        serie = pd.to_numeric(df[col], errors="coerce")

        # Se considera réplica si contiene al menos un dato numérico.
        if serie.notna().sum() > 0:
            replicas.append(col)

    if not replicas:
        raise ValueError(
            "No se detectaron columnas numéricas de respuesta/repetición."
        )

    return replicas


def preparar_datos(df, nombre_hoja):
    """
    Detecta concentración y réplicas.
    Calcula la media de las réplicas para cada fila/nivel.
    """
    col_conc = buscar_columna_concentracion(df)
    replicas = detectar_replicas(df, col_conc)

    datos = df[[col_conc] + replicas].copy()

    datos[col_conc] = pd.to_numeric(datos[col_conc], errors="coerce")

    for col in replicas:
        datos[col] = pd.to_numeric(datos[col], errors="coerce")

    datos = datos.dropna(subset=[col_conc]).copy()

    # Media de réplicas por nivel
    datos["Respuesta_media"] = datos[replicas].mean(axis=1, skipna=True)
    datos["N_replicas"] = datos[replicas].count(axis=1)

    # Conservar solamente filas con al menos una réplica
    datos = datos[datos["N_replicas"] > 0].copy()

    if datos.empty:
        raise ValueError(f"La hoja '{nombre_hoja}' no contiene datos válidos.")

    return datos, col_conc, replicas


def mostrar_estructura(datos, hoja, col_conc, replicas):
    print("\n" + "=" * 72)
    print(f"HOJA: {hoja}")
    print("=" * 72)
    print(f"Columna de concentración detectada: {col_conc}")
    print(f"Réplicas detectadas ({len(replicas)}): {', '.join(map(str, replicas))}")
    print("\nDatos utilizados:")
    print(
        datos[
            [col_conc] + replicas + ["Respuesta_media", "N_replicas"]
        ].to_string(index=False)
    )


def seleccionar_hoja(hojas, texto):
    """
    Busca una hoja por coincidencia con 'Analito' o 'Interferente'.
    Si no la encuentra, usa la hoja indicada por posición.
    """
    texto = texto.lower()

    for hoja in hojas:
        if texto in str(hoja).lower():
            return hoja

    return None


# ============================================================
# MÉTODO COMPLETO
# ============================================================

def metodo_completo(df_analito, df_interferente, hoja_a, hoja_i):

    datos_a, conc_a, reps_a = preparar_datos(df_analito, hoja_a)
    datos_i, conc_i, reps_i = preparar_datos(df_interferente, hoja_i)

    mostrar_estructura(datos_a, hoja_a, conc_a, reps_a)
    mostrar_estructura(datos_i, hoja_i, conc_i, reps_i)

    # Datos para regresión
    x_a = datos_a[conc_a].to_numpy(dtype=float)
    y_a = datos_a["Respuesta_media"].to_numpy(dtype=float)

    x_i = datos_i[conc_i].to_numpy(dtype=float)
    y_i = datos_i["Respuesta_media"].to_numpy(dtype=float)

    if len(x_a) < 2 or len(x_i) < 2:
        raise ValueError(
            "El método completo requiere al menos dos niveles de concentración "
            "para cada curva."
        )

    if len(np.unique(x_a)) < 2 or len(np.unique(x_i)) < 2:
        raise ValueError(
            "El método completo requiere al menos dos concentraciones diferentes."
        )

    reg_a = stats.linregress(x_a, y_a)
    reg_i = stats.linregress(x_i, y_i)

    KA = reg_a.slope
    KI = reg_i.slope

    if KA == 0:
        raise ZeroDivisionError(
            "La pendiente del analito (KA) es cero; no se puede calcular Ks."
        )

    Ks = KI / KA

    pasa = Ks <= CRITERIO_KS

    print("\n" + "=" * 72)
    print("RESULTADOS – DÄNZER MÉTODO COMPLETO")
    print("=" * 72)

    print("\nANALITO")
    print(f"Niveles evaluados : {len(datos_a)}")
    print(f"Réplicas detectadas: {len(reps_a)}")
    print(f"KA (pendiente)    : {KA:.6g}")
    print(f"Intercepto        : {reg_a.intercept:.6g}")
    print(f"R²                : {reg_a.rvalue**2:.6f}")
    print(f"p pendiente       : {reg_a.pvalue:.6g}")

    print("\nINTERFERENTE")
    print(f"Niveles evaluados : {len(datos_i)}")
    print(f"Réplicas detectadas: {len(reps_i)}")
    print(f"KI (pendiente)    : {KI:.6g}")
    print(f"Intercepto        : {reg_i.intercept:.6g}")
    print(f"R²                : {reg_i.rvalue**2:.6f}")
    print(f"p pendiente       : {reg_i.pvalue:.6g}")

    print("\nÍNDICE DE SELECTIVIDAD")
    print(f"Ks = KI / KA      : {Ks:.6f}")
    print(f"Criterio           : Ks <= {CRITERIO_KS:.2f}")

    if pasa:
        print("CONCLUSIÓN: CUMPLE EL CRITERIO DE SELECTIVIDAD.")
    else:
        print("CONCLUSIÓN: NO CUMPLE EL CRITERIO DE SELECTIVIDAD.")

    # --------------------------------------------------------
    # Gráfica conjunta Dänzer
    # --------------------------------------------------------
    # Las curvas del analito y del interferente se muestran
    # en el mismo sistema de ejes para comparar sus pendientes.
    fig, ax = plt.subplots(figsize=(11, 7))

    xline_a = np.linspace(np.min(x_a), np.max(x_a), 300)
    yline_a = reg_a.intercept + reg_a.slope * xline_a

    xline_i = np.linspace(np.min(x_i), np.max(x_i), 300)
    yline_i = reg_i.intercept + reg_i.slope * xline_i

    ax.scatter(
        x_a, y_a,
        s=80,
        marker="o",
        label="Analito – media de réplicas"
    )
    ax.plot(
        xline_a, yline_a,
        linewidth=2,
        label=f"Analito – regresión (KA = {KA:.5g})"
    )

    ax.scatter(
        x_i, y_i,
        s=80,
        marker="s",
        label="Interferente – media de réplicas"
    )
    ax.plot(
        xline_i, yline_i,
        linewidth=2,
        linestyle="--",
        label=f"Interferente – regresión (KI = {KI:.5g})"
    )

    ax.set_title(
        f"Selectividad Dänzer – Curvas de analito e interferente\n"
        f"Ks = {Ks:.4f} | Criterio ≤ {CRITERIO_KS:.2f}"
    )
    ax.set_xlabel("Concentración")
    ax.set_ylabel("Respuesta media")
    ax.grid(alpha=0.25)
    ax.legend()
    plt.tight_layout()
    plt.show()

    return {
        "KA": KA,
        "KI": KI,
        "Ks": Ks,
        "cumple": pasa,
        "datos_analito": datos_a,
        "datos_interferente": datos_i
    }


# ============================================================
# MÉTODO SIMPLIFICADO
# ============================================================

def metodo_simplificado(df_analito, df_interferente, hoja_a, hoja_i):

    datos_a, conc_a, reps_a = preparar_datos(df_analito, hoja_a)
    datos_i, conc_i, reps_i = preparar_datos(df_interferente, hoja_i)

    mostrar_estructura(datos_a, hoja_a, conc_a, reps_a)
    mostrar_estructura(datos_i, hoja_i, conc_i, reps_i)

    # Debe existir un único nivel en cada material
    concentraciones_a = datos_a[conc_a].dropna().unique()
    concentraciones_i = datos_i[conc_i].dropna().unique()

    if len(concentraciones_a) != 1:
        raise ValueError(
            "Método simplificado: la hoja del analito debe tener "
            "un único nivel de concentración."
        )

    if len(concentraciones_i) != 1:
        raise ValueError(
            "Método simplificado: la hoja del interferente debe tener "
            "un único nivel de concentración."
        )

    C_A = float(concentraciones_a[0])
    C_I = float(concentraciones_i[0])

    if C_A == 0 or C_I == 0:
        raise ValueError(
            "Las concentraciones del método simplificado deben ser diferentes de cero."
        )

    # Todas las respuestas de las réplicas
    respuestas_a = df_analito[reps_a].apply(
        pd.to_numeric, errors="coerce"
    ).to_numpy().flatten()
    respuestas_a = respuestas_a[~np.isnan(respuestas_a)]

    respuestas_i = df_interferente[reps_i].apply(
        pd.to_numeric, errors="coerce"
    ).to_numpy().flatten()
    respuestas_i = respuestas_i[~np.isnan(respuestas_i)]

    if len(respuestas_a) == 0 or len(respuestas_i) == 0:
        raise ValueError("No se encontraron respuestas numéricas válidas.")

    media_a = np.mean(respuestas_a)
    media_i = np.mean(respuestas_i)

    KA = media_a / C_A
    KI = media_i / C_I

    if KA == 0:
        raise ZeroDivisionError(
            "KA es cero; no se puede calcular Ks."
        )

    Ks = KI / KA
    pasa = Ks <= CRITERIO_KS

    print("\n" + "=" * 72)
    print("RESULTADOS – DÄNZER MÉTODO SIMPLIFICADO")
    print("=" * 72)

    print("\nANALITO")
    print(f"Concentración     : {C_A:.6g}")
    print(f"N.º de réplicas   : {len(respuestas_a)}")
    print(f"Respuesta media   : {media_a:.6g}")
    print(f"KA                : {KA:.6g}")

    print("\nINTERFERENTE")
    print(f"Concentración     : {C_I:.6g}")
    print(f"N.º de réplicas   : {len(respuestas_i)}")
    print(f"Respuesta media   : {media_i:.6g}")
    print(f"KI                : {KI:.6g}")

    print("\nÍNDICE DE SELECTIVIDAD")
    print(f"Ks = KI / KA      : {Ks:.6f}")
    print(f"Criterio           : Ks <= {CRITERIO_KS:.2f}")

    if pasa:
        print("CONCLUSIÓN: CUMPLE EL CRITERIO DE SELECTIVIDAD.")
    else:
        print("CONCLUSIÓN: NO CUMPLE EL CRITERIO DE SELECTIVIDAD.")

    # --------------------------------------------------------
    # Gráfica
    # --------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    axes[0].boxplot(
        respuestas_a,
        labels=["Analito"],
        patch_artist=True
    )
    axes[0].scatter(
        np.ones(len(respuestas_a)),
        respuestas_a,
        s=45,
        alpha=0.75,
        label="Réplicas"
    )
    axes[0].set_title("Dänzer simplificado – Analito")
    axes[0].set_ylabel("Respuesta")
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].boxplot(
        respuestas_i,
        labels=["Interferente"],
        patch_artist=True
    )
    axes[1].scatter(
        np.ones(len(respuestas_i)),
        respuestas_i,
        s=45,
        alpha=0.75,
        label="Réplicas"
    )
    axes[1].set_title("Dänzer simplificado – Interferente")
    axes[1].set_ylabel("Respuesta")
    axes[1].grid(axis="y", alpha=0.25)

    fig.suptitle(
        f"Selectividad Dänzer – Ks = {Ks:.4f} | Criterio ≤ {CRITERIO_KS:.2f}",
        fontsize=14
    )
    plt.tight_layout()
    plt.show()

    return {
        "KA": KA,
        "KI": KI,
        "Ks": Ks,
        "cumple": pasa,
        "datos_analito": datos_a,
        "datos_interferente": datos_i
    }


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("=" * 72)
    print("SELECTIVIDAD – MÉTODO DE DÄNZER")
    print("=" * 72)

    print("\nSeleccione el procedimiento:")
    print("1. Método completo")
    print("2. Método simplificado")

    while True:
        opcion = input("\nIngrese 1 o 2: ").strip()
        if opcion in ("1", "2"):
            break
        print("Opción no válida. Ingrese 1 o 2.")

    nombre_archivo = input(
        f"\nNombre del archivo Excel "
        f"[Enter = {ARCHIVO_POR_DEFECTO}]: "
    ).strip()

    if not nombre_archivo:
        nombre_archivo = ARCHIVO_POR_DEFECTO

    if not nombre_archivo.lower().endswith(".xlsx"):
        nombre_archivo += ".xlsx"

    archivo = os.path.join(CARPETA, nombre_archivo)

    if not os.path.exists(archivo):
        raise FileNotFoundError(
            f"\nNo se encontró el archivo:\n{archivo}"
        )

    print(f"\nArchivo: {archivo}")

    hojas = pd.ExcelFile(archivo).sheet_names

    print("\nHojas detectadas:")
    for i, hoja in enumerate(hojas, start=1):
        print(f"{i}. {hoja}")

    # Intentar localizar Analito e Interferente
    hoja_a = seleccionar_hoja(hojas, "analito")
    hoja_i = seleccionar_hoja(hojas, "interferente")

    # Si no existen con esos nombres, pedir selección
    if hoja_a is None:
        print("\nNo se encontró una hoja llamada/conteniendo 'Analito'.")
        indice = int(input("Indique el número de hoja para ANALITO: ")) - 1
        hoja_a = hojas[indice]

    if hoja_i is None:
        print("\nNo se encontró una hoja llamada/conteniendo 'Interferente'.")
        indice = int(input("Indique el número de hoja para INTERFERENTE: ")) - 1
        hoja_i = hojas[indice]

    print(f"\nHoja ANALITO      : {hoja_a}")
    print(f"Hoja INTERFERENTE : {hoja_i}")

    df_analito = pd.read_excel(archivo, sheet_name=hoja_a)
    df_interferente = pd.read_excel(archivo, sheet_name=hoja_i)

    if opcion == "1":
        metodo_completo(
            df_analito,
            df_interferente,
            hoja_a,
            hoja_i
        )
    else:
        metodo_simplificado(
            df_analito,
            df_interferente,
            hoja_a,
            hoja_i
        )

    print("\nAnálisis finalizado.")


if __name__ == "__main__":
    main()
