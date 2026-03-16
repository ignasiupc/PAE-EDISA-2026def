# Detector ArUco 3D

Este proyecto queda reorganizado alrededor de `detector_3d.py`, que ahora es el
punto de entrada principal.

## Estructura actual

```text
detector_3d.py                 <- Aplicacion principal
config/markers_3d.json         <- Configuracion activa del panel ArUco
calibration/calibrar_camara.py <- Utilidad para recalibrar la camara
assets/detector_3d/svg/        <- Marcadores SVG del panel 4x4
docs/guia_aruco.ipynb          <- Material de apoyo
legacy/                        <- Sistema anterior y prototipos desplazados
```

## Archivos importantes para correr

- `detector_3d.py`
- `config/markers_3d.json`

El script lleva la matriz de camara y los coeficientes de distorsion embebidos,
asi que no depende de `camera_params.json` para arrancar.

## Ejecucion

```bash
pip install -r requirements.txt
python detector_3d.py
```

Si quieres cambiar la distribucion del panel o las etiquetas, edita
`config/markers_3d.json`.

## Calibracion

`calibration/calibrar_camara.py` guarda la salida en
`config/camera_calibration.json` para que luego puedas copiar los valores al
bloque `AppConfig` de `detector_3d.py`.

## Contenido legado

La carpeta `legacy/` conserva el flujo antiguo basado en `main.py`, `src/`,
configuracion de almacen y prototipos anteriores. Se ha dejado aparte para que
no interfiera con el trabajo centrado en `detector_3d.py`.
