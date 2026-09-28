# ============================================================
# SELECTIVIDAD – MÉTODO DE DÄNZER
# COMPLETO + SIMPLIFICADO
# ============================================================
# El programa pregunta al inicio:
#   1. Método completo
#   2. Método simplificado
#
# MÉTODO COMPLETO
# ----------------
# Excel:
# Hoja Analito:
# Concentracion | R1 | R2 | R3 | R4...
# 0             | ...| ...| ...| ...
# 10            | ...| ...| ...| ...
#
# Hoja Interferente:
# Concentracion | R1 | R2 | R3 | R4...
#
# Las réplicas están en COLUMNAS.
# Se calcula la media por nivel y luego la regresión.
# El nivel 0, si existe, SE INCLUYE en la regresión.
#
# MÉTODO SIMPLIFICADO
# --------------------
# Excel:
# Hoja Analito:
# Concentracion | Respuesta
# 0.5           | ...
# 0.5           | ...
#
# Hoja Interferente:
# Concentracion | Respuesta
# 100           | ...
# 100           | ...
#
# Las réplicas están en FILAS.
# Se calcula la media de las réplicas.
# ============================================================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

CARPETA = r"D:\Ciencia_de_Datos\Validación de métodos químicos"
ARCHIVO_POR_DEFECTO = "Selectividad_Danzer_completo.xlsx"
CRITERIO_KS = 0.30


def normalizar(texto):
    texto = str(texto).strip().lower()
    reemplazos = {
        "á": "a", "é": "e", "í": "i",
        "ó": "o", "ú": "u", "ü": "u"
    }
    for a, b in reemplazos.items():
        texto = texto.replace(a, b)
    return texto


def detectar_hojas(hojas):
    hoja_analito = next(
        (h for h in hojas if "analito" in normalizar(h)),
        None
    )
    hoja_interferente = next(
        (h for h in hojas if "interferente" in normalizar(h)),
        None
    )

    if hoja_analito is None:
        raise ValueError(
            "No se encontró una hoja identificable como 'Analito'."
        )

    if hoja_interferente is None:
        raise ValueError(
            "No se encontró una hoja identificable como 'Interferente'."
        )

    return hoja_analito, hoja_interferente


def detectar_columna_concentracion(df):
    for c in df.columns:
        nombre = normalizar(c)
        if any(p in nombre for p in
               ["concentracion", "concentr", "nivel"]):
            return c

    numericas = df.select_dtypes(include=np.number).columns.tolist()

    if not numericas:
        raise ValueError(
            "No se encontró una columna de concentración."
        )

    return numericas[0]


def detectar_columna_respuesta(df, excluir=None):
    for c in df.columns:
        if c == excluir:
            continue

        nombre = normalizar(c)

        if any(p in nombre for p in [
            "respuesta", "senal", "signal", "absorbancia",
            "intensidad", "emision"
        ]):
            return c

    numericas = [
        c for c in df.select_dtypes(include=np.number).columns
        if c != excluir
    ]

    if not numericas:
        raise ValueError(
            "No se encontraron columnas de respuesta."
        )

    return numericas[0]


def detectar_replicas_completo(df, col_conc):
    """
    En el método completo, todas las columnas numéricas distintas
    de Concentracion se consideran réplicas.
    """
    replicas = []

    for c in df.columns:
        if c == col_conc:
            continue

        serie = pd.to_numeric(df[c], errors="coerce")

        # Una columna de réplica debe contener al menos un valor numérico.
        if serie.notna().any():
            replicas.append(c)

    if not replicas:
        raise ValueError(
            "No se encontraron columnas de réplicas en el método completo."
        )

    return replicas


def preparar_completo(df, nombre_hoja):
    col_conc = detectar_columna_concentracion(df)
    columnas_replicas = detectar_replicas_completo(df, col_conc)

    concentracion = pd.to_numeric(
        df[col_conc], errors="coerce"
    )

    matriz = df[columnas_replicas].apply(
        pd.to_numeric, errors="coerce"
    )

    datos = pd.DataFrame({
        "Concentracion": concentracion
    })

    for c in columnas_replicas:
        datos[c] = matriz[c]

    datos = datos.dropna(
        subset=["Concentracion"],
        how="any"
    )

    # Media de las réplicas de cada nivel.
    datos["Respuesta_media"] = datos[columnas_replicas].mean(
        axis=1,
        skipna=True
    )

    datos = datos.dropna(
        subset=["Respuesta_media"]
    )

    if len(datos) < 2:
        raise ValueError(
            f"La hoja '{nombre_hoja}' necesita al menos dos "
            "niveles de concentración."
        )

    return datos, col_conc, columnas_replicas


def preparar_simplificado(df, nombre_hoja):
    col_conc = detectar_columna_concentracion(df)
    col_resp = detectar_columna_respuesta(
        df,
        excluir=col_conc
    )

    datos = pd.DataFrame({
        "Concentracion": pd.to_numeric(
            df[col_conc], errors="coerce"
        ),
        "Respuesta": pd.to_numeric(
            df[col_resp], errors="coerce"
        )
    }).dropna()

    if datos.empty:
        raise ValueError(
            f"La hoja '{nombre_hoja}' no contiene datos válidos."
        )

    niveles = datos["Concentracion"].unique()

    if len(niveles) != 1:
        raise ValueError(
            f"La hoja '{nombre_hoja}' debe contener un único "
            "nivel de concentración en el método simplificado."
        )

    concentracion = float(niveles[0])

    if concentracion <= 0:
        raise ValueError(
            f"La concentración de '{nombre_hoja}' debe ser mayor que cero."
        )

    respuestas = datos["Respuesta"].to_numpy(float)

    if len(respuestas) < 2:
        raise ValueError(
            f"La hoja '{nombre_hoja}' necesita al menos dos réplicas."
        )

    return datos, col_conc, col_resp


def regresion_completa(datos):
    x = datos["Concentracion"].to_numpy(float)
    y = datos["Respuesta_media"].to_numpy(float)

    reg = stats.linregress(x, y)

    return x, y, reg


def calcular_simplificado(datos_A, datos_I):
    C_A = float(datos_A["Concentracion"].iloc[0])
    C_I = float(datos_I["Concentracion"].iloc[0])

    y_A = datos_A["Respuesta"].to_numpy(float)
    y_I = datos_I["Respuesta"].to_numpy(float)

    media_A = np.mean(y_A)
    media_I = np.mean(y_I)

    KA = media_A / C_A
    KI = media_I / C_I

    if np.isclose(KA, 0):
        raise ZeroDivisionError(
            "KA es cero o demasiado cercano a cero."
        )

    Ks = KI / KA
    cumple = Ks <= CRITERIO_KS

    return C_A, C_I, y_A, y_I, media_A, media_I, KA, KI, Ks, cumple


def ejecutar_completo(df_A, df_I, nombre_A, nombre_I):

    datos_A, col_CA, reps_A = preparar_completo(
        df_A, nombre_A
    )
    datos_I, col_CI, reps_I = preparar_completo(
        df_I, nombre_I
    )

    x_A, y_A, reg_A = regresion_completa(datos_A)
    x_I, y_I, reg_I = regresion_completa(datos_I)

    KA = reg_A.slope
    KI = reg_I.slope

    if np.isclose(KA, 0):
        raise ZeroDivisionError(
            "KA es cero o demasiado cercano a cero."
        )

    Ks = KI / KA
    cumple = Ks <= CRITERIO_KS

    print("\n" + "=" * 75)
    print("RESULTADOS – DÄNZER COMPLETO")
    print("=" * 75)

    print("\nANALITO")
    print(f"  Réplicas detectadas : {len(reps_A)}")
    print(f"  Niveles              : {len(x_A)}")
    print(f"  KA (pendiente)       : {KA:.8f}")
    print(f"  Intercepto           : {reg_A.intercept:.8f}")
    print(f"  R²                   : {reg_A.rvalue**2:.6f}")

    print("\nINTERFERENTE")
    print(f"  Réplicas detectadas : {len(reps_I)}")
    print(f"  Niveles              : {len(x_I)}")
    print(f"  KI (pendiente)       : {KI:.8f}")
    print(f"  Intercepto           : {reg_I.intercept:.8f}")
    print(f"  R²                   : {reg_I.rvalue**2:.6f}")

    print("\nCOEFICIENTE DE SELECTIVIDAD")
    print(f"  Ks = KI / KA         : {Ks:.6f}")
    print(f"  Criterio             : Ks <= {CRITERIO_KS:.2f}")

    if cumple:
        print("\nCONCLUSIÓN:")
        print("  EL MÉTODO CUMPLE EL CRITERIO DE SELECTIVIDAD DE DÄNZER.")
    else:
        print("\nCONCLUSIÓN:")
        print("  EL MÉTODO NO CUMPLE EL CRITERIO DE SELECTIVIDAD DE DÄNZER.")

    # Gráfica conjunta: ambas curvas en los mismos ejes.
    fig, ax = plt.subplots(figsize=(11, 7))

    xline_A = np.linspace(
        np.min(x_A), np.max(x_A), 300
    )
    yline_A = (
        reg_A.intercept +
        reg_A.slope * xline_A
    )

    xline_I = np.linspace(
        np.min(x_I), np.max(x_I), 300
    )
    yline_I = (
        reg_I.intercept +
        reg_I.slope * xline_I
    )

    ax.scatter(
        x_A, y_A,
        s=80,
        marker="o",
        label="Analito – media de réplicas"
    )
    ax.plot(
        xline_A, yline_A,
        linewidth=2,
        label=f"Analito – regresión (KA = {KA:.5g})"
    )

    ax.scatter(
        x_I, y_I,
        s=80,
        marker="s",
        label="Interferente – media de réplicas"
    )
    ax.plot(
        xline_I, yline_I,
        linewidth=2,
        linestyle="--",
        label=f"Interferente – regresión (KI = {KI:.5g})"
    )

    ax.set_title(
        f"Selectividad Dänzer – Curvas de analito e interferente\n"
        f"Ks = {Ks:.4f} | Criterio ≤ {CRITERIO_KS:.2f}",
        fontsize=14,
        fontweight="bold"
    )
    ax.set_xlabel("Concentración")
    ax.set_ylabel("Respuesta media")
    ax.grid(alpha=0.25)
    ax.legend()

    plt.tight_layout()
    plt.show()


def ejecutar_simplificado(df_A, df_I, nombre_A, nombre_I):

    datos_A, col_CA, col_RA = preparar_simplificado(
        df_A, nombre_A
    )
    datos_I, col_CI, col_RI = preparar_simplificado(
        df_I, nombre_I
    )

    (
        C_A, C_I, y_A, y_I,
        media_A, media_I,
        KA, KI, Ks, cumple
    ) = calcular_simplificado(
        datos_A, datos_I
    )

    print("\n" + "=" * 75)
    print("RESULTADOS – DÄNZER SIMPLIFICADO")
    print("=" * 75)

    print("\nANALITO")
    print(f"  Concentración       : {C_A:g}")
    print(f"  Réplicas detectadas : {len(y_A)}")
    print(f"  Respuesta promedio  : {media_A:.6f}")
    print(f"  KA                  : {KA:.8f}")

    print("\nINTERFERENTE")
    print(f"  Concentración       : {C_I:g}")
    print(f"  Réplicas detectadas : {len(y_I)}")
    print(f"  Respuesta promedio  : {media_I:.6f}")
    print(f"  KI                  : {KI:.8f}")

    print("\nCOEFICIENTE DE SELECTIVIDAD")
    print(f"  Ks = KI / KA        : {Ks:.6f}")
    print(f"  Criterio            : Ks <= {CRITERIO_KS:.2f}")

    if cumple:
        print("\nCONCLUSIÓN:")
        print("  EL MÉTODO CUMPLE EL CRITERIO DE SELECTIVIDAD DE DÄNZER.")
    else:
        print("\nCONCLUSIÓN:")
        print("  EL MÉTODO NO CUMPLE EL CRITERIO DE SELECTIVIDAD DE DÄNZER.")

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    axes[0].boxplot(y_A, patch_artist=True)
    axes[0].scatter(
        np.ones(len(y_A)), y_A,
        s=70, label="Réplicas"
    )
    axes[0].axhline(
        media_A,
        linewidth=2,
        label=f"Media = {media_A:.4f}"
    )
    axes[0].set_title(
        "Analito",
        fontsize=13,
        fontweight="bold"
    )
    axes[0].set_ylabel("Respuesta instrumental")
    axes[0].set_xticks([1])
    axes[0].set_xticklabels([f"C = {C_A:g}"])
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend()

    axes[1].boxplot(y_I, patch_artist=True)
    axes[1].scatter(
        np.ones(len(y_I)), y_I,
        s=70, label="Réplicas"
    )
    axes[1].axhline(
        media_I,
        linewidth=2,
        label=f"Media = {media_I:.4f}"
    )
    axes[1].set_title(
        "Interferente",
        fontsize=13,
        fontweight="bold"
    )
    axes[1].set_ylabel("Respuesta instrumental")
    axes[1].set_xticks([1])
    axes[1].set_xticklabels([f"C = {C_I:g}"])
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend()

    estado = "CUMPLE" if cumple else "NO CUMPLE"

    fig.suptitle(
        f"Selectividad Dänzer – Método simplificado\n"
        f"Ks = {Ks:.4f} | Criterio ≤ {CRITERIO_KS:.2f} | {estado}",
        fontsize=15,
        fontweight="bold"
    )

    plt.tight_layout()
    plt.show()


def main():

    print("=" * 75)
    print("SELECTIVIDAD – MÉTODO DE DÄNZER")
    print("=" * 75)

    print("\nSeleccione el procedimiento:")
    print("1. Método completo")
    print("2. Método simplificado")

    opcion = input("\nIngrese 1 o 2: ").strip()

    if opcion not in ("1", "2"):
        raise ValueError("Debe seleccionar 1 o 2.")

    nombre = input(
        f"\nNombre del archivo Excel "
        f"[Enter = {ARCHIVO_POR_DEFECTO}]: "
    ).strip()

    if not nombre:
        nombre = ARCHIVO_POR_DEFECTO

    if not nombre.lower().endswith(".xlsx"):
        nombre += ".xlsx"

    archivo = os.path.join(CARPETA, nombre)

    if not os.path.exists(archivo):
        raise FileNotFoundError(
            f"\nNo se encontró el archivo:\n{archivo}"
        )

    print(f"\nArchivo: {archivo}")

    hojas = pd.ExcelFile(archivo).sheet_names

    print("\nHojas detectadas:")
    for i, hoja in enumerate(hojas, 1):
        print(f"  {i}. {hoja}")

    hoja_A, hoja_I = detectar_hojas(hojas)

    print(f"\nHoja ANALITO      : {hoja_A}")
    print(f"Hoja INTERFERENTE : {hoja_I}")

    df_A = pd.read_excel(
        archivo,
        sheet_name=hoja_A
    )
    df_I = pd.read_excel(
        archivo,
        sheet_name=hoja_I
    )

    if opcion == "1":
        ejecutar_completo(
            df_A, df_I,
            hoja_A, hoja_I
        )
    else:
        ejecutar_simplificado(
            df_A, df_I,
            hoja_A, hoja_I
        )

    print("\nAnálisis finalizado.")


if __name__ == "__main__":
    main()
