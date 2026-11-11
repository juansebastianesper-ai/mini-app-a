from __future__ import annotations

import math
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

UNITS = {
    "longitud": {
        "label": "Longitud",
        "units": {
            "mm": {"label": "Milímetro (mm)", "factor": 0.001},
            "cm": {"label": "Centímetro (cm)", "factor": 0.01},
            "m": {"label": "Metro (m)", "factor": 1},
            "km": {"label": "Kilómetro (km)", "factor": 1000},
            "in": {"label": "Pulgada (in)", "factor": 0.0254},
            "ft": {"label": "Pie (ft)", "factor": 0.3048},
            "yd": {"label": "Yarda (yd)", "factor": 0.9144},
            "mi": {"label": "Milla (mi)", "factor": 1609.344},
        },
    },
    "masa": {
        "label": "Masa",
        "units": {
            "mg": {"label": "Miligramo (mg)", "factor": 0.000001},
            "g": {"label": "Gramo (g)", "factor": 0.001},
            "kg": {"label": "Kilogramo (kg)", "factor": 1},
            "t": {"label": "Tonelada métrica (t)", "factor": 1000},
            "oz": {"label": "Onza (oz)", "factor": 0.028349523125},
            "lb": {"label": "Libra (lb)", "factor": 0.45359237},
        },
    },
    "temperatura": {
        "label": "Temperatura",
        "units": {
            "C": {"label": "Celsius (°C)"},
            "F": {"label": "Fahrenheit (°F)"},
            "K": {"label": "Kelvin (K)"},
        },
    },
    "volumen": {
        "label": "Volumen",
        "units": {
            "ml": {"label": "Mililitro (ml)", "factor": 0.001},
            "l": {"label": "Litro (l)", "factor": 1},
            "m3": {"label": "Metro cúbico (m³)", "factor": 1000},
            "tsp": {"label": "Cucharadita (US)", "factor": 0.00492892159375},
            "tbsp": {"label": "Cucharada (US)", "factor": 0.01478676478125},
            "cup": {"label": "Taza (US)", "factor": 0.2365882365},
            "gal": {"label": "Galón (US)", "factor": 3.785411784},
        },
    },
    "superficie": {
        "label": "Superficie",
        "units": {
            "cm2": {"label": "Centímetro cuadrado (cm²)", "factor": 0.0001},
            "m2": {"label": "Metro cuadrado (m²)", "factor": 1},
            "ha": {"label": "Hectárea (ha)", "factor": 10000},
            "km2": {"label": "Kilómetro cuadrado (km²)", "factor": 1000000},
            "ft2": {"label": "Pie cuadrado (ft²)", "factor": 0.09290304},
            "acre": {"label": "Acre", "factor": 4046.8564224},
        },
    },
    "tiempo": {
        "label": "Tiempo",
        "units": {
            "ms": {"label": "Milisegundo (ms)", "factor": 0.001},
            "s": {"label": "Segundo (s)", "factor": 1},
            "min": {"label": "Minuto (min)", "factor": 60},
            "h": {"label": "Hora (h)", "factor": 3600},
            "d": {"label": "Día (d)", "factor": 86400},
            "wk": {"label": "Semana", "factor": 604800},
        },
    },
    "velocidad": {
        "label": "Velocidad",
        "units": {
            "m/s": {"label": "Metros por segundo (m/s)", "factor": 1},
            "km/h": {"label": "Kilómetros por hora (km/h)", "factor": 1 / 3.6},
            "mph": {"label": "Millas por hora (mph)", "factor": 0.44704},
            "kn": {"label": "Nudos (kn)", "factor": 0.514444},
        },
    },
}

app = FastAPI(title="Conversor de unidades", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class ConversionRequest(BaseModel):
    category: str
    from_unit: str
    to_unit: str
    value: Annotated[float, Field(allow_inf_nan=False)]


def convert_value(category: str, from_unit: str, to_unit: str, value: float) -> float:
    definition = UNITS.get(category)
    if definition is None:
        raise HTTPException(status_code=422, detail="La categoría no es válida.")

    units = definition["units"]
    if from_unit not in units or to_unit not in units:
        raise HTTPException(status_code=422, detail="La unidad no es válida para esta categoría.")

    if category == "temperatura":
        to_celsius = {
            "C": lambda number: number,
            "F": lambda number: (number - 32) * 5 / 9,
            "K": lambda number: number - 273.15,
        }
        celsius_value = to_celsius[from_unit](value)
        if celsius_value < -273.15:
            raise HTTPException(
                status_code=422,
                detail="La temperatura no puede ser inferior al cero absoluto.",
            )
        from_celsius = {
            "C": lambda number: number,
            "F": lambda number: number * 9 / 5 + 32,
            "K": lambda number: number + 273.15,
        }
        result = from_celsius[to_unit](celsius_value)
    else:
        result = value * units[from_unit]["factor"] / units[to_unit]["factor"]

    if not math.isfinite(result):
        raise HTTPException(status_code=422, detail="El resultado está fuera del rango permitido.")
    return result


@app.get("/")
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/units")
def get_units() -> dict:
    return UNITS


@app.post("/api/convert")
def convert(request: ConversionRequest) -> dict:
    result = convert_value(
        request.category, request.from_unit, request.to_unit, request.value
    )
    return {"value": result}
