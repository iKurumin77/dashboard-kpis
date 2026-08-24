"""One-off script to regenerate the corrupted data/ejemplo/ventas.xlsx sample file."""
from pathlib import Path
from datetime import datetime, timedelta
import random

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "ejemplo" / "ventas.xlsx"

vendedores = ["Ana Torres", "Luis Ramirez", "Carla Gomez", "Miguel Diaz"]
productos = ["Laptop", "Monitor", "Teclado", "Mouse", "Silla"]

random.seed(42)
rows = []
start = datetime(2026, 6, 1)
for i in range(120):
    fecha = start + timedelta(days=random.randint(0, 60))
    rows.append({
        "fecha": fecha,
        "vendedor": random.choice(vendedores),
        "producto": random.choice(productos),
        "monto": round(random.uniform(50, 2500), 2),
    })

df = pd.DataFrame(rows).sort_values("fecha")
df.to_excel(DEST, index=False, engine="openpyxl")
print(f"Wrote {len(df)} rows to {DEST}")
