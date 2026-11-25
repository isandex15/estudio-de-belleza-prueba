// PAGOS PERSONAL
document.addEventListener('DOMContentLoaded', function() {
   
    const mensajeEl = document.getElementById('mensajePagoPersonalData');
    const mensaje = mensajeEl ? JSON.parse(mensajeEl.dataset.mensaje || 'null') : null;

    if (mensaje) {
        Swal.fire({
            icon: mensaje.icon,
            title: mensaje.title,
            text: mensaje.text,
            confirmButtonText: 'Aceptar'
        });
    }

    const formRegistrar = document.getElementById('formRegistrarPagoPersonal');
    const formAnular = document.getElementById('formAnularPagoPersonal');
    const servicioSelect = document.getElementById('cod_servicio_personal');
    const bancoSelect = document.getElementById('banco_pago_personal');
    const detalle = document.getElementById('detalleServicioPersonal');
    const tableEl = document.getElementById('pagospersonalTable');
    const fechaPagoPersonal = document.getElementById('fecha_pago_personal');

    const modalRegistro = document.getElementById('modalRegistrarPagoPersonal');
    const btnAgregarBanco = document.getElementById('btnAgregarBanco');
    const modalAgregarBanco = document.getElementById('modalAgregarBanco');
    const formAgregarBanco = document.getElementById('formAgregarBanco');
    const nombreBancoNuevo = document.getElementById('nombre_banco_nuevo');
    const errorNombreBanco = document.getElementById('errorNombreBanco');
    const referenciaPagoInput = document.getElementById('referencia_pago_personal');

    if (referenciaPagoInput) {
        referenciaPagoInput.addEventListener('blur', function() {
            const referencia = referenciaPagoInput.value.trim();
            if (!referencia) return;

            const datos = new FormData();
            datos.append('verificar_referencia', '1');
            datos.append('referencia_pago', referencia);
            fetch('/admin?ruta=pagospersonal', { method: 'POST', body: datos })
                .then(function(response) { return response.json(); })
                .then(function(res) {
                    if (res.registrada) {
                        referenciaPagoInput.classList.add('is-invalid');
                        Swal.fire({
                            icon: 'warning',
                            title: 'Referencia ya registrada',
                            text: 'Esta referencia ya pertenece a un pago personal.'
                        });
                    } else {
                        referenciaPagoInput.classList.remove('is-invalid');
                    }
                })
                .catch(function() {});
        });
    }

    if (btnAgregarBanco) {
        btnAgregarBanco.addEventListener('click', function() {
            modalAgregarBanco.addEventListener('hidden.bs.modal', function() {
                if (modalRegistro) {
                    bootstrap.Modal.getOrCreateInstance(modalRegistro).show();
                }
            }, { once: true });

            if (modalRegistro && window.bootstrap) {
                const instancia = bootstrap.Modal.getInstance(modalRegistro);
                if (instancia) {
                    modalRegistro.addEventListener('hidden.bs.modal', function() {
                        bootstrap.Modal.getOrCreateInstance(modalAgregarBanco).show();
                    }, { once: true });
                    instancia.hide();
                    return;
                }
            }
            bootstrap.Modal.getOrCreateInstance(modalAgregarBanco).show();
        });
    }

    if (nombreBancoNuevo) {
        nombreBancoNuevo.addEventListener('input', function() {
            const valorAnterior = nombreBancoNuevo.value;
            const valorLimpio = valorAnterior.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/g, '');
            nombreBancoNuevo.value = valorLimpio;
            if (valorAnterior !== valorLimpio) {
                errorNombreBanco.textContent = 'Este campo solo permite letras.';
                nombreBancoNuevo.classList.add('is-invalid');
            } else if (nombreBancoNuevo.value.length >= 35) {
                errorNombreBanco.textContent = 'limite de caracteres alcanzado';
                nombreBancoNuevo.classList.add('is-invalid');
            } else {
                errorNombreBanco.textContent = '';
                nombreBancoNuevo.classList.remove('is-invalid');
            }
        });
    }

    if (formAgregarBanco) {
        formAgregarBanco.addEventListener('submit', function(event) {
            event.preventDefault();
            const nombre = nombreBancoNuevo.value.trim();
            if (!nombre || nombre.length > 35 || /[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/.test(nombre)) {
                errorNombreBanco.textContent = !nombre ? 'Este campo es obligatorio.' : (nombre.length > 35 ? 'limite de caracteres alcanzado' : 'Este campo solo permite letras.');
                nombreBancoNuevo.classList.add('is-invalid');
                return;
            }

            fetch('/admin?ruta=pagospersonal', { method: 'POST', body: new FormData(formAgregarBanco) })
                .then(function(response) {
                    if (!response.ok) throw new Error('Error en la solicitud');
                    return response.json();
                })
                .then(function(res) {
                    if (!res || res.icon !== 'success') {
                        errorNombreBanco.textContent = res.text || 'No se pudo registrar el banco.';
                        nombreBancoNuevo.classList.add('is-invalid');
                        return;
                    }
                    bancoSelect.add(new Option(res.nombre_banco, res.cod_banco));
                    bancoSelect.value = String(res.cod_banco);
                    bootstrap.Modal.getInstance(modalAgregarBanco).hide();
                    formAgregarBanco.reset();
                    nombreBancoNuevo.classList.remove('is-invalid');
                })
                .catch(function() {
                    errorNombreBanco.textContent = 'No se pudo registrar el banco.';
                    nombreBancoNuevo.classList.add('is-invalid');
                });
        });
    }

    document.addEventListener('click', function(event) {
        const btn = event.target.closest('.btn-detalle-pago-personal');
        if (!btn) return;

        const setText = function(id, value) {
            const element = document.getElementById(id);
            if (element) element.textContent = value || 'Sin información';
        };
        setText('detalleReferencia', btn.dataset.referencia);
        setText('detalleServicio', btn.dataset.servicio);
        setText('detalleCliente', btn.dataset.cliente);
        setText('detalleEspecialista', btn.dataset.especialista);
        setText('detalleFechaHora', `${btn.dataset.fecha} ${btn.dataset.hora}`);
        setText('detallePorcentaje', `${btn.dataset.porcentaje}%`);
        setText('detalleTipoPago', btn.dataset.tipoPago);
        setText('detalleMoneda', btn.dataset.moneda);
        setText('detalleBanco', btn.dataset.banco);
        setText('detalleMonto', `$ ${btn.dataset.monto}`);
        const comprobanteWrap = document.getElementById('detalleComprobanteWrap');
        const comprobante = document.getElementById('detalleComprobante');
        if (comprobanteWrap && comprobante) {
            comprobante.src = btn.dataset.comprobante || '';
            comprobanteWrap.hidden = !btn.dataset.comprobante;
        }
    });

    if (window.flatpickr) {
        flatpickr('#hora_pago_personal', {
            allowInput: true,
            dateFormat: 'H:i',
            enableTime: true,
            minuteIncrement: 5,
            noCalendar: true,
            time_24hr: true
        });
    }

    // DataTable
    if (tableEl && window.jQuery && window.jQuery.fn && window.jQuery.fn.DataTable) {
        $('#pagospersonalTable').DataTable({
            responsive: true,
            autoWidth: false,
            language: {
                processing: 'Procesando...',
                search: 'Buscar:',
                lengthMenu: 'Mostrar _MENU_ registros',
                info: 'Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros',
                infoEmpty: 'Mostrando registros del 0 al 0 de un total de 0 registros',
                infoFiltered: '(filtrado de un total de _MAX_ registros)',
                loadingRecords: 'Cargando...',
                zeroRecords: 'No se encontraron resultados',
                emptyTable: 'Ningún dato disponible en esta tabla',
                paginate: { first: 'Primero', previous: 'Anterior', next: 'Siguiente', last: 'Último' },
                aria: { sortAscending: ': Activar para ordenar la columna de manera ascendente', sortDescending: ': Activar para ordenar la columna de manera descendente' }
            }
        });
    }

    // Mostrar detalle al seleccionar servicio
    function mostrarDetalleServicio(option) {
        if (!option || !option.value) {
            if (detalle) detalle.style.display = 'none';
            return;
        }
        const precio = parseFloat(option.dataset.precio || 0);
        if (detalle) {
            detalle.style.display = 'block';
            detalle.innerHTML = `Servicio seleccionado: <strong>${option.text}</strong><br>Cliente: <strong>${option.dataset.cliente || 'Sin cliente'}</strong><br>Especialista: <strong>${option.dataset.especialista || 'Sin especialista'}</strong><br>Monto total del servicio: <strong>${precio.toFixed(2)} $</strong>`;
        }
    }

    if (servicioSelect) {
        servicioSelect.addEventListener('change', function() {
            const option = servicioSelect.options[servicioSelect.selectedIndex];
            if (option && option.value) {
                const datos = new FormData();
                datos.append('verificar_pago_personal', '1');
                datos.append('cod_servicio', option.value);
                fetch('/admin?ruta=pagospersonal', { method: 'POST', body: datos })
                    .then(response => response.json())
                    .then(res => {
                        if (!res.registrado) return;
                        servicioSelect.value = '';
                        mostrarDetalleServicio(null);
                        Swal.fire({
                            icon: 'warning',
                            title: 'Pago personal ya registrado',
                            text: 'El servicio seleccionado ya tiene un pago personal registrado.'
                        });
                    })
                    .catch(() => {});
            }
            mostrarDetalleServicio(option);
        });
    }

    if (modalRegistro && servicioSelect) {
        modalRegistro.addEventListener('show.bs.modal', function() {
            const ahora = new Date();
            const fechaHoy = `${ahora.getFullYear()}-${String(ahora.getMonth() + 1).padStart(2, '0')}-${String(ahora.getDate()).padStart(2, '0')}`;
            const serviciosDeHoy = Array.from(servicioSelect.options).filter(function(option) {
                return option.value && option.dataset.fechaRealizacion === fechaHoy;
            });

            servicioSelect.querySelectorAll('option').forEach(function(option) {
                if (!option.value) {
                    option.hidden = false;
                    option.disabled = false;
                    return;
                }

                const esDeHoy = option.dataset.fechaRealizacion === fechaHoy;
                option.hidden = !esDeHoy;
                option.disabled = !esDeHoy;
            });

            if (!serviciosDeHoy.length) {
                servicioSelect.value = '';
                servicioSelect.disabled = true;
                mostrarDetalleServicio(null);
                return;
            }

            servicioSelect.disabled = false;
            servicioSelect.value = serviciosDeHoy[0].value;
            mostrarDetalleServicio(serviciosDeHoy[0]);
        });
    }

    // fecha a la fecha actual (no pasado ni futuro)
    if (fechaPagoPersonal) {
        const hoy = new Date();
        const anio = hoy.getFullYear();
        const mes = String(hoy.getMonth() + 1).padStart(2, '0');
        const dia = String(hoy.getDate()).padStart(2, '0');
        const fechaHoy = `${anio}-${mes}-${dia}`;
        fechaPagoPersonal.setAttribute('min', fechaHoy);
        fechaPagoPersonal.setAttribute('max', fechaHoy);
        // Establecer la fecha por defecto a hoy
        fechaPagoPersonal.value = fechaHoy;

        fechaPagoPersonal.addEventListener('change', function () {
            if (!this.value) {
                Swal.fire({ icon: 'error', title: 'Fecha requerida', text: 'Debe seleccionar una fecha de pago.' });
            } else if (this.value !== fechaHoy) {
                Swal.fire({ icon: 'error', title: 'Fecha inválida', text: 'La fecha de pago debe ser la fecha actual.' });
                this.value = '';
            }
        });
    }

    // Manejo del registro (submit)
    if (formRegistrar) {
        formRegistrar.addEventListener('submit', function(e) {
            e.preventDefault();
            //  la fecha debe ser la fecha actual
            if (fechaPagoPersonal) {
                const valorFecha = fechaPagoPersonal.value ? fechaPagoPersonal.value.trim() : '';
                const hoy = new Date();
                const anio = hoy.getFullYear();
                const mes = String(hoy.getMonth() + 1).padStart(2, '0');
                const dia = String(hoy.getDate()).padStart(2, '0');
                const fechaHoy = `${anio}-${mes}-${dia}`;
                if (!valorFecha) {
                    Swal.fire({ icon: 'error', title: 'Fecha requerida', text: 'Seleccione la fecha de pago.' });
                    return;
                }
                if (valorFecha !== fechaHoy) {
                    Swal.fire({ icon: 'error', title: 'Fecha inválida', text: 'La fecha de pago debe ser la fecha actual.' });
                    return;
                }
            }

            const horaInput = document.getElementById('hora_pago_personal');
            if (horaInput && horaInput.value && horaInput.value.length === 5) {
                horaInput.value = `${horaInput.value}:00`;
            }

            fetch('/admin?ruta=pagospersonal', { method: 'POST', body: new FormData(formRegistrar) })
                .then(function(response) {
                    if (!response.ok) throw new Error('Error en la solicitud');
                    return response.json();
                })
                .then(function(res) {
                    if (res && res.icon === 'success') {
                        const modal = document.getElementById('modalRegistrarPagoPersonal');
                        formRegistrar.reset();
                        if (detalle) detalle.style.display = 'none';
                        $('#pagospersonalTable').load(location.href + ' #pagospersonalTable>*', '');

                        const mostrarExito = function() {
                            document.querySelectorAll('.modal-backdrop').forEach(function(backdrop) {
                                backdrop.remove();
                            });
                            document.body.classList.remove('modal-open');
                            if (res.notificacion) {
                                window.dispatchEvent(new CustomEvent('pago-personal-registrado'));
                            }
                            Swal.fire({
                                icon: res.icon,
                                title: res.title,
                                text: res.text,
                                timer: 2000,
                                timerProgressBar: true,
                                showConfirmButton: false,
                                backdrop: false
                            });
                        };

                        if (modal && window.bootstrap) {
                            modal.addEventListener('hidden.bs.modal', mostrarExito, { once: true });
                            bootstrap.Modal.getOrCreateInstance(modal).hide();
                        } else {
                            mostrarExito();
                        }
                        return;
                    }

                    // Si el servidor devuelve errores por campos, mostrarlos
                    if (res && res.errors) {
                        const mensajes = [];
                        for (const k in res.errors) {
                            if (Object.prototype.hasOwnProperty.call(res.errors, k)) {
                                mensajes.push(res.errors[k]);
                            }
                        }
                        Swal.fire({ icon: 'error', title: res.title || 'Error', html: mensajes.join('<br>') });
                        return;
                    }

                    Swal.fire({ icon: res && res.icon ? res.icon : 'error', title: res && res.title ? res.title : 'Error', text: res && res.text ? res.text : 'No se pudo procesar la solicitud.' });
                })
                .catch(function() {
                    Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo conectar con el servidor.' });
                });
        });
    }

    
    const inputAnular = document.getElementById('cod_pago_personal_a_anular');
    let filaPagoPersonalAnular = null;
    if (inputAnular) {
        document.querySelectorAll('.btn-anular-personal').forEach(function(btn) {
            btn.addEventListener('click', function() {
                const cod = btn.dataset.codPagoPersonal || btn.getAttribute('data-cod-pago-personal');
                if (cod) {
                    inputAnular.value = cod;
                    filaPagoPersonalAnular = btn.closest('tr');
                }
            });
        });
    }

    // Anular pago personal
    if (formAnular) {
        formAnular.addEventListener('submit', function(e) {
            e.preventDefault();
            fetch('/admin?ruta=pagospersonal', { method: 'POST', body: new FormData(formAnular) })
                .then(function(response) {
                    if (!response.ok) throw new Error('Error en la solicitud');
                    return response.json();
                })
                .then(function(res) {
                    if (res && res.icon === 'success') {
                        if (filaPagoPersonalAnular) {
                            const celdas = filaPagoPersonalAnular.children;
                            const estado = celdas[celdas.length - 2];
                            if (estado) estado.innerHTML = '<span class="badge bg-danger">Anulado</span>';
                            const boton = filaPagoPersonalAnular.querySelector('.btn-anular-personal');
                            if (boton) {
                                boton.disabled = true;
                                boton.removeAttribute('data-bs-toggle');
                                boton.removeAttribute('data-bs-target');
                            }
                        }

                        const modal = document.getElementById('modalAnularPagoPersonal');
                        const mostrarExito = function() {
                            document.querySelectorAll('.modal-backdrop').forEach(function(backdrop) {
                                backdrop.remove();
                            });
                            document.body.classList.remove('modal-open');
                            Swal.fire({
                                icon: res.icon,
                                title: res.title,
                                text: res.text || 'El pago personal se anuló correctamente.',
                                timer: 1400,
                                showConfirmButton: false,
                                backdrop: false
                            });
                        };

                        if (modal && window.bootstrap) {
                            modal.addEventListener('hidden.bs.modal', mostrarExito, { once: true });
                            bootstrap.Modal.getOrCreateInstance(modal).hide();
                        } else {
                            mostrarExito();
                        }
                        formAnular.reset();
                        return;
                    }
                    Swal.fire({ icon: res && res.icon ? res.icon : 'error', title: res && res.title ? res.title : 'Error', text: res && res.text ? res.text : 'No se pudo anular el pago personal.' });
                })
                .catch(function() {
                    Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo conectar con el servidor.' });
                });
        });
    }
});
