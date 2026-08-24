# Dashboard KPIs

Tablero de control con los KPIs de **Ventas**, **Inventario** y **Productividad** de tu negocio, con gráficos, filtros, exportación a Excel/PDF y soporte para Español, English y 日本語.

Esta guía está pensada para que **cualquier persona, sin conocimientos técnicos**, pueda descargar, instalar y usar la aplicación.

---

## 📥 Cómo descargar e instalar la app (recomendado)

Esta es la forma más simple: instala el programa como cualquier otro programa de Windows, con su ícono en el escritorio.

1. **Descarga el instalador**: pide a quien te compartió el proyecto el archivo `DashboardKPIsInstaller.exe` (se genera dentro de la carpeta `installer/Output/`).
2. Haz **doble clic** en `DashboardKPIsInstaller.exe`.
3. Si Windows muestra una advertencia de "Editor desconocido" (SmartScreen), haz clic en **Más información** y luego en **Ejecutar de todas formas**. Esto es normal en programas que no están firmados digitalmente.
4. Sigue los pasos del instalador (Siguiente → Siguiente → Instalar).
5. Al finalizar, marca la casilla **"Launch Dashboard KPIs"** y haz clic en **Finalizar**. También puedes abrir la app luego desde el ícono que quedó en el **Escritorio** o en el **Menú Inicio**.
6. Espera unos segundos: se abrirá tu navegador automáticamente mostrando el panel.

> Para desinstalar, ve a **Configuración → Aplicaciones → Dashboard KPIs → Desinstalar**, como cualquier otro programa.

---

## 📁 Cómo descargar e instalar la app (sin instalador)

Si en cambio recibiste la carpeta completa del proyecto (por ejemplo `dashboard-kpis.zip`):

1. Descomprime el archivo `.zip` en cualquier carpeta de tu computadora (por ejemplo, en `Documentos`).
2. Entra a la carpeta `dashboard-kpis`.
3. Haz **doble clic en `run_app.bat`**.

Ese archivo automáticamente:
- revisa que tengas Python instalado,
- crea un entorno aislado para la app (`.venv`) la primera vez,
- instala todo lo necesario,
- abre la app en tu navegador.

La primera vez puede tardar 1-2 minutos (está instalando). Las siguientes veces abrirá casi de inmediato.

> **NO CIERRES** la ventana negra que se abre mientras usas la app: ahí es donde corre el programa. Para cerrar la app, simplemente cierra esa ventana.

### Requisito: tener Python instalado

Si al hacer doble clic en `run_app.bat` aparece un error diciendo que no se encontró Python:

1. Ve a [python.org/downloads](https://www.python.org/downloads/) y descarga la última versión (3.11 o superior).
2. Durante la instalación, **marca la casilla "Add Python to PATH"** antes de darle a instalar. Este paso es muy importante.
3. Vuelve a hacer doble clic en `run_app.bat`.

---

## 🖥️ Usando la aplicación

### Primera vez que la abres

Verás una pantalla de bienvenida con dos opciones:

- **Subir tu archivo de ventas** (Excel `.xlsx` o CSV) arrastrándolo o haciendo clic para seleccionarlo.
- **"¿No tienes un archivo a mano? Prueba con datos de ejemplo"**, para ver la app funcionando con datos de muestra.

Si subes tu propio archivo, la app te ayudará a indicar qué columna corresponde a qué dato (fecha, vendedor, producto, monto, etc.) antes de continuar.

### Navegación

En la barra lateral izquierda encontrarás:

- **Pestañas**: `Ventas`, `Inventario`, `Productividad`.
- **🔄 Reiniciar aplicación**: borra todo y vuelve al inicio (útil si algo se ve raro).
- **Cargar otro archivo**: vuelve a la pantalla de carga para usar otro archivo.
- **Selector de idioma**: Español, English, 日本語.
- **Modo oscuro/claro**.
- **Filtros generales**: fecha, vendedor, producto, empleado.

### Descargar informes

Dentro de cada pestaña hay un panel **"Exportar vista"** con botones para descargar los datos filtrados en **Excel** o **PDF**.

---

## 📊 Usar tus propios datos

Puedes cargar tus datos de dos formas:

### Opción A: Desde la app (recomendada, no requiere tocar archivos)

Usa el botón **"Cargar otro archivo"** en la barra lateral y sube tu Excel/CSV siguiendo el asistente de columnas.

### Opción B: Reemplazando los archivos de ejemplo

1. Ve a la carpeta `data/ejemplo/` dentro del proyecto.
2. Reemplaza (o edita) los archivos `ventas.xlsx`, `inventario.xlsx` y `productividad.xlsx` con tus propios datos, respetando las columnas esperadas:

| Archivo | Columnas esperadas |
|---|---|
| `ventas` | `fecha`, `vendedor`, `producto`, `monto` |
| `inventario` | `producto`, `stock_actual` (opcional: `ventas_unidades`) |
| `productividad` | `fecha`, `empleado`, `pedidos_completados`, `tiempo_proceso_min` |

3. Cierra y vuelve a abrir la aplicación para ver los cambios.

> Si prefieres usar otra carpeta, cambia la línea `ruta:` dentro de `config/config.yaml` (sección `fuente_datos`) para que apunte a tu carpeta, por ejemplo `data/mis_datos`.

---

## 🌐 Cambiar el idioma o el nombre de la empresa

Abre `config/config.yaml` con el Bloc de notas y edita:

```yaml
empresa:
  nombre: "Nombre de tu empresa"

idioma_default: "es"   # "es", "en" o "ja"
```

---

## 🛠️ Solución de problemas comunes

| Problema | Qué hacer |
|---|---|
| Windows SmartScreen bloquea el instalador | Clic en "Más información" → "Ejecutar de todas formas" |
| `run_app.bat` dice que no encuentra Python | Instala Python desde python.org marcando "Add Python to PATH" |
| La app quedó "trabada" o se ve un error raro | Usa el botón **🔄 Reiniciar aplicación** en la barra lateral |
| El navegador no se abrió solo | Copia la dirección que aparece en la ventana (ej. `http://localhost:8501`) y pégala en tu navegador |
| Ya hay una app corriendo en ese puerto | Cierra la ventana anterior de la app antes de abrir una nueva |

Los errores inesperados quedan registrados en `logs/errores.log`, por si necesitas compartirlos para pedir ayuda.

---

## 👩‍💻 Para desarrolladores: generar el instalador desde el código

Si tienes el código fuente y quieres generar tú mismo el `.exe` y el instalador:

### 1. Preparar el entorno de desarrollo

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

### 2. Instalar Inno Setup (solo para el instalador)

Descarga e instala [Inno Setup](https://jrsoftware.org/isdl.php) (versión 6). El script de build lo detecta automáticamente si está instalado en la ruta por defecto o en el `PATH`.

### 3. Ejecutar el build

```powershell
.\build.bat
```

Este script:
1. Genera el ícono de la app (`assets/icono.ico`).
2. Empaqueta la app en un único ejecutable con PyInstaller (`dist/DashboardKPIs.exe`).
3. Compila el instalador con Inno Setup (`installer/Output/DashboardKPIsInstaller.exe`), si Inno Setup está disponible.

Si Inno Setup no está instalado, el script te avisará y podrás compilar manualmente abriendo `installer/instalador.iss` con la aplicación Inno Setup y presionando **Compile**.

### Estructura del proyecto

```
dashboard-kpis/
├── src/                    # Código de la aplicación (Streamlit)
├── build/launcher.py       # Punto de entrada usado al empaquetar con PyInstaller
├── config/config.yaml      # Configuración de la app (empresa, idioma, origen de datos)
├── locales/                # Traducciones (es, en, ja)
├── data/ejemplo/           # Datos de muestra
├── assets/                 # CSS, ícono
├── installer/              # Script de Inno Setup
├── run_app.bat             # Inicio con un doble clic (modo desarrollo/portable)
├── build.bat                # Genera el ejecutable e instalador
├── requirements.txt          # Dependencias para ejecutar la app
└── requirements-dev.txt       # Dependencias adicionales para empaquetar (PyInstaller, Pillow)
```


