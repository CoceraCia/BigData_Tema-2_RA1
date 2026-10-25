# Sales Data Cleaning

Python script that cleans a sales CSV with data quality problems.

> The original `ventas_con_problemas.csv` wasn't available on the platform, so I generated one with AI with made-up data and the same fields.

## What it does
- Initial exploration (shape, types, nulls, describe)
- Fixes or removes: duplicates, nulls, invalid dates, negative values, wrong totals and outliers (IQR)
- Report on screen and in `informe.txt`
- Charts: `grafico_*.png`
- Saves the clean data in `ventas_limpias.csv`

## Run it
```bash
pip install pandas numpy matplotlib seaborn
python main.py
```
