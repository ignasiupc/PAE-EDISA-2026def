# Sistema de Localizacion de Drones mediante ArUco en Almacen

Programa de vision por computadora que identifica marcadores ArUco instalados
en un almacen para que un dron se ubique a si mismo en tiempo real.

## Estructura del proyecto

```text
main.py                        <- Punto de entrada principal
src/                           <- Nucleo de la aplicacion
config/                        <- Configuracion activa del sistema
scripts/                       <- Utilidades del flujo principal
assets/markers/png/            <- Marcadores PNG listos para imprimir
assets/markers/svg/            <- SVG de referencia y prototipos
examples/                      <- Prototipos y pruebas que no usa main.py
examples/calibration/          <- Calibracion especifica de ejemplos
examples/config/               <- Configuracion de prototipos
notebooks/                     <- Material de apoyo y experimentacion
```

`main.py` y `src/` forman la aplicacion principal. El resto se separo como
soporte, recursos o ejemplos para que la raiz sea mas coherente.

## Instalacion rapida

```bash
pip install -r requirements.txt
```

## Flujo principal

### 1. Generar e imprimir los marcadores

```bash
python scripts/generate_markers.py --sheet
```

Genera un PNG por marcador y una hoja completa en `assets/markers/png/`.

### 2. Calibrar la camara

```bash
python -m src.camera_calibration --source 0 --output config/camera_params.json
```

Usa un tablero de ajedrez (9x6 cuadrados de 2.5 cm). Las capturas se guardan
automaticamente cuando el tablero permanece inmovil.

### 3. Configurar el almacen

Edita `config/warehouse_config.json` con las dimensiones reales y la posicion
exacta de cada marcador instalado en el almacen.

### 4. Ejecutar el sistema

```bash
python main.py --source 0
python main.py --source vuelo.mp4
python main.py --simulate
python main.py --simulate --save-log
```

Controles:

- `q`: salir.
- `r`: borrar la trayectoria del mapa.

## Ejemplos y material auxiliar

- `examples/` contiene detectores y pruebas independientes del flujo principal.
- `examples/calibration/calibrar_camara.py` es una utilidad pensada para los
  prototipos, no para `main.py`.
- `notebooks/guia_aruco.ipynb` agrupa explicaciones y ejercicios.

## Sistema de coordenadas

```text
        Y (Norte)
        ^
        |
O-------+---------- X (Este)
(0,0,0) |
        |
Origen: esquina inferior-izquierda del almacen
Z = altura (metros)
```

## Como funciona la localizacion

1. OpenCV detecta los marcadores ArUco en cada frame.
2. `solvePnP` estima la pose relativa camara-marcador.
3. Se invierte la transformacion para obtener la posicion del dron respecto al marcador.
4. Esa posicion se lleva al sistema mundo usando el mapa del almacen.
5. Si hay varios marcadores visibles, se fusionan las estimaciones.
6. El filtro de Kalman suaviza la trayectoria entre frames.
