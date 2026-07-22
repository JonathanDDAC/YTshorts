# Buscador de YouTube Shorts

Aplicación en Python (Flask) que busca Shorts de YouTube, los ordena por
número de vistas, y permite filtrar por idioma, país y fecha de publicación.

---

## 1. Requisitos previos

- Tener **Python instalado** (3.9 o superior). Verifícalo abriendo una
  terminal y escribiendo:
  ```
  python --version
  ```
  Si no lo tienes, descárgalo desde https://www.python.org/downloads/
  (al instalar, marca la casilla **"Add Python to PATH"**).

- Tener **Visual Studio Code** instalado, con la extensión oficial
  **"Python"** (de Microsoft) instalada desde el panel de Extensiones.

---

## 2. Abrir el proyecto en VS Code

1. Abre VS Code.
2. Ve a **Archivo → Abrir carpeta...** y selecciona la carpeta
   `youtube-shorts-app` (la que contiene este README).

---

## 3. Configurar tu API Key

1. Dentro de la carpeta del proyecto, busca el archivo **`.env.example`**.
2. Haz una copia de ese archivo y renómbrala a **`.env`** (sin el ".example").
   - En VS Code: clic derecho sobre `.env.example` → "Copiar" → clic derecho
     en la carpeta → "Pegar" → renombra la copia a `.env`.
3. Abre el archivo `.env` y reemplaza `PEGA_AQUI_TU_API_KEY` por la clave
   que copiaste de Google Cloud Console. Debe quedar así (con tu clave real):
   ```
   YOUTUBE_API_KEY=AIzaSyD1234567890ejemplo
   ```
4. Guarda el archivo.

---

## 4. Instalar las dependencias

Abre una terminal dentro de VS Code: menú **Terminal → Nueva terminal**.
Luego escribe (y presiona Enter después de cada línea):

```bash
pip install -r requirements.txt
```

Esto instala Flask y las librerías necesarias para hablar con YouTube.

---

## 5. Ejecutar la aplicación

En la misma terminal, escribe:

```bash
python app.py
```

Vas a ver un mensaje como:

```
Abre tu navegador en: http://127.0.0.1:5000
```

Abre esa dirección en tu navegador (Chrome, Edge, etc.) y ya puedes usar
la aplicación.

Para **detenerla**, vuelve a la terminal y presiona `Ctrl + C`.

---

## 6. Cómo usar la aplicación

1. Escribe un tema o palabra clave (por ejemplo: "recetas rápidas").
2. Opcional: escribe el código de país (ej: `CO` para Colombia, `US` para
   Estados Unidos, `ES` para España, `MX` para México).
3. Opcional: escribe el código de idioma (ej: `es`, `en`, `pt`).
4. Opcional: elige un rango de fechas de publicación.
5. Elige cuántos resultados quieres (máximo 50 por búsqueda).
6. Clic en **"Buscar Shorts"**.
7. Los resultados aparecen ordenados de mayor a menor número de vistas.
   Puedes cambiar el orden, o filtrar por idioma/país usando los
   controles que aparecen arriba de la tabla — esto no vuelve a
   consultar YouTube, es instantáneo.
8. Haz clic en cualquier título para abrir el video directamente en YouTube.

---

## Notas importantes

- **Cuota gratuita:** la API de YouTube te da 10.000 unidades gratis por
  día. Cada búsqueda gasta aproximadamente 100-150 unidades, así que
  puedes hacer decenas de búsquedas diarias sin costo.
- **¿Por qué a veces el país o idioma dicen "No especificado"?**
  No todos los creadores de contenido llenan esa información en YouTube,
  así que a veces YouTube simplemente no la tiene.
- El filtro de país (`regionCode`) le dice a YouTube "muéstrame lo popular
  en este país", pero no garantiza que el creador viva ahí. El país que
  se muestra en la tabla de resultados sí viene del perfil del canal.

---

## Estructura del proyecto

```
youtube-shorts-app/
├── app.py              → Backend en Flask (consulta la API de YouTube)
├── requirements.txt    → Lista de librerías necesarias
├── .env.example        → Plantilla para tu API Key
├── templates/
│   └── index.html      → Estructura de la página
└── static/
    ├── style.css        → Estilos visuales
    └── script.js        → Lógica del navegador (filtros, tabla, orden)
```
