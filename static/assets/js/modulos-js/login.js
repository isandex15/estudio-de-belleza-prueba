console.log("abrio login");

document.addEventListener('DOMContentLoaded', function () {
 

    $('#formRegistrarCliente').on('submit', function (e) {
        e.preventDefault();
        if (!$('#formRegistrarCliente').parsley().validate()) return;
        $.ajax({
            url: '/admin?ruta=cliente',
            type: 'POST',
            data: $(this).serialize(),
            dataType: 'json',
            success: function (res) {
                Swal.fire({
                    icon: res.icon,
                    title: res.title,
                    text: res.text,
                    showConfirmButton: true,
                    confirmButtonText: 'Aceptar',
                    timer: 2000,
                    timerProgressBar: true
                }).then(() => {
                    if (res.icon === 'success') {
                        $('#formRegistrarCliente')[0].reset();
                        $('#formRegistrarCliente').parsley().reset();
                        document.getElementById('back-to-login-register').click();
                    }
                });
            },
            error: function (xhr, status, error) {
                console.log("========== ERROR AJAX ==========");
                console.log("HTTP:", xhr.status);
                console.log("Status:", status);
                console.log("Error:", error);
                console.log("Respuesta:", xhr.responseText);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error.'
                });
            }
        });
    });

    $('#resetPasswordForm').on('submit', function (e) {
        e.preventDefault();
        const pass = $('#newPassword').val();
        const confirm = $('#confirmPassword').val();

        if (pass !== confirm) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Las contraseñas no coinciden'
            });
            return;
        }

        $.ajax({
            url: '/admin?ruta=login',
            type: 'POST',
            data: $(this).serialize(),
            dataType: 'json',
            success: function (res) {
                Swal.fire({
                    icon: res.icon,
                    title: res.title,
                    text: res.text
                });

                if (res.icon === 'success') {
                    $('#resetPasswordForm')[0].reset();
                    $('#back-to-login-reset').click();
                }
            },
            error: function () {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error en el servidor'
                });
            }
        });
    });

    const registrarceLink = document.getElementById('registrarce-link');
    const backToLoginResetButton = document.getElementById('back-to-login-reset');
    const backToLoginRegisterButton = document.getElementById('back-to-login-register');
    const forgotPasswordLink = document.getElementById('forgot-password-link');

    if (registrarceLink) {
        registrarceLink.addEventListener('click', function (e) {
            e.preventDefault();
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('resetPasswordContainer').style.display = 'none';
            document.getElementById('registerContainer').style.display = 'block';
        });
    }

    if (backToLoginResetButton) {
        backToLoginResetButton.addEventListener('click', function () {
            document.getElementById('resetPasswordContainer').style.display = 'none';
            document.getElementById('registerContainer').style.display = 'none';
            document.getElementById('loginForm').style.display = 'block';
        });
    }

    if (backToLoginRegisterButton) {
        backToLoginRegisterButton.addEventListener('click', function () {
            document.getElementById('resetPasswordContainer').style.display = 'none';
            document.getElementById('registerContainer').style.display = 'none';
            document.getElementById('loginForm').style.display = 'block';
        });
    }

    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function (e) {
            e.preventDefault();
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('registerContainer').style.display = 'none';
            document.getElementById('resetPasswordContainer').style.display = 'block';
        });
    }

    function limpiarResetPassword() {
        const form = $('#resetPasswordForm');
        form[0].reset();
        form.parsley().reset();
        $('#resetPasswordForm').find('.is-invalid, .is-valid').removeClass('is-invalid is-valid');
        $('#resetPasswordForm .parsley-errors-list').remove();
    }

    function togglePasswordVisibility(toggleId, inputId, iconId) {
        const toggle = document.getElementById(toggleId);

        if (toggle) {
            toggle.addEventListener('click', function () {
                const input = document.getElementById(inputId);
                const icon = document.getElementById(iconId);

                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        }
    }

    togglePasswordVisibility('toggle-login-password', 'login-password', 'eye-icon-login');
    togglePasswordVisibility('toggle-new-password', 'newPassword', 'eye-icon-new');
    togglePasswordVisibility('toggle-confirm-password', 'confirmPassword', 'eye-icon-confirm');
    togglePasswordVisibility('toggle-register-password', 'register-password', 'eye-icon-register');

    const form = document.getElementById('formRegistrarCliente');

    function mostrarError(input, mensaje) {
        ocultarError(input);

        const error = document.createElement('div');
        error.className = 'error-message';
        error.style.color = 'red';
        error.innerText = mensaje;

        input.parentNode.insertBefore(error, input.nextSibling);
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
    }

    function ocultarError(input) {
        const error = input.parentNode.querySelector('.error-message');

        if (error) {
            error.remove();
        }

        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    }

    function validarLetras(event) {
        const input = event.target;
        const valorOriginal = input.value;
        const valor = valorOriginal.replace(/[^a-zA-ZñÑáéíóúÁÉÍÓÚ]/g, '');

        input.value = valor;

        if (valorOriginal !== valor) {
            mostrarError(input, 'Solo se permiten letras.');
        } else if (valor === '') {
            mostrarError(input, 'Solo se permiten letras.');
        } else {
            ocultarError(input);
        }
    }

    function validarNumeros(event) {
        const input = event.target;
        const valorOriginal = input.value;
        const valor = valorOriginal.replace(/[^0-9]/g, '');

        input.value = valor;

        if (valorOriginal !== valor) {
            mostrarError(input, 'Solo se permiten números.');
        } else if (valor === '') {
            mostrarError(input, 'Solo se permiten números.');
        } else {
            ocultarError(input);
        }
    }

    function validarCorreo(event) {
        const input = event.target;
        const valorOriginal = input.value;
        const valor = valorOriginal.replace(/[^a-zA-Z0-9ñÑ._%+\-@]/g, '');

        input.value = valor;

        const regexCorreo = /^[a-zA-Z0-9ñÑ._%+\-]+@[a-zA-Z0-9ñÑ.-]+\.[a-zA-Z]{2,}$/;

        if (valorOriginal !== valor) {
            mostrarError(input, 'Caracter no permitido en el correo.');
        } else if (valor === '') {
            mostrarError(input, 'El correo es obligatorio.');
        } else if (!regexCorreo.test(valor)) {
            mostrarError(input, 'Formato de correo no válido.');
        } else {
            ocultarError(input);
        }
    }

    function validarContraseña(event) {
        const input = event.target;

        if (input.value.length < 6) {
            mostrarError(input, 'La contraseña debe tener al menos 6 caracteres.');
        } else {
            ocultarError(input);
        }
    }

    if (form) {
        const cedulaReg = document.getElementById('cedula_reg');
        const correoReg = document.getElementById('correo_reg');
        const telefonoReg = document.getElementById('telefono_reg');
        const nombreUsuarioReg = document.getElementById('nombre_usuario_reg');
        const apellidoUsuarioReg = document.getElementById('apellido_usuario_reg');
        const registerPassword = document.getElementById('register-password');

        if (cedulaReg) {
            cedulaReg.addEventListener('input', validarNumeros);
        }

        if (correoReg) {
            correoReg.addEventListener('input', validarCorreo);
        }

        if (telefonoReg) {
            telefonoReg.addEventListener('input', validarNumeros);
        }

        if (nombreUsuarioReg) {
            nombreUsuarioReg.addEventListener('input', validarLetras);
        }

        if (apellidoUsuarioReg) {
            apellidoUsuarioReg.addEventListener('input', validarLetras);
        }

        if (registerPassword) {
            registerPassword.addEventListener('input', validarContraseña);
        }
    }

    const cedulaInput = document.getElementById('reset-cedula');

    if (cedulaInput) {
        const errorContainer = document.createElement('div');
        errorContainer.style.color = 'red';
        errorContainer.style.marginTop = '5px';
        errorContainer.style.fontSize = '0.9rem';
        errorContainer.style.display = 'none';

        cedulaInput.parentNode.appendChild(errorContainer);

        cedulaInput.addEventListener('input', function (event) {
            const input = event.target;
            const valorOriginal = input.value;
            const valorFiltrado = valorOriginal.replace(/[^0-9]/g, '');

            if (valorOriginal !== valorFiltrado) {
                input.value = valorFiltrado;
                errorContainer.innerText = 'Solo se permiten números';
                errorContainer.style.display = 'block';
            } else {
                errorContainer.innerText = '';
                errorContainer.style.display = 'none';
            }
        });
    }

    const regexRol = /^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]+$/;
    const regexNoPermitidosRol = /[^a-zA-ZÁÉÍÓÚáéíóúñÑ\s]/g;

    $('#formRol input, #formEditRol input').on('input', function () {
        const originalValue = this.value;
        this.value = this.value.replace(regexNoPermitidosRol, '');

        if (this.value !== originalValue) {
            $(this).addClass('is-invalid').removeClass('is-valid');

            if ($(this).next('.invalid-feedback').length === 0) {
                $(this).after('<div class="invalid-feedback">En este campo solo se permiten letras.</div>');
            } else {
                $(this).next('.invalid-feedback').text('En este campo solo se permiten letras.').show();
            }
        } else {
            $(this).removeClass('is-invalid').addClass('is-valid');
            $(this).next('.invalid-feedback').hide();
        }
    });

    if (window.Parsley) {
        window.Parsley.on('field:error', function () {
            this.$element.addClass('is-invalid').removeClass('is-valid');

            if (this.$element.next('.invalid-feedback').length === 0) {
                this.$element.after('<div class="invalid-feedback">' + this.getErrorsMessages()[0] + '</div>');
            } else {
                this.$element.next('.invalid-feedback').text(this.getErrorsMessages()[0]).show();
            }
        });

        window.Parsley.on('field:success', function () {
            this.$element.removeClass('is-invalid').addClass('is-valid');
            this.$element.next('.invalid-feedback').hide();
        });
    }

    $('#back-to-login-register').on('click', function () {
        const form = $('#formRegistrarCliente');

        form.find('.is-invalid, .is-valid').removeClass('is-invalid is-valid');
        form.find('.invalid-feedback').remove();

        form.find('input, textarea, select').each(function () {
            const type = $(this).attr('type');

            if (type === 'checkbox' || type === 'radio') {
                $(this).prop('checked', false);
            } else {
                $(this).val('');
            }
        });
    });
    // ================== captcha ==================
    let captchaValor = "";

    function generarCaptcha() {
        const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
        let texto = "";

        for (let i = 0; i < 5; i++) {
            texto += chars.charAt(Math.floor(Math.random() * chars.length));
        }

        captchaValor = texto;

        let html = "";

        for (let i = 0; i < texto.length; i++) {
            const colores = ["#0d6efd", "#198754", "#dc3545", "#fd7e14", "#6f42c1"];
            const color = colores[Math.floor(Math.random() * colores.length)];

            html += `<span style="color:${color}; font-size:32px; letter-spacing:4px;">${texto[i]}</span>`;
        }

        $("#captchaTexto").html(html);
        $("#captchaRespuesta").val("");
        $("#captchaMensaje").html("");
        $("#captchaEstado").html("");
    }

    $(document).on("click", "#registrarce-link", function (e) {
        e.preventDefault();
        generarCaptcha();
        $("#modalCaptchaSimple").modal("show");
    });

    $(document).on("click", "#nuevoCaptchaSimple", function () {
        generarCaptcha();
        $("#captchaRespuesta").focus();
    });

    $(document).on("input", "#captchaRespuesta", function () {
        let valor = $(this).val().toUpperCase();
        valor = valor.replace(/[^A-Z2-9]/g, '');
        $(this).val(valor);
    });

    $(document).on("click", "#verificarCaptchaSimple", function () {
        const respuesta = $("#captchaRespuesta").val().trim().toUpperCase();

        if (respuesta === "") {
            $("#captchaEstado").html(`
            <div class="alert alert-danger py-2 mb-0">
                Debes ingresar el código
            </div>
        `);
            $("#captchaRespuesta").focus();
            return;
        }

        if (respuesta === captchaValor) {
            $("#captchaEstado").html(`
            <div class="alert alert-success py-2 mb-0">
                ✔ Verificación exitosa
            </div>
        `);

            setTimeout(() => {
                $("#modalCaptchaSimple").modal("hide");
                $("#captchaEstado").html("");
                $("#loginForm").hide();
                $("#registerContainer").show();
            }, 900);
        } else {
            $("#captchaEstado").html(`
            <div class="alert alert-danger py-2 mb-0">
                ✖ Código incorrecto
            </div>
        `);

            $("#captchaRespuesta").val("").focus();
        }
    });


    $('#cedula_reg').on('blur', function () {
        const buscar = $(this).val().trim();

        if (buscar === '') {
            console.log('Campo vacío');
            return;
        }

        $.ajax({
            url: '/admin?ruta=cliente',
            type: 'POST',
            data: {
                buscar: buscar
            },
            dataType: 'json',
            success: function (response) {
                if (response.existe === true) {
                    Swal.fire({
                        title: 'Advertencia',
                        text: 'La cédula ya se encuentra registrada.',
                        icon: 'warning'
                    }).then(function () {
                        $('#cedula_reg').val('').focus();
                    });
                }
            }
        });
    });






    $(document).ready(function () {

        let captchaVerificado = false;
        let verificandoCaptcha = false;
        let generandoCaptcha = false;
        let temporizadorCierre = null;
        let temporizadorNuevaImagen = null;

        const bordeNormal = "#bfdbfe";
        const bordeError = "#dc3545";
        const bordeCorrecto = "#198754";

        if (window.Parsley) {
            window.Parsley.options.excluded =
                'input[type=button], input[type=submit], input[type=reset], input[type=hidden], #pow-answer';
        }

        function estiloImagenCaptcha() {
            $("#pow-image").css({
                display: "none",
                width: "260px",
                height: "85px",
                maxWidth: "100%",
                objectFit: "contain",
                background: "#eff6ff",
                border: "2px solid #93c5fd",
                borderRadius: "12px",
                padding: "5px",
                boxShadow: "0 4px 14px rgba(37, 99, 235, 0.15)"
            });
        }

      
        function estadoCampo(estado) {
            const $campo = $("#pow-answer");

            if (estado === "error") {
                $campo.css({
                    border: "2px solid " + bordeError,
                    background: "#fff1f2",
                    color: "#dc3545",
                    boxShadow: "0 0 0 3px rgba(220,53,69,.10)"
                });
            } else if (estado === "correcto") {
                $campo.css({
                    border: "2px solid " + bordeCorrecto,
                    background: "#eaf8ef",
                    color: "#198754",
                    boxShadow: "0 0 0 3px rgba(25,135,84,.10)"
                });
            } else {
                $campo.css({
                    border: "1px solid " + bordeNormal,
                    background: "#f8fbff",
                    color: "#1d4ed8",
                    boxShadow: "none"
                });
            }
        }

        // Mostrar mensaje
        function mostrarMensaje(texto, estado) {
            const correcto = estado === "correcto";

            $("#pow-message")
                .text(texto)
                .stop(true, true)
                .css({
                    display: "block",
                    color: correcto ? "#198754" : "#dc3545",
                    background: correcto ? "#eaf8ef" : "#fff1f2",
                    border: correcto
                        ? "1px solid #bbebcb"
                        : "1px solid #fecdd3"
                })
                .fadeIn(150);
        }

        // Ocultar mensajes
        function ocultarMensaje() {
            $("#pow-message").stop(true, true).hide().text("");
        }

        // Abrir o cerrar CAPTCHA
        $("#pow-check").on("change", function () {

            if (captchaVerificado) {
                $(this).prop("checked", true);
                return;
            }

            if (this.checked) {
                $("#pow-panel").stop(true, true).slideDown(250);

                $("#pow-chevron")
                    .removeClass("bi-chevron-down")
                    .addClass("bi-chevron-up");

                if (!$("#pow-image").attr("src")) {
                    generarCaptcha();
                }
            } else {
                if (generandoCaptcha || verificandoCaptcha) {
                    $(this).prop("checked", true);
                    return;
                }

                $("#pow-panel").stop(true, true).slideUp(250);

                $("#pow-chevron")
                    .removeClass("bi-chevron-up")
                    .addClass("bi-chevron-down");

                ocultarMensaje();
                estadoCampo("normal");
            }
        });

        // Generar CAPTCHA mediante Flask y la API externa
        function generarCaptcha() {

            if (generandoCaptcha || verificandoCaptcha || captchaVerificado) {
                return;
            }

            generandoCaptcha = true;

            clearTimeout(temporizadorNuevaImagen);
            temporizadorNuevaImagen = null;

            const $imagen = $("#pow-image");

            $imagen
                .stop(true, true)
                .off(".powcaptcha")
                .hide()
                .removeAttr("src");

            estiloImagenCaptcha();

            $("#pow-answer").val("").prop("disabled", true);
            $("#pow-refresh, #pow-verify").prop("disabled", true);

            estadoCampo("normal");
            ocultarMensaje();

            $.ajax({
                url: "/admin?ruta=login",
                type: "POST",
                dataType: "json",
                data: {
                    generar_captcha: 1
                },

                success: function (respuesta) {

                    if (respuesta.status && respuesta.imagen) {

                        $imagen
                            .off(".powcaptcha")
                            .one("load.powcaptcha", function () {

                                $(this).stop(true, true).fadeIn(200);

                                if (!captchaVerificado) {
                                    $("#pow-answer").prop("disabled", false);
                                    $("#pow-refresh, #pow-verify").prop("disabled", false);
                                }
                            })
                            .one("error.powcaptcha", function () {

                                $(this).hide();

                                mostrarMensaje(
                                    "No se pudo cargar la imagen CAPTCHA. Inténtalo nuevamente.",
                                    "error"
                                );

                              
                            })
                            .attr("src", respuesta.imagen);

                        // Si el navegador ya cargó la imagen
                        if ($imagen[0].complete && $imagen[0].naturalWidth > 0) {

                            $imagen.stop(true, true).fadeIn(200);

                            if (!captchaVerificado) {
                                $("#pow-answer").prop("disabled", false);
                                $("#pow-refresh, #pow-verify").prop("disabled", false);
                            }
                        }
                    } else {
                        mostrarMensaje(
                            respuesta.mensaje || "No se pudo generar el CAPTCHA.",
                            "error"
                        );

                        
                    }
                },

                error: function (xhr) {
                    console.error("Error al generar CAPTCHA:", xhr.responseText);

                    mostrarMensaje(
                        "No se pudo conectar con el servicio CAPTCHA. Inténtalo nuevamente.",
                        "error"
                    );
                },

                complete: function () {
                    generandoCaptcha = false;

                    if (
                        !captchaVerificado &&
                        $("#pow-image").is(":visible") &&
                        $("#pow-image")[0].naturalWidth > 0
                    ) {
                        $("#pow-refresh, #pow-verify, #pow-answer").prop("disabled", false);
                    }
                }
            });
        }

        // Actualizar manualmente la imagen
        $("#pow-refresh").on("click", function (e) {
            e.preventDefault();

            if (!generandoCaptcha && !verificandoCaptcha && !captchaVerificado) {
                generarCaptcha();
            }
        });

        $("#pow-answer").on("input", function () {

            if (captchaVerificado) {
                return;
            }

            this.value = this.value
                .replace(/[^a-zA-Z0-9]/g, "")
                .toUpperCase()
                .slice(0, 6);

            ocultarMensaje();
            estadoCampo("normal");
        });

        // Verificar CAPTCHA independientemente de la cédula y contraseña
        $("#pow-verify").on("click", function (e) {
            e.preventDefault();

            if (generandoCaptcha || verificandoCaptcha || captchaVerificado) {
                return;
            }

            clearTimeout(temporizadorNuevaImagen);
            temporizadorNuevaImagen = null;

            const respuesta = $("#pow-answer").val().trim().toUpperCase();

            if (!/^[A-Z0-9]{6}$/.test(respuesta)) {
                estadoCampo("error");

                mostrarMensaje(
                    "Introduce las 6 letras y números de la imagen.",
                    "error"
                );

                return;
            }

            verificandoCaptcha = true;

            $("#pow-verify, #pow-refresh, #pow-answer").prop("disabled", true);

            $.ajax({
                url: "/admin?ruta=login",
                type: "POST",
                dataType: "json",
                data: {
                    verificar_captcha: 1,
                    respuesta: respuesta
                },

                success: function (resultado) {

                    if (resultado.verificado === true) {

                        captchaVerificado = true;

                        estadoCampo("correcto");
                        mostrarMensaje("Código correcto.", "correcto");

                        $("#pow-check")
                            .prop("checked", true)
                            .prop("disabled", true);

                        $("#pow-answer, #pow-refresh, #pow-verify")
                            .prop("disabled", true);

                        $("#pow-shield")
                            .css({
                                background: "#e8f8ef",
                                color: "#198754"
                            })
                            .html('<i class="bi bi-check-circle-fill"></i>');

                        $("#pow-open").css({
                            border: "1px solid #198754",
                            background: "#f0fdf4",
                            cursor: "default"
                        });

                        temporizadorCierre = setTimeout(function () {

                            $("#pow-captcha").stop(true, true).fadeOut(350, function () {

                                ocultarMensaje();

                                $("#pow-image")
                                    .hide()
                                    .removeAttr("src");

                                $("#pow-panel").hide();
                            });

                        }, 700);

                    } else {

                        estadoCampo("error");

                        mostrarMensaje(
                            "Código incorrecto. Inténtalo nuevamente.",
                            "error"
                        );

                        temporizadorNuevaImagen = setTimeout(function () {

                            temporizadorNuevaImagen = null;

                            if (!captchaVerificado) {
                                generarCaptcha();
                            }

                        }, 900);
                    }
                },

                error: function (xhr) {
                    console.error("Error al verificar CAPTCHA:", xhr.responseText);

                    estadoCampo("error");

                    mostrarMensaje(
                        "No se pudo verificar el código. Inténtalo nuevamente.",
                        "error"
                    );
                },

                complete: function () {
                    verificandoCaptcha = false;

                    if (
                        !captchaVerificado &&
                        !generandoCaptcha &&
                        !temporizadorNuevaImagen
                    ) {
                        $("#pow-verify, #pow-refresh, #pow-answer").prop("disabled", false);
                    }
                }
            });
        });

        // Enviar formulario de inicio de sesión al pulsar Acceso
        $("#loginForm").on("submit", function (e) {

            e.preventDefault();

            const $form = $(this);
            const $boton = $("#loginButton");

            // PRIMERO: comprobar que el CAPTCHA fue verificado
            if (!captchaVerificado) {

                if (!$("#pow-check").prop("checked")) {
                    $("#pow-check").prop("checked", true).trigger("change");
                } else {
                    $("#pow-panel").stop(true, true).slideDown(250);
                }

                mostrarMensaje(
                    "Verifica el CAPTCHA primero.",
                    "error"
                );

                return false;
            }

            // SEGUNDO: validar cédula y contraseña solamente al pulsar Acceso
            if (!$form.parsley().validate()) {
                return false;
            }

        
            if ($boton.prop("disabled")) {
                return false;
            }

            $boton.prop("disabled", true);

            // Enviar cédula y contraseña al controlador Flask
            $.ajax({
                url: "/admin?ruta=login",
                type: "POST",
                dataType: "json",
                data: $form.serialize(),

                success: function (respuesta) {

                    if (respuesta.redirect) {

                        Swal.fire({
                            icon: respuesta.icon || "success",
                            title: respuesta.title || "Correcto",
                            text: respuesta.text || "Inicio de sesión exitoso",
                            timer: 1500,
                            showConfirmButton: false
                        }).then(function () {
                            window.location.href = respuesta.redirect;
                        });

                    } else {

                        Swal.fire({
                            icon: respuesta.icon || "error",
                            title: respuesta.title || "Error",
                            text: respuesta.text || "No se pudo iniciar sesión"
                        });
                    }
                },

                error: function (xhr) {
                    console.error("Error de inicio de sesión:", xhr.responseText);

                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: "No se pudo procesar el inicio de sesión."
                    });
                },

                complete: function () {
                    $boton.prop("disabled", false);
                }
            });

            return false;
        });

       
        estiloImagenCaptcha();

    });






});