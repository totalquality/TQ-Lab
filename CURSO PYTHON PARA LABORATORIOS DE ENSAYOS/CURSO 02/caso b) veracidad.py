import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# ============================================================
# VERACIDAD — CASO B: INTERVALO DE REFERENCIA
# Cada hoja del Excel = un nivel de concentración.
# Para cada nivel se solicita límite inferior y superior.
# Se contrasta cada límite por separado.
# ============================================================

archivo = r"D:\Ciencia_de_Datos\Validación de métodos químicos\veracidad.xlsx"
alpha = 0.05


def numero(mensaje):
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("Ingrese un valor numérico válido.")


def intervalo(nivel, numero_nivel):
    print("\n" + "-" * 80)
    print(f"INTERVALO DE REFERENCIA — {nivel}")
    print("-" * 80)

    li = numero(
        f"{numero_nivel} nivel, ¿qué VALOR MÍNIMO tiene el intervalo? "
    )

    while True:
        ls = numero(
            f"{numero_nivel} nivel, ¿qué VALOR MÁXIMO tiene el intervalo? "
        )
        if ls > li:
            return li, ls
        print("El valor máximo debe ser mayor que el valor mínimo.")


def preparar(hoja):
    cols = hoja.select_dtypes(include=np.number).columns.tolist()
    if not cols:
        raise ValueError("La hoja no contiene columnas numéricas.")
    series = []
    for c in cols:
        x = pd.to_numeric(hoja[c], errors="coerce").dropna()
        if len(x):
            series.append(x)
    if not series:
        raise ValueError("No existen resultados numéricos válidos.")
    return cols, pd.concat(series, ignore_index=True)


def resumen_descriptivo(nivel, x, li, ls):
    print("\n" + "=" * 80)
    print(f"ESTADÍSTICA DESCRIPTIVA — {nivel}")
    print("=" * 80)
    print(f"N                   = {len(x)}")
    print(f"Media               = {x.mean():.6f}")
    print(f"Mediana             = {x.median():.6f}")
    print(f"Desv. estándar      = {x.std(ddof=1):.6f}")
    print(f"Límite inferior     = {li:.6f}")
    print(f"Límite superior     = {ls:.6f}")


def t_intervalo(nivel, x, li, ls):
    n = len(x); media = x.mean(); sd = x.std(ddof=1); gl = n - 1
    if n < 2 or sd == 0:
        raise ValueError(f"{nivel}: se necesitan al menos 2 resultados y SD > 0.")
    se = sd / np.sqrt(n)

    # Inferior: H0: mu = LI ; H1: mu > LI
    t_li = (media - li) / se
    p_li = stats.t.sf(t_li, gl)

    # Superior: H0: mu = LS ; H1: mu < LS
    t_ls = (media - ls) / se
    p_ls = stats.t.cdf(t_ls, gl)

    pasa_li = p_li < alpha
    pasa_ls = p_ls < alpha
    dentro = pasa_li and pasa_ls
    tcrit = stats.t.ppf(1 - alpha, gl)

    print("\n" + "=" * 80)
    print(f"RESULTADO — t DE STUDENT — {nivel}")
    print("=" * 80)
    print(f"Media = {media:.6f} | SD = {sd:.6f} | N = {n} | gl = {gl}")

    print("\nCONTRASTE — LÍMITE INFERIOR")
    print(f"H₀: μ =  {li:.6f}")
    print(f"H₁: μ >  {li:.6f}")
    print(f"t calculado = {t_li:.6f}")
    print(f"t crítico   = {tcrit:.6f}")
    print(f"p-valor     = {p_li:.6f}")
    print(f"p < α       = {'SÍ' if pasa_li else 'NO'}")

    print("\nCONTRASTE — LÍMITE SUPERIOR")
    print(f"H₀: μ =  {ls:.6f}")
    print(f"H₁: μ <  {ls:.6f}")
    print(f"t calculado = {t_ls:.6f}")
    print(f"t crítico   = {-tcrit:.6f}")
    print(f"p-valor     = {p_ls:.6f}")
    print(f"p < α       = {'SÍ' if pasa_ls else 'NO'}")

    conclusion = ("El valor se encuentra estadísticamente dentro del intervalo de referencia."
                  if dentro else
                  "No se cumplen simultáneamente los dos contrastes para demostrar que el valor esté dentro del intervalo.")
    print("\nCONCLUSIÓN")
    print(conclusion)

    return dict(N=n, media=media, li=li, ls=ls, t_li=t_li, p_li=p_li,
                t_ls=t_ls, p_ls=p_ls, dentro="SÍ" if dentro else "NO",
                conclusion=conclusion)


def wilcoxon_unilateral(diferencias, alternativa):
    d = diferencias[diferencias != 0]
    if len(d) == 0:
        return np.nan, np.nan, np.nan, np.nan, 0, False
    a = np.abs(d.to_numpy())
    rangos = stats.rankdata(a, method="average")
    wpos = rangos[d.to_numpy() > 0].sum()
    wneg = rangos[d.to_numpy() < 0].sum()
    _, frec = np.unique(a, return_counts=True)
    empates = bool(np.any(frec > 1))
    r = stats.wilcoxon(d, zero_method="wilcox", correction=True,
                        alternative=alternativa, method="approx")
    return r.statistic, r.pvalue, wneg, wpos, len(d), empates


def wilcoxon_intervalo(nivel, x, li, ls):
    # Inferior: H0: mediana = LI ; H1: mediana > LI
    W_li, p_li, Wn_li, Wp_li, n_li, emp_li = wilcoxon_unilateral(x-li, "greater")
    # Superior: H0: mediana = LS ; H1: mediana < LS
    W_ls, p_ls, Wn_ls, Wp_ls, n_ls, emp_ls = wilcoxon_unilateral(x-ls, "less")

    pasa_li = p_li < alpha
    pasa_ls = p_ls < alpha
    dentro = pasa_li and pasa_ls

    print("\n" + "=" * 80)
    print(f"RESULTADO — WILCOXON — {nivel}")
    print("=" * 80)
    print(f"Mediana = {x.median():.6f} | N original = {len(x)}")

    print("\nCONTRASTE — LÍMITE INFERIOR")
    print(f"H₀: mediana =  {li:.6f}")
    print(f"H₁: mediana >  {li:.6f}")
    print(f"W− = {Wn_li:.4f} | W+ = {Wp_li:.4f} | W usado = {W_li:.4f}")
    print(f"N efectivo = {n_li} | Empates = {'SÍ' if emp_li else 'NO'}")
    print(f"p-valor = {p_li:.6f} | p < α = {'SÍ' if pasa_li else 'NO'}")

    print("\nCONTRASTE — LÍMITE SUPERIOR")
    print(f"H₀: mediana =  {ls:.6f}")
    print(f"H₁: mediana <  {ls:.6f}")
    print(f"W− = {Wn_ls:.4f} | W+ = {Wp_ls:.4f} | W usado = {W_ls:.4f}")
    print(f"N efectivo = {n_ls} | Empates = {'SÍ' if emp_ls else 'NO'}")
    print(f"p-valor = {p_ls:.6f} | p < α = {'SÍ' if pasa_ls else 'NO'}")

    conclusion = ("El valor se encuentra estadísticamente dentro del intervalo de referencia."
                  if dentro else
                  "No se cumplen simultáneamente los dos contrastes para demostrar que el valor esté dentro del intervalo.")
    print("\nCONCLUSIÓN")
    print(conclusion)

    return dict(N=len(x), mediana=x.median(), li=li, ls=ls, W_li=W_li,
                p_li=p_li, W_ls=W_ls, p_ls=p_ls,
                dentro="SÍ" if dentro else "NO", conclusion=conclusion)


def grafica(nivel, x, li, ls, r, prueba):
    fig = plt.figure(figsize=(14, 7))
    gs = fig.add_gridspec(1, 2, width_ratios=[3.5, 1.5], wspace=0.08)
    ax = fig.add_subplot(gs[0]); info = fig.add_subplot(gs[1])

    ax.axvspan(li, ls, alpha=0.15, label="Intervalo de referencia")
    ax.axvline(li, linestyle="--", linewidth=2, color="red", label="Límite inferior")
    ax.axvline(ls, linestyle="--", linewidth=2, color="red", label="Límite superior")

    if prueba == "t":
        media = x.mean(); sd = x.std(ddof=1); gl = len(x)-1
        se = sd / np.sqrt(len(x))
        tc = stats.t.ppf(1-alpha/2, gl)
        m = tc * se
        ax.errorbar(media, 0, xerr=[[m], [m]], fmt="o", markersize=10,
                    capsize=7, linewidth=2.5, label="Media ± IC 95 %")
        ax.axvline(media, linestyle=":", linewidth=2, label="Media experimental")
        texto = (f"Media = {media:.6f}\nIC 95 % = {media-m:.6f} – {media+m:.6f}\n\n"
                 f"p inferior = {r['p_li']:.6f}\np superior = {r['p_ls']:.6f}\n\n"
                 f"α = {alpha:.2f}\n\nDentro del intervalo = {r['dentro']}")
        titulo = f"Veracidad — {nivel} — t de una muestra"
    else:
        med = x.median()
        ax.boxplot(x, vert=False, widths=0.35, patch_artist=True)
        ax.axvline(med, linestyle=":", linewidth=2, label="Mediana experimental")
        texto = (f"Mediana = {med:.6f}\n\np inferior = {r['p_li']:.6f}\n"
                 f"p superior = {r['p_ls']:.6f}\n\nα = {alpha:.2f}\n\n"
                 f"Dentro del intervalo = {r['dentro']}")
        titulo = f"Veracidad — {nivel} — Wilcoxon de una muestra"

    ax.set_yticks([0] if prueba == "t" else [1])
    ax.set_yticklabels([nivel]); ax.set_xlabel("Resultado", fontsize=12)
    ax.set_title("Evaluación mediante intervalo de referencia", fontsize=14, fontweight="bold")
    ax.grid(axis="x", alpha=0.20); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.legend()

    info.axis("off")
    info.text(0.05, 0.95, "RESULTADO ESTADÍSTICO", fontsize=15, fontweight="bold",
              transform=info.transAxes, verticalalignment="top")
    info.text(0.05, 0.82, texto, fontsize=10.5, transform=info.transAxes,
              verticalalignment="top", linespacing=1.20)

    fig.suptitle(titulo, fontsize=21, fontweight="bold", y=0.97)
    fig.text(0.5, 0.015, "Se requiere p < α en ambos límites para demostrar estadísticamente la ubicación dentro del intervalo.",
             ha="center", fontsize=10, style="italic")
    plt.tight_layout(rect=[0, 0.05, 1, 0.94])
    plt.show()


# ============================================================
# CARGA Y SELECCIÓN
# ============================================================

print("\n" + "#" * 90)
print("VERACIDAD — CASO B: INTERVALO DE REFERENCIA")
print("#" * 90)
print(f"Archivo: {archivo}")
print(f"Nivel de significancia: α = {alpha}")

datos_excel = pd.read_excel(archivo, sheet_name=None)
if not datos_excel:
    raise ValueError("No se encontraron hojas en el archivo.")

print("\nHojas detectadas:")
for h in datos_excel:
    print(f"  - {h}")

resultados = []

for numero_nivel, (nivel, hoja) in enumerate(datos_excel.items(), start=1):

    print("\n" + "#" * 90)
    print(f"{numero_nivel}° NIVEL: {nivel}")
    print("#" * 90)

    cols, x = preparar(hoja)
    print(f"Columnas numéricas detectadas: {', '.join(cols)}")
    print(f"Resultados utilizados: {len(x)}")

    # ------------------------------------------------------------
    # La prueba estadística se selecciona INDEPENDIENTEMENTE
    # para cada nivel.
    # ------------------------------------------------------------
    print(f"\nSELECCIÓN DE LA PRUEBA — {numero_nivel}° NIVEL: {nivel}")
    print("1 → t de Student de una muestra")
    print("2 → T de Wilcoxon de una muestra")

    while True:
        opcion = input(
            f"Seleccione la prueba para el {numero_nivel}° nivel (1 o 2): "
        ).strip()

        if opcion in ("1", "2"):
            break

        print("Opción no válida. Escriba 1 o 2.")

    # Los límites también se solicitan independientemente para cada nivel.
    li, ls = intervalo(nivel, f"{numero_nivel}°")
    resumen_descriptivo(nivel, x, li, ls)

    if opcion == "1":
        r = t_intervalo(nivel, x, li, ls)
        grafica(nivel, x, li, ls, r, "t")
        r["Prueba"] = "t de Student"
    else:
        r = wilcoxon_intervalo(nivel, x, li, ls)
        grafica(nivel, x, li, ls, r, "wilcoxon")
        r["Prueba"] = "Wilcoxon"

    r["Nivel"] = nivel
    r["N° nivel"] = numero_nivel
    resultados.append(r)

# ============================================================
# RESUMEN FINAL
# ============================================================

print("\n" + "#" * 90)
print("RESUMEN FINAL — VERACIDAD POR INTERVALO")
print("#" * 90)

cols_resumen = ["N° nivel", "Nivel", "Prueba", "N", "li", "ls", "p_li", "p_ls", "dentro"]
tabla = pd.DataFrame(resultados)
print(tabla[[c for c in cols_resumen if c in tabla.columns]].to_string(index=False))

print("\nCada nivel fue evaluado de manera independiente con la prueba seleccionada para ese nivel.")
print("\nCRITERIO:")
print(f"p < α ({alpha}) en el límite inferior → evidencia de que el valor está por encima del mínimo.")
print(f"p < α ({alpha}) en el límite superior → evidencia de que el valor está por debajo del máximo.")
print("Deben cumplirse ambos contrastes para concluir que el valor está dentro del intervalo.")
