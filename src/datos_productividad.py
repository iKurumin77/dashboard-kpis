from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils import obtener_ruta_fuente, ruta_datos_local


@dataclass
class DatosProductividad:
    df: pd.DataFrame

    @classmethod
    def cargar(cls, config: dict[str, Any]) -> "DatosProductividad":
        tipo = config.get("fuente_datos", {}).get("tipo", "excel")
        ruta = obtener_ruta_fuente(config)

        if tipo == "excel":
            archivo = ruta_datos_local(ruta) / "productividad.xlsx"
            df = pd.read_excel(archivo, sheet_name=0)
        elif tipo == "csv":
            archivo = ruta_datos_local(ruta) / "productividad.csv"
            df = pd.read_csv(archivo, parse_dates=["fecha"])
        else:
            raise ValueError("Tipo de fuente de datos no soportado para productividad")

        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df = df.dropna(subset=["fecha"])
        return cls(df)

    def filtrar(self, fecha_inicio: str | None, fecha_fin: str | None, empleado: str | None) -> pd.DataFrame:
        df = self.df.copy()
        if fecha_inicio:
            df = df[df["fecha"] >= pd.to_datetime(fecha_inicio)]
        if fecha_fin:
            df = df[df["fecha"] <= pd.to_datetime(fecha_fin)]
        if empleado:
            df = df[df["empleado"] == empleado]
        return df

    def por_empleado(self, df_filtrado: pd.DataFrame) -> pd.DataFrame:
        return df_filtrado.groupby("empleado")["pedidos_completados"].sum().reset_index().sort_values("pedidos_completados", ascending=False)

    def tiempo_promedio(self, df_filtrado: pd.DataFrame) -> float:
        if df_filtrado.empty:
            return 0.0
        return df_filtrado["tiempo_proceso_min"].mean()

    def comparacion_periodo(self, df_filtrado: pd.DataFrame) -> float:
        fechas = df_filtrado["fecha"].sort_values()
        if fechas.empty:
            return 0.0

        inicio = fechas.min()
        fin = fechas.max()
        dias = (fin - inicio).days or 1
        inicio_anterior = inicio - pd.Timedelta(days=dias + 1)
        fin_anterior = inicio - pd.Timedelta(days=1)
        periodo_anterior = self.df[(self.df["fecha"] >= inicio_anterior) & (self.df["fecha"] <= fin_anterior)]
        total_actual = df_filtrado["pedidos_completados"].sum()
        total_anterior = periodo_anterior["pedidos_completados"].sum()
        if total_anterior == 0:
            return float("inf") if total_actual > 0 else 0.0
        return ((total_actual - total_anterior) / total_anterior) * 100
