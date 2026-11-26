// Dónde está la web de Ojo Ciudadano.
//
// La portada prueba los servidores EN ESTE ORDEN y abre el primero que responde. Para cambiar
// de servidor basta con editar esta lista y subirla a GitHub: Cloudflare publica la
// portada nueva en menos de un minuto.
//
//   url     dirección pública del servidor, sin barra al final
//   nombre  solo para los mensajes y el registro de la consola
window.OC_SERVIDORES = [
  { url: "https://oc-origen.sourcia.solutions", nombre: "ordenador fijo" },
  // Reserva: se añade aquí cuando exista (por ejemplo, una copia en Streamlit Community Cloud).
  // { url: "https://ojo-ciudadano.streamlit.app", nombre: "reserva" },
];
