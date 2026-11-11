# Conversor de unidades

Aplicación web en español para convertir longitud, masa, temperatura, volumen, superficie, tiempo y velocidad.

## Ejecutar

Desde la raíz del proyecto, activa el entorno virtual y ejecuta:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Abre [http://127.0.0.1:8000](http://127.0.0.1:8000) en el navegador. La API de conversión está disponible en `POST /api/convert` y el catálogo de unidades en `GET /api/units`.

Para instalar las dependencias en otro entorno:

```powershell
python -m pip install -r requirements.txt
```
