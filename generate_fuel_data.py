import pandas as pd
import numpy as np
import random
from datetime import datetime

random.seed(42)
np.random.seed(42)

# Countries with region and base fuel price (USD/liter approx)
countries = [
    # Asia
    ("China",        "Asia",  "East Asia",       0.95,  1.04),
    ("Japan",        "Asia",  "East Asia",       1.55,  1.40),
    ("South Korea",  "Asia",  "East Asia",       1.65,  1.45),
    ("India",        "Asia",  "South Asia",      1.10,  0.90),
    ("Pakistan",     "Asia",  "South Asia",      0.85,  0.78),
    ("Bangladesh",   "Asia",  "South Asia",      0.90,  0.82),
    ("Vietnam",      "Asia",  "Southeast Asia",  0.95,  0.88),
    ("Thailand",     "Asia",  "Southeast Asia",  1.20,  1.10),
    ("Indonesia",    "Asia",  "Southeast Asia",  0.75,  0.68),
    ("Malaysia",     "Asia",  "Southeast Asia",  0.52,  0.48),
    ("Philippines",  "Asia",  "Southeast Asia",  1.15,  1.05),
    ("Singapore",    "Asia",  "Southeast Asia",  2.15,  1.95),
    ("Myanmar",      "Asia",  "Southeast Asia",  0.88,  0.82),
    ("Saudi Arabia", "Asia",  "Middle East",     0.38,  0.32),
    ("UAE",          "Asia",  "Middle East",     0.68,  0.60),
    ("Kuwait",       "Asia",  "Middle East",     0.30,  0.28),
    ("Iran",         "Asia",  "Middle East",     0.05,  0.04),
    ("Iraq",         "Asia",  "Middle East",     0.45,  0.40),
    ("Israel",       "Asia",  "Middle East",     1.88,  1.70),
    ("Kazakhstan",   "Asia",  "Central Asia",    0.52,  0.48),
    # Non-Asia
    ("USA",          "World", "North America",   0.95,  0.88),
    ("Canada",       "World", "North America",   1.25,  1.15),
    ("Mexico",       "World", "North America",   1.05,  0.98),
    ("Germany",      "World", "Europe",          1.85,  1.65),
    ("France",       "World", "Europe",          1.90,  1.70),
    ("UK",           "World", "Europe",          1.95,  1.75),
    ("Italy",        "World", "Europe",          1.88,  1.68),
    ("Spain",        "World", "Europe",          1.65,  1.55),
    ("Netherlands",  "World", "Europe",          2.10,  1.90),
    ("Norway",       "World", "Europe",          2.25,  2.00),
    ("Russia",       "World", "Europe",          0.62,  0.55),
    ("Turkey",       "World", "Europe",          1.20,  1.10),
    ("Poland",       "World", "Europe",          1.45,  1.35),
    ("Brazil",       "World", "South America",   1.35,  1.25),
    ("Argentina",    "World", "South America",   0.88,  0.80),
    ("Colombia",     "World", "South America",   0.98,  0.90),
    ("Venezuela",    "World", "South America",   0.02,  0.02),
    ("Nigeria",      "World", "Africa",          0.55,  0.50),
    ("South Africa", "World", "Africa",          1.15,  1.05),
    ("Egypt",        "World", "Africa",          0.45,  0.40),
    ("Ethiopia",     "World", "Africa",          1.10,  0.98),
    ("Australia",    "World", "Oceania",         1.45,  1.38),
    ("New Zealand",  "World", "Oceania",         1.68,  1.55),
]

years  = [2019, 2020, 2021, 2022, 2023, 2024]
months = range(1, 13)

# Year multipliers to simulate COVID drop + energy crisis
year_effect = {2019: 1.00, 2020: 0.82, 2021: 0.98, 2022: 1.35, 2023: 1.15, 2024: 1.10}

rows = []
for year in years:
    for month in months:
        for (country, continent, subregion, base_gas, base_diesel) in countries:
            ym = year_effect[year]
            noise = np.random.normal(1.0, 0.04)

            gasoline_price = round(base_gas * ym * noise, 3)
            diesel_price   = round(base_diesel * ym * noise * np.random.normal(1.0, 0.02), 3)
            lpg_price      = round(base_gas * 0.65 * ym * noise, 3)

            rows.append({
                "Country":        country,
                "Continent":      continent,
                "Sub-Region":     subregion,
                "Year":           year,
                "Month":          month,
                "Date":           f"{year}-{month:02d}-01",
                "Gasoline_Price": max(0.01, gasoline_price),
                "Diesel_Price":   max(0.01, diesel_price),
                "LPG_Price":      max(0.01, lpg_price),
                "Currency":       "USD",
                "Unit":           "per liter",
            })

df = pd.DataFrame(rows)
df.to_csv("fuel_prices.csv", index=False)
print(f"Dataset gerado: {len(df)} registos")
print(df.head(10).to_string())
print("\nColunas:", list(df.columns))
