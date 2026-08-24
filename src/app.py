from __future__ import annotations

from datetime import datetime
from typing import Any
import logging
from pathlib import Path

import streamlit as st

from src.componentes_ui import (
    filtros_generales,
    grafico_barras,
    grafico_lineas,
    mostrar_kpi_cards,
    mostrar_tabla,
)
from src.datos_inventario import DatosInventario
from src.datos_productividad import DatosProductividad
from src.datos_ventas import DatosVentas
from src.exportar import exportar_excel, exportar_pdf
from src.i18n import I18n, get_i18n, t, validate_translation_keys
from src.utils import (
    cargar_config,
    cargar_usuario_config,
    guardar_usuario_config,
    obtener_ruta_fuente,
    ruta_datos_local,
    crear_carpeta_si_no_existe,
    get_app_root,
    get_data_dir,
)
from src.custom_ui import load_styles, sidebar_branding, sidebar_menu, theme_toggle, show_toast
from src.theme import register_plotly_template, get_plotly_template


def configurar_pagina(config: dict[str, Any], idioma: str) -> I18n:
    st.set_page_config(
        page_title=config.get("empresa", {}).get("nombre", "Dashboard KPIs"),
        page_icon="📊",
        layout="wide",
    )
    return get_i18n(idioma)


def _save_uploaded_dataframe(df, filename: str) -> str:
    # Save uploaded dataframe to a writable per-user folder (not the app install folder)
    from src.utils import get_data_dir

    carpeta = get_data_dir() / "uploads"
    crear_carpeta_si_no_existe(carpeta)
    destino = carpeta / filename
    try:
        df.to_excel(destino, index=False)
    except Exception:
        try:
            df.to_csv(destino.with_suffix('.csv'), index=False)
            destino = destino.with_suffix('.csv')
        except Exception:
            destino = ""
    return str(destino)


def detectar_tipo_por_columnas(cols: list[str]) -> str | None:
    # heurísticas simples para detectar tipo de archivo
    lower = [c.lower() for c in cols]
    if any(x in lower for x in ("monto", "venta", "amount")) and any(x in lower for x in ("vendedor", "salesperson", "seller")):
        return "ventas"
    if any(x in lower for x in ("stock", "stock_actual", "cantidad")):
        return "inventario"
    if any(x in lower for x in ("pedidos_completados", "orders_completed", "pedidos")) or any(x in lower for x in ("tiempo_proceso_min", "time")):
        return "productividad"
    return None


def mostrar_onboarding():
    st.header(t("onboarding.bienvenida"))
    st.markdown(t("onboarding.instruccion"))
    # ensure uploader_version exists in session_state to force widget recreation on reset
    if "uploader_version" not in st.session_state:
        st.session_state["uploader_version"] = 0
    uploader_key = f"uploader_{st.session_state['uploader_version']}"
    uploaded = st.file_uploader(
        t("uploader.prompt"),
        type=["xlsx", "csv"],
        accept_multiple_files=True,
        key=uploader_key,
    )
    if st.button(t("onboarding.usar_ejemplo")):
        # load example data by restarting app flow (user will see dashboard)
        st.session_state["use_example_data"] = True
        st.rerun()

    if uploaded:
        for f in uploaded:
            with st.spinner(t("actions.processing")):
                try:
                    import pandas as pd
                    from io import BytesIO

                    data = f.read()
                    try:
                        df = pd.read_excel(BytesIO(data))
                    except Exception:
                        df = pd.read_csv(BytesIO(data))
                    st.subheader(f.name)
                    st.dataframe(df.head(5))

                    cols = df.columns.tolist()
                    tipo = detectar_tipo_por_columnas(cols)
                    tipo_sel = tipo or st.selectbox(t("uploader.select_tipo"), options=["ventas", "inventario", "productividad"], index=0)

                    # mapping required fields
                    mapping = {}
                    if tipo_sel == "ventas":
                        required = ["fecha", "vendedor", "producto", "monto"]
                    elif tipo_sel == "inventario":
                        required = ["producto", "stock_actual"]
                    else:
                        required = ["fecha", "empleado", "pedidos_completados", "tiempo_proceso_min"]

                    st.markdown(t("uploader.map_instruccion"))
                    for field in required:
                        sel = st.selectbox(t("uploader.map_field", field=field), options=[""] + cols, key=f"map_{f.name}_{field}")
                        mapping[field] = sel or None

                    if st.button(t("actions.upload_confirm"), key=f"confirm_{f.name}"):
                        # rename columns according to mapping
                        df2 = df.copy()
                        rename_map = {v: k for k, v in mapping.items() if v}
                        df2 = df2.rename(columns=rename_map)
                        saved = _save_uploaded_dataframe(df2, f.name)
                        # persist mapping
                        usuario_cfg = cargar_usuario_config()
                        uploads = usuario_cfg.get("uploads", {})
                        uploads[f.name] = {"path": saved, "mapping": mapping, "tipo": tipo_sel}
                        usuario_cfg["uploads"] = uploads
                        guardar_usuario_config(usuario_cfg)
                        st.success(t("actions.upload_success"))
                        # increment uploader_version to ensure uploader is reset on next render
                        st.session_state["uploader_version"] = st.session_state.get("uploader_version", 0) + 1
                        st.rerun()
                except Exception:
                    st.error(t("errores.file_invalid"))



def cargar_datos(config: dict[str, Any]) -> tuple[DatosVentas | None, DatosInventario | None, DatosProductividad | None]:
    tipo = config.get("fuente_datos", {}).get("tipo", "excel")
    ruta = obtener_ruta_fuente(config)
    ruta_absoluta = ruta_datos_local(ruta)
    ventas = inventario = productividad = None

    if not ruta_absoluta.exists():
        st.warning(t("mensajes.ruta_no_encontrada", ruta=str(ruta_absoluta)))
        return None, None, None

    try:
        ventas = DatosVentas.cargar(config)
    except Exception:
        logging.exception("Fallo al cargar datos de ventas")
        ventas = None
    try:
        inventario = DatosInventario.cargar(config)
    except Exception:
        logging.exception("Fallo al cargar datos de inventario")
        inventario = None
    try:
        productividad = DatosProductividad.cargar(config)
    except Exception:
        logging.exception("Fallo al cargar datos de productividad")
        productividad = None

    return ventas, inventario, productividad


def mostrar_encabezado(config: dict[str, Any]) -> None:
    st.title(t("app.titulo"))
    st.markdown(f"**{config.get('empresa', {}).get('nombre', '')}**")


def obtener_idioma_actual(config: dict[str, Any]) -> str:
    usuario_config = cargar_usuario_config()
    return usuario_config.get("idioma", config.get("idioma_default", "es"))


def guardar_idioma(idioma: str) -> None:
    usuario_config = cargar_usuario_config()
    usuario_config["idioma"] = idioma
    guardar_usuario_config(usuario_config)


def main() -> None:
    # set up logging for unhandled exceptions (writable per-user folder, not the install folder)
    logs_dir = Path(get_data_dir()) / "logs"
    crear_carpeta_si_no_existe(logs_dir)
    logging.basicConfig(
        filename=str(logs_dir / "errores.log"),
        level=logging.ERROR,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    try:
        config = cargar_config()
        idioma_actual = obtener_idioma_actual(config)
        configurar_pagina(config, idioma_actual)
        # validate translation keys in development (prints missing keys to console)
        try:
            validate_translation_keys()
        except Exception:
            pass
        # load custom CSS/theme and register plotly template
        load_styles()
        register_plotly_template()

        # Sidebar: branding + menu + preferences
        sidebar_branding(config)
        # Emergency restart button always available
        if st.sidebar.button(t("actions.restart"), key="button_restart"):
            usuario_cfg = cargar_usuario_config()
            usuario_cfg.pop("uploads", None)
            guardar_usuario_config(usuario_cfg)
            st.session_state.clear()
            st.rerun()
        # quick action: cargar otro archivo (visible cuando ya hay datos cargados)
        if st.sidebar.button(t("actions.reset"), key="button_reset"):
            show_toast(t("actions.restarting"))
            usuario_cfg = cargar_usuario_config()
            usuario_cfg.pop("uploads", None)
            guardar_usuario_config(usuario_cfg)
            # clear relevant session state entries and bump uploader version so widget is recreated
            keys = list(st.session_state.keys())
            for k in keys:
                if k.startswith("map_") or k.startswith("confirm_") or k in ("ventas_df", "inventario_df", "productividad_df", "use_example_data"):
                    st.session_state.pop(k, None)
            st.session_state["uploader_version"] = st.session_state.get("uploader_version", 0) + 1
            st.rerun()

        # language selection still stored via existing helpers
        idioma = st.sidebar.selectbox(
            t("sidebar.seleccionar_idioma"),
            options=["es", "en", "ja"],
            format_func=lambda x: {"es": "Español", "en": "English", "ja": "日本語"}.get(x, x),
            index=["es", "en", "ja"].index(idioma_actual),
        )
        if idioma != idioma_actual:
            guardar_idioma(idioma)
            st.rerun()

        # theme toggle
        usuario_config = cargar_usuario_config()
        theme_now = usuario_config.get("theme", "dark")
        nuevo_theme = theme_toggle(theme_now)
        if nuevo_theme != theme_now:
            usuario_config["theme"] = nuevo_theme
            guardar_usuario_config(usuario_config)
            st.rerun()

        # apply theme class to document
        from src.custom_ui import apply_theme, spinner_html
        apply_theme(usuario_config.get("theme", "dark"))

        intervalo = st.sidebar.number_input(
            t("sidebar.intervalo_refresco"),
            min_value=1,
            max_value=60,
            value=config.get("refresco", {}).get("intervalo_minutos", 5),
            help=t("sidebar.intervalo_refresco_help"),
        )

        # navigation menu (replaces top tabs with sidebar menu)
        seleccion = sidebar_menu()

        st_autorefresh(intervalo)
        mostrar_encabezado(config)

        import pandas as pd

        usuario_cfg = cargar_usuario_config()
        uploads_cfg = usuario_cfg.get("uploads", {})
        # Only touch the on-disk data source once the user explicitly chose to proceed
        # (via "Try example data" or after confirming an upload). Otherwise always show onboarding,
        # even if the example/config data files exist on disk.
        data_source_ready = bool(st.session_state.get("use_example_data")) or bool(uploads_cfg)
        if not data_source_ready:
            mostrar_onboarding()
            return

        ventas, inventario, productividad = cargar_datos(config)
        df_ventas = ventas.df if ventas else st.session_state.get("ventas_df", None) or pd.DataFrame()
        df_productividad = productividad.df if productividad else st.session_state.get("productividad_df", None) or pd.DataFrame()
        df_inventario = inventario.df if inventario else st.session_state.get("inventario_df", None) or pd.DataFrame()

        no_data_loaded = ventas is None and inventario is None and productividad is None
        if no_data_loaded and uploads_cfg:
            st.warning(t("mensajes.uploads_no_data"))
            usuario_cfg.pop("uploads", None)
            guardar_usuario_config(usuario_cfg)
            mostrar_onboarding()
            return

        # If no data loaded and no uploaded files configured, show onboarding/upload UI
        if no_data_loaded:
            mostrar_onboarding()
            return

        filtros = filtros_generales(df_ventas, df_productividad, df_inventario)

        # show selected page
        if seleccion == t("tabs.ventas"):
            if ventas is None:
                st.warning(t("mensajes.error_ventas"))
            else:
                # show custom spinner while filtering/loading
                ph = st.empty()
                ph.markdown(spinner_html(t("mensajes.cargando")), unsafe_allow_html=True)
                df_filtrado = ventas.filtrar(
                    fecha_inicio=filtros.get("fecha_inicio"),
                    fecha_fin=filtros.get("fecha_fin"),
                    vendedor=filtros.get("vendedor"),
                    producto=filtros.get("producto"),
                )
                ph.empty()
                mostrar_ventas(ventas, df_filtrado)
                mostrar_exportacion(df_filtrado, "ventas")

        elif seleccion == t("tabs.inventario"):
            if inventario is None:
                st.warning(t("mensajes.error_inventario"))
            else:
                ph = st.empty()
                ph.markdown(spinner_html(t("mensajes.cargando")), unsafe_allow_html=True)
                df_filtrado = inventario.df
                ph.empty()
                mostrar_inventario(inventario, config)
                mostrar_exportacion(df_filtrado, "inventario")

        else:
            if productividad is None:
                st.warning(t("mensajes.error_productividad"))
            else:
                ph = st.empty()
                ph.markdown(spinner_html(t("mensajes.cargando")), unsafe_allow_html=True)
                df_filtrado = productividad.filtrar(
                    fecha_inicio=filtros.get("fecha_inicio"),
                    fecha_fin=filtros.get("fecha_fin"),
                    empleado=filtros.get("empleado"),
                )
                ph.empty()
                mostrar_productividad(productividad, df_filtrado)
                mostrar_exportacion(df_filtrado, "productividad")

    except Exception:
        logging.exception("Unhandled exception in main loop")
        # show friendly error UI
        st.title(t("errores.unhandled_title"))
        st.error(t("errores.unhandled_message"))
        if st.button(t("actions.restart"), key="button_restart_error"):
            usuario_cfg = cargar_usuario_config()
            usuario_cfg.pop("uploads", None)
            guardar_usuario_config(usuario_cfg)
            st.session_state.clear()
            st.rerun()


def st_autorefresh(intervalo_minutos: int) -> None:
    if intervalo_minutos <= 0:
        return
    ms = int(intervalo_minutos * 60 * 1000)
    st.markdown(
        f"<script>window.setTimeout(function() {{window.location.reload();}}, {ms});</script>",
        unsafe_allow_html=True,
    )


def mostrar_ventas(ventas: DatosVentas, df_filtrado: Any) -> None:
    resumen = ventas.resumen_periodo(df_filtrado)
    comparacion = ventas.comparacion_anterior(df_filtrado)
    tarjetas = {
        "ventas.total_periodo": {"valor": f"${resumen['total']:,.2f}"},
        "ventas.comparacion_periodo": {"valor": f"{comparacion:.1f}%" if comparacion != float('inf') else t("mensajes.sin_datos"), "delta": None},
    }
    mostrar_kpi_cards(tarjetas)

    grafico_barras(ventas.ventas_por_vendedor(df_filtrado), "vendedor", "monto", "ventas.ventas_por_vendedor")
    grafico_barras(ventas.ventas_por_producto(df_filtrado), "producto", "monto", "ventas.ventas_por_producto")
    grafico_lineas(ventas.tendencia(df_filtrado, frecuencia="D"), "fecha", "monto", "ventas.tendencia_diaria")


def mostrar_inventario(inventario: DatosInventario, config: dict[str, Any]) -> None:
    st.subheader(t("inventario.titulo"))
    umbral = config.get("alertas", {}).get("stock_minimo", 10)
    bajo_stock = inventario.productos_bajo_stock(umbral)
    if not bajo_stock.empty:
        st.warning(t("inventario.alerta_bajo_stock", umbral=umbral))
    mostrar_tabla(inventario.df, "inventario.stock_actual")
    mostrar_tabla(bajo_stock, "inventario.productos_bajo_stock")
    mostrar_tabla(inventario.rotacion(), "inventario.rotacion")


def mostrar_productividad(productividad: DatosProductividad, df_filtrado: Any) -> None:
    pedidos_empleado = productividad.por_empleado(df_filtrado)
    tiempo_promedio = productividad.tiempo_promedio(df_filtrado)
    comparacion = productividad.comparacion_periodo(df_filtrado)
    tarjetas = {
        "productividad.pedidos_completados": {"valor": f"{pedidos_empleado['pedidos_completados'].sum():,.0f}"},
        "productividad.tiempo_promedio": {"valor": f"{tiempo_promedio:.1f} {t('productividad.minutos')}"},
        "productividad.comparacion_periodo": {"valor": f"{comparacion:.1f}%" if comparacion != float('inf') else t("mensajes.sin_datos"), "delta": None},
    }
    mostrar_kpi_cards(tarjetas)
    grafico_barras(pedidos_empleado, "empleado", "pedidos_completados", "productividad.pedidos_por_empleado")


def mostrar_exportacion(df: Any, nombre: str) -> None:
    if df is None or df.empty:
        return
    with st.expander(t("exportar.titulo")):
        datos_excel = exportar_excel(df, nombre)
        datos_pdf = exportar_pdf(df, "exportar.resumen")
        col1, col2 = st.columns(2)
        col1.download_button(
            t("exportar.a_excel"),
            data=datos_excel,
            file_name=f"{nombre}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_excel_{nombre}",
        )
        col2.download_button(
            t("exportar.a_pdf"),
            data=datos_pdf,
            file_name=f"{nombre}.pdf",
            mime="application/pdf",
            key=f"download_pdf_{nombre}",
        )


if __name__ == "__main__":
    main()
