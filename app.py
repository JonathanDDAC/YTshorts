"""
Aplicacion: Buscador de YouTube Shorts
----------------------------------------
Este archivo es el "cerebro" de la aplicacion. Levanta un servidor web
local (con Flask) que:
  1. Muestra la pagina (templates/index.html)
  2. Recibe busquedas desde esa pagina
  3. Le pregunta a YouTube (usando tu API Key) por videos Shorts
  4. Ordena y filtra los resultados
  5. Se los devuelve a la pagina para mostrarlos en una tabla

No necesitas entender cada linea para poder usarla, pero dejamos
comentarios en cada bloque para que puedas ir aprendiendo.
"""

import os
import re
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Carga la API Key desde el archivo .env (ver .env.example)
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

app = Flask(__name__)

# Duracion maxima (en segundos) para que un video cuente como "Short"
DURACION_MAXIMA_SHORT = 60


def parsear_duracion_iso8601(duracion_iso):
    """
    YouTube entrega la duracion en un formato raro, ej: 'PT45S' o 'PT1M5S'.
    Esta funcion la convierte a segundos normales (numero entero).
    """
    patron = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duracion_iso)
    if not patron:
        return 0
    horas = int(patron.group(1) or 0)
    minutos = int(patron.group(2) or 0)
    segundos = int(patron.group(3) or 0)
    return horas * 3600 + minutos * 60 + segundos


def formatear_fecha(fecha_iso):
    """Convierte '2026-07-10T12:00:00Z' en algo legible: '10/07/2026'."""
    try:
        fecha = datetime.strptime(fecha_iso, "%Y-%m-%dT%H:%M:%SZ")
        return fecha.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return fecha_iso


@app.route("/")
def index():
    """Muestra la pagina principal (el formulario y la tabla vacia)."""
    return render_template("index.html")


@app.route("/api/search")
def buscar_shorts():
    """
    Este es el endpoint que la pagina llama cuando el usuario da clic
    en "Buscar". Lee los filtros desde la URL y consulta YouTube.
    """
    if not API_KEY or API_KEY == "PEGA_AQUI_TU_API_KEY":
        return jsonify({
            "error": "No configuraste tu API Key todavia. "
                     "Revisa el archivo .env en la carpeta del proyecto."
        }), 400

    # --- 1. Leemos los filtros que mando la pagina web ---
    consulta = request.args.get("q", "").strip()
    region = request.args.get("region", "").strip().upper()   # ej: CO, US, ES
    idioma = request.args.get("language", "").strip().lower()  # ej: es, en
    fecha_desde = request.args.get("date_from", "").strip()    # YYYY-MM-DD
    fecha_hasta = request.args.get("date_to", "").strip()      # YYYY-MM-DD
    cantidad = request.args.get("max_results", "25")

    if not consulta:
        return jsonify({"error": "Escribe un tema o palabra clave para buscar."}), 400

    try:
        cantidad = max(1, min(int(cantidad), 50))  # YouTube permite maximo 50 por pagina
    except ValueError:
        cantidad = 25

    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)

        # --- 2. Armamos los parametros de busqueda ---
        parametros_busqueda = {
            "part": "snippet",
            "q": consulta,
            "type": "video",
            "videoDuration": "short",   # YouTube: videos de menos de 4 minutos
            "order": "viewCount",       # pedimos que ya vengan ordenados por vistas
            "maxResults": cantidad,
        }
        if region:
            parametros_busqueda["regionCode"] = region
        if idioma:
            parametros_busqueda["relevanceLanguage"] = idioma
        if fecha_desde:
            parametros_busqueda["publishedAfter"] = f"{fecha_desde}T00:00:00Z"
        if fecha_hasta:
            parametros_busqueda["publishedBefore"] = f"{fecha_hasta}T23:59:59Z"

        resultado_busqueda = youtube.search().list(**parametros_busqueda).execute()
        ids_videos = [item["id"]["videoId"] for item in resultado_busqueda.get("items", [])]

        if not ids_videos:
            return jsonify({"videos": []})

        # --- 3. Pedimos los detalles reales de cada video (vistas, duracion, etc) ---
        detalles = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(ids_videos)
        ).execute()

        # --- 4. Buscamos el pais de cada canal (para el filtro de pais) ---
        ids_canales = list({video["snippet"]["channelId"] for video in detalles.get("items", [])})
        paises_por_canal = {}
        if ids_canales:
            # La API solo acepta 50 canales por consulta, los pedimos en bloques
            for i in range(0, len(ids_canales), 50):
                bloque = ids_canales[i:i + 50]
                info_canales = youtube.channels().list(
                    part="snippet", id=",".join(bloque)
                ).execute()
                for canal in info_canales.get("items", []):
                    paises_por_canal[canal["id"]] = canal["snippet"].get("country", "")

        # --- 5. Armamos la lista final, solo con videos que SI son Shorts (<=60s) ---
        videos = []
        for item in detalles.get("items", []):
            duracion_segundos = parsear_duracion_iso8601(item["contentDetails"]["duration"])
            if duracion_segundos > DURACION_MAXIMA_SHORT:
                continue  # no es un short de verdad, lo saltamos

            snippet = item["snippet"]
            estadisticas = item.get("statistics", {})
            video_id = item["id"]

            videos.append({
                "titulo": snippet.get("title", "(sin titulo)"),
                "canal": snippet.get("channelTitle", ""),
                "link": f"https://www.youtube.com/shorts/{video_id}",
                "miniatura": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                "vistas": int(estadisticas.get("viewCount", 0)),
                "fecha_publicacion": formatear_fecha(snippet.get("publishedAt", "")),
                "fecha_iso": snippet.get("publishedAt", ""),
                "idioma": snippet.get("defaultAudioLanguage") or snippet.get("defaultLanguage") or "No especificado",
                "pais": paises_por_canal.get(snippet.get("channelId"), "") or "No especificado",
                "duracion_segundos": duracion_segundos,
            })

        # --- 6. Ordenamos de mayor a menor numero de vistas ---
        videos.sort(key=lambda v: v["vistas"], reverse=True)

        return jsonify({"videos": videos})

    except HttpError as error:
        mensaje = "Ocurrio un error consultando YouTube."
        if error.resp.status == 403:
            mensaje = ("Tu API Key no tiene permisos o se acabo la cuota diaria gratuita. "
                       "Intenta de nuevo manana o revisa la consola de Google Cloud.")
        return jsonify({"error": mensaje}), 500
    except Exception as error:
        return jsonify({"error": f"Error inesperado: {str(error)}"}), 500


if __name__ == "__main__":
    print("\n Abre tu navegador en: http://127.0.0.1:5000 \n")
    app.run(debug=True)
