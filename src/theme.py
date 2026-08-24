"""Theme helpers and Plotly template for the dashboard."""
from typing import Dict
import plotly.io as pio

PALETTE: Dict[str, str] = {
    "bg": "#0f1720",
    "bg_light": "#f6f7fb",
    "text": "#e6eef8",
    "muted": "#9aa4b2",
    "accent": "#7c5cff",
    "positive": "#22c55e",
    "negative": "#fb7047",
}


def register_plotly_template():
    template = pio.templates["plotly"]
    layout = {
        "font": {"family": "Inter, Arial, sans-serif", "color": PALETTE["text"]},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "colorway": [PALETTE["accent"], PALETTE["positive"], PALETTE["negative"]],
        "legend": {"bgcolor": "rgba(0,0,0,0)"},
        "margin": {"l": 10, "r": 10, "t": 40, "b": 10},
    }
    pio.templates["dashboard_theme"] = template
    pio.templates["dashboard_theme"].layout.update(layout)


def get_plotly_template():
    return "dashboard_theme"
