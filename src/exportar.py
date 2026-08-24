from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
from fpdf import FPDF

from src.i18n import t


def exportar_excel(df: pd.DataFrame, nombre: str) -> bytes:
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=nombre[:31])
        return buffer.getvalue()


def exportar_pdf(df: pd.DataFrame, titulo: str) -> bytes:
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, txt=t(titulo), ln=True)
    pdf.set_font("Arial", size=10)
    pdf.ln(5)

    columnas = df.columns.tolist()
    ancho_col = 260 / max(len(columnas), 1)
    pdf.set_font("Arial", "B", 9)
    for columna in columnas:
        pdf.cell(ancho_col, 8, txt=str(columna), border=1)
    pdf.ln()
    pdf.set_font("Arial", size=8)

    for _, fila in df.iterrows():
        for columna in columnas:
            texto = str(fila[columna]) if fila[columna] is not None else ""
            pdf.cell(ancho_col, 6, txt=texto[:30], border=1)
        pdf.ln()
        if pdf.get_y() > 185:
            pdf.add_page()
            pdf.set_font("Arial", "B", 9)
            for columna in columnas:
                pdf.cell(ancho_col, 8, txt=str(columna), border=1)
            pdf.ln()
            pdf.set_font("Arial", size=8)

    # fpdf2's output(dest="S") already returns raw bytes (bytearray), no need to encode
    return bytes(pdf.output(dest="S"))
