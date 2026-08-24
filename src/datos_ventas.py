from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils import obtener_ruta_fuente, ruta_datos_local


@dataclass
class DatosVentas:
    df: pd.DataFrame

    @classmethod
    def cargar(cls, config: dict[str, Any]) -> "DatosVentas":
        tipo = config.get("fuente_datos", {}).get("tipo", "excel")
        ruta = obtener_ruta_fuente(config)

        if tipo == "excel":
            archivo = ruta_datos_local(ruta) / "ventas.xlsx"
            df = pd.read_excel(archivo, sheet_name=0)
        elif tipo == "csv":
            archivo = ruta_datos_local(ruta) / "ventas.csv"
            df = pd.read_csv(archivo, parse_dates=["fecha"])
        else:
            raise ValueError("Tipo de fuente de datos no soportado para ventas")

        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df = df.dropna(subset=["fecha"])
        return cls(df)

    def filtrar(self, fecha_inicio: str | None, fecha_fin: str | None, vendedor: str | None, producto: str | None) -> pd.DataFrame:
        df = self.df.copy()
        if fecha_inicio:
            df = df[df["fecha"] >= pd.to_datetime(fecha_inicio)]
        if fecha_fin:
            df = df[df["fecha"] <= pd.to_datetime(fecha_fin)]
        if vendedor:
            df = df[df["vendedor"] == vendedor]
        if producto:
            df = df[df["producto"] == producto]
        return df

    def resumen_periodo(self, df_filtrado: pd.DataFrame) -> dict[str, Any]:
        total = df_filtrado["monto"].sum()
        return {
            "total": total,
        }

    def comparacion_anterior(self, df_filtrado: pd.DataFrame) -> float:
        fechas = df_filtrado["fecha"].sort_values()
        if fechas.empty:
            return 0.0

        inicio = fechas.min()
        fin = fechas.max()
        periodo_actual = df_filtrado[(df_filtrado["fecha"] >= inicio) & (df_filtrado["fecha"] <= fin)]
        dias = (fin - inicio).days or 1
        inicio_anterior = inicio - pd.Timedelta(days=dias + 1)
        fin_anterior = inicio - pd.Timedelta(days=1)
        periodo_anterior = self.df[(self.df["fecha"] >= inicio_anterior) & (self.df["fecha"] <= fin_anterior)]
        total_actual = periodo_actual["monto"].sum()
        total_anterior = periodo_anterior["monto"].sum()
        if total_anterior == 0:
            return float("inf") if total_actual > 0 else 0.0
        return ((total_actual - total_anterior) / total_anterior) * 100

    def ventas_por_vendedor(self, df_filtrado: pd.DataFrame) -> pd.DataFrame:
        return df_filtrado.groupby("vendedor")["monto"].sum().reset_index().sort_values("monto", ascending=False)

    def ventas_por_producto(self, df_filtrado: pd.DataFrame) -> pd.DataFrame:
        return df_filtrado.groupby("producto")["monto"].sum().reset_index().sort_values("monto", ascending=False)

    def tendencia(self, df_filtrado: pd.DataFrame, frecuencia: str = "D") -> pd.DataFrame:
        if df_filtrado.empty:
            return pd.DataFrame(columns=["fecha", "monto"])
        df = df_filtrado.set_index("fecha").resample(frecuencia)["monto"].sum().reset_index()
        return df
