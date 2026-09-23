# ============================================================
# LÍMITE DE DETECCIÓN DEL MÉTODO (LDM) Y
# LÍMITE DE CUANTIFICACIÓN DEL MÉTODO (LCM)
#
# Basado en las fórmulas del PDF de Validación de Métodos:
#
# 1) BLANCO DE MUESTRA
#
# LDM = X_Bks + t_(n-1,α) × S_Bks
#
# LCM = X_Bks + K × S_Bks
#
# donde K = 5, 6 y 10
#
# 2) BLANCO FORTIFICADO
#
# LDM = t_(n-1,α) × S_BF
#
# LCM = K × S_BF
#
# donde K = 5, 6 y 10
#
# α = 0.01 (99 % de una cola)
#
# El script:
# - Utiliza únicamente la primera hoja.
# - Utiliza exclusivamente la columna B como resultados.
# - Pregunta en cada nivel:
#       1. Blanco de muestra
#       2. Blanco fortificado
# - Detecta automáticamente todas las columnas numéricas.
# - Agrupa los valores numéricos del nivel.
# - Calcula media y desviación estándar.
# - Calcula LDM.
# - Calcula LCM con K = 5, 6 y 10.
# - Genera una gráfica por nivel mostrando LDM y los 3 LCM.
# - Genera un resumen general de todos los niveles.
#
# IMPORTANTE:
# La ruta de Windows está configurada según lo indicado.
# ============================================================


import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

archivo = (
    r"D:\Ciencia_de_Datos\Validación de métodos químicos"
    r"\LDM_LCM.xlsx"
)

ALPHA = 0.01  # 99 % de una cola

K_VALUES = [5, 6, 10]


# ============================================================
# 2. FUNCIONES
# ============================================================

def leer_columna_B_hoja1(datos_excel, nombre_hoja):
    """
    Para LDM/LCM se utiliza exclusivamente la primera hoja del archivo.

    La columna A contiene la numeración de los datos.
    Los resultados analíticos están en la columna B.

    Por ello:
    - se ignora la columna A;
    - se toma exclusivamente la columna B;
    - n = número de datos válidos de la columna B;
    - GL = n - 1.
    """

    datos = datos_excel[nombre_hoja].copy()

    if datos.shape[1] < 2:
        raise ValueError(
            "La primera hoja debe tener al menos dos columnas. "
            "La columna A corresponde a la numeración y la columna B "
            "contiene los resultados analíticos."
        )

    # Columna B por posición, independientemente de su nombre.
    valores = pd.to_numeric(
        datos.iloc[:, 1],
        errors="coerce"
    ).dropna().to_numpy(dtype=float)

    if len(valores) < 2:
        raise ValueError(
            "La columna B de la primera hoja debe contener al menos "
            "dos resultados numéricos."
        )

    nombre_columna_B = str(datos.columns[1])

    return datos, nombre_columna_B, valores

def preguntar_tipo_blanco(
    numero_nivel,
    nombre_nivel
):

    print("\n" + "=" * 95)

    print(
        f"NIVEL {numero_nivel} — {nombre_nivel}"
    )

    print(
        "SELECCIÓN DEL PROCEDIMIENTO PARA LDM & LCM"
    )

    print("=" * 95)

    print(
        "\nSeleccione el tipo de blanco que utilizará:"
    )

    print(
        "1. Blanco de muestra"
    )

    print(
        "2. Blanco fortificado"
    )

    while True:

        opcion = input(
            f"\n[NIVEL {numero_nivel}: {nombre_nivel}] "
            "Ingrese una opción (1 o 2): "
        ).strip()

        if opcion in ["1", "2"]:

            return opcion

        print(
            "Opción no válida. Debe seleccionar 1 o 2."
        )


def calcular_resultados(
    valores,
    tipo_blanco
):

    n = len(valores)

    media = float(
        np.mean(valores)
    )

    sd = float(
        np.std(
            valores,
            ddof=1
        )
    )

    gl = n - 1

    # --------------------------------------------------------
    # t crítico
    #
    # La presentación utiliza t_(n-1, α).
    # Se interpreta como valor crítico unilateral:
    #
    # t = t_(1-α, n-1)
    # --------------------------------------------------------

    t_critico = float(
        stats.t.ppf(
            1 - ALPHA,
            gl
        )
    )

    if tipo_blanco == "1":

        nombre_blanco = (
            "Blanco de muestra"
        )

        # LDM = X_Bks + t × S_Bks
        LDM = (
            media
            +
            t_critico * sd
        )

        # LCM = X_Bks + K × S_Bks
        LCM = {
            K: media + K * sd
            for K in K_VALUES
        }

        formula_LDM = (
            "LDM = X_Bks + t × S_Bks"
        )

        formula_LCM = (
            "LCM = X_Bks + K × S_Bks"
        )

    else:

        nombre_blanco = (
            "Blanco fortificado"
        )

        # LDM = t × S_BF
        LDM = (
            t_critico * sd
        )

        # LCM = K × S_BF
        LCM = {
            K: K * sd
            for K in K_VALUES
        }

        formula_LDM = (
            "LDM = t × S_BF"
        )

        formula_LCM = (
            "LCM = K × S_BF"
        )

    return {
        "n": n,
        "media": media,
        "sd": sd,
        "gl": gl,
        "alpha": ALPHA,
        "t_critico": t_critico,
        "tipo_blanco": nombre_blanco,
        "LDM": LDM,
        "LCM": LCM,
        "formula_LDM": formula_LDM,
        "formula_LCM": formula_LCM
    }


def grafica_LDM_LCM(
    nombre_hoja,
    resultado
):
    """
    Gráfica tipo carta de control, con colores y tres cifras
    significativas.

    Se muestran líneas horizontales para:
    - LDM
    - LCM K=5
    - LCM K=6
    - LCM K=10

    Además, se genera una animación GIF en la que los límites
    aparecen progresivamente, como una presentación tipo video.
    """

    from matplotlib.animation import FuncAnimation, PillowWriter

    LDM = resultado["LDM"]
    LCM5 = resultado["LCM"][5]
    LCM6 = resultado["LCM"][6]
    LCM10 = resultado["LCM"][10]

    limites = [
        ("LDM", LDM, "#D62728"),
        ("LCM K=5", LCM5, "#1F77B4"),
        ("LCM K=6", LCM6, "#FF7F0E"),
        ("LCM K=10", LCM10, "#2CA02C")
    ]

    valores_limites = [
        LDM,
        LCM5,
        LCM6,
        LCM10
    ]

    def formato_3_cifras(valor):
        """
        Tres cifras significativas.
        """
        if valor == 0:
            return "0"

        return f"{valor:.3g}"

    ymin = min(valores_limites)
    ymax = max(valores_limites)

    if ymax == ymin:
        margen = max(abs(ymax) * 0.15, 1)
    else:
        margen = (ymax - ymin) * 0.20

    # ========================================================
    # FIGURA ESTÁTICA
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(14, 8)
    )

    ax.set_facecolor("#F7F9FC")

    for nombre, valor, color in limites:

        ax.axhline(
            valor,
            color=color,
            linewidth=3.2,
            linestyle="-",
            label=f"{nombre} = {formato_3_cifras(valor)}"
        )

    ax.set_xlim(0, 10)

    ax.set_xticks(
        np.arange(0, 11, 1)
    )

    ax.set_ylim(
        ymin - margen * 0.25,
        ymax + margen
    )

    ax.set_xlabel(
        "Eje de referencia",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_ylabel(
        "Concentración / respuesta",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_title(
        f"LDM Y LCM — {nombre_hoja}\n"
        "Límites de detección y cuantificación",
        fontsize=18,
        fontweight="bold"
    )

    ax.grid(
        axis="y",
        linestyle="--",
        linewidth=0.8,
        alpha=0.30
    )

    ax.spines[
        "top"
    ].set_visible(False)

    ax.spines[
        "right"
    ].set_visible(False)

    ax.legend(
        loc="upper left",
        frameon=True,
        fontsize=11
    )

    # Etiquetas de valor a la derecha
    for nombre, valor, color in limites:

        ax.annotate(
            formato_3_cifras(valor),
            xy=(10, valor),
            xytext=(10, 0),
            textcoords="offset points",
            color=color,
            fontsize=11,
            fontweight="bold",
            va="center"
        )

    plt.tight_layout()

    plt.show()


    # ========================================================
    # ANIMACIÓN TIPO VIDEO
    # ========================================================

    fig_anim, ax_anim = plt.subplots(
        figsize=(14, 8)
    )

    ax_anim.set_facecolor("#F7F9FC")

    ax_anim.set_xlim(0, 10)

    ax_anim.set_ylim(
        ymin - margen * 0.25,
        ymax + margen
    )

    ax_anim.set_xticks(
        np.arange(0, 11, 1)
    )

    ax_anim.set_xlabel(
        "Eje de referencia",
        fontsize=13,
        fontweight="bold"
    )

    ax_anim.set_ylabel(
        "Concentración / respuesta",
        fontsize=13,
        fontweight="bold"
    )

    ax_anim.set_title(
        f"LDM Y LCM — {nombre_hoja}\n"
        "Evolución de los límites",
        fontsize=18,
        fontweight="bold"
    )

    ax_anim.grid(
        axis="y",
        linestyle="--",
        linewidth=0.8,
        alpha=0.30
    )

    ax_anim.spines[
        "top"
    ].set_visible(False)

    ax_anim.spines[
        "right"
    ].set_visible(False)

    lineas = []
    etiquetas = []

    for nombre, valor, color in limites:

        linea, = ax_anim.plot(
            [],
            [],
            color=color,
            linewidth=3.2
        )

        lineas.append(linea)

        etiqueta = ax_anim.text(
            0,
            valor,
            "",
            color=color,
            fontsize=11,
            fontweight="bold",
            va="center"
        )

        etiquetas.append(etiqueta)

    def init():

        for linea in lineas:

            linea.set_data(
                [],
                []
            )

        for etiqueta in etiquetas:

            etiqueta.set_text("")

        return (
            lineas
            +
            etiquetas
        )

    def animate(frame):

        # Cada límite entra progresivamente.
        limite_actual = min(
            frame // 25,
            len(limites)
        )

        for i, (
            nombre,
            valor,
            color
        ) in enumerate(limites):

            if i < limite_actual:

                # Línea horizontal que se dibuja
                # desde izquierda hacia derecha.
                progreso = min(
                    max(
                        (frame - i * 25) / 20,
                        0
                    ),
                    1
                )

                x_final = 10 * progreso

                lineas[i].set_data(
                    [0, x_final],
                    [valor, valor]
                )

                if progreso >= 1:

                    etiquetas[i].set_position(
                        (10.15, valor)
                    )

                    etiquetas[i].set_text(
                        f"{nombre} = "
                        f"{formato_3_cifras(valor)}"
                    )

            else:

                lineas[i].set_data(
                    [],
                    []
                )

                etiquetas[i].set_text("")

        return (
            lineas
            +
            etiquetas
        )

    anim = FuncAnimation(
        fig_anim,
        animate,
        init_func=init,
        frames=125,
        interval=80,
        blit=True,
        repeat=False
    )

    # Guardar como GIF porque es muy fácil de reproducir
    # en presentaciones y mensajería.
    gif_path = Path(
        f"LDM_LCM_{nombre_hoja}.gif"
    )

    try:

        anim.save(
            gif_path,
            writer=PillowWriter(
                fps=12
            )
        )

        print(
            "\nAnimación creada:"
        )

        print(
            gif_path.resolve()
        )

    except Exception as error:

        print(
            "\nNo se pudo guardar la animación GIF."
        )

        print(
            f"Detalle: {error}"
        )

    plt.show()


# ============================================================
# 3. ENCABEZADO
# ============================================================

print("\n" + "#" * 110)

print(
    "LÍMITE DE DETECCIÓN Y CUANTIFICACIÓN"
)

print(
    "LDM | LCM (K = 5, 6 y 10) — t de Student al 99 % de una cola"
)

print("#" * 110)

print(
    "\nArchivo:"
)

print(
    archivo
)


# ============================================================
# 4. VERIFICAR ARCHIVO
# ============================================================

ruta = Path(
    archivo
)

if not ruta.exists():

    # Ruta alternativa útil si se ejecuta sobre el archivo
    # adjunto dentro del entorno de ChatGPT.

    posibles = [
        Path(
            "/mnt/data/files/LDM_LCM.xlsx"
        ),
        Path(
            "/mnt/data/LDM_LCM.xlsx"
        ),
        Path(
            "/mnt/data/files/LDM_LCM (1).xlsx"
        ),
        Path(
            "/mnt/data/LDM_LCM (1).xlsx"
        )
    ]

    encontrado = None

    for posible in posibles:

        if posible.exists():

            encontrado = posible
            break

    if encontrado is not None:

        archivo = str(
            encontrado
        )

        print(
            "\nNo se encontró la ruta de Windows."
        )

        print(
            "Se utilizará el archivo disponible:"
        )

        print(
            archivo
        )

    else:

        raise FileNotFoundError(
            "\nNo se encontró LDM_LCM.xlsx.\n"
            "Verifique que el archivo esté ubicado en:\n"
            "D:\\Ciencia_de_Datos\\Validación de métodos químicos\\"
            "LDM_LCM.xlsx"
        )


# ============================================================
# 5. LEER TODAS LAS HOJAS
# ============================================================

datos_excel = pd.read_excel(
    archivo,
    sheet_name=None
)

nombres_niveles = list(
    datos_excel.keys()
)

if not nombres_niveles:

    raise ValueError(
        "El archivo no contiene hojas."
    )


print("\n" + "=" * 95)

print(
    "NIVELES DETECTADOS"
)

print("=" * 95)

for numero, nombre in enumerate(
    nombres_niveles,
    start=1
):

    print(
        f"{numero} → {nombre}"
    )


# ============================================================
# 6. UTILIZAR ÚNICAMENTE LA PRIMERA HOJA
# ============================================================
#
# Para LDM/LCM no se consideran niveles.
# El estudio se realiza sobre la primera hoja del archivo.
# ============================================================

datos_excel = pd.read_excel(
    archivo,
    sheet_name=None
)

nombres_hojas = list(
    datos_excel.keys()
)

if not nombres_hojas:
    raise ValueError(
        "El archivo no contiene hojas."
    )

nombre_hoja = nombres_hojas[0]

print("\n" + "=" * 95)
print("HOJA UTILIZADA PARA LDM Y LCM")
print("=" * 95)

print(
    f"Se utilizará únicamente la primera hoja: "
    f"{nombre_hoja}"
)

print(
    "En este parámetro de validación no se consideran niveles."
)


# ============================================================
# 7. LEER DATOS DE LA PRIMERA HOJA
# ============================================================

datos, nombre_columna_B, valores = leer_columna_B_hoja1(
    datos_excel,
    nombre_hoja
)

print("\n" + "-" * 95)

print(
    "DATOS UTILIZADOS PARA LDM Y LCM"
)

print("-" * 95)

print(
    "Estructura utilizada:"
)

print(
    "  • Columna A → numeración de los datos (NO se utiliza)"
)

print(
    f"  • Columna B → resultados analíticos (SE UTILIZA): "
    f"{nombre_columna_B}"
)

print(
    f"\nNúmero total de datos de la columna B = "
    f"{len(valores)}"
)

print(
    f"Grados de libertad = n - 1 = "
    f"{len(valores) - 1}"
)


# ============================================================
# 8. SELECCIONAR TIPO DE BLANCO
# ============================================================

print("\n" + "=" * 95)

print(
    "SELECCIÓN DEL PROCEDIMIENTO PARA LDM Y LCM"
)

print("=" * 95)

print(
    "\nSeleccione el tipo de blanco que utilizará:"
)

print(
    "1. Blanco de muestra"
)

print(
    "2. Blanco fortificado"
)

while True:

    opcion = input(
        "\nIngrese una opción (1 o 2): "
    ).strip()

    if opcion in ["1", "2"]:
        break

    print(
        "Opción no válida. Debe seleccionar 1 o 2."
    )


# ============================================================
# 9. CALCULAR LDM Y LCM
# ============================================================

resultado = calcular_resultados(
    valores,
    opcion
)


# ============================================================
# 10. MOSTRAR ESTADÍSTICOS
# ============================================================

print("\n" + "=" * 95)

print(
    "ESTADÍSTICOS DEL ESTUDIO"
)

print("=" * 95)

print(
    f"Tipo de blanco                = "
    f"{resultado['tipo_blanco']}"
)

print(
    f"n                             = "
    f"{resultado['n']}"
)

print(
    f"Media                         = "
    f"{resultado['media']:.8f}"
)

print(
    f"Desviación estándar (S)       = "
    f"{resultado['sd']:.8f}"
)

print(
    f"Grados de libertad            = "
    f"{resultado['gl']}"
)

print(
    f"α                             = "
    f"{resultado['alpha']}"
)

print(
    f"t crítico t(n-1, α)           = "
    f"{resultado['t_critico']:.8f}"
)


# ============================================================
# 11. LÍMITE DE DETECCIÓN DEL MÉTODO — LDM
# ============================================================

print("\n" + "=" * 95)

print(
    "LÍMITE DE DETECCIÓN DEL MÉTODO — LDM"
)

print("=" * 95)

print(
    f"Fórmula: {resultado['formula_LDM']}"
)

print(
    f"\nLDM = {resultado['LDM']:.8f}"
)


# ============================================================
# 12. LÍMITE DE CUANTIFICACIÓN DEL MÉTODO — LCM
# ============================================================

print("\n" + "=" * 95)

print(
    "LÍMITE DE CUANTIFICACIÓN DEL MÉTODO — LCM"
)

print("=" * 95)

print(
    f"Fórmula: {resultado['formula_LCM']}"
)

print(
    "\nResultados para los tres valores de K:"
)

print(
    f"K = 5   → LCM = "
    f"{resultado['LCM'][5]:.8f}"
)

print(
    f"K = 6   → LCM = "
    f"{resultado['LCM'][6]:.8f}"
)

print(
    f"K = 10  → LCM = "
    f"{resultado['LCM'][10]:.8f}"
)


# ============================================================
# 13. RESUMEN FINAL
# ============================================================

resumen = pd.DataFrame({

    "Parámetro": [

        "Hoja utilizada",

        "Tipo de blanco",

        "n",

        "Media",

        "Desviación estándar",

        "Grados de libertad",

        "α",

        "t crítico",

        "LDM",

        "LCM — K=5",

        "LCM — K=6",

        "LCM — K=10"
    ],

    "Resultado": [

        nombre_hoja,

        resultado["tipo_blanco"],

        resultado["n"],

        f"{resultado['media']:.8f}",

        f"{resultado['sd']:.8f}",

        resultado["gl"],

        resultado["alpha"],

        f"{resultado['t_critico']:.8f}",

        f"{resultado['LDM']:.8f}",

        f"{resultado['LCM'][5]:.8f}",

        f"{resultado['LCM'][6]:.8f}",

        f"{resultado['LCM'][10]:.8f}"
    ]
})


print("\n" + "=" * 95)

print(
    "RESUMEN FINAL — LDM Y LCM"
)

print("=" * 95)

display(
    resumen
)


# ============================================================
# 14. GRÁFICA
# ============================================================

print(
    "\nGenerando gráfica de LDM y LCM..."
)

grafica_LDM_LCM(
    nombre_hoja,
    resultado
)


# ============================================================
# 15. FIN
# ============================================================

print("\n" + "#" * 110)

print(
    "ANÁLISIS DE LDM Y LCM TERMINADO"
)

print("#" * 110)

