# WP3

Estructura principal:

- `programa_unificado.py`: entrada unica para ejecutar los pipelines.
- `app/`: codigo del lanzador unificado.
- `config/`: dependencias y configuracion compartida.
- `docs/`: documentacion y notas de conexion.
- `modelos/`: modelos generales que no pertenecen a un pipeline concreto.
- `datos/`: datasets o fotos de entrada compartidas.
- `deteccion_cajas/`: detector de cajas. Sus entradas estan en `data/`, modelos en `models/` y resultados en `outputs/`.
- `volumetria/`: pipeline de volumetria. Sus entradas estan en `data/`, modelos en `models/` y resultados en `outputs/`.
- `cache/`: caches y artefactos generados.

Uso rapido:

```powershell
python programa_unificado.py --help
pip install -r config/requirements_unificado.txt
```
