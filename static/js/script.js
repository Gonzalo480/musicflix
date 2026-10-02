setTimeout(function () {

    const mensajes = document.querySelectorAll(".mensaje");

    mensajes.forEach(function (mensaje) {

        mensaje.style.opacity = "0";

        setTimeout(function () {
            mensaje.remove();
        }, 500);

    });

}, 3000);