#Cálculo de la desviación estándar de repetibilidad (sr) para un nivel de trabajo 

import pandas as pd 
import numpy as np 

# 1. Importar datos 
datos = pd.read_excel(r"D:\Ciencia_de_Datos\Validación de métodos químicos\precision.xlsx",sheet_name="hoja1") 

# 2. Desviación estándar de cada analista 
estadisticas = datos.describe() 

# 3. Extraer las desviaciones estándar 
s = estadisticas.loc["std"] 

# 4. Número de resultados de cada analista 
n = datos.count() 

# 5. Calcular desviación estándar de repetibilidad 
Sr = np.sqrt( 
    np.sum((n - 1) * s**2) / 
    np.sum(n - 1) 
) 

print(f"Desviación estándar de repetibilidad (Sr) = {Sr:.4f} mg/L")

# ============================================================
# ADICIÓN: %RSD EXPERIMENTAL, HORWITZ Y HORRAT(r)
# ============================================================
#
# La ecuación de Horwitz requiere C como fracción másica
# adimensional.
#
# El usuario selecciona al inicio el factor correspondiente:
#   1. ppm -> 10^-6
#   2. ppb -> 10^-9
#   3. %   -> 10^-2
#
# No se genera gráfica de Horwitz.

# ------------------------------------------------------------
# 6. Concentración media experimental
# ------------------------------------------------------------

concentracion_experimental = datos.mean(numeric_only=True).mean()

# ------------------------------------------------------------
# 7. %RSD experimental
# ------------------------------------------------------------

RSD_experimental = (Sr / concentracion_experimental) * 100

print("\n" + "=" * 75)
print("EVALUACIÓN DE PRECISIÓN FRENTE A HORWITZ")
print("=" * 75)

print(f"Concentración media experimental = {concentracion_experimental:.6g}")
print(f"Desviación estándar Sr           = {Sr:.6g}")
print(f"%RSD experimental                = {RSD_experimental:.4f} %")

# ------------------------------------------------------------
# 8. Selección de la unidad / factor para la fracción másica
# ------------------------------------------------------------

print("\nSELECCIÓN DE LA FRACCIÓN MÁSICA PARA HORWITZ")
print("-" * 75)
print("Seleccione la unidad de concentración para convertir C a fracción másica:")
print("1. ppm  -> factor 10^-6")
print("2. ppb  -> factor 10^-9")
print("3. %    -> factor 10^-2")

opcion = input("Ingrese una opción (1, 2 o 3): ").strip()

factores = {
    "1": (1e-6, "ppm"),
    "2": (1e-9, "ppb"),
    "3": (1e-2, "%")
}

if opcion not in factores:
    raise ValueError("Opción no válida. Debe seleccionar 1, 2 o 3.")

factor_masico, unidad_concentracion = factores[opcion]
C = concentracion_experimental * factor_masico

if C <= 0:
    raise ValueError(
        "La concentración convertida a fracción másica debe ser > 0."
    )

print(f"\nUnidad seleccionada              = {unidad_concentracion}")
print(f"Factor de conversión             = {factor_masico:.0e}")
print(f"C = {C:.6e} (fracción másica)")

# ------------------------------------------------------------
# 9. %RSD de Horwitz para reproducibilidad
# ------------------------------------------------------------
#
# PRSDR (%) = 2 C^(-0.15)

PRSDR = 2 * (C ** (-0.15))

# ------------------------------------------------------------
# 10. %RSD de Horwitz para repetibilidad
# ------------------------------------------------------------
#
# Objetivo solicitado:
# PRSD_r = 0.5 × PRSDR

factor_repetibilidad = 0.5
PRSD_repetibilidad = factor_repetibilidad * PRSDR

print("\nRESULTADOS DE HORWITZ")
print("-" * 75)
print(f"%RSD Horwitz - reproducibilidad (PRSDR) = {PRSDR:.4f} %")
print(f"Factor reproducibilidad → repetibilidad = {factor_repetibilidad:.2f}")
print(
    f"%RSD Horwitz - repetibilidad "
    f"(0.5 × PRSDR)                       = {PRSD_repetibilidad:.4f} %"
)

# ------------------------------------------------------------
# 11. HorRat(r)
# ------------------------------------------------------------
#
# HorRat(r) = RSDr / PRSDR
#
# Criterio de referencia para estudios de validación:
# 0.3 ≤ HorRat(r) ≤ 1.3

HorRat_r = RSD_experimental / PRSDR

print("\nHORRAT(r)")
print("-" * 75)
print(f"HorRat(r) = %RSD experimental / PRSDR = {HorRat_r:.4f}")
print("Criterio de referencia: 0.3 ≤ HorRat(r) ≤ 1.3")

if 0.3 <= HorRat_r <= 1.3:
    conclusion_horrat = "PASA"
else:
    conclusion_horrat = "NO PASA"

print(f"Conclusión HorRat(r): {conclusion_horrat}")

# ------------------------------------------------------------
# 12. Comparación directa contra el objetivo de repetibilidad
# ------------------------------------------------------------

if RSD_experimental <= PRSD_repetibilidad:
    conclusion_objetivo = "PASA"
else:
    conclusion_objetivo = "NO PASA"

print("\nCOMPARACIÓN CON EL OBJETIVO DE REPETIBILIDAD")
print("-" * 75)
print(f"%RSD experimental              = {RSD_experimental:.4f} %")
print(f"%RSD Horwitz repetibilidad     = {PRSD_repetibilidad:.4f} %")
print(f"Conclusión frente al objetivo  = {conclusion_objetivo}")

# ------------------------------------------------------------
# 13. CONCLUSIÓN FINAL
# ------------------------------------------------------------

print("\nCONCLUSIÓN")
print("-" * 75)

if conclusion_horrat == "PASA":
    print(
        "El %RSD experimental se encuentra dentro del intervalo de "
        "referencia establecido para HorRat(r) (0.3–1.3)."
    )
else:
    print(
        "El %RSD experimental se encuentra fuera del intervalo de "
        "referencia establecido para HorRat(r) (0.3–1.3)."
    )

if conclusion_objetivo == "PASA":
    print(
        "Además, el %RSD experimental es menor o igual al objetivo "
        "de repetibilidad definido como 0.5 × PRSDR."
    )
else:
    print(
        "Además, el %RSD experimental supera el objetivo de "
        "repetibilidad definido como 0.5 × PRSDR."
    )

# ------------------------------------------------------------
# 14. RESUMEN FINAL EN TABLA
# ------------------------------------------------------------

resumen = pd.DataFrame({
    "Indicador": [
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
print("RESUMEN DE PRECISIÓN")
print("=" * 75)

display(resumen)
