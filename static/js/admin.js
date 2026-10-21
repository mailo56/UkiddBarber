// Pide confirmación antes de eliminar o cancelar algo en el panel.
// Un solo listener delegado: no hace falta tocar cada formulario.

document.addEventListener("submit", function (evento) {

    const accion = evento.target.getAttribute("action") || "";

    let mensaje = null;

    if (accion.includes("/eliminar/")) {
        mensaje = "¿Seguro que quieres eliminar este registro? " +
                  "Esta acción no se puede deshacer.";
    } else if (accion.includes("/cancelar/")) {
        mensaje = "¿Cancelar esta reserva? " +
                  "El horario volverá a quedar disponible.";
    }

    if (mensaje && !window.confirm(mensaje)) {
        evento.preventDefault();
    }

});
