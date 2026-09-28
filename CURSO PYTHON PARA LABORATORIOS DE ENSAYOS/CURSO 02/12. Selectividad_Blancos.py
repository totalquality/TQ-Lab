# -*- coding: utf-8 -*-
"""
SELECTIVIDAD — MÉTODO DE COMPARACIÓN UTILIZANDO BLANCOS DE MUESTRA

Caso:
    Blanco de muestra
    Blanco de muestra fortificado

El procedimiento implementado sigue la lógica del ejemplo planteado:
1. Calcula la media del blanco de muestra.
2. Calcula la media del blanco fortificado.
3. Corrige por la respuesta del blanco:
       C_observada = C_fortificado - C_blanco
4. Calcula el porcentaje de error respecto a la concentración esperada:
       Error (%) = |C_observada - C_esperada| / C_esperada * 100
5. Compara el error con el máximo sesgo/error permitido indicado por el usuario.

IMPORTANTE:
La Guía INM consultada presenta una ecuación denominada "Error (%)"
cuya formulación literal difiere de la operación anterior. Este script
implementa la lógica del ejemplo solicitado: concentración observada
corregida por blanco versus concentración esperada. No se presenta esta
fórmula como una transcripción literal de la ecuación de la Guía.

Archivo esperado:
    D:\\Ciencia_de_Datos\\Validación de métodos químicos\\Selectividad_Blancos.xlsx

La estructura puede ser la del archivo proporcionado:
    Hoja 1

    Tipo de muestra | Réplica 1 | Réplica 2 | Réplica 3
    Blanco de muestra | ...
    Blanco fortificado | ...

El programa también intenta detectar automáticamente nombres similares
y columnas de réplicas.
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURACIÓN
# ============================================================

CARPETA = r"D:\Ciencia_de_Datos\Validación de métodos químicos"
ARCHIVO_DEFECTO = "Selectividad_Blancos.xlsx"
ALPHA = 0.05


# ============================================================
# FUNCIONES
# ============================================================

def normalizar_texto(texto):
    texto = str(texto).strip().lower()
    reemplazos = {
        "á": "a", "é": "e", "í": "i",
        "ó": "o", "ú": "u", "ü": "u",
        "ñ": "n"
    }
    for a, b in reemplazos.items():
        texto = texto.replace(a, b)
    return texto


def buscar_archivo():
    print("\n" + "=" * 72)
    print("SELECTIVIDAD — COMPARACIÓN UTILIZANDO BLANCOS DE MUESTRA")
    print("=" * 72)

    nombre = input(
        f"\nNombre del archivo Excel [Enter = {ARCHIVO_DEFECTO}]: "
    ).strip()

    if not nombre:
        nombre = ARCHIVO_DEFECTO

    ruta = os.path.join(CARPETA, nombre)

    if not os.path.exists(ruta):
        # Permitir que el usuario escriba una ruta completa
        if os.path.exists(nombre):
            ruta = nombre
        else:
            raise FileNotFoundError(
                f"\nNo se encontró el archivo:\n{ruta}\n"
                "Verifique el nombre y la carpeta."
            )

    return ruta


def detectar_filas(df):
    """Detecta las filas de blanco y blanco fortificado."""

    if df.shape[0] < 2:
        raise ValueError(
            "Se requieren al menos dos filas: "
            "Blanco de muestra y Blanco fortificado."
        )

    primera_columna = df.columns[0]
    etiquetas = df[primera_columna].astype(str).map(normalizar_texto)

    idx_blanco = None
    idx_fortificado = None

    for idx, etiqueta in etiquetas.items():
        # Fortificado debe evaluarse primero para evitar que
        # "blanco fortificado" sea tomado como blanco.
        if "fortific" in etiqueta:
            idx_fortificado = idx
        elif "blanco" in etiqueta:
            idx_blanco = idx

    if idx_blanco is None:
        idx_blanco = df.index[0]

    if idx_fortificado is None:
        idx_fortificado = df.index[1]

    return idx_blanco, idx_fortificado


def obtener_replicas(df):
    """Detecta columnas numéricas de réplicas."""

    columnas = []

    for col in df.columns[1:]:
        serie = pd.to_numeric(df[col], errors="coerce")
        if serie.notna().any():
            columnas.append(col)

    if len(columnas) < 2:
        raise ValueError(
            "No se encontraron suficientes columnas numéricas "
            "para las réplicas."
        )

    return columnas


def limpiar_valores(df, fila, columnas):
    valores = pd.to_numeric(
        df.loc[fila, columnas], errors="coerce"
    ).dropna().astype(float).values

    if len(valores) == 0:
        raise ValueError(
            "No se encontraron datos numéricos en una de las filas."
        )

    return valores


def resumen(valores):
    return {
        "n": len(valores),
        "media": np.mean(valores),
        "sd": np.std(valores, ddof=1) if len(valores) > 1 else np.nan,
        "min": np.min(valores),
        "max": np.max(valores),
    }


def graficar_resultados(error_pct, limite_error):
    """
    Gráfico específico para el criterio de selectividad:

    Eje Y  : % de Error
    Línea  : % de Error máximo permitido
    Punto  : % de Error experimental

    El punto experimental queda por debajo o por encima
    del límite según el resultado.
    """

    fig, ax = plt.subplots(figsize=(10, 7))

    # Línea del límite máximo permitido
    ax.axhline(
        limite_error,
        linestyle="--",
        linewidth=2.5,
        label=f"Error máximo permitido = {limite_error:.3f}%"
    )

    # Punto experimental
    ax.scatter(
        [0],
        [error_pct],
        s=220,
        color="red",
        edgecolor="black",
        linewidth=1.5,
        zorder=5,
        label=f"Error experimental = {error_pct:.3f}%"
    )

    # Etiqueta del punto
    ax.annotate(
        f"{error_pct:.3f}%",
        xy=(0, error_pct),
        xytext=(18, 12),
        textcoords="offset points",
        fontsize=12,
        fontweight="bold",
        color="red",
        bbox=dict(
            boxstyle="round,pad=0.35",
            facecolor="white",
            edgecolor="red"
        )
    )

    # Resultado
    cumple = error_pct <= limite_error

    if cumple:
        texto_resultado = "CUMPLE"
    else:
        texto_resultado = "NO CUMPLE"

    ax.text(
        0.98,
        0.95,
        texto_resultado,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=15,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor="white",
            edgecolor="black",
            linewidth=1.5
        )
    )

    # Eje X sin interpretación cuantitativa
    ax.set_xlim(-0.5, 0.5)
    ax.set_xticks([0])
    ax.set_xticklabels(["Error experimental"])

    ax.set_ylabel("% de Error", fontsize=12)
    ax.set_xlabel("Evaluación de selectividad", fontsize=12)

    ax.set_title(
        "Selectividad — Evaluación del porcentaje de error",
        fontsize=15,
        fontweight="bold"
    )

    # El eje Y parte de cero para facilitar la comparación
    # entre error experimental y límite.
    max_y = max(limite_error, error_pct, 1)
    ax.set_ylim(0, max_y * 1.25)

    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper left")

    plt.tight_layout()
    plt.show()


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

try:
    ruta = buscar_archivo()

    print("\nArchivo seleccionado:")
    print(ruta)

    # --------------------------------------------------------
    # Lectura
    # --------------------------------------------------------
    hojas = pd.read_excel(ruta, sheet_name=None)

    print("\nHojas detectadas:")
    for i, hoja in enumerate(hojas.keys(), start=1):
        print(f"  {i}. {hoja}")

    # Para este enfoque se utiliza la primera hoja disponible.
    nombre_hoja = list(hojas.keys())[0]
    df = hojas[nombre_hoja].copy()

    print(f"\nHoja utilizada: {nombre_hoja}")

    if df.empty:
        raise ValueError("La hoja seleccionada está vacía.")

    # --------------------------------------------------------
    # Detección de filas
    # --------------------------------------------------------
    idx_blanco, idx_fortificado = detectar_filas(df)

    columnas_replicas = obtener_replicas(df)

    blanco = limpiar_valores(
        df, idx_blanco, columnas_replicas
    )

    fortificado = limpiar_valores(
        df, idx_fortificado, columnas_replicas
    )

    # --------------------------------------------------------
    # Mostrar datos detectados
    # --------------------------------------------------------
    print("\n" + "=" * 72)
    print("DATOS DETECTADOS")
    print("=" * 72)

    print("\nBlanco de muestra:")
    print(np.array2string(blanco, precision=6))

    print("\nBlanco de muestra fortificado:")
    print(np.array2string(fortificado, precision=6))

    # --------------------------------------------------------
    # Concentración esperada
    # --------------------------------------------------------
    print("\n" + "-" * 72)
    print("DATOS DEL ESTUDIO")
    print("-" * 72)

    while True:
        try:
            c_esperada = float(
                input(
                    "\nIngrese la concentración esperada de la "
                    "fortificación: "
                ).replace(",", ".")
            )

            if c_esperada <= 0:
                print("La concentración esperada debe ser > 0.")
                continue

            break

        except ValueError:
            print("Ingrese un número válido.")

    # --------------------------------------------------------
    # Cálculos descriptivos
    # --------------------------------------------------------
    r_blanco = resumen(blanco)
    r_fort = resumen(fortificado)

    media_blanco = r_blanco["media"]
    media_fort = r_fort["media"]

    # Corrección por el blanco
    c_observada = media_fort - media_blanco

    # Error respecto a la concentración esperada
    error_pct = (
        abs(c_observada - c_esperada)
        / c_esperada
        * 100
    )

    # --------------------------------------------------------
    # Criterio de aceptación
    # --------------------------------------------------------
    print("\n" + "-" * 72)
    print("CRITERIO DE ACEPTACIÓN")
    print("-" * 72)

    while True:
        try:
            limite_error = float(
                input(
                    "\nIngrese el máximo error/sesgo permitido (%) "
                    "para este nivel: "
                ).replace(",", ".")
            )

            if limite_error < 0:
                print("El límite no puede ser negativo.")
                continue

            break

        except ValueError:
            print("Ingrese un número válido.")

    cumple = error_pct <= limite_error

    # --------------------------------------------------------
    # Resultados
    # --------------------------------------------------------
    print("\n" + "=" * 72)
    print("RESULTADOS")
    print("=" * 72)

    print("\nBLANCO DE MUESTRA")
    print(f"  n                  = {r_blanco['n']}")
    print(f"  Media              = {media_blanco:.6f}")
    print(f"  Desviación estándar= {r_blanco['sd']:.6f}")

    print("\nBLANCO FORTIFICADO")
    print(f"  n                  = {r_fort['n']}")
    print(f"  Media              = {media_fort:.6f}")
    print(f"  Desviación estándar= {r_fort['sd']:.6f}")

    print("\nCÁLCULO DE SELECTIVIDAD")
    print(
        f"  Concentración esperada              = "
        f"{c_esperada:.6f}"
    )
    print(
        f"  Concentración observada corregida   = "
        f"{c_observada:.6f}"
    )
    print(
        f"  Error (%)                            = "
        f"{error_pct:.3f}%"
    )
    print(
        f"  Error máximo permitido               = "
        f"{limite_error:.3f}%"
    )

    print("\n" + "-" * 72)

    if cumple:
        print("CONCLUSIÓN: EL MÉTODO CUMPLE EL CRITERIO DE SELECTIVIDAD.")
        print(
            "La diferencia entre la concentración observada, "
            "corregida por el blanco, y la concentración esperada "
            "no supera el límite establecido."
        )
    else:
        print(
            "CONCLUSIÓN: EL MÉTODO NO CUMPLE EL CRITERIO "
            "DE SELECTIVIDAD."
        )
        print(
            "La diferencia entre la concentración observada, "
            "corregida por el blanco, y la concentración esperada "
            "supera el límite establecido."
        )

    # --------------------------------------------------------
    # Tabla resumen
    # --------------------------------------------------------
    tabla = pd.DataFrame({
        "Indicador": [
            "Media blanco de muestra",
            "Media blanco fortificado",
            "Concentración esperada",
            "Concentración observada corregida",
            "Error (%)",
            "Error máximo permitido (%)",
            "Resultado"
        ],
        "Valor": [
            media_blanco,
            media_fort,
            c_esperada,
            c_observada,
            error_pct,
            limite_error,
            "CUMPLE" if cumple else "NO CUMPLE"
        ]
    })

    print("\nTABLA RESUMEN")
    print(tabla.to_string(index=False))

    # --------------------------------------------------------
    # Gráfico
    # --------------------------------------------------------
    graficar_resultados(
        error_pct,
        limite_error
    )

except Exception as e:
    print("\n" + "=" * 72)
    print("ERROR")
    print("=" * 72)
    print(str(e))

input("\nPresione ENTER para finalizar...")
