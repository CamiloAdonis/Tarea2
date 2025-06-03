# scraper/scraper.py

import requests
import time
import json
import pymongo
from datetime import datetime
import os

LEFT   = -70.85
RIGHT  = -70.45
BOTTOM = -33.75
TOP    = -33.30

BASE_URL = "https://www.waze.com/live-map/api/georss"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.waze.com/es-419/live-map/"
}

MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))

client = pymongo.MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/")
db = client["waze"]
collection = db["eventos"]

def obtener_snapshot_georss():
    params = {
        "top": TOP,
        "bottom": BOTTOM,
        "left": LEFT,
        "right": RIGHT,
        "env": "row",
        "types": "alerts,traffic,users"
    }
    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
        print("Status code:", resp.status_code)
        if resp.status_code == 200:
            return resp.json()
        else:
            print("Error al pedir datos (código):", resp.status_code)
            return None
    except Exception as e:
        print("Excepción al solicitar datos:", e)
        return None

def recolectar_eventos_georss(cantidad_objetivo=10000, espera_segundos=5):
    eventos_totales = []
    intento = 0
    while len(eventos_totales) < cantidad_objetivo:
        intento += 1
        data = obtener_snapshot_georss()
        if data is None:
            print(f"[Intento {intento}] No se pudo obtener datos, reintentando en {espera_segundos}s…")
            time.sleep(espera_segundos)
            continue

        nuevos = []
        for clave in ("alerts", "traffic", "users"):
            if clave in data and isinstance(data[clave], list):
                nuevos.extend(data[clave])

        print(f"[Intento {intento}] Se obtuvieron {len(nuevos)} eventos nuevos.")
        eventos_totales.extend(nuevos)

        for evento in nuevos:
            evento['timestamp'] = datetime.utcnow()

        if nuevos:
            try:
                collection.insert_many(nuevos)
            except Exception as e:
                print(f"[Mongo] Error al insertar: {e}")

        if len(eventos_totales) >= cantidad_objetivo:
            break

        time.sleep(espera_segundos)

if __name__ == "__main__":
    META = int(os.getenv("META", "10000"))
    DELAY = int(os.getenv("DELAY", "5"))
    print(f"Iniciando recolección de {META} eventos (alerts+traffic+users)…\n")
    recolectar_eventos_georss(cantidad_objetivo=META, espera_segundos=DELAY)
    print(f"\n¡Listo! Datos almacenados en MongoDB.\n")
