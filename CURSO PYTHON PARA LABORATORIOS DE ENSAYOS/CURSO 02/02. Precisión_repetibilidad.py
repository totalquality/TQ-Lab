# ============================================================
# CÁLCULO DE LA DESVIACIÓN ESTÁNDAR DE REPETIBILIDAD (Sr)
# PARA TODOS LOS NIVELES DE TRABAJO
#
# Cada hoja del Excel = un nivel de trabajo.
#
# Para cada nivel se calcula:
#   1. Desviación estándar de cada analista/columna
#   2. Sr de repetibilidad agrupada
#   3. Concentración media experimental
#   4. %RSD experimental
#   5. PRSDR de Horwitz
#   6. %RSD Horwitz para repetibilidad = 0.5 × PRSDR
#   7. HorRat(r)
#   8. Comparación directa contra 0.5 × PRSDR
#   9. Conclusión
#
# Mantiene la misma estructura y criterios del script original.
# ============================================================


# ============================================================
# 1. BIBLIOTECAS
# ============================================================

import pandas as pd
import numpy as np


# ============================================================
# 2. CONFIGURACIÓN
# ============================================================

archivo = (
    r"D:\Ciencia_de_Datos\Validación de métodos químicos"
    r"\precision.xlsx"
)

alpha = 0.05  # Se conserva como referencia, aunque HorRat(r)
              # y el objetivo 0.5×PRSDR no utilizan alpha.


# ============================================================
# 3. FUNCIÓN PARA SELECCIONAR LA UNIDAD
# ============================================================

def seleccionar_unidad(numero, nombre_nivel):

    print("\n" + "=" * 75)
    print(f"NIVEL {numero} — {nombre_nivel}")
    print("SELECCIÓN DE LA FRACCIÓN MÁSICA PARA HORWITZ")
    print("=" * 75)

    print(
        "Seleccione la unidad de concentración para convertir "
        "C a fracción másica:"
    )

    print("1. ppm  -> factor 10^-6")
    print("2. ppb  -> factor 10^-9")
    print("3. %    -> factor 10^-2")

    factores = {
        "1": (1e-6, "ppm"),
        "2": (1e-9, "ppb"),
        "3": (1e-2, "%")
    }

    while True:

        opcion = input(
            f"[NIVEL {numero}: {nombre_nivel}] "
            "Ingrese una opción (1, 2 o 3): "
        ).strip()

        if opcion in factores:
            return factores[opcion]

        print(
            "Opción no válida. Debe seleccionar 1, 2 o 3."
        )


# ============================================================
# 4. ENCABEZADO
# ============================================================

print("\n" + "#" * 90)
print("PRECISIÓN — REPETIBILIDAD")
print("CÁLCULO DE Sr PARA TODOS LOS NIVELES DE TRABAJO")
print("#" * 90)

print("\nArchivo:")
print(archivo)


# ============================================================
# 5. VERIFICAR ARCHIVO
# ============================================================

from pathlib import Path

ruta = Path(archivo)

if not ruta.exists():

    print("\n" + "!" * 90)
    print("NO SE ENCONTRÓ EL ARCHIVO")
    print("!" * 90)
    print(f"Ruta buscada:\n{archivo}")

    raise FileNotFoundError(
        f"No se encontró el archivo Excel:\n{archivo}"
    )


# ============================================================
# 6. IMPORTAR TODAS LAS HOJAS
# ============================================================

datos_excel = pd.read_excel(
    archivo,
    sheet_name=None
)

print("\nNIVELES DETECTADOS")
print("-" * 75)

for i, nombre_hoja in enumerate(
    datos_excel.keys(),
    start=1
):
    print(f"{i} → {nombre_hoja}")


# ============================================================
# 7. LISTA PARA EL RESUMEN FINAL
# ============================================================

resultados_finales = []


# ============================================================
# 8. PROCESAR CADA NIVEL
# ============================================================

for numero, (nombre_hoja, datos) in enumerate(
    datos_excel.items(),
    start=1
):

    print("\n\n")

    print("█" * 90)
    print(
        f"█   NIVEL {numero} — {nombre_hoja}"
    )
    print(
        "█   EVALUACIÓN DE PRECISIÓN — REPETIBILIDAD"
    )
    print(
        "█   Todos los cálculos siguientes pertenecen "
        "EXCLUSIVAMENTE a este nivel."
    )
    print("█" * 90)


    # ========================================================
    # 8.1 SELECCIONAR COLUMNAS NUMÉRICAS
    # ========================================================

    columnas_numericas = (
        datos
        .select_dtypes(include=np.number)
        .columns
        .tolist()
    )

    if len(columnas_numericas) == 0:

        print(
            f"\nADVERTENCIA: el nivel '{nombre_hoja}' "
            "no contiene columnas numéricas."
        )

        print(
            "Se omitirá este nivel."
        )

        continue

    print("\nColumnas numéricas detectadas:")

    for columna in columnas_numericas:
        print(f"  → {columna}")


    # ========================================================
    # 8.2 DATOS NUMÉRICOS
    # ========================================================

    datos_numericos = datos[
        columnas_numericas
    ].apply(
        pd.to_numeric,
        errors="coerce"
    )


    # ========================================================
    # 8.3 ESTADÍSTICAS DE CADA ANALISTA/COLUMNA
    # ========================================================

    estadisticas = datos_numericos.describe()

    s = estadisticas.loc["std"]

    n = datos_numericos.count()


    # ========================================================
    # 8.4 MOSTRAR ESTADÍSTICAS
    # ========================================================

    tabla_estadisticas = pd.DataFrame({
        "N": n,
        "Desviación estándar (s)": s
    })

    print("\n" + "-" * 75)
    print("DESVIACIÓN ESTÁNDAR DE CADA ANALISTA/COLUMNA")
    print("-" * 75)

    display(
        tabla_estadisticas
    )


    # ========================================================
    # 8.5 SR DE REPETIBILIDAD
    # ========================================================
    #
    # Sr = sqrt[
    #       Σ((n_i - 1) s_i²)
    #       /
    #       Σ(n_i - 1)
    #      ]
    #
    # Se conserva exactamente la estructura del script original.
    # ========================================================

    denominador = np.sum(
        n - 1
    )

    if denominador <= 0:

        raise ValueError(
            f"El nivel '{nombre_hoja}' no tiene suficientes "
            "datos para calcular Sr."
        )

    Sr = np.sqrt(
        np.sum(
            (n - 1) * s**2
        )
        /
        denominador
    )


    # ========================================================
    # 8.6 CONCENTRACIÓN MEDIA EXPERIMENTAL
    # ========================================================

    concentracion_experimental = (
        datos_numericos
        .mean()
        .mean()
    )

    if concentracion_experimental <= 0:

        raise ValueError(
            f"La concentración media experimental del nivel "
            f"'{nombre_hoja}' debe ser > 0."
        )


    # ========================================================
    # 8.7 %RSD EXPERIMENTAL
    # ========================================================

    RSD_experimental = (
        Sr
        /
        concentracion_experimental
    ) * 100


    # ========================================================
    # 8.8 MOSTRAR RESULTADOS EXPERIMENTALES
    # ========================================================

    print("\n" + "=" * 75)
    print(
        f"EVALUACIÓN DE PRECISIÓN FRENTE A HORWITZ"
        f" — {nombre_hoja}"
    )
    print("=" * 75)

    print(
        f"Concentración media experimental = "
        f"{concentracion_experimental:.6g}"
    )

    print(
        f"Desviación estándar Sr           = "
        f"{Sr:.6g}"
    )

    print(
        f"%RSD experimental                = "
        f"{RSD_experimental:.4f} %"
    )


    # ========================================================
    # 8.9 SELECCIÓN DE UNIDAD
    # ========================================================

    factor_masico, unidad_concentracion = (
        seleccionar_unidad(
            numero,
            nombre_hoja
        )
    )

    C = (
        concentracion_experimental
        *
        factor_masico
    )

    if C <= 0:

        raise ValueError(
            "La concentración convertida a fracción "
            "másica debe ser > 0."
        )


    print(
        f"\nUnidad seleccionada              = "
        f"{unidad_concentracion}"
    )

    print(
        f"Factor de conversión             = "
        f"{factor_masico:.0e}"
    )

    print(
        f"C = {C:.6e} (fracción másica)"
    )


    # ========================================================
    # 8.10 %RSD HORWITZ — REPRODUCIBILIDAD
    # ========================================================
    #
    # PRSDR (%) = 2 C^(-0.15)
    # ========================================================

    PRSDR = (
        2
        *
        (
            C ** (-0.15)
        )
    )


    # ========================================================
    # 8.11 %RSD HORWITZ — REPETIBILIDAD
    # ========================================================
    #
    # PRSD_r = 0.5 × PRSDR
    # ========================================================

    factor_repetibilidad = 0.5

    PRSD_repetibilidad = (
        factor_repetibilidad
        *
        PRSDR
    )


    # ========================================================
    # 8.12 MOSTRAR HORWITZ
    # ========================================================

    print("\nRESULTADOS DE HORWITZ")
    print("-" * 75)

    print(
        f"%RSD Horwitz - reproducibilidad "
        f"(PRSDR) = {PRSDR:.4f} %"
    )

    print(
        f"Factor reproducibilidad → repetibilidad "
        f"= {factor_repetibilidad:.2f}"
    )

    print(
        f"%RSD Horwitz - repetibilidad "
        f"(0.5 × PRSDR) = {PRSD_repetibilidad:.4f} %"
    )


    # ========================================================
    # 8.13 HORRAT(r)
    # ========================================================
    #
    # HorRat(r) = RSD experimental / PRSDR
    #
    # Criterio:
    # 0.3 ≤ HorRat(r) ≤ 1.3
    # ========================================================

    HorRat_r = (
        RSD_experimental
        /
        PRSDR
    )


    print("\nHORRAT(r)")
    print("-" * 75)

    print(
        f"HorRat(r) = %RSD experimental / PRSDR "
        f"= {HorRat_r:.4f}"
    )

    print(
        "Criterio de referencia: "
        "0.3 ≤ HorRat(r) ≤ 1.3"
    )


    if (
        0.3
        <= HorRat_r
        <= 1.3
    ):

        conclusion_horrat = "PASA"

    else:

        conclusion_horrat = "NO PASA"


    print(
        f"Conclusión HorRat(r): "
        f"{conclusion_horrat}"
    )


    # ========================================================
    # 8.14 COMPARACIÓN CONTRA OBJETIVO DE REPETIBILIDAD
    # ========================================================

    if (
        RSD_experimental
        <=
        PRSD_repetibilidad
    ):

        conclusion_objetivo = "PASA"

    else:

        conclusion_objetivo = "NO PASA"


    print(
        "\nCOMPARACIÓN CON EL OBJETIVO "
        "DE REPETIBILIDAD"
    )

    print("-" * 75)

    print(
        f"%RSD experimental              = "
        f"{RSD_experimental:.4f} %"
    )

    print(
        f"%RSD Horwitz repetibilidad     = "
        f"{PRSD_repetibilidad:.4f} %"
    )

    print(
        f"Conclusión frente al objetivo  = "
        f"{conclusion_objetivo}"
    )


    # ========================================================
    # 8.15 CONCLUSIÓN FINAL
    # ========================================================

    print("\nCONCLUSIÓN")
    print("-" * 75)

    if (
        conclusion_horrat
        ==
        "PASA"
    ):

        print(
            "El %RSD experimental se encuentra dentro "
            "del intervalo de referencia establecido "
            "para HorRat(r) (0.3–1.3)."
        )

    else:

        print(
            "El %RSD experimental se encuentra fuera "
            "del intervalo de referencia establecido "
            "para HorRat(r) (0.3–1.3)."
        )


    if (
        conclusion_objetivo
        ==
        "PASA"
    ):

        print(
            "Además, el %RSD experimental es menor o "
            "igual al objetivo de repetibilidad definido "
            "como 0.5 × PRSDR."
        )

    else:

        print(
            "Además, el %RSD experimental supera el "
            "objetivo de repetibilidad definido como "
            "0.5 × PRSDR."
        )


    # ========================================================
    # 8.16 RESUMEN DEL NIVEL
    # ========================================================

    resumen_nivel = pd.DataFrame({
        "Indicador": [
            "Nivel",
            "Concentración media",
            "Unidad seleccionada",
            "Factor de conversión",
            "Fracción másica C",
            "Sr experimental",
            "%RSD experimental",
            "%RSD Horwitz — reproducibilidad",
            "%RSD Horwitz — repetibilidad (0.5×PRSDR)",
            "HorRat(r)",
            "Criterio HorRat(r)",
            "Resultado HorRat(r)",
            "Resultado frente a objetivo 0.5×PRSDR"
        ],
        "Resultado": [
            nombre_hoja,
            f"{concentracion_experimental:.6g}",
            unidad_concentracion,
            f"{factor_masico:.0e}",
            f"{C:.6e}",
            f"{Sr:.6g}",
            f"{RSD_experimental:.4f} %",
            f"{PRSDR:.4f} %",
            f"{PRSD_repetibilidad:.4f} %",
            f"{HorRat_r:.4f}",
            "0.3 – 1.3",
            conclusion_horrat,
            conclusion_objetivo
        ]
    })

    print("\n" + "=" * 75)
    print(
        f"RESUMEN DE PRECISIÓN — {nombre_hoja}"
    )
    print("=" * 75)

    display(
        resumen_nivel
    )


    # ========================================================
    # 8.17 GUARDAR RESULTADO PARA RESUMEN GENERAL
    # ========================================================

    resultados_finales.append({
        "Nivel": nombre_hoja,
        "N": int(n.sum()),
        "Concentración media": concentracion_experimental,
        "Unidad": unidad_concentracion,
        "C": C,
        "Sr": Sr,
        "%RSD experimental": RSD_experimental,
        "%RSD Horwitz reproducibilidad": PRSDR,
        "%RSD Horwitz repetibilidad": PRSD_repetibilidad,
        "HorRat(r)": HorRat_r,
        "Resultado HorRat(r)": conclusion_horrat,
        "Resultado 0.5×PRSDR": conclusion_objetivo
    })


    # ========================================================
    # 8.18 FIN DEL NIVEL
    # ========================================================

    print("\n" + "─" * 90)
    print(
        f"FIN DEL NIVEL {numero} — {nombre_hoja}"
    )
    print("─" * 90)


# ============================================================
# 9. RESUMEN FINAL DE TODOS LOS NIVELES
# ============================================================

print("\n\n")

print("#" * 110)
print("RESUMEN FINAL — PRECISIÓN / REPETIBILIDAD")
print("#" * 110)

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
# 10. FIN
# ============================================================

print("\n" + "#" * 110)
print("ANÁLISIS DE REPETIBILIDAD PARA TODOS LOS NIVELES TERMINADO")
print("#" * 110)
