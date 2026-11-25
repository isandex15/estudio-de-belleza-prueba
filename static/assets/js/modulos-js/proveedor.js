console.log("Abrió proveedores");

const regexSoloNumeros = /^\d+$/;
const regexSoloLetras = /^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]+$/;
const regexCorreo = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

$(document).ready(function () {


    $('#formRegistrarProveedor, #formEditarProveedor')
        .attr('novalidate', 'novalidate');


    // =====================================================
    // MOSTRAR ERROR
    // =====================================================

    function mostrarError(campo, mensaje) {

        campo
            .addClass('is-invalid')
            .removeClass('is-valid');

        let feedback = campo.siblings('.invalid-feedback');

        if (feedback.length === 0) {

            campo.after(
                '<div class="invalid-feedback"></div>'
            );

            feedback = campo.siblings('.invalid-feedback');
        }

        feedback
            .text(mensaje)
            .show();
    }


  
    function quitarError(campo) {

        campo
            .removeClass('is-invalid');

        const feedback =
            campo.siblings('.invalid-feedback');

        if (feedback.length > 0) {

            feedback
                .hide()
                .text('');
        }
    }


    // =====================================================
    // CAMPO VÁLIDO
    // =====================================================

    function campoValido(campo) {

        quitarError(campo);

        campo.addClass('is-valid');
    }


    // =====================================================
    // CÉDULA
    // =====================================================

    $('#cedula, #edit_cedula').on('keydown', function (e) {

        const campo = $(this);
        const valor = campo.val();

        const teclasPermitidas = [
            'Backspace',
            'Delete',
            'ArrowLeft',
            'ArrowRight',
            'ArrowUp',
            'ArrowDown',
            'Tab',
            'Home',
            'End'
        ];

        if (teclasPermitidas.includes(e.key)) {
            return;
        }

        // Solo números
        if (!/^\d$/.test(e.key)) {

            e.preventDefault();

            mostrarError(
                campo,
                'Solo se permiten números.'
            );

            return;
        }

        // Máximo 8
        if (valor.length >= 8) {

            e.preventDefault();

            mostrarError(
                campo,
                'Máximo de caracteres.'
            );

            return;
        }

    });


    // =====================================================
    // CÉDULA INPUT
    // =====================================================

    $('#cedula, #edit_cedula').on('input', function () {

        const campo = $(this);

        let valor = campo.val();

        valor = valor.replace(/\D/g, '');

        if (valor.length > 8) {

            valor = valor.substring(0, 8);

            mostrarError(
                campo,
                'Máximo de caracteres.'
            );

        }

        campo.val(valor);

        if (valor !== '') {

            quitarError(campo);

        }

    });


    // =====================================================
    // PEGAR CÉDULA
    // =====================================================

    $('#cedula, #edit_cedula').on('paste', function (e) {

        const campo = $(this);

        const texto =
            (
                e.originalEvent.clipboardData ||
                window.clipboardData
            ).getData('text');

        if (!regexSoloNumeros.test(texto)) {

            e.preventDefault();

            mostrarError(
                campo,
                'Solo se permiten números.'
            );

            return;
        }

        if (
            campo.val().length +
            texto.length > 8
        ) {

            e.preventDefault();

            mostrarError(
                campo,
                'Máximo de caracteres.'
            );

        }

    });


    // =====================================================
    // NOMBRE
    // =====================================================

    $('#nombre, #edit_nombre').on('keydown', function (e) {

        const campo = $(this);
        const valor = campo.val();

        const teclasPermitidas = [
            'Backspace',
            'Delete',
            'ArrowLeft',
            'ArrowRight',
            'ArrowUp',
            'ArrowDown',
            'Tab',
            'Home',
            'End'
        ];

        if (teclasPermitidas.includes(e.key)) {
            return;
        }

        // Solo letras y espacios
        if (
            e.key.length === 1 &&
            !/^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]$/.test(e.key)
        ) {

            e.preventDefault();

            mostrarError(
                campo,
                'Solo se permiten letras.'
            );

            return;
        }

        // Máximo 20
        if (valor.length >= 20) {

            e.preventDefault();

            mostrarError(
                campo,
                'Máximo de caracteres.'
            );

            return;
        }

    });


    // =====================================================
    // NOMBRE INPUT
    // =====================================================

    $('#nombre, #edit_nombre').on('input', function () {

        const campo = $(this);

        let valor = campo.val();

        // Eliminar números y caracteres especiales
        valor = valor.replace(
            /[^a-zA-ZÁÉÍÓÚáéíóúñÑ\s]/g,
            ''
        );

        if (valor.length > 20) {

            valor = valor.substring(0, 20);

            mostrarError(
                campo,
                'Máximo de caracteres.'
            );

        }

        campo.val(valor);

        if (valor.trim() !== '') {

            quitarError(campo);

        }

    });


    // =====================================================
    // APELLIDO
    // =====================================================

    $('#apellido, #edit_apellido').on('keydown', function (e) {

        const campo = $(this);
        const valor = campo.val();

        const teclasPermitidas = [
            'Backspace',
            'Delete',
            'ArrowLeft',
            'ArrowRight',
            'ArrowUp',
            'ArrowDown',
            'Tab',
            'Home',
            'End'
        ];

        if (teclasPermitidas.includes(e.key)) {
            return;
        }

        // Solo letras y espacios
        if (
            e.key.length === 1 &&
            !/^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]$/.test(e.key)
        ) {

            e.preventDefault();

            mostrarError(
                campo,
                'Solo se permiten letras.'
            );

            return;
        }

        // Máximo 20
        if (valor.length >= 20) {

            e.preventDefault();

            mostrarError(
                campo,
                'Máximo de caracteres.'
            );

            return;
        }

    });


    // =====================================================
    // APELLIDO INPUT
    // =====================================================

    $('#apellido, #edit_apellido').on('input', function () {

        const campo = $(this);

        let valor = campo.val();

        valor = valor.replace(
            /[^a-zA-ZÁÉÍÓÚáéíóúñÑ\s]/g,
            ''
        );

        if (valor.length > 20) {

            valor = valor.substring(0, 20);

            mostrarError(
                campo,
                'Máximo de caracteres.'
            );

        }

        campo.val(valor);

        if (valor.trim() !== '') {

            quitarError(campo);

        }

    });


    // =====================================================
    // RIF
    // =====================================================

    $('#rif, #edit_rif').on('focus', function () {

        const campo = $(this);

        if (campo.val() === '') {

            campo.val('J');

        }

    });


    // =====================================================
    // RIF KEYDOWN
    // =====================================================

    $('#rif, #edit_rif').on('keydown', function (e) {

        const campo = $(this);

        let valor = campo.val();

        const teclasPermitidas = [
            'Backspace',
            'Delete',
            'ArrowLeft',
            'ArrowRight',
            'ArrowUp',
            'ArrowDown',
            'Tab',
            'Home',
            'End'
        ];

        if (teclasPermitidas.includes(e.key)) {

            // No permitir borrar la J
            if (
                (e.key === 'Backspace' ||
                 e.key === 'Delete') &&
                valor.length <= 1
            ) {

                e.preventDefault();

            }

            return;
        }

        // Solo números después de J
        if (!/^\d$/.test(e.key)) {

            e.preventDefault();

            mostrarError(
                campo,
                'Después de la J solo se permiten números.'
            );

            return;
        }

        // Máximo 11 caracteres incluyendo J
        if (valor.length >= 11) {

            e.preventDefault();

            mostrarError(
                campo,
                'Máximo 11 caracteres.'
            );

            return;
        }

    });


    // =====================================================
    // RIF INPUT
    // =====================================================

    $('#rif, #edit_rif').on('input', function () {

        const campo = $(this);

        let valor = campo.val();

        // Siempre comenzar con J
        if (
            valor.length === 0 ||
            valor.charAt(0).toUpperCase() !== 'J'
        ) {

            valor =
                'J' +
                valor.replace(/\D/g, '');

        } else {

            valor =
                'J' +
                valor.substring(1)
                    .replace(/\D/g, '');
        }

        // Máximo 11
        if (valor.length > 11) {

            valor = valor.substring(0, 11);

            mostrarError(
                campo,
                'Máximo 11 caracteres.'
            );

        }

        campo.val(valor);

    });


    // =====================================================
    // TELÉFONO
    // =====================================================

    $('#telefono, #edit_telefono').on('keydown', function (e) {

        const campo = $(this);
        const valor = campo.val();

        const teclasPermitidas = [
            'Backspace',
            'Delete',
            'ArrowLeft',
            'ArrowRight',
            'ArrowUp',
            'ArrowDown',
            'Tab',
            'Home',
            'End'
        ];

        if (teclasPermitidas.includes(e.key)) {
            return;
        }

        // Solo números
        if (!/^\d$/.test(e.key)) {

            e.preventDefault();

            mostrarError(
                campo,
                'Solo se permiten números.'
            );

            return;
        }

        // Máximo 11
        if (valor.length >= 11) {

            e.preventDefault();

            mostrarError(
                campo,
                'Máximo de caracteres.'
            );

            return;
        }

    });


    // =====================================================
    // TELÉFONO INPUT
    // =====================================================

    $('#telefono, #edit_telefono').on('input', function () {

        const campo = $(this);

        let valor = campo.val();

        valor = valor.replace(/\D/g, '');

        if (valor.length > 11) {

            valor = valor.substring(0, 11);

            mostrarError(
                campo,
                'Máximo de caracteres.'
            );

        }

        campo.val(valor);

    });


    // =====================================================
    // CORREO
    // =====================================================

    $('#correo, #edit_correo').on('input', function () {

        const campo = $(this);

        let valor = campo.val();

        // Máximo 100
        if (valor.length > 100) {

            valor = valor.substring(0, 100);

            campo.val(valor);

            mostrarError(
                campo,
                'Máximo 100 caracteres.'
            );

            return;
        }

        // Validar solamente si hay contenido
        if (valor !== '') {

            if (!regexCorreo.test(valor)) {

                mostrarError(
                    campo,
                    'Ingrese un correo electrónico válido.'
                );

            } else {

                campoValido(campo);

            }

        } else {

            quitarError(campo);

        }

    });


    // =====================================================
    // PLACEHOLDER CORREO
    // =====================================================

    $('#correo, #edit_correo').attr(
        'placeholder',
        'ejemplo@correo.com'
    );


    // =====================================================
    // VALIDAR CORREO AL SALIR
    // =====================================================

    $('#correo, #edit_correo').on('blur', function () {

        const campo = $(this);

        const valor = campo.val().trim();

        if (valor === '') {

            mostrarError(
                campo,
                'Este campo no puede estar vacío.'
            );

            return;
        }

        if (!regexCorreo.test(valor)) {

            mostrarError(
                campo,
                'Ingrese un correo electrónico válido.'
            );

            return;
        }

        campoValido(campo);

    });


    // =====================================================
    // REGISTRAR PROVEEDOR
    // =====================================================

    $('#formRegistrarProveedor').on(
        'submit',
        function (e) {

            e.preventDefault();

            const form = this;

            const btn =
                $(form).find(
                    'button[type="submit"]'
                );

            let valido = true;


            const cedula =
                $('#cedula');

            const nombre =
                $('#nombre');

            const apellido =
                $('#apellido');

            const rif =
                $('#rif');

            const telefono =
                $('#telefono');

            const correo =
                $('#correo');


            // ---------------------------------------------
            // CÉDULA
            // ---------------------------------------------

            if (cedula.val().trim() === '') {

                mostrarError(
                    cedula,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !regexSoloNumeros.test(
                    cedula.val()
                )
            ) {

                mostrarError(
                    cedula,
                    'Solo se permiten números.'
                );

                valido = false;

            } else if (
                cedula.val().length > 8
            ) {

                mostrarError(
                    cedula,
                    'Máximo 8 caracteres.'
                );

                valido = false;
            }


            // ---------------------------------------------
            // NOMBRE
            // ---------------------------------------------

            if (nombre.val().trim() === '') {

                mostrarError(
                    nombre,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !regexSoloLetras.test(
                    nombre.val().trim()
                )
            ) {

                mostrarError(
                    nombre,
                    'Solo se permiten letras.'
                );

                valido = false;

            } else if (
                nombre.val().length > 20
            ) {

                mostrarError(
                    nombre,
                    'Máximo 20 caracteres.'
                );

                valido = false;
            }


            // ---------------------------------------------
            // APELLIDO
            // ---------------------------------------------

            if (apellido.val().trim() === '') {

                mostrarError(
                    apellido,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !regexSoloLetras.test(
                    apellido.val().trim()
                )
            ) {

                mostrarError(
                    apellido,
                    'Solo se permiten letras.'
                );

                valido = false;

            } else if (
                apellido.val().length > 20
            ) {

                mostrarError(
                    apellido,
                    'Máximo 20 caracteres.'
                );

                valido = false;
            }


            // ---------------------------------------------
            // RIF
            // ---------------------------------------------

            if (
                rif.val().trim() === '' ||
                rif.val() === 'J'
            ) {

                mostrarError(
                    rif,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !/^J\d+$/.test(
                    rif.val()
                )
            ) {

                mostrarError(
                    rif,
                    'El RIF debe comenzar con J y continuar con números.'
                );

                valido = false;

            } else if (
                rif.val().length > 11
            ) {

                mostrarError(
                    rif,
                    'Máximo 11 caracteres.'
                );

                valido = false;
            }


            // ---------------------------------------------
            // TELÉFONO
            // ---------------------------------------------

            if (
                telefono.val().trim() === ''
            ) {

                mostrarError(
                    telefono,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !regexSoloNumeros.test(
                    telefono.val()
                )
            ) {

                mostrarError(
                    telefono,
                    'Solo se permiten números.'
                );

                valido = false;

            } else if (
                telefono.val().length > 11
            ) {

                mostrarError(
                    telefono,
                    'Máximo 11 caracteres.'
                );

                valido = false;
            }


            // ---------------------------------------------
            // CORREO
            // ---------------------------------------------

            if (
                correo.val().trim() === ''
            ) {

                mostrarError(
                    correo,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !regexCorreo.test(
                    correo.val().trim()
                )
            ) {

                mostrarError(
                    correo,
                    'Ingrese un correo electrónico válido.'
                );

                valido = false;

            } else if (
                correo.val().length > 100
            ) {

                mostrarError(
                    correo,
                    'Máximo 100 caracteres.'
                );

                valido = false;
            }


            // ---------------------------------------------
            // DETENER
            // ---------------------------------------------

            if (!valido) {

                return;

            }


            // ---------------------------------------------
            // ENVIAR
            // ---------------------------------------------

            btn.prop(
                'disabled',
                true
            );

            $.post(
                '/admin?ruta=proveedor',
                $(form).serialize(),
                function (res) {

                    alerta(res).then(
                        function () {

                            if (
                                res.icon ===
                                'success'
                            ) {

                                form.reset();

                                $(form)
                                    .find(
                                        '.is-invalid, .is-valid'
                                    )
                                    .removeClass(
                                        'is-invalid is-valid'
                                    );

                                $(form)
                                    .find(
                                        '.invalid-feedback'
                                    )
                                    .hide();

                                cerrarModal(
                                    '#modalRegistrar'
                                );

                                $('#table1').load(
                                    location.href +
                                    ' #table1>*',
                                    ''
                                );

                            }

                            btn.prop(
                                'disabled',
                                false
                            );

                        }
                    );

                },
                'json'
            );

        }
    );


    // =====================================================
    // EDITAR PROVEEDOR
    // =====================================================

    $('#formEditarProveedor').on(
        'submit',
        function (e) {

            e.preventDefault();

            const form = this;

            const btn =
                $(form).find(
                    'button[type="submit"]'
                );

            let valido = true;

            const cedula =
                $('#edit_cedula');

            const nombre =
                $('#edit_nombre');

            const apellido =
                $('#edit_apellido');

            const rif =
                $('#edit_rif');

            const telefono =
                $('#edit_telefono');

            const correo =
                $('#edit_correo');


            // CÉDULA
            if (cedula.val().trim() === '') {

                mostrarError(
                    cedula,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !regexSoloNumeros.test(
                    cedula.val()
                )
            ) {

                mostrarError(
                    cedula,
                    'Solo se permiten números.'
                );

                valido = false;

            } else if (
                cedula.val().length > 8
            ) {

                mostrarError(
                    cedula,
                    'Máximo 8 caracteres.'
                );

                valido = false;
            }


            // NOMBRE
            if (nombre.val().trim() === '') {

                mostrarError(
                    nombre,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !regexSoloLetras.test(
                    nombre.val().trim()
                )
            ) {

                mostrarError(
                    nombre,
                    'Solo se permiten letras.'
                );

                valido = false;

            } else if (
                nombre.val().length > 20
            ) {

                mostrarError(
                    nombre,
                    'Máximo 20 caracteres.'
                );

                valido = false;
            }


            // APELLIDO
            if (apellido.val().trim() === '') {

                mostrarError(
                    apellido,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !regexSoloLetras.test(
                    apellido.val().trim()
                )
            ) {

                mostrarError(
                    apellido,
                    'Solo se permiten letras.'
                );

                valido = false;

            } else if (
                apellido.val().length > 20
            ) {

                mostrarError(
                    apellido,
                    'Máximo 20 caracteres.'
                );

                valido = false;
            }


            // RIF
            if (
                rif.val().trim() === '' ||
                rif.val() === 'J'
            ) {

                mostrarError(
                    rif,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !/^J\d+$/.test(
                    rif.val()
                )
            ) {

                mostrarError(
                    rif,
                    'El RIF debe comenzar con J y continuar con números.'
                );

                valido = false;

            } else if (
                rif.val().length > 11
            ) {

                mostrarError(
                    rif,
                    'Máximo 11 caracteres.'
                );

                valido = false;
            }


            // TELÉFONO
            if (
                telefono.val().trim() === ''
            ) {

                mostrarError(
                    telefono,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !regexSoloNumeros.test(
                    telefono.val()
                )
            ) {

                mostrarError(
                    telefono,
                    'Solo se permiten números.'
                );

                valido = false;

            } else if (
                telefono.val().length > 11
            ) {

                mostrarError(
                    telefono,
                    'Máximo 11 caracteres.'
                );

                valido = false;
            }


            // CORREO
            if (
                correo.val().trim() === ''
            ) {

                mostrarError(
                    correo,
                    'Este campo no puede estar vacío.'
                );

                valido = false;

            } else if (
                !regexCorreo.test(
                    correo.val().trim()
                )
            ) {

                mostrarError(
                    correo,
                    'Ingrese un correo electrónico válido.'
                );

                valido = false;

            } else if (
                correo.val().length > 100
            ) {

                mostrarError(
                    correo,
                    'Máximo 100 caracteres.'
                );

                valido = false;
            }


            if (!valido) {

                return;

            }


            btn.prop(
                'disabled',
                true
            );


            $.post(
                '/admin?ruta=proveedor',
                $(form).serialize(),
                function (res) {

                    alerta(res).then(
                        function () {

                            if (
                                res.icon ===
                                'success'
                            ) {

                                form.reset();

                                $(form)
                                    .find(
                                        '.is-invalid, .is-valid'
                                    )
                                    .removeClass(
                                        'is-invalid is-valid'
                                    );

                                $(form)
                                    .find(
                                        '.invalid-feedback'
                                    )
                                    .hide();

                                cerrarModal(
                                    '#modalEditar'
                                );

                                $('#table1').load(
                                    location.href +
                                    ' #table1>*',
                                    ''
                                );

                            }

                            btn.prop(
                                'disabled',
                                false
                            );

                        }
                    );

                },
                'json'
            );

        }
    );


    // =====================================================
    // ELIMINAR PROVEEDOR
    // =====================================================

    $('#formEliminarProveedor').on(
        'submit',
        function (e) {

            e.preventDefault();

            $.post(
                '/admin?ruta=proveedor',
                $(this).serialize(),
                function (res) {

                    alerta(res).then(
                        function () {

                            cerrarModal(
                                '#modalEliminar'
                            );

                            if (
                                res.icon ===
                                'success'
                            ) {

                                $('#table1').load(
                                    location.href +
                                    ' #table1>*',
                                    ''
                                );

                            }

                        }
                    );

                },
                'json'
            );

        }
    );


    // =====================================================
    // CERRAR MODAL
    // =====================================================

    function cerrarModal(id) {

        $(id).modal('hide');

        $(id).on(
            'hidden.bs.modal',
            function () {

                $('.modal-backdrop').remove();

                $('body')
                    .removeClass(
                        'modal-open'
                    );

                $(this).off(
                    'hidden.bs.modal'
                );

            }
        );

    }


    // =====================================================
    // ALERTA
    // =====================================================

    function alerta(res) {

        return Swal.fire({

            icon: res.icon,

            title: res.title,

            text: res.text,

            showConfirmButton: true,

            confirmButtonText: 'Aceptar',

            timer: 2000,

            timerProgressBar: true,

            backdrop: false

        });

    }


    // =====================================================
    // MODAL EDITAR
    // =====================================================

    const modalEditar =
        document.getElementById(
            'modalEditar'
        );

    if (modalEditar) {

        modalEditar.addEventListener(
            'show.bs.modal',
            function (event) {

                const button =
                    event.relatedTarget;

                const cod =
                    button.getAttribute(
                        'data-cod_proveedor'
                    );

                const cedula =
                    button.getAttribute(
                        'data-cedula'
                    );

                const nombre =
                    button.getAttribute(
                        'data-nombre'
                    );

                const apellido =
                    button.getAttribute(
                        'data-apellido'
                    );

                const rif =
                    button.getAttribute(
                        'data-rif'
                    );

                const telefono =
                    button.getAttribute(
                        'data-telefono'
                    );

                const correo =
                    button.getAttribute(
                        'data-correo'
                    );

                const status =
                    button.getAttribute(
                        'data-status'
                    );

                const form =
                    modalEditar.querySelector(
                        'form'
                    );

                if (form) {

                    form.querySelector(
                        '#edit_cod_proveedor'
                    ).value = cod;

                    form.querySelector(
                        '#edit_cedula'
                    ).value = cedula;

                    form.querySelector(
                        '#edit_nombre'
                    ).value = nombre;

                    form.querySelector(
                        '#edit_apellido'
                    ).value = apellido;

                    form.querySelector(
                        '#edit_rif'
                    ).value = rif;

                    form.querySelector(
                        '#edit_telefono'
                    ).value = telefono;

                    form.querySelector(
                        '#edit_correo'
                    ).value = correo;

                    form.querySelector(
                        '#edit_status'
                    ).value = status;

                    // Limpiar errores
                    $(form)
                        .find(
                            '.is-invalid, .is-valid'
                        )
                        .removeClass(
                            'is-invalid is-valid'
                        );

                    $(form)
                        .find(
                            '.invalid-feedback'
                        )
                        .hide();

                }

            }
        );

    }


    // =====================================================
    // MODAL ELIMINAR
    // =====================================================

    const modalEliminar =
        document.getElementById(
            'modalEliminar'
        );

    if (modalEliminar) {

        modalEliminar.addEventListener(
            'show.bs.modal',
            function (event) {

                const button =
                    event.relatedTarget;

                const cod =
                    button.getAttribute(
                        'data-cod_proveedor'
                    );

                const form =
                    document.getElementById(
                        'formEliminarProveedor'
                    );

                if (form) {

                    form.querySelector(
                        '#delete_cod_proveedor'
                    ).value = cod;

                }

            }
        );

    }

});