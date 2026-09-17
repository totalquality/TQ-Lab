from pathlib import Path
from datetime import datetime, time, timedelta
import shutil
import unicodedata
import re

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.worksheet.page import PageMargins


# ============================================================
# GENERADOR AUTOMÁTICO DE INFORMES DE ENSAYO
# ============================================================
#
# FUENTES:
#   DataCom.xlsx
#   DataOpe.xlsx
#   DataLab.xlsx
#
# SALIDA:
#   Excel A4 VERTICAL
#   Control_Informes.xlsx
#
# IMPORTANTE:
#   En esta versión NO se genera PDF.
#   El Excel queda preparado para que puedas acomodarlo
#   manualmente antes de imprimir/guardar como PDF.
# ============================================================


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

CARPETA_BASE = Path(r"D:\Ciencia_de_Datos\IE")

ARCHIVO_COM = CARPETA_BASE / "DataCom.xlsx"
ARCHIVO_OPE = CARPETA_BASE / "DataOpe.xlsx"
ARCHIVO_LAB = CARPETA_BASE / "DataLab.xlsx"

ARCHIVO_CONTROL = CARPETA_BASE / "Control_Informes.xlsx"

CARPETA_SALIDA_DEFAULT = CARPETA_BASE / "Informes"


# ============================================================
# 2. FUNCIONES
# ============================================================

def normalizar_texto(valor):
    if valor is None:
        return ""

    texto = str(valor).replace("\xa0", " ")

    texto = unicodedata.normalize(
        "NFKD", texto
    ).encode(
        "ascii", "ignore"
    ).decode("ascii")

    texto = texto.upper()

    texto = texto.replace("/", " ")
    texto = texto.replace("-", " ")
    texto = texto.replace("_", " ")

    texto = re.sub(r"[^A-Z0-9 ]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def buscar_columna(df, posibles):
    mapa = {}

    for columna in df.columns:
        mapa[normalizar_texto(columna)] = columna

    for nombre in posibles:
        clave = normalizar_texto(nombre)

        if clave in mapa:
            return mapa[clave]

    return None


def buscar_columna_contiene(df, palabras):
    for columna in df.columns:
        nombre = normalizar_texto(columna)

        if all(
            normalizar_texto(palabra) in nombre
            for palabra in palabras
        ):
            return columna

    return None


def texto(valor):
    if pd.isna(valor):
        return ""

    return str(valor).strip()


def fecha_sin_hora(valor):
    if pd.isna(valor):
        return ""

    try:
        fecha = pd.to_datetime(valor)
        return fecha.strftime("%d/%m/%Y")
    except Exception:
        return texto(valor)


def hora_texto(valor):
    """
    Convierte correctamente:
      - datetime.time
      - datetime
      - timedelta
      - valores numéricos de Excel
      - texto HH:MM:SS / HH:MM

    y devuelve siempre HH:MM.
    """

    if pd.isna(valor):
        return ""

    if isinstance(valor, time):
        return valor.strftime("%H:%M")

    if isinstance(valor, datetime):
        return valor.strftime("%H:%M")

    if isinstance(valor, timedelta):
        segundos = int(valor.total_seconds()) % 86400
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        return f"{horas:02d}:{minutos:02d}"

    if isinstance(valor, (int, float)):
        # Excel almacena una hora como fracción del día.
        if 0 <= float(valor) < 1:
            total_minutos = round(float(valor) * 24 * 60)
            horas = (total_minutos // 60) % 24
            minutos = total_minutos % 60
            return f"{horas:02d}:{minutos:02d}"

    texto_valor = texto(valor)

    # Si viene como HH:MM:SS
    coincidencia = re.match(
        r"^(\d{1,2}):(\d{2})(?::\d{2})?$",
        texto_valor
    )

    if coincidencia:
        return (
            f"{int(coincidencia.group(1)):02d}:"
            f"{int(coincidencia.group(2)):02d}"
        )

    return texto_valor


def comprobar_archivo(ruta):
    if not ruta.exists():
        print()
        print("ERROR: No se encontró:")
        print(ruta)
        print()
        return False

    return True


def pedir_fecha_emision():
    while True:
        entrada = input(
            "Ingrese la fecha de emisión (aaaa/mm/dd): "
        ).strip()

        try:
            return datetime.strptime(
                entrada,
                "%Y/%m/%d"
            )

        except ValueError:
            print(
                "Formato incorrecto. Ejemplo: 2026/09/12"
            )


def preguntar_si_no(mensaje):
    while True:
        respuesta = input(
            f"{mensaje} (Si/No): "
        ).strip()

        respuesta = normalizar_texto(respuesta)

        if respuesta in ["SI", "S"]:
            return True

        if respuesta in ["NO", "N"]:
            return False

        print("Responda solamente Si o No.")


def siguiente_numero_informe():
    anio = datetime.now().year
    prefijo = int(str(anio)[-2:]) * 1000

    if not ARCHIVO_CONTROL.exists():
        return prefijo + 1

    try:
        control = pd.read_excel(ARCHIVO_CONTROL)

        if control.empty:
            return prefijo + 1

        if "Nº Informe" not in control.columns:
            return prefijo + 1

        numeros = []

        for valor in control["Nº Informe"].dropna():
            encontrados = re.findall(
                r"\d+",
                str(valor)
            )

            if encontrados:
                try:
                    numeros.append(
                        int(encontrados[-1])
                    )
                except ValueError:
                    pass

        if not numeros:
            return prefijo + 1

        ultimo = max(numeros)

        if str(ultimo).startswith(str(anio)[-2:]):
            return ultimo + 1

        return prefijo + 1

    except Exception as e:
        print(
            f"Advertencia leyendo Control_Informes.xlsx: {e}"
        )
        return prefijo + 1


# ============================================================
# 3. INICIO
# ============================================================

print()
print("=" * 70)
print("       GENERADOR AUTOMÁTICO DE INFORMES DE ENSAYO")
print("=" * 70)
print()
print("VERSIÓN: EXCEL A4 VERTICAL - SIN PDF")
print()
print("Carpeta de trabajo:")
print(CARPETA_BASE)
print()


# ============================================================
# 4. COMPROBAR ARCHIVOS
# ============================================================

for archivo in [
    ARCHIVO_COM,
    ARCHIVO_OPE,
    ARCHIVO_LAB
]:
    if not comprobar_archivo(archivo):
        raise SystemExit


# ============================================================
# 5. ORDEN DE SERVICIO
# ============================================================

orden_servicio = input(
    "Ingrese la Orden de Servicio (ej. OS-2601): "
).strip()

if not orden_servicio:
    print("ERROR: No ingresó una O/S.")
    raise SystemExit

print()
print(f"Buscando información de: {orden_servicio}")
print()


# ============================================================
# 6. DATACOM
# ============================================================

print("1. Cargando DataCom...")

data_com = pd.read_excel(ARCHIVO_COM)

col_os_com = buscar_columna(
    data_com,
    [
        "Orden de Servicio O/S",
        "Orden de Servicio",
        "O/S",
        "OS"
    ]
)

if col_os_com is None:
    print(
        "ERROR: No se encontró la columna "
        "'Orden de Servicio O/S' en DataCom."
    )
    print("Columnas encontradas:")

    for columna in data_com.columns:
        print(f"   [{columna}]")

    raise SystemExit

com = data_com[
    data_com[col_os_com]
    .astype(str)
    .str.strip()
    == orden_servicio
]

if com.empty:
    print(
        f"ERROR: {orden_servicio} no existe en DataCom."
    )
    raise SystemExit

print(
    f"   ✓ O/S identificada como [{col_os_com}]"
)
print("   ✓ O/S encontrada.")


# ============================================================
# 7. DATAOPE
# ============================================================

print()
print("2. Cargando DataOpe...")

data_ope = pd.read_excel(ARCHIVO_OPE)

col_os_ope = buscar_columna(
    data_ope,
    [
        "Orden de Servicio O/S",
        "Orden de Servicio",
        "O/S",
        "OS"
    ]
)

if col_os_ope is None:
    print(
        "ERROR: No se encontró la columna O/S "
        "en DataOpe."
    )
    raise SystemExit

ope = data_ope[
    data_ope[col_os_ope]
    .astype(str)
    .str.strip()
    == orden_servicio
]

if ope.empty:
    print(
        f"ERROR: {orden_servicio} no existe en DataOpe."
    )
    raise SystemExit

print(
    f"   ✓ O/S identificada como [{col_os_ope}]"
)
print("   ✓ O/S encontrada.")


# ============================================================
# 8. DATALAB - HOJA 1
# ============================================================

print()
print("3. Cargando DataLab - Hoja1...")

data_lab = pd.read_excel(
    ARCHIVO_LAB,
    sheet_name="Hoja1"
)

col_os_lab = buscar_columna(
    data_lab,
    [
        "Orden de Servicio O/S",
        "Orden de Servicio",
        "O/S",
        "OS"
    ]
)

if col_os_lab is None:
    print(
        "ERROR: No se encontró la columna O/S "
        "en DataLab."
    )
    raise SystemExit

lab = data_lab[
    data_lab[col_os_lab]
    .astype(str)
    .str.strip()
    == orden_servicio
]

if lab.empty:
    print(
        f"ERROR: {orden_servicio} no existe en DataLab."
    )
    raise SystemExit

print(
    f"   ✓ O/S identificada como [{col_os_lab}]"
)
print("   ✓ O/S encontrada.")


# ============================================================
# 9. DATALAB - HOJA 2 PARA MÉTODOS DE ENSAYO
# ============================================================
#
# Hoja2 contiene TODOS los métodos del laboratorio.
# En el informe NO se copia toda la Hoja2.
#
# Se filtra exclusivamente por los parámetros que aparecen
# en DataLab - Hoja1 para la O/S indicada.
# ============================================================

print()
print("4. Cargando DataLab - Hoja2 para métodos...")

nombres_hojas = pd.ExcelFile(
    ARCHIVO_LAB
).sheet_names

if "Hoja2" not in nombres_hojas:
    print()
    print(
        "ERROR: No existe 'Hoja2' en el DataLab."
    )
    print()
    print("Hojas encontradas:")

    for hoja in nombres_hojas:
        print(f"   [{hoja}]")

    raise SystemExit

data_metodos = pd.read_excel(
    ARCHIVO_LAB,
    sheet_name="Hoja2"
)

print("   ✓ Hoja2 encontrada.")


# ============================================================
# 10. DATALAB - HOJA 3 PARA LCM
# ============================================================


print()
print("4. Buscando LCM en DataLab - Hoja3...")

nombres_hojas = pd.ExcelFile(
    ARCHIVO_LAB
).sheet_names

if "Hoja3" not in nombres_hojas:
    print()
    print(
        "ERROR: No existe 'Hoja3' en el DataLab "
        "que está leyendo este script."
    )
    print()
    print(
        "Hojas encontradas:"
    )

    for hoja in nombres_hojas:
        print(f"   [{hoja}]")

    print()
    print(
        "Para esta versión, la tabla de LCM debe "
        "estar en Hoja3."
    )

    raise SystemExit


data_lcm = pd.read_excel(
    ARCHIVO_LAB,
    sheet_name="Hoja3"
)

print("   ✓ Hoja3 encontrada.")


# ============================================================
# 10. IDENTIFICAR COLUMNAS DATALAB
# ============================================================

col_id_lab = buscar_columna(
    lab,
    [
        "ID Ensayo",
        "ID Muestra",
        "Código de muestra"
    ]
)

col_parametro = buscar_columna(
    lab,
    [
        "Parámetro",
        "Parametro"
    ]
)

col_resultado = buscar_columna(
    lab,
    [
        "Resultado",
        "Resultados"
    ]
)

col_unidad = buscar_columna(
    lab,
    [
        "Unidades",
        "Unidad"
    ]
)


if col_id_lab is None:
    print(
        "ERROR: No se encontró ID Ensayo en DataLab."
    )
    raise SystemExit

if col_parametro is None:
    print(
        "ERROR: No se encontró Parámetro en DataLab."
    )
    raise SystemExit

if col_resultado is None:
    print(
        "ERROR: No se encontró Resultado en DataLab."
    )
    raise SystemExit


# ============================================================
# 11. ID ENSAYO DATAOPE
# ============================================================

col_id_ope = buscar_columna(
    ope,
    [
        "ID Ensayo",
        "ID Muestra",
        "Código de muestra"
    ]
)

if col_id_ope is None:
    print(
        "ERROR: No se encontró ID Ensayo en DataOpe."
    )
    raise SystemExit


# ============================================================
# 12. INCERTIDUMBRE DESDE HOJA 1
# ============================================================
#
# IMPORTANTE:
# La incertidumbre se busca en DataLab - Hoja1,
# como solicitaste.
#
# Se admiten nombres como:
#   Incertidumbre
#   Incertidumbre ±
#   Incertidumbre de medida
#   U
#
# Si no existe una columna de incertidumbre y respondes
# "Si", se mostrará "---" para indicar que no aplica /
# no está disponible en la fuente.
# ============================================================

col_incertidumbre = buscar_columna(
    lab,
    [
        "Incertidumbre",
        "Incertidumbre ±",
        "Incertidumbre de medida",
        "U",
        "U ±"
    ]
)

if col_incertidumbre is None:
    col_incertidumbre = buscar_columna_contiene(
        lab,
        ["INCERTIDUMBRE"]
    )

if col_incertidumbre:
    print(
        f"   ✓ Incertidumbre desde Hoja1: "
        f"[{col_incertidumbre}]"
    )
else:
    print(
        "   ⚠ No se encontró columna de "
        "incertidumbre en Hoja1."
    )


# ============================================================
# 13. LCM DESDE HOJA 3
# ============================================================

col_parametro_lcm = buscar_columna(
    data_lcm,
    [
        "Parámetro",
        "Parametro"
    ]
)

col_lcm = buscar_columna(
    data_lcm,
    [
        "LCM",
        "L.C.M.",
        "Límite de Cuantificación del método",
        "Limite de Cuantificacion del metodo",
        "Límite de Cuantificación",
        "Limite de Cuantificacion"
    ]
)

if col_lcm is None:
    col_lcm = buscar_columna_contiene(
        data_lcm,
        [
            "LIMITE",
            "CUANTIFICACION"
        ]
    )

if col_parametro_lcm is None:
    print(
        "ERROR: Hoja3 no tiene columna Parámetro."
    )
    raise SystemExit

if col_lcm is None:
    print(
        "ERROR: No pude identificar la columna LCM "
        "en Hoja3."
    )

    print("Columnas de Hoja3:")

    for columna in data_lcm.columns:
        print(f"   [{columna}]")

    raise SystemExit

print(
    f"   ✓ Parámetro LCM: [{col_parametro_lcm}]"
)
print(
    f"   ✓ LCM: [{col_lcm}]"
)


# ============================================================
# 14. IDENTIFICAR COLUMNAS DE HOJA 2
# ============================================================

col_parametro_metodo = buscar_columna(
    data_metodos,
    [
        "Parámetro",
        "Parametro"
    ]
)

col_norma_metodo = buscar_columna(
    data_metodos,
    [
        "Norma Referencia",
        "Norma de Referencia",
        "Norma"
    ]
)

col_titulo_metodo = buscar_columna(
    data_metodos,
    [
        "Título",
        "Titulo"
    ]
)

if col_parametro_metodo is None:
    print(
        "ERROR: Hoja2 no tiene columna Parámetro."
    )
    raise SystemExit

if col_norma_metodo is None:
    print(
        "ERROR: Hoja2 no tiene columna Norma Referencia."
    )
    raise SystemExit

if col_titulo_metodo is None:
    print(
        "ERROR: Hoja2 no tiene columna Título."
    )
    raise SystemExit

print(
    f"   ✓ Parámetro método: [{col_parametro_metodo}]"
)
print(
    f"   ✓ Norma referencia: [{col_norma_metodo}]"
)
print(
    f"   ✓ Título: [{col_titulo_metodo}]"
)


# ============================================================
# 15. FECHA DE EMISIÓN E INCERTIDUMBRE
# ============================================================

print()
print("=" * 70)
print("DATOS A DEFINIR ANTES DE GENERAR")
print("=" * 70)
print()

fecha_emision = pedir_fecha_emision()

print()

reportar_incertidumbre = preguntar_si_no(
    "¿Se reportará incertidumbre?"
)

print()


# ============================================================
# 15. MUESTRAS
# ============================================================

muestras = (
    ope[col_id_ope]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

if len(muestras) == 0:
    print(
        "ERROR: No se encontraron muestras."
    )
    raise SystemExit

print("Muestras encontradas:")

for muestra in muestras:
    print(f"   ✓ {muestra}")


# ============================================================
# 16. CORRELATIVO
# ============================================================

numero = siguiente_numero_informe()

codigo_informe = f"IE {numero}"

print()
print(
    f"Correlativo asignado: {codigo_informe}"
)


# ============================================================
# 17. RUTA DE SALIDA
# ============================================================

print()
print(
    "Indique la carpeta donde desea guardar "
    "el informe."
)
print(
    "Puede ser una carpeta local, otro disco "
    "o una carpeta sincronizada."
)
print()

ruta_salida = input(
    "Ruta de salida "
    "[Enter = D:\\Ciencia_de_Datos\\IE\\Informes]: "
).strip()

if ruta_salida:
    carpeta_salida = Path(ruta_salida)
else:
    carpeta_salida = CARPETA_SALIDA_DEFAULT

carpeta_salida.mkdir(
    parents=True,
    exist_ok=True
)


archivo_excel = (
    carpeta_salida /
    f"{codigo_informe}.xlsx"
)


# ============================================================
# 18. CREAR LIBRO
# ============================================================

print()
print("Generando Excel A4 vertical...")

wb = Workbook()

ws = wb.active

ws.title = "Informe de Ensayo"


# ============================================================
# 19. ESTILOS
# ============================================================

arial9 = Font(
    name="Arial",
    size=9
)

arial10 = Font(
    name="Arial",
    size=10
)

arial10_negrita = Font(
    name="Arial",
    size=10,
    bold=True
)

arial12 = Font(
    name="Arial",
    size=12,
    bold=True
)

arial16 = Font(
    name="Arial",
    size=16,
    bold=True
)


centrado = Alignment(
    horizontal="center",
    vertical="center",
    wrap_text=True
)

izquierda = Alignment(
    horizontal="left",
    vertical="center",
    wrap_text=True
)

arriba = Alignment(
    horizontal="left",
    vertical="top",
    wrap_text=True
)


borde = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin")
)


# ============================================================
# 20. A4 VERTICAL
# ============================================================

ws.page_setup.paperSize = ws.PAPERSIZE_A4

ws.page_setup.orientation = "portrait"

ws.page_setup.fitToWidth = 1

ws.page_setup.fitToHeight = 0

ws.sheet_properties.pageSetUpPr.fitToPage = True

ws.page_margins = PageMargins(
    left=0.25,
    right=0.25,
    top=0.45,
    bottom=0.70,
    header=0.20,
    footer=0.40
)

ws.print_options.horizontalCentered = True


# ============================================================
# 21. TÍTULO
# ============================================================

ws.merge_cells("A1:F1")

ws["A1"] = "INFORME DE ENSAYO"

ws["A1"].font = arial16

ws["A1"].alignment = centrado

ws.row_dimensions[1].height = 27


ws.merge_cells("A2:F2")

ws["A2"] = codigo_informe

ws["A2"].font = Font(
    name="Arial",
    size=14,
    bold=True
)

ws["A2"].alignment = centrado

ws.row_dimensions[2].height = 23

# DOS FILAS EN BLANCO ENTRE EL TÍTULO Y LOS DATOS DEL CLIENTE.
# Las filas 3 y 4 quedan libres para dar una separación visual prudente.
ws.row_dimensions[3].height = 18
ws.row_dimensions[4].height = 18


# ============================================================
# 22. DATOS DEL CLIENTE
# ============================================================

ws.merge_cells("A5:F5")

ws["A4"] = "DATOS DEL CLIENTE"

ws["A4"].font = arial12

ws["A4"].alignment = izquierda


fila_com = com.iloc[0]


def obtener_com(nombre):
    columna = buscar_columna(
        com,
        [nombre]
    )

    if columna is None:
        return ""

    return texto(
        fila_com[columna]
    )


datos_cliente = [
    (
        "Nombre del cliente",
        obtener_com("Nombre del cliente")
    ),
    (
        "Dirección del cliente",
        obtener_com("Dirección del cliente")
    ),
    (
        "Solicitado por",
        obtener_com("Solicitado por")
    ),
    (
        "Proyecto",
        obtener_com("Nombre del proyecto")
    ),
    (
        "Muestreo realizado por",
        obtener_com("Muestreo realizado por")
    ),
    (
        "Procedencia de la muestra",
        obtener_com("Procedencia de la muestra")
    )
]


fila = 6

for etiqueta, valor in datos_cliente:

    ws[f"A{fila}"] = etiqueta
    ws[f"A{fila}"].font = arial10_negrita
    ws[f"A{fila}"].alignment = arriba

    ws.merge_cells(
        start_row=fila,
        start_column=2,
        end_row=fila,
        end_column=5
    )

    ws[f"B{fila}"] = valor
    ws[f"B{fila}"].font = arial10
    ws[f"B{fila}"].alignment = arriba

    fila += 1


# ============================================================
# 23. DATOS DE LABORATORIO
# ============================================================

fila += 1

ws.merge_cells(
    start_row=fila,
    start_column=1,
    end_row=fila,
    end_column=6
)

ws[f"A{fila}"] = "DATOS DE LABORATORIO"

ws[f"A{fila}"].font = arial12

ws[f"A{fila}"].alignment = izquierda

fila += 1


fila_ope = ope.iloc[0]


def obtener_ope(nombre):
    columna = buscar_columna(
        ope,
        [nombre]
    )

    if columna is None:
        return ""

    return texto(
        fila_ope[columna]
    )


datos_laboratorio = [
    (
        "Plan de muestreo",
        obtener_ope("Plan de Muestreo PM")
    ),
    (
        "Cantidad de muestras y presentación",
        obtener_ope(
            "Cantidad de muestras y presentación"
        )
    ),
    (
        "Producto",
        obtener_ope("Producto")
    )
]


for etiqueta, valor in datos_laboratorio:

    ws[f"A{fila}"] = etiqueta
    ws[f"A{fila}"].font = arial10_negrita
    ws[f"A{fila}"].alignment = arriba

    ws.merge_cells(
        start_row=fila,
        start_column=2,
        end_row=fila,
        end_column=5
    )

    ws[f"B{fila}"] = valor
    ws[f"B{fila}"].font = arial10
    ws[f"B{fila}"].alignment = arriba

    fila += 1


# ============================================================
# 24. FECHAS
# ============================================================

col_fecha_recepcion = buscar_columna(
    lab,
    [
        "Fecha de recepción de muestras"
    ]
)

col_fecha_inicio = buscar_columna(
    lab,
    [
        "Fecha de inicio del análisis"
    ]
)


fecha_recepcion = ""

fecha_inicio = ""


if col_fecha_recepcion:
    fecha_recepcion = fecha_sin_hora(
        lab.iloc[0][col_fecha_recepcion]
    )


if col_fecha_inicio:
    fecha_inicio = fecha_sin_hora(
        lab.iloc[0][col_fecha_inicio]
    )


datos_fechas = [
    (
        "Fecha de recepción",
        fecha_recepcion
    ),
    (
        "Fecha de inicio del análisis",
        fecha_inicio
    ),
    (
        "Fecha de emisión",
        fecha_emision.strftime("%d/%m/%Y")
    )
]


for etiqueta, valor in datos_fechas:

    ws[f"A{fila}"] = etiqueta
    ws[f"A{fila}"].font = arial10_negrita
    ws[f"A{fila}"].alignment = arriba

    ws.merge_cells(
        start_row=fila,
        start_column=2,
        end_row=fila,
        end_column=5
    )

    ws[f"B{fila}"] = valor
    ws[f"B{fila}"].font = arial10
    ws[f"B{fila}"].alignment = arriba

    fila += 1


# ============================================================
# 25. IDENTIFICACIÓN DE MUESTRAS - VERTICAL
# ============================================================
#
# Ya NO se ponen E001, E002, etc. en columnas horizontales.
#
# Cada muestra tendrá su propio bloque vertical.
#
# Esto permite mantener el documento A4 VERTICAL.
# ============================================================

fila += 1

ws.merge_cells(
    start_row=fila,
    start_column=1,
    end_row=fila,
    end_column=6
)

ws[f"A{fila}"] = (
    "IDENTIFICACIÓN DE MUESTRAS"
)

ws[f"A{fila}"].font = arial12

ws[f"A{fila}"].alignment = izquierda

fila += 1


# Detectar las dos columnas de hora.
columnas_hora = []

for columna in ope.columns:

    nombre = normalizar_texto(
        columna
    )

    if nombre.startswith(
        "HORA DE MUESTREO"
    ):
        columnas_hora.append(columna)


col_hora_inicial = (
    columnas_hora[0]
    if len(columnas_hora) >= 1
    else None
)

col_hora_final = (
    columnas_hora[1]
    if len(columnas_hora) >= 2
    else None
)


col_fecha_inicial = buscar_columna(
    ope,
    [
        "Fecha inicial del muestreo"
    ]
)

col_fecha_final = buscar_columna(
    ope,
    [
        "Fecha final de muestreo"
    ]
)


for indice_muestra, muestra in enumerate(
    muestras,
    start=1
):

    datos_muestra = ope[
        ope[col_id_ope]
        .astype(str)
        .str.strip()
        == muestra
    ]


    if datos_muestra.empty:
        continue


    registro = datos_muestra.iloc[0]


    def dato_muestra(nombre):
        columna = buscar_columna(
            datos_muestra,
            [nombre]
        )

        if columna is None:
            return ""

        return registro[columna]


    col_codigo_cliente = buscar_columna(
        datos_muestra,
        ["Código de cliente"]
    )

    col_producto = buscar_columna(
        datos_muestra,
        ["Producto"]
    )

    col_ubicacion = buscar_columna(
        datos_muestra,
        ["Ubicación geográfica"]
    )

    col_estacion = buscar_columna(
        datos_muestra,
        [
            "Descripción de la Estación de Muestreo"
        ]
    )


    # --------------------------------------------------------
    # Encabezado de muestra
    # --------------------------------------------------------

    ws.merge_cells(
        start_row=fila,
        start_column=1,
        end_row=fila,
        end_column=5
    )

    ws[f"A{fila}"] = (
        f"MUESTRA {muestra}"
    )

    ws[f"A{fila}"].font = arial10_negrita

    ws[f"A{fila}"].alignment = izquierda

    fila += 1


    # --------------------------------------------------------
    # Función para escribir una fila vertical
    # --------------------------------------------------------

    def escribir_campo_muestra(
        etiqueta,
        valor
    ):

        nonlocal_fila = None

        return


    campos_muestra = [

        (
            "ID Ensayo",
            muestra
        ),

        (
            "Código de cliente",
            texto(
                registro[col_codigo_cliente]
            )
            if col_codigo_cliente
            else ""
        ),

        (
            "Producto",
            texto(
                registro[col_producto]
            )
            if col_producto
            else ""
        ),

        (
            "Fecha inicial del muestreo",
            fecha_sin_hora(
                registro[col_fecha_inicial]
            )
            if col_fecha_inicial
            else ""
        ),

        (
            "Hora de muestreo",
            hora_texto(
                registro[col_hora_inicial]
            )
            if col_hora_inicial
            else ""
        ),

        (
            "Fecha final de muestreo",
            fecha_sin_hora(
                registro[col_fecha_final]
            )
            if col_fecha_final
            else ""
        ),

        (
            "Hora de muestreo",
            hora_texto(
                registro[col_hora_final]
            )
            if col_hora_final
            else ""
        ),

        (
            "Ubicación geográfica",
            texto(
                registro[col_ubicacion]
            )
            if col_ubicacion
            else ""
        ),

        (
            "Descripción de la Estación de Muestreo",
            texto(
                registro[col_estacion]
            )
            if col_estacion
            else ""
        )

    ]


    for etiqueta, valor in campos_muestra:

        ws[f"A{fila}"] = etiqueta

        ws[f"A{fila}"].font = arial10_negrita

        ws[f"A{fila}"].alignment = arriba

        ws[f"A{fila}"].border = borde


        ws.merge_cells(
            start_row=fila,
            start_column=2,
            end_row=fila,
            end_column=6
        )

        ws[f"B{fila}"] = valor

        ws[f"B{fila}"].font = arial10

        ws[f"B{fila}"].alignment = arriba

        ws[f"B{fila}"].border = borde

        fila += 1


    if indice_muestra < len(muestras):

        fila += 1


# Parámetros solicitados por la O/S: son los parámetros presentes
# en DataLab-Hoja1 para la O/S indicada.
parametros = (
    lab[col_parametro]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

# ============================================================
# 26. RESULTADOS DE ENSAYO
# ============================================================

fila += 1


ws.merge_cells(
    start_row=fila,
    start_column=1,
    end_row=fila,
    end_column=5
)

ws[f"A{fila}"] = (
    "RESULTADOS DE ENSAYO"
)

ws[f"A{fila}"].font = arial12

ws[f"A{fila}"].alignment = izquierda

fila += 1


# La tabla de resultados queda vertical en las filas.
#
# Columnas:
# A = Parámetro
# B = LCM
# C = Unidad
# D = E001
# E = E002
# ...
#
# Esto permite mantener A4 vertical.


encabezados_resultados = [

    "Parámetro",

    "Límite de Cuantificación\ndel método (LCM)",

    "Unidad"

]


for muestra in muestras:

    encabezados_resultados.append(
        muestra
    )


for columna, encabezado in enumerate(
    encabezados_resultados,
    start=1
):

    celda = ws.cell(
        row=fila,
        column=columna
    )

    celda.value = encabezado

    celda.font = arial10_negrita

    celda.alignment = centrado

    celda.border = borde


fila += 1


# ============================================================
# 27. TABLA LCM
# ============================================================

tabla_metodos = {}


for _, registro_metodo in (
    data_lcm.iterrows()
):

    parametro_metodo = texto(
        registro_metodo[
            col_parametro_lcm
        ]
    )

    if not parametro_metodo:
        continue

    clave = normalizar_texto(
        parametro_metodo
    )

    tabla_metodos[clave] = texto(
        registro_metodo[col_lcm]
    )


# ============================================================
# 28. RESULTADOS Y LCM
# ============================================================

parametros = (
    lab[col_parametro]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)


for parametro in parametros:

    clave_parametro = normalizar_texto(
        parametro
    )

    lcm = tabla_metodos.get(
        clave_parametro,
        "---"
    )


    datos_parametro = lab[
        lab[col_parametro]
        .astype(str)
        .str.strip()
        == parametro
    ]


    # --------------------------------------------------------
    # Unidad del parámetro
    # --------------------------------------------------------

    unidad = ""

    if col_unidad:

        unidades = (
            datos_parametro[
                col_unidad
            ]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        if len(unidades) > 0:
            unidad = unidades[0]


    # --------------------------------------------------------
    # Resultados E001, E002...
    # --------------------------------------------------------

    valores = [
        parametro,
        lcm,
        unidad
    ]


    for muestra in muestras:

        resultado_muestra = (
            datos_parametro[
                datos_parametro[
                    col_id_lab
                ]
                .astype(str)
                .str.strip()
                == muestra
            ]
        )


        if resultado_muestra.empty:

            valores.append("")

        else:

            resultado = (
                resultado_muestra.iloc[0][
                    col_resultado
                ]
            )

            # Se conserva < 2.0, < 0.5, etc.
            valores.append(
                texto(resultado)
            )


    for columna, valor in enumerate(
        valores,
        start=1
    ):

        celda = ws.cell(
            row=fila,
            column=columna
        )

        celda.value = valor

        celda.font = arial10

        celda.alignment = centrado

        celda.border = borde


    fila += 1


    # ========================================================
    # 29. INCERTIDUMBRE
    # ========================================================
    #
    # Se coloca inmediatamente debajo de cada parámetro.
    #
    # A = Incertidumbre ±
    # B = ---
    # C = misma unidad del parámetro
    # D/E/... = valor de incertidumbre o ---
    #
    # La fuente es DataLab - Hoja1.
    # ========================================================

    if reportar_incertidumbre:

        valores_incertidumbre = [

            "Incertidumbre ±",

            "---",

            unidad

        ]


        for muestra in muestras:

            resultado_muestra = (
                datos_parametro[
                    datos_parametro[
                        col_id_lab
                    ]
                    .astype(str)
                    .str.strip()
                    == muestra
                ]
            )


            valor_incertidumbre = ""


            if (
                not resultado_muestra.empty
                and col_incertidumbre
            ):

                valor_incertidumbre = texto(
                    resultado_muestra.iloc[0][
                        col_incertidumbre
                    ]
                )


            if not valor_incertidumbre:
                valor_incertidumbre = "---"


            valores_incertidumbre.append(
                valor_incertidumbre
            )


        for columna, valor in enumerate(
            valores_incertidumbre,
            start=1
        ):

            celda = ws.cell(
                row=fila,
                column=columna
            )

            celda.value = valor

            celda.font = arial10

            celda.alignment = centrado

            celda.border = borde
    

        fila += 1


# ============================================================


# 30. MÉTODOS DE ENSAYO
# ============================================================
#
# Se muestra únicamente el método asociado a los parámetros
# solicitados en la O/S indicada.
#
# NO se copia toda la Hoja2.
# La Hoja2 funciona como catálogo maestro de métodos y se
# filtra utilizando los parámetros presentes en DataLab-Hoja1
# para esta O/S.
# ============================================================

fila += 1

ws.merge_cells(
    start_row=fila,
    start_column=1,
    end_row=fila,
    end_column=5
)

ws[f"A{fila}"] = "MÉTODOS DE ENSAYO"

ws[f"A{fila}"].font = arial12

ws[f"A{fila}"].alignment = izquierda

fila += 1


encabezados_metodos = [
    "Parámetro",
    "Norma de referencia",
    "Título"
]


# Encabezados: A = Parámetro, B = Norma de referencia,
# C:E = Título, unido para que el texto se lea horizontalmente.
ws["A" + str(fila)] = encabezados_metodos[0]
ws["B" + str(fila)] = encabezados_metodos[1]
ws["A" + str(fila)].font = arial10_negrita
ws["B" + str(fila)].font = arial10_negrita
ws["A" + str(fila)].alignment = centrado
ws["B" + str(fila)].alignment = centrado
ws["A" + str(fila)].border = borde
ws["B" + str(fila)].border = borde

ws.merge_cells(
    start_row=fila,
    start_column=3,
    end_row=fila,
    end_column=5
)
ws["C" + str(fila)] = encabezados_metodos[2]
ws["C" + str(fila)].font = arial10_negrita
ws["C" + str(fila)].alignment = centrado
for cc in range(3, 6):
    ws.cell(row=fila, column=cc).border = borde

fila += 1


# Crear catálogo normalizado de Hoja2.
# Si hubiera más de una fila para un parámetro, se conserva
# cada método registrado para ese parámetro.

metodos_os = data_metodos.copy()

metodos_os["_CLAVE_PARAMETRO"] = (
    metodos_os[col_parametro_metodo]
    .astype(str)
    .map(normalizar_texto)
)


parametros_normalizados = [
    normalizar_texto(parametro)
    for parametro in parametros
]


metodos_os = metodos_os[
    metodos_os["_CLAVE_PARAMETRO"].isin(
        parametros_normalizados
    )
]


# Mantener el orden de los parámetros de la O/S.
for parametro in parametros:

    clave = normalizar_texto(parametro)

    coincidencias = metodos_os[
        metodos_os["_CLAVE_PARAMETRO"] == clave
    ]


    for _, metodo in coincidencias.iterrows():

        valores_metodo = [
            texto(metodo[col_parametro_metodo]),
            texto(metodo[col_norma_metodo]),
            texto(metodo[col_titulo_metodo])
        ]


        # A = Parámetro, B = Norma de referencia, C:E = Título.
        ws["A" + str(fila)] = valores_metodo[0]
        ws["B" + str(fila)] = valores_metodo[1]

        ws["A" + str(fila)].font = arial9
        ws["B" + str(fila)].font = arial9
        ws["A" + str(fila)].alignment = arriba
        ws["B" + str(fila)].alignment = arriba
        ws["A" + str(fila)].border = borde
        ws["B" + str(fila)].border = borde

        ws.merge_cells(
            start_row=fila,
            start_column=3,
            end_row=fila,
            end_column=5
        )
        ws["C" + str(fila)] = valores_metodo[2]
        ws["C" + str(fila)].font = arial9
        ws["C" + str(fila)].alignment = arriba
        for cc in range(3, 6):
            ws.cell(row=fila, column=cc).border = borde

        ws.row_dimensions[fila].height = 34

        fila += 1


# Si algún parámetro de la O/S no tiene método en Hoja2,
# se deja una advertencia visible para revisión.
parametros_con_metodo = set(
    metodos_os["_CLAVE_PARAMETRO"].dropna()
)

parametros_sin_metodo = [
    parametro
    for parametro in parametros
    if normalizar_texto(parametro)
    not in parametros_con_metodo
]


if parametros_sin_metodo:

    ws.merge_cells(
        start_row=fila,
        start_column=1,
        end_row=fila,
        end_column=3
    )

    ws[f"A{fila}"] = (
        "REVISAR: no se encontró método en Hoja2 para: "
        + ", ".join(parametros_sin_metodo)
    )

    ws[f"A{fila}"].font = Font(
        name="Arial",
        size=9,
        bold=True
    )

    ws[f"A{fila}"].alignment = arriba

    fila += 1


# ============================================================



# 31. OBSERVACIONES
# ============================================================

fila += 1


ultima_columna_resultados = (
    3 + len(muestras)
)


ws.merge_cells(
    start_row=fila,
    start_column=1,
    end_row=fila,
    end_column=ultima_columna_resultados
)

ws[f"A{fila}"] = "OBSERVACIONES"

ws[f"A{fila}"].font = arial12

ws[f"A{fila}"].alignment = izquierda

fila += 1


observaciones = (

    "• El lugar en que se realizan las actividades de "
    "laboratorio fue realizada en el Laboratorio.\n\n"

    "• Cuando se reporte la incertidumbre del resultado "
    "asociado, este se reporta utilizando un factor de "
    "cobertura de k=1.96 al 95% de confianza.\n\n"

    "• Este documento al ser emitido sin el símbolo de "
    "acreditación, no se encuentra dentro del marco de la "
    "acreditación otorgada por el INACAL-DA.\n\n"

    "• La(s) muestra(s) recepcionadas se encuentran "
    "cumpliendo lo establecido en la tabla del P-OPE-03 "
    "Métodos, preservantes y tiempo de vida."

)


# El bloque de observaciones termina exactamente en la fila 70.
fila_observaciones_inicio = fila
fila_observaciones_fin = max(fila_observaciones_inicio, 70)

ws.merge_cells(
    start_row=fila_observaciones_inicio,
    start_column=1,
    end_row=fila_observaciones_fin,
    end_column=ultima_columna_resultados
)

ws[f"A{fila}"] = observaciones

ws[f"A{fila}"].font = arial9

ws[f"A{fila}"].alignment = arriba


# ============================================================
# 31. ESPACIO EN BLANCO PARA FIRMAS
# ============================================================
#
# NO SE INSERTAN CASILLAS.
# NO SE INSERTAN TEXTOS DE FIRMA.
# Solo se deja espacio libre.
# Se reservan 13 filas en blanco para firmas y revisión manuscrita.
# ============================================================

fila += 13


# ============================================================
# 32. FIN DEL DOCUMENTO
# ============================================================

ws.merge_cells(
    start_row=fila,
    start_column=1,
    end_row=fila,
    end_column=ultima_columna_resultados
)

ws[f"A{fila}"] = (
    "──────────────── FIN DEL DOCUMENTO ────────────────"
)

ws[f"A{fila}"].font = Font(
    name="Arial",
    size=10,
    bold=True
)

ws[f"A{fila}"].alignment = centrado


# ============================================================
# ============================================================
# 33. PIE DE PÁGINA
# ============================================================
#
# IMPORTANTE:
# Excel tiene un límite REAL de 255 caracteres para cada
# encabezado o pie de página.
#
# El texto legal solicitado supera ese límite. Por eso:
#
#   1) El pie de página REAL de Excel llevará una leyenda
#      centrada en Arial 6, compatible con Excel.
#
#   2) El texto legal COMPLETO se coloca además en el
#      bloque inferior del documento, centrado y en Arial 6,
#      para conservar íntegramente el texto solicitado.
#
# Así no se pierde contenido ni se provoca una reparación
# del archivo por exceder el límite del pie de página.
# ============================================================

pie_completo = (
    "Resultados válidos únicamente para las muestras/ítems "
    "identificados y ensayados; no aplicables a otras unidades "
    "o lotes. Cuando el laboratorio no realiza el muestreo, "
    "los resultados corresponden a la muestra tal como fue "
    "recibida y la información proporcionada por el cliente "
    "es responsabilidad de este. Los resultados no constituyen "
    "certificación de conformidad de producto ni certificación "
    "del sistema de gestión de calidad. Modificaciones o "
    "adiciones de muestras/servicios se gestionan conforme al "
    "P-COM-01. No se permite la reproducción parcial sin "
    "autorización escrita. La adulteración, falsificación o "
    "uso indebido del presente informe podrá generar las "
    "responsabilidades que correspondan conforme a la "
    "legislación vigente."
)

# Pie real de Excel, centrado, Arial 6.
pie_excel = (
    "Resultados válidos únicamente para las muestras/ítems "
    "identificados y ensayados; no aplicables a otras unidades "
    "o lotes. Cuando el laboratorio no realiza el muestreo, "
    "los resultados corresponden a la muestra tal como fue "
    "recibida..."
)

ws.oddFooter.center.text = pie_excel
ws.oddFooter.center.font = "Arial"
ws.oddFooter.center.size = 6

# Texto legal completo en el pie visual del documento.
# Se conserva íntegramente en la hoja y se centra.
fila += 2

ws.merge_cells(
    start_row=fila,
    start_column=1,
    end_row=fila + 2,
    end_column=ultima_columna_resultados
)

ws[f"A{fila}"] = pie_completo
ws[f"A{fila}"].font = Font(name="Arial", size=6)
ws[f"A{fila}"].alignment = Alignment(
    horizontal="center",
    vertical="center",
    wrap_text=True
)

for rr in range(fila, fila + 3):
    ws.row_dimensions[rr].height = 18


# 34. ANCHOS
# ============================================================

anchos = {

    "A": 32,

    "B": 24,

    "C": 13,

    "D": 17,

    "E": 17,

    # F es deliberadamente más estrecha (aprox. la mitad de E).
    # Esto permite ampliar el área del informe sin que se vea excesivamente ancho.
    "F": 8.5,

    "G": 17,

    "H": 17,

    "I": 17

}


for columna, ancho in anchos.items():

    ws.column_dimensions[
        columna
    ].width = ancho


# ============================================================
# 35. ALTURAS
# ============================================================

for numero_fila in range(
    1,
    ws.max_row + 1
):

    if (
        ws.row_dimensions[
            numero_fila
        ].height
        is None
    ):

        ws.row_dimensions[
            numero_fila
        ].height = 18


# ============================================================
# 36. ALTURA OBSERVACIONES
# ============================================================

# Se busca la fila que contiene OBSERVACIONES y se le da
# suficiente espacio visual.

for r in range(
    1,
    ws.max_row + 1
):

    if ws[f"A{r}"].value == "OBSERVACIONES":

        for rr in range(
            r + 1,
            min(71, ws.max_row + 1)
        ):
            ws.row_dimensions[rr].height = 24

        break


# ============================================================
# 37. CONFIGURACIÓN FINAL A4 VERTICAL, PÁGINAS Y MEMBRETE
# ============================================================
#
# El informe está preparado para impresión en HOJAS A4
# MEMBRETADAS.
#
# 1) A4 real, vertical.
# 2) Una sola página de ancho (A:F).
# 3) La altura NO se comprime.
# 4) Si el informe ocupa 3 páginas, Excel imprimirá:
#       Página 1 -> encabezado
#       Página 2 -> encabezado
#       Página 3 -> encabezado
# 5) Las filas 1 y 2 son el encabezado visible del informe y
#    se repiten automáticamente en cada página impresa.
# 6) La numeración es 1/3, 2/3, 3/3, etc.
# 7) Se deja un margen inferior prudente para no invadir la
#    zona inferior de la hoja membretada.
# ============================================================

ws.page_setup.paperSize = ws.PAPERSIZE_A4
ws.page_setup.orientation = "portrait"

# Una sola página de ancho (A:F).
ws.page_setup.fitToWidth = 1

# Varias páginas de alto según sea necesario.
# NO reducir todo el informe a una sola página.
ws.page_setup.fitToHeight = 0

ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.sheet_properties.pageSetUpPr.autoPageBreaks = True

# El informe ocupa A:F.
ws.print_area = f"A1:F{ws.max_row}"

# ------------------------------------------------------------
# ENCABEZADO REPETIDO EN TODAS LAS PÁGINAS
# ------------------------------------------------------------
# Excel repetirá físicamente las filas 1 y 2 en cada página.
# No es solamente un encabezado de pantalla: forma parte del
# área de impresión repetida.
ws.print_title_rows = "$1:$2"

# ------------------------------------------------------------
# MÁRGENES PARA HOJA MEMBRETADA
# ------------------------------------------------------------
# Se aumenta el margen inferior para dejar una zona prudente
# libre en la parte baja de cada A4.
ws.page_margins = PageMargins(
    left=0.25,
    right=0.25,
    top=0.45,
    bottom=1.15,
    header=0.20,
    footer=0.50
)

ws.print_options.horizontalCentered = True

# ------------------------------------------------------------
# PAGINACIÓN
# ------------------------------------------------------------
# &P = página actual
# &N = total de páginas
#
# La numeración se coloca a la derecha para no interferir con
# el espacio central destinado al pie de página/membrete.
ws.oddFooter.right.text = "&P/&N"
ws.oddFooter.right.font = "Arial"
ws.oddFooter.right.size = 6

ws.evenFooter.right.text = "&P/&N"
ws.evenFooter.right.font = "Arial"
ws.evenFooter.right.size = 6

# No se fuerza una cantidad fija de páginas:
# Excel determinará automáticamente si son 1, 2, 3, etc.
ws.page_setup.pageOrder = "downThenOver"

# ============================================================
# 38. GUARDAR EXCEL
# ============================================================

wb.save(
    archivo_excel
)


print()
print("=" * 70)
print("              EXCEL GENERADO CORRECTAMENTE")
print("=" * 70)
print()
print(archivo_excel)
print()
print("A4: VERTICAL - PAGINACIÓN AUTOMÁTICA - HOJA MEMBRETADA")
print("PDF: NO GENERADO")
print("Encabezado repetido: filas 1 y 2")
print("Paginación: &P/&N (ej. 1/2, 2/2)")
print(
    "Incertidumbre: "
    + (
        "SÍ"
        if reportar_incertidumbre
        else "NO"
    )
)
print()


# ============================================================
# 39. ACTUALIZAR CONTROL
# ============================================================

nuevo_registro = pd.DataFrame({

    "Nº Informe": [
        codigo_informe
    ],

    "O/S": [
        orden_servicio
    ],

    "Fecha emisión": [
        fecha_emision.strftime(
            "%d/%m/%Y"
        )
    ],

    "Fecha generación": [
        datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )
    ],

    "Incertidumbre reportada": [
        "Si"
        if reportar_incertidumbre
        else "No"
    ],

    "Estado": [
        "Borrador"
    ],

    "Archivo Excel": [
        str(archivo_excel)
    ]

})


if ARCHIVO_CONTROL.exists():

    control = pd.read_excel(
        ARCHIVO_CONTROL
    )

    control = pd.concat(
        [
            control,
            nuevo_registro
        ],
        ignore_index=True
    )

else:

    control = nuevo_registro


control.to_excel(
    ARCHIVO_CONTROL,
    index=False
)


print(
    "✓ Control_Informes.xlsx actualizado:"
)

print(
    ARCHIVO_CONTROL
)

print()
print("=" * 70)
print("                 PROCESO TERMINADO")
print("=" * 70)
print()
