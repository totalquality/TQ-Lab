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
