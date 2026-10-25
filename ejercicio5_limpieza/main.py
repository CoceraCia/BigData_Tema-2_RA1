# EJERCICIO 5: Script en Python que carga ventas_con_problemas.csv, identifica y corrige los problemas
# de calidad de datos (nulos, fechas invalidas, negativos, totales incorrectos, outliers y duplicados),
# genera un informe, crea visualizaciones y guarda los datos limpios en un nuevo CSV.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

INPUT = "ventas_con_problemas.csv"
OUTPUT = "ventas_limpias.csv"
NUMERIC = ["cantidad", "precio_unitario", "total"]
CRITICAL = ["fecha", "producto", "cantidad", "precio_unitario", "total"]

# aqui voy guardando cuantos problemas encuentro de cada tipo
problems = {}


def main():
    df_original = pd.read_csv(INPUT)
    explore(df_original)

    df = df_original.copy()
    df = removeDuplicates(df)
    df = handleNulls(df)
    df = handleDates(df)
    df = handleNegatives(df)
    df = handleTotals(df)
    df = handleOutliers(df)

    report(df_original, df)
    charts(df_original, df)

    df.to_csv(OUTPUT, index=False)
    print(f"\nClean data saved in {OUTPUT}")


def explore(df: pd.DataFrame):
    print("------------- INITIAL EXPLORATION -------------")
    print(f"Rows: {df.shape[0]}  Columns: {df.shape[1]}")
    print(df.head())
    print("\nData types:")
    print(df.dtypes)
    print("\nNull values per column:")
    print(df.isnull().sum())
    print("\nDescribe:")
    print(df.describe())


def removeDuplicates(df: pd.DataFrame) -> pd.DataFrame:
    n = df.duplicated().sum()
    problems["Duplicados"] = int(n)
    return df.drop_duplicates()


def handleNulls(df: pd.DataFrame) -> pd.DataFrame:
    nulls = df[CRITICAL].isnull().any(axis=1)
    problems["Valores nulos"] = int(nulls.sum())

    # si solo falta el total pero tengo cantidad y precio lo puedo recalcular
    canFix = df["total"].isnull() & df["cantidad"].notnull() & df["precio_unitario"].notnull()
    df.loc[canFix, "total"] = (df.loc[canFix, "cantidad"] * df.loc[canFix, "precio_unitario"]).round(2)

    # el resto no se puede recuperar -> fuera
    return df.dropna(subset=CRITICAL)


def handleDates(df: pd.DataFrame) -> pd.DataFrame:
    # errors="coerce" convierte en NaT todo lo que no sea una fecha valida (2026-02-30, texto, etc)
    dates = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="coerce")
    problems["Fechas inválidas"] = int(dates.isnull().sum())
    df = df.assign(fecha=dates)
    return df.dropna(subset=["fecha"])


def handleNegatives(df: pd.DataFrame) -> pd.DataFrame:
    negatives = (df[NUMERIC] < 0).any(axis=1)
    problems["Valores negativos"] = int(negatives.sum())
    # entiendo que el signo esta mal puesto, asi que me quedo con el valor absoluto
    df[NUMERIC] = df[NUMERIC].abs()
    return df


def handleTotals(df: pd.DataFrame) -> pd.DataFrame:
    expected = (df["cantidad"] * df["precio_unitario"]).round(2)
    wrong = (df["total"] - expected).abs() > 0.01
    problems["Totales incorrectos"] = int(wrong.sum())
    # la cantidad y el precio son los datos de origen, el total se recalcula
    df.loc[wrong, "total"] = expected[wrong]
    return df


def handleOutliers(df: pd.DataFrame) -> pd.DataFrame:
    # metodo IQR sobre la cantidad
    q1 = df["cantidad"].quantile(0.25)
    q3 = df["cantidad"].quantile(0.75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    lower = q1 - 1.5 * iqr
    outliers = (df["cantidad"] > upper) | (df["cantidad"] < lower)
    problems["Outliers"] = int(outliers.sum())
    print(f"\nOutlier limits (cantidad): {lower} - {upper}")
    return df[~outliers]


def report(original: pd.DataFrame, clean: pd.DataFrame):
    lines = []
    lines.append("------------------- REPORT -------------------")
    lines.append(f"Original rows: {len(original)}")
    lines.append(f"Rows after cleaning: {len(clean)}")
    lines.append(f"Removed rows: {len(original) - len(clean)}")
    lines.append("\nProblems found and fixed:")
    for k, v in problems.items():
        lines.append(f"  - {k}: {v}")
    lines.append("\nDescriptive statistics (clean data):")
    stats = clean[NUMERIC].agg(["mean", "median", "std"]).round(2)
    lines.append(stats.to_string())
    text = "\n".join(lines)
    print("\n" + text)
    with open("informe.txt", "w", encoding="utf-8") as f:
        f.write(text)


def charts(original: pd.DataFrame, clean: pd.DataFrame):
    sns.set_theme(style="whitegrid")
    before = original.copy()
    for col in NUMERIC:
        before[col] = pd.to_numeric(before[col], errors="coerce")

    # 1. problemas por tipo
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=list(problems.values()), y=list(problems.keys()), ax=ax, color="#6C8EBF")
    ax.set_title("Problemas encontrados por tipo")
    ax.set_xlabel("Número de filas")
    fig.tight_layout()
    fig.savefig("grafico_problemas.png", dpi=120)

    # 2. boxplot de la cantidad antes y despues
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    sns.boxplot(y=before["cantidad"], ax=axes[0], color="#F8CECC")
    axes[0].set_title("Cantidad ANTES de limpiar")
    sns.boxplot(y=clean["cantidad"], ax=axes[1], color="#D5E8D4")
    axes[1].set_title("Cantidad DESPUÉS de limpiar")
    fig.tight_layout()
    fig.savefig("grafico_cantidad.png", dpi=120)

    # 3. distribucion del total antes y despues
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    sns.histplot(before["total"].dropna(), bins=30, ax=axes[0], color="#B85450")
    axes[0].set_title("Total ANTES de limpiar")
    sns.histplot(clean["total"], bins=30, ax=axes[1], color="#82B366")
    axes[1].set_title("Total DESPUÉS de limpiar")
    fig.tight_layout()
    fig.savefig("grafico_total.png", dpi=120)

    # 4. ventas por dia con los datos limpios
    fig, ax = plt.subplots(figsize=(10, 4))
    daily = clean.groupby(clean["fecha"].dt.date)["total"].sum()
    ax.plot(daily.index, daily.values, marker="o", color="#6C8EBF")
    ax.set_title("Ventas por día (datos limpios)")
    ax.set_ylabel("Total (€)")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig("grafico_ventas_dia.png", dpi=120)

    plt.close("all")
    print("Charts saved (grafico_*.png)")


if __name__ == "__main__":
    main()
