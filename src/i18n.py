import json
from pathlib import Path
from typing import Any

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
DEFAULT_LANG = "es"

class I18n:
    """Carga traducciones desde archivos JSON y ofrece acceso con t(key)."""

    def __init__(self, idioma: str = DEFAULT_LANG) -> None:
        self.idioma = idioma
        self.textos = self._cargar_idioma(idioma)

    def _cargar_idioma(self, idioma: str) -> dict[str, Any]:
        archivo = LOCALES_DIR / f"{idioma}.json"
        if not archivo.exists():
            archivo = LOCALES_DIR / f"{DEFAULT_LANG}.json"
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)

    def cambiar_idioma(self, idioma: str) -> None:
        self.idioma = idioma
        self.textos = self._cargar_idioma(idioma)

    def t(self, clave: str, **kwargs: Any) -> str:
        partes = clave.split(".")
        valor: Any = self.textos
        for parte in partes:
            if isinstance(valor, dict) and parte in valor:
                valor = valor[parte]
            else:
                # Try fallback to default language (Spanish)
                if self.idioma != DEFAULT_LANG:
                    try:
                        with open(LOCALES_DIR / f"{DEFAULT_LANG}.json", "r", encoding="utf-8") as f:
                            default_texts = json.load(f)
                        v = default_texts
                        for p in partes:
                            if isinstance(v, dict) and p in v:
                                v = v[p]
                            else:
                                v = None
                                break
                        if isinstance(v, str):
                            resultado = str(v)
                            if kwargs:
                                try:
                                    resultado = resultado.format(**kwargs)
                                except Exception:
                                    pass
                            return resultado
                    except Exception:
                        pass
                # final fallback: human-friendly text in Spanish
                human = clave.replace("_", " ").replace(".", " ").capitalize()
                return human
        resultado = str(valor)
        if kwargs:
            try:
                resultado = resultado.format(**kwargs)
            except Exception:
                pass
        return resultado

    def __call__(self, clave: str, **kwargs: Any) -> str:
        return self.t(clave, **kwargs)

_i18n_instance: I18n | None = None


def get_i18n(idioma: str | None = None) -> I18n:
    global _i18n_instance
    if _i18n_instance is None or idioma:
        idioma = idioma or DEFAULT_LANG
        _i18n_instance = I18n(idioma)
    return _i18n_instance


def t(clave: str, **kwargs: Any) -> str:
    return get_i18n().t(clave, **kwargs)


def _extract_keys_from_source(src_dir: Path) -> set:
    import re
    keys: set = set()
    # negative lookbehind avoids matching "get(", "format(", "self.t(" etc. as false positives
    pattern = re.compile(r"(?<![a-zA-Z0-9_.])t\(\s*[\"']([a-zA-Z0-9_\.\-]+)[\"']")
    for py in Path(src_dir).rglob("*.py"):
        try:
            text = py.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in pattern.finditer(text):
            keys.add(m.group(1))
    return keys


def validate_translation_keys(src_root: str | None = None) -> None:
    """Print missing translation keys per locale to console for developers.

    Call this in development to see which keys are missing in each locale.
    """
    src_root = Path(src_root or Path(__file__).resolve().parent.parent / "src")
    used = _extract_keys_from_source(src_root)
    locales = list(LOCALES_DIR.glob("*.json"))
    for loc in locales:
        try:
            data = json.loads(loc.read_text(encoding="utf-8"))
        except Exception:
            print(f"[i18n] Could not read locale {loc.name}")
            continue
        missing = []
        for key in sorted(used):
            parts = key.split(".")
            # skip invalid keys like "." or keys with empty segments
            if any(p == "" for p in parts):
                continue
            v = data
            ok = True
            for p in parts:
                if isinstance(v, dict) and p in v:
                    v = v[p]
                else:
                    ok = False
                    break
            if not ok:
                missing.append(key)
        if missing:
            print(f"[i18n] Missing {len(missing)} keys in {loc.name}:")
            for k in missing:
                print(f"  - {k}")
