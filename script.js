// ============================================
// Variables globales
// ============================================
let todosLosVideos = [];   // guarda TODOS los resultados que llegaron del servidor

const form = document.getElementById("form-busqueda");
const contenedorResultados = document.getElementById("resultados");
const controlesResultado = document.getElementById("controles-resultado");
const mensajeError = document.getElementById("mensaje-error");
const mensajeCargando = document.getElementById("mensaje-cargando");
const mensajeVacio = document.getElementById("mensaje-vacio");
const contadorResultados = document.getElementById("contador-resultados");
const selectIdioma = document.getElementById("filtro-idioma");
const selectPais = document.getElementById("filtro-pais");
const selectOrden = document.getElementById("orden-vistas");

// ============================================
// Cuando el usuario envía el formulario de búsqueda
// ============================================
form.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  ocultarMensajes();
  mensajeCargando.hidden = false;
  controlesResultado.hidden = true;
  contenedorResultados.innerHTML = "";

  const datos = new FormData(form);
  const parametros = new URLSearchParams();
  for (const [clave, valor] of datos.entries()) {
    if (valor) parametros.append(clave, valor);
  }

  try {
    const respuesta = await fetch(`/api/search?${parametros.toString()}`);
    const cuerpo = await respuesta.json();

    mensajeCargando.hidden = true;

    if (!respuesta.ok) {
      mostrarError(cuerpo.error || "Ocurrió un error al buscar.");
      return;
    }

    todosLosVideos = cuerpo.videos || [];

    if (todosLosVideos.length === 0) {
      mensajeVacio.hidden = false;
      return;
    }

    prepararFiltros(todosLosVideos);
    controlesResultado.hidden = false;
    dibujarTabla(todosLosVideos);

  } catch (error) {
    mensajeCargando.hidden = true;
    mostrarError("No se pudo conectar con el servidor. ¿Está corriendo app.py?");
  }
});

// ============================================
// Filtros y orden (se aplican sobre lo que ya tenemos, sin volver a llamar a YouTube)
// ============================================
selectIdioma.addEventListener("change", aplicarFiltros);
selectPais.addEventListener("change", aplicarFiltros);
selectOrden.addEventListener("change", aplicarFiltros);

function aplicarFiltros() {
  let lista = [...todosLosVideos];

  if (selectIdioma.value) {
    lista = lista.filter(v => v.idioma === selectIdioma.value);
  }
  if (selectPais.value) {
    lista = lista.filter(v => v.pais === selectPais.value);
  }

  lista.sort((a, b) => selectOrden.value === "asc" ? a.vistas - b.vistas : b.vistas - a.vistas);

  dibujarTabla(lista);
}

function prepararFiltros(videos) {
  const idiomas = [...new Set(videos.map(v => v.idioma))].sort();
  const paises = [...new Set(videos.map(v => v.pais))].sort();

  selectIdioma.innerHTML = '<option value="">Todos</option>' +
    idiomas.map(i => `<option value="${i}">${i}</option>`).join("");

  selectPais.innerHTML = '<option value="">Todos</option>' +
    paises.map(p => `<option value="${p}">${p}</option>`).join("");

  selectOrden.value = "desc";
}

// ============================================
// Dibuja la tabla de resultados en pantalla
// ============================================
function dibujarTabla(videos) {
  contadorResultados.textContent = `${videos.length} video${videos.length === 1 ? "" : "s"}`;

  if (videos.length === 0) {
    contenedorResultados.innerHTML = "";
    mensajeVacio.hidden = false;
    return;
  }
  mensajeVacio.hidden = true;

  const filas = videos.map(v => `
    <tr>
      <td><img class="miniatura-video" src="${v.miniatura}" alt="Miniatura de ${escaparHtml(v.titulo)}" loading="lazy"></td>
      <td class="titulo-video">
        <a href="${v.link}" target="_blank" rel="noopener noreferrer">${escaparHtml(v.titulo)}</a>
        <span class="canal">${escaparHtml(v.canal)}</span>
      </td>
      <td class="vistas">${formatearNumero(v.vistas)}</td>
      <td>${v.fecha_publicacion}</td>
      <td><span class="etiqueta">${escaparHtml(v.idioma)}</span></td>
      <td><span class="etiqueta">${escaparHtml(v.pais)}</span></td>
      <td>${v.duracion_segundos}s</td>
    </tr>
  `).join("");

  contenedorResultados.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Miniatura</th>
          <th>Título / Canal</th>
          <th>Vistas</th>
          <th>Publicado</th>
          <th>Idioma</th>
          <th>País</th>
          <th>Duración</th>
        </tr>
      </thead>
      <tbody>${filas}</tbody>
    </table>
  `;
}

// ============================================
// Utilidades pequeñas
// ============================================
function formatearNumero(numero) {
  if (numero >= 1_000_000) return (numero / 1_000_000).toFixed(1).replace(".0", "") + "M";
  if (numero >= 1_000) return (numero / 1_000).toFixed(1).replace(".0", "") + "K";
  return String(numero);
}

function escaparHtml(texto) {
  const div = document.createElement("div");
  div.textContent = texto || "";
  return div.innerHTML;
}

function mostrarError(texto) {
  mensajeError.textContent = texto;
  mensajeError.hidden = false;
}

function ocultarMensajes() {
  mensajeError.hidden = true;
  mensajeVacio.hidden = true;
  mensajeCargando.hidden = true;
}
