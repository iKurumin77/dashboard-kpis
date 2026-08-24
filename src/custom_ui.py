from pathlib import Path
import streamlit as st
from streamlit_option_menu import option_menu
from src.i18n import t


def load_styles():
    css_path = Path(__file__).parent.parent / "assets" / "styles.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def apply_theme(theme: str):
    """Apply theme by toggling a class on the document element."""
    if theme == "light":
        js = "<script>document.documentElement.classList.add('light-mode');</script>"
    else:
        js = "<script>document.documentElement.classList.remove('light-mode');</script>"
    st.markdown(js, unsafe_allow_html=True)


def show_toast(message: str, duration: int = 2500) -> None:
    toast_html = f"""
    <style>
    .toast-message {{
      position: fixed;
      top: 1rem;
      right: 1rem;
      z-index: 9999;
      background: rgba(15, 23, 40, 0.95);
      color: #f8fafc;
      padding: 14px 18px;
      border-radius: 14px;
      box-shadow: 0 18px 40px rgba(0, 0, 0, 0.2);
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 0.95rem;
      line-height: 1.3;
      max-width: 320px;
      opacity: 0.98;
    }}
    </style>
    <div class="toast-message">{message}</div>
    <script>
      setTimeout(() => {{
        const toast = document.querySelector('.toast-message');
        if (toast) toast.remove();
      }}, {duration});
    </script>
    """
    st.markdown(toast_html, unsafe_allow_html=True)


def spinner_html(message: str = "Cargando...") -> str:
    return f"<div class='spinner-overlay'><div class='spinner-dot'></div><div style='color:var(--text)'>{message}</div></div>"


def sidebar_branding(config: dict):
    logo_path = config.get("empresa", {}).get("logo", None)
    with st.sidebar:
        st.markdown(
            f"<div class='app-header'><div class='logo'></div><div class='brand'>{config.get('empresa', {}).get('nombre', 'Dashboard KPIs')}</div></div>",
            unsafe_allow_html=True,
        )


def sidebar_menu(default: str = "Visión general") -> str:
    choices = [t("tabs.ventas"), t("tabs.inventario"), t("tabs.productividad")]
    selected = option_menu(None, choices, icons=["bar-chart-fill", "box-seam", "speedometer2"], menu_icon="cast", default_index=0, orientation="vertical")
    return selected


def theme_toggle(current_theme: str):
    # current_theme: 'dark' or 'light'
    col1, col2 = st.sidebar.columns([1,4])
    with col2:
        new = st.checkbox(t("sidebar.modo_oscuro"), value=(current_theme == "dark"))
    return "dark" if new else "light"
