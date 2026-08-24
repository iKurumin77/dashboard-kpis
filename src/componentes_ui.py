from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import plotly.express as px
from src.theme import get_plotly_template
import streamlit as st

from src.i18n import t


def mostrar_kpi_cards(mensajes: dict[str, Any]) -> None:
    # Render cards with custom CSS for a SaaS look
    keys = list(mensajes.keys())
    columnas = st.columns(len(keys))
    for columna, clave in zip(columnas, keys):
        valor = mensajes[clave]
        title = t(clave)
        value = valor.get("valor", "-")
        delta = valor.get("delta", None)
        delta_html = ""
        if delta is not None:
            cls = "delta-up" if (isinstance(delta, (int, float)) and delta >= 0) else "delta-down"
            arrow = "▲" if (isinstance(delta, (int, float)) and delta >= 0) else "▼"
            delta_html = f"<span class='kpi-delta {cls}'>{arrow} {delta}</span>"

        card_html = f"""
        <div class='kpi-card'>
            <div class='kpi-title'>{title}</div>
            <div style='display:flex; align-items:baseline; gap:8px;'>
                <div class='kpi-value'>{value}</div>
                {delta_html}
            </div>
        </div>
        """
        card_html = card_html.replace("<div class='kpi-value'>", f"<div class='kpi-value' data-value=\"{value}\">")
        columna.markdown(card_html, unsafe_allow_html=True)

    js = r"""
    <script>
    setTimeout(()=>{
      document.querySelectorAll('.kpi-card').forEach(el => el.classList.add('loaded'));
      document.querySelectorAll('.plotly-graph-div').forEach(el => el.classList.add('loaded'));
      document.querySelectorAll('.kpi-value').forEach(el => {
        const target = el.getAttribute('data-value') || el.innerText;
        const n = parseFloat(String(target).replace(/[^0-9\.\-]/g, '')) || 0;
        const sign = n < 0 ? -1 : 1;
        const abs = Math.abs(n);
        let i = 0;
        const steps = 30;
        const dur = 700;
        const timer = setInterval(()=>{
          i += 1;
          const val = Math.round((abs * (i/steps)) * 100) / 100;
          el.innerText = (sign * val).toLocaleString();
          if (i >= steps) { clearInterval(timer); el.innerText = target; }
        }, dur/steps);
      });
    }, 80);
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)


def grafico_barras(df: pd.DataFrame, x: str, y: str, titulo: str) -> None:
    if df.empty:
        st.info(t("mensajes.sin_datos"))
        return
    fig = px.bar(df, x=x, y=y, title=t(titulo), labels={x: t(x), y: t(y)}, template=get_plotly_template())
    fig.update_layout(margin=dict(l=0, r=0, t=35, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)


def grafico_lineas(df: pd.DataFrame, x: str, y: str, titulo: str) -> None:
    if df.empty:
        st.info(t("mensajes.sin_datos"))
        return
    fig = px.line(df, x=x, y=y, title=t(titulo), markers=True, labels={x: t(x), y: t(y)}, template=get_plotly_template())
    fig.update_layout(margin=dict(l=0, r=0, t=35, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)


def mostrar_tabla(df: pd.DataFrame, titulo: str) -> None:
    if df.empty:
        st.info(t("mensajes.sin_datos"))
        return
    st.subheader(t(titulo))
    st.dataframe(df)


def filtros_generales(df_ventas: pd.DataFrame, df_productividad: pd.DataFrame, df_inventario: pd.DataFrame) -> dict[str, Any]:
    st.sidebar.subheader(t("filtros.titulo"))

    fecha_min = pd.to_datetime(df_ventas["fecha"].min()) if not df_ventas.empty else None
    fecha_max = pd.to_datetime(df_ventas["fecha"].max()) if not df_ventas.empty else None
    fechainicio = st.sidebar.date_input(
        t("filtros.fecha_inicio"),
        value=fecha_min.date() if fecha_min is not None else date.today(),
    )
    fechafin = st.sidebar.date_input(
        t("filtros.fecha_fin"),
        value=fecha_max.date() if fecha_max is not None else date.today(),
    )

    vendedores = []
    if "vendedor" in df_ventas.columns:
        vendedores = sorted(df_ventas["vendedor"].dropna().unique().tolist())
    productos = []
    if "producto" in df_ventas.columns:
        productos = sorted(df_ventas["producto"].dropna().unique().tolist())
    empleados = []
    if "empleado" in df_productividad.columns:
        empleados = sorted(df_productividad["empleado"].dropna().unique().tolist())

    vendedor = st.sidebar.selectbox(t("filtros.vendedor"), options=[""] + vendedores, index=0)
    producto = st.sidebar.selectbox(t("filtros.producto"), options=[""] + productos, index=0)
    empleado = st.sidebar.selectbox(t("filtros.empleado"), options=[""] + empleados, index=0)

    return {
        "fecha_inicio": str(fechainicio) if fechainicio else None,
        "fecha_fin": str(fechafin) if fechafin else None,
        "vendedor": vendedor or None,
        "producto": producto or None,
        "empleado": empleado or None,
    }
