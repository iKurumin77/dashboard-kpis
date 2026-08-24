from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils import obtener_ruta_fuente, ruta_datos_local


@dataclass
class DatosInventario:
    df: pd.DataFrame

    @classmethod
    def cargar(cls, config: dict[str, Any]) -> "DatosInventario":
        tipo = config.get("fuente_datos", {}).get("tipo", "excel")
        ruta = obtener_ruta_fuente(config)

        if tipo == "excel":
            archivo = ruta_datos_local(ruta) / "inventario.xlsx"
            df = pd.read_excel(archivo, sheet_name=0)
        elif tipo == "csv":
            archivo = ruta_datos_local(ruta) / "inventario.csv"
            df = pd.read_csv(archivo)
        else:
            raise ValueError("Tipo de fuente de datos no soportado para inventario")

        return cls(df)

    def productos_bajo_stock(self, umbral: int) -> pd.DataFrame:
        return self.df[self.df["stock_actual"] <= umbral].sort_values("stock_actual")

    def rotacion(self) -> pd.DataFrame:
        if "ventas_unidades" not in self.df.columns:
            return pd.DataFrame(columns=["producto", "rotacion"])
        df = self.df.copy()
        df["rotacion"] = df["ventas_unidades"] / df["stock_actual"].replace(0, pd.NA)
        return df[["producto", "rotacion"]].sort_values("rotacion", ascending=False)
