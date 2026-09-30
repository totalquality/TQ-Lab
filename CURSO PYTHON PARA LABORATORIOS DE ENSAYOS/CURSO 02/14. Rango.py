import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# ESTUDIO DEL RANGO DEL MÉTODO
# NIVELES Y RÉPLICAS DETECTADOS AUTOMÁTICAMENTE
#
# Excel:
#   Cada hoja = un nivel
#   Los valores numéricos de cada hoja = réplicas
#
# Ejemplo:
#   nivel1 -> 3 réplicas
#   nivel2 -> 3 réplicas
#   nivel3 -> 3 réplicas
#
# El programa detecta automáticamente:
#   - número de niveles = número de hojas
#   - número de réplicas = valores numéricos de cada hoja
# ============================================================

archivo = Path(
    r"D:\Ciencia_de_Datos\Validación de métodos químicos\Rango.xlsx"
)


# ------------------------------------------------------------
# FUNCIONES
# ------------------------------------------------------------
def solicitar_numero(mensaje):
    while True:
        try:
            return float(input(mensaje).replace(",", "."))
        except ValueError:
            print("Ingrese un valor numérico válido.")


def criterio_veracidad(nivel, hoja_actual):
    print("\n" + "=" * 65)
    print(f"{nivel} | Hoja: {hoja_actual} — CRITERIO DE VERACIDAD")
    print("=" * 65)

    minimo = solicitar_numero(f"[{nivel}] Límite MÍNIMO de veracidad: ")
    maximo = solicitar_numero(f"[{nivel}] Límite MÁXIMO de veracidad: ")

    if minimo > maximo:
        print("El mínimo no puede ser mayor que el máximo.")
        return criterio_veracidad(nivel, hoja_actual)

    return minimo, maximo


def criterio_precision(nivel, hoja_actual):
    print("\n" + "=" * 65)
    print(f"{nivel} | Hoja: {hoja_actual} — CRITERIO DE PRECISIÓN")
    print("=" * 65)

    maximo = solicitar_numero(f"[{nivel}] %RSD MÁXIMO aceptable: ")

    if maximo < 0:
        print("El %RSD máximo no puede ser negativo.")
        return criterio_precision(nivel, hoja_actual)

    return maximo


def obtener_replicas(df):
    """
    Busca todos los valores numéricos de la hoja.
    Esto permite que las réplicas estén en una columna
    o en una fila.
    """
    numericos = df.apply(pd.to_numeric, errors="coerce")
    valores = numericos.to_numpy().ravel()
    valores = valores[np.isfinite(valores)]

    if len(valores) == 0:
        raise ValueError("La hoja no contiene datos numéricos.")

    return valores


# ------------------------------------------------------------
# 1. VERIFICAR ARCHIVO
# ------------------------------------------------------------
if not archivo.exists():
    raise FileNotFoundError(
        f"\nNo se encontró el archivo:\n{archivo}\n"
        "Verifique la ruta."
    )


# ------------------------------------------------------------
# 2. DETECTAR NIVELES
# ------------------------------------------------------------
excel = pd.ExcelFile(archivo)
hojas = excel.sheet_names

numero_niveles = len(hojas)

if numero_niveles == 0:
    raise ValueError("El archivo no contiene hojas.")

print("\n" + "=" * 75)
print("ESTUDIO DEL RANGO DEL MÉTODO")
print("=" * 75)
print(f"Archivo: {archivo.name}")
print(f"Niveles detectados: {numero_niveles}")
print("=" * 75)

print("\n" + "╔" + "═" * 68 + "╗")
print("║              CRITERIOS A INGRESAR POR NIVEL                 ║")
print("╠" + "═" * 68 + "╣")
for i, hoja_resumen in enumerate(hojas, start=1):
    print(f"║ Nivel {i} ({hoja_resumen})".ljust(69) + "║")
    print("║   • Veracidad: límite mínimo y límite máximo".ljust(69) + "║")
    print("║   • Precisión: %RSD máximo aceptable".ljust(69) + "║")
print("╚" + "═" * 68 + "╝")


# ------------------------------------------------------------
# 3. LEER AUTOMÁTICAMENTE CADA NIVEL
# ------------------------------------------------------------
resultados = []
datos_grafico = []

for i, hoja in enumerate(hojas, start=1):

    nivel = f"Nivel {i}"

    df = pd.read_excel(
        archivo,
        sheet_name=hoja,
        header=None
    )

    replicas = obtener_replicas(df)
    numero_replicas = len(replicas)

    print("\n" + "#" * 75)
    print(f"              {nivel.upper()}  |  HOJA: {hoja}")
    print("#" * 75)
    print(f"  Vas a ingresar los criterios del {nivel}:")
    print("    1) Veracidad → límite mínimo y límite máximo")
    print("    2) Precisión → %RSD máximo aceptable")
    print(f"  Réplicas detectadas en este nivel: {numero_replicas}")
    print("-" * 75)

    for j, valor in enumerate(replicas, start=1):
        print(f"Réplica {j}: {valor:.6g}")

    # --------------------------------------------------------
    # CRITERIOS DEL NIVEL
    # --------------------------------------------------------
    vmin, vmax = criterio_veracidad(nivel, hoja)
    pmax = criterio_precision(nivel, hoja)

    # --------------------------------------------------------
    # ESTADÍSTICOS
    # --------------------------------------------------------
    media = np.mean(replicas)

    if numero_replicas >= 2:
        sd = np.std(replicas, ddof=1)
        rsd = sd / abs(media) * 100 if media != 0 else np.nan
    else:
        sd = np.nan
        rsd = np.nan

    # --------------------------------------------------------
    # VERACIDAD
    # --------------------------------------------------------
    resultados_veracidad = (
        (replicas >= vmin) &
        (replicas <= vmax)
    )

    veracidad_ok = bool(np.all(resultados_veracidad))

    # --------------------------------------------------------
    # PRECISIÓN
    # --------------------------------------------------------
    precision_ok = bool(
        np.isfinite(rsd) and rsd <= pmax
    )

    nivel_ok = veracidad_ok and precision_ok

    print("\nRESULTADOS")
    print(f"Media = {media:.6f}")
    print(f"SD = {sd:.6f}")
    print(f"%RSD = {rsd:.4f}%")

    print(
        f"Veracidad: {vmin:.6g} ≤ resultado ≤ {vmax:.6g} "
        f"→ {'CUMPLE' if veracidad_ok else 'NO CUMPLE'}"
    )

    print(
        f"Precisión: %RSD ≤ {pmax:.4f}% "
        f"→ {'CUMPLE' if precision_ok else 'NO CUMPLE'}"
    )

    print(
        f"Conclusión {nivel}: "
        f"{'CUMPLE' if nivel_ok else 'NO CUMPLE'}"
    )

    resultados.append({
        "Nivel": nivel,
        "Hoja": hoja,
        "n": numero_replicas,
        "Media": media,
        "SD": sd,
        "%RSD": rsd,
        "Veracidad mín.": vmin,
        "Veracidad máx.": vmax,
        "Veracidad": (
            "CUMPLE" if veracidad_ok else "NO CUMPLE"
        ),
        "%RSD máximo": pmax,
        "Precisión": (
            "CUMPLE" if precision_ok else "NO CUMPLE"
        ),
        "Conclusión": (
            "CUMPLE" if nivel_ok else "NO CUMPLE"
        )
    })

    # Guardar cada réplica para el gráfico
    for valor in replicas:
        datos_grafico.append({
            "Nivel": nivel,
            "Resultado": valor
        })


# ------------------------------------------------------------
# 4. RESUMEN FINAL
# ------------------------------------------------------------
res = pd.DataFrame(resultados)

print("\n" + "=" * 95)
print("RESUMEN FINAL DEL ESTUDIO")
print("=" * 95)
print(res.to_string(index=False))

general_ok = bool(
    (res["Conclusión"] == "CUMPLE").all()
)

print("\n" + "-" * 95)

if general_ok:
    print(
        "CONCLUSIÓN GENERAL: EL RANGO EVALUADO "
        "CUMPLE LOS CRITERIOS ESTABLECIDOS."
    )
else:
    print(
        "CONCLUSIÓN GENERAL: EL RANGO EVALUADO "
        "NO CUMPLE TODOS LOS CRITERIOS ESTABLECIDOS."
    )

print("-" * 95)


# ============================================================
# GRÁFICO RESUMEN — INTERVALO DEL MÉTODO
# ============================================================
# Una única recta con todos los niveles.
# Cada nivel tiene un color distinto.
# Se informa:
#   • valor medio
#   • PASA / NO PASA VERACIDAD
#   • PASA / NO PASA PRECISIÓN
# ============================================================

niveles_medios = res["Media"].to_numpy()

# Paleta visual por nivel
paleta = [
    "#C62828", "#1565C0", "#2E7D32", "#EF6C00",
    "#6A1B9A", "#00838F", "#AD1457", "#4E342E"
]

fig, ax = plt.subplots(figsize=(14, 5.5))

# Fondo muy suave para dar aspecto de infografía
ax.set_facecolor("#FAFAFA")
fig.patch.set_facecolor("white")

# Recta principal del intervalo
ax.hlines(
    1,
    niveles_medios.min(),
    niveles_medios.max(),
    linewidth=8,
    color="#B8860B",
    alpha=0.85,
    zorder=1
)

# Puntos y textos por nivel
for i, valor in enumerate(niveles_medios):

    nivel = res.loc[i, "Nivel"]
    veracidad = res.loc[i, "Veracidad"]
    precision = res.loc[i, "Precisión"]

    color_nivel = paleta[i % len(paleta)]

    veracidad_ok = veracidad == "CUMPLE"
    precision_ok = precision == "CUMPLE"

    texto_veracidad = (
        "✓ PASA VERACIDAD"
        if veracidad_ok
        else "✗ NO PASA VERACIDAD"
    )

    texto_precision = (
        "✓ PASA PRECISIÓN"
        if precision_ok
        else "✗ NO PASA PRECISIÓN"
    )

    # Punto del nivel
    ax.scatter(
        valor,
        1,
        s=260,
        color=color_nivel,
        edgecolor="white",
        linewidth=2.5,
        zorder=4
    )

    # Nombre del nivel
    ax.annotate(
        nivel,
        (valor, 1),
        xytext=(0, 23),
        textcoords="offset points",
        ha="center",
        fontsize=12,
        fontweight="bold",
        color=color_nivel
    )

    # Valor medio
    ax.annotate(
        f"{valor:.4g}",
        (valor, 1),
        xytext=(0, -30),
        textcoords="offset points",
        ha="center",
        fontsize=10,
        fontweight="bold",
        color="#333333"
    )

    # Estado de veracidad
    ax.annotate(
        texto_veracidad,
        (valor, 1),
        xytext=(0, 58),
        textcoords="offset points",
        ha="center",
        fontsize=9.5,
        fontweight="bold",
        color="#2E7D32" if veracidad_ok else "#C62828"
    )

    # Estado de precisión
    ax.annotate(
        texto_precision,
        (valor, 1),
        xytext=(0, 76),
        textcoords="offset points",
        ha="center",
        fontsize=9.5,
        fontweight="bold",
        color="#2E7D32" if precision_ok else "#C62828"
    )

# Cmin y Cmax
ax.text(
    niveles_medios.min(),
    0.82,
    "Cmin",
    ha="center",
    fontsize=11,
    fontweight="bold",
    color="#8D6E00"
)

ax.text(
    niveles_medios.max(),
    0.82,
    "Cmax",
    ha="center",
    fontsize=11,
    fontweight="bold",
    color="#8D6E00"
)

# Intervalo visual superior
distancia = abs(niveles_medios.max() - niveles_medios.min())
if distancia == 0:
    distancia = max(abs(niveles_medios.min()), 1)

ax.set_xlim(
    niveles_medios.min() - 0.12 * distancia,
    niveles_medios.max() + 0.12 * distancia
)
ax.set_ylim(0.68, 1.48)

ax.set_yticks([])
ax.set_xlabel(
    "Concentración / nivel evaluado",
    fontsize=11,
    fontweight="bold"
)

ax.set_title(
    "RESUMEN DEL RANGO DEL MÉTODO",
    fontsize=17,
    fontweight="bold",
    pad=18
)

ax.text(
    0.5,
    1.02,
    "Veracidad y precisión por nivel",
    transform=ax.transAxes,
    ha="center",
    fontsize=11,
    color="#666666"
)

# Línea decorativa inferior
ax.axhline(
    0.74,
    xmin=0.08,
    xmax=0.92,
    linewidth=1,
    color="#DDDDDD"
)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.grid(False)

plt.tight_layout()
plt.show()

print("\\nEstudio finalizado.")

