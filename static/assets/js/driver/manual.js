
document.addEventListener('DOMContentLoaded', function () {
    const botonAyuda = document.getElementById('ayudaSistema');
    if (!botonAyuda || !window.driver || !window.driver.js) return;

    const pasos = {
        encabezado: [
            {
                element: '#notificacionesDropdown',
                popover: {
                    title: 'Notificaciones',
                    description: 'Aquí puedes consultar las notificaciones del sistema.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#ayudaSistema',
                popover: {
                    title: 'Centro de ayuda',
                    description: 'Desde este icono puedes iniciar nuevamente el recorrido guiado.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#dropdownMenuButton .icono-usuario-verde',
                popover: {
                    title: 'Perfil de usuario',
                    description: 'Desde aquí puedes acceder a tu perfil y cerrar tu sesión.',
                    side: 'bottom',
                    align: 'center'
                }
            }
        ],

        primeravessistema: [

            {
                element: '#notificacionesDropdown',
                popover: {
                    title: 'Notificaciones',
                    description: 'Aquí puedes consultar las notificaciones y los avisos del sistema.',
                    side: 'bottom',
                    align: 'center'
                }
            },

            {
                element: '#ayudaSistema',
                popover: {
                    title: 'Centro de ayuda',
                    description: 'Desde este icono puedes consultar la guía para aprender a utilizar el sistema.',
                    side: 'bottom',
                    align: 'center'
                }
            },


            {
                element: '#dropdownMenuButton .icono-usuario-verde',
                popover: {
                    title: 'Perfil de usuario',
                    description: 'Desde este menú puedes acceder a las opciones de tu perfil y cerrar sesión.',
                    side: 'bottom',
                    align: 'center'
                }
            },


            {
                element: '[data-modulo="footer"]',
                popover: {
                    title: 'Pie de página',
                    description: 'En esta sección se muestra el copyright del sistema. Cuando registres tu empresa, también aparecerá el nombre de tu negocio.',
                    side: 'top',
                    align: 'center'
                }
            },


            {
                element: '#sidebar .sidebar-header .logo',
                popover: {
                    title: 'Logo de la empresa',
                    description: 'Aquí aparecerá la imagen o el logo de tu negocio después de registrarlo en el sistema.',
                    side: 'right',
                    align: 'center'
                }
            },


            {
                element: '#toggle-dark',
                popover: {
                    title: 'Cambiar el tema',
                    description: 'Utiliza este interruptor para cambiar entre el modo claro y el modo oscuro del sistema.',
                    side: 'right',
                    align: 'center'
                }
            },


            {
                element: '#sidebar .sidebar-menu',
                popover: {
                    title: 'Menú de módulos',
                    description: 'Este menú contiene los módulos del sistema. Continuaremos hacia Configuración para mostrarte dónde registrar tu empresa.',
                    side: 'right',
                    align: 'center'
                },
                onHighlightStarted: function () {
                    const sidebar = document.querySelector('#sidebar');
                    const menu = document.querySelector('#sidebar .sidebar-menu');

                    if (sidebar && menu) {
                        // Permitir desplazarse verticalmente por el sidebar
                        sidebar.style.overflowY = 'auto';
                        sidebar.style.overscrollBehavior = 'contain';

                        // Desplazar el menú hasta el final para mostrar Configuración
                        menu.scrollIntoView({
                            behavior: 'smooth',
                            block: 'end'
                        });
                    }
                }
            },

            // 8. CONFIGURACIÓN: ABRIR EL SUBMENÚ
            {
                element: '#menuConfiguracion',
                popover: {
                    title: 'Configuración',
                    description: 'Aquí encontrarás las opciones de configuración. El menú se abrirá para mostrarte la opción Empresa.',
                    side: 'right',
                    align: 'center'
                },
                onHighlightStarted: function () {
                    const menu = document.querySelector('#menuConfiguracion');
                    if (!menu) return;

                    const enlace = menu.querySelector('a.sidebar-link');
                    const submenus = menu.querySelector('ul');

                    if (submenus) {
                        const submenuOculto =
                            getComputedStyle(submenus).display === 'none';

                        if (submenuOculto) {
                            enlace?.click();
                        }

                        // Garantizar que Empresa quede visible
                        submenus.style.display = 'block';
                    }

                    menu.classList.add('active');
                    menu.classList.add('open');

                    // Desplazar el sidebar hasta Configuración
                    menu.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            },


            {
                element: '#enlaceRegistrarEmpresa',
                popover: {
                    title: 'Registrar empresa',
                    description: 'Esta es la opción Empresa. Selecciónala para abrir el formulario y registrar los datos de tu negocio.',
                    side: 'right',
                    align: 'center'
                },
                onHighlightStarted: function () {
                    const empresa = document.querySelector('#enlaceRegistrarEmpresa');

                    if (empresa) {
                        empresa.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }
                }
            }

        ],


        inicio: [
            {
                element: '#calendar',
                popover: {
                    title: 'Calendario de reservas',
                    description: 'Aquí puedes consultar las fechas y las reservas registradas en el calendario.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '.fc-header-toolbar',
                popover: {
                    title: 'Navegación del calendario',
                    description: 'Utiliza Anterior, Siguiente y Hoy para cambiar de fecha. También puedes visualizar el calendario por mes, semana o día.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '.fc-daygrid-day:not(.fc-day-other)',
                popover: {
                    title: 'Seleccionar fecha disponible',
                    description: 'Pulsa una celda del calendario para seleccionar una fecha de hoy o futura e iniciar el registro de una reserva.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#calendar .fc-event',
                popover: {
                    title: 'Reserva registrada',
                    description: 'Aquí aparecen las reservas existentes. Pulsa una reserva para consultar sus detalles.',
                    side: 'top',
                    align: 'center'
                }
            }
        ],


        panel: [],

        clientes: [
            {
                element: '[data-bs-target="#modalRegistrarCliente"]',
                popover: {
                    title: 'Registrar clientes',
                    description: 'Pulsa este botón para abrir el formulario y registrar un nuevo cliente.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de clientes',
                    description: 'Aquí puedes consultar los clientes registrados y sus datos.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar',
                popover: {
                    title: 'Editar cliente',
                    description: 'Este botón permite modificar los datos del cliente seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar',
                popover: {
                    title: 'Eliminar cliente',
                    description: 'Este botón permite iniciar el proceso de eliminación del cliente seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        reservas: [
            {
                element: 'a[href="/admin?ruta=inicio"].btn',
                popover: {
                    title: 'Registrar reserva',
                    description: 'Pulsa este botón para ir al formulario y registrar una nueva reserva.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de reservas',
                    description: 'Aquí puedes consultar las reservas registradas, los datos de los clientes, los servicios, las fechas, las horas y sus estados.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 tbody tr button[data-bs-target="#editModalReserva"]',
                popover: {
                    title: 'Editar reserva',
                    description: 'Este botón permite modificar los datos de una reserva activa.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 tbody tr button[data-bs-target="#deleteModalReservas"]',
                popover: {
                    title: 'Cancelar o eliminar reserva',
                    description: 'Desde este botón puedes iniciar el proceso de cancelación o eliminación de la reserva seleccionada.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        disponibilidad: [
            {
                element: '#tab-estilistas',
                popover: {
                    title: 'Pestaña de estilistas',
                    description: 'Selecciona esta pestaña para consultar la disponibilidad registrada de los estilistas.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Disponibilidad de estilistas',
                    description: 'Aquí puedes consultar la cédula, el especialista, el nombre, la fecha, la hora y el estado de cada registro.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#tab-manicuristas',
                popover: {
                    title: 'Pestaña de manicuristas',
                    description: 'Pulsa aquí para consultar la disponibilidad registrada de las manicuristas.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#table2',
                popover: {
                    title: 'Disponibilidad de manicuristas',
                    description: 'En esta tabla puedes consultar los datos y el estado de las disponibilidades de las manicuristas.',
                    side: 'top',
                    align: 'center'
                }
            }
        ],

        tiposervicio: [],

        promociones: [],

        compras: [],

        proveedores: [],

        productos: [],

        tipoproducto: [],

        marca: [],

        categoria: [],


        unidadmedida: [
            {
                element: '[data-bs-target="#modalRegistrarMedida"]',
                popover: {
                    title: 'Registrar medida',
                    description: 'Pulsa este botón para abrir el formulario y registrar una nueva medida.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de unidades de medida',
                    description: 'Aquí puedes consultar el código, el nombre y el estado de las medidas registradas.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar',
                popover: {
                    title: 'Editar medida',
                    description: 'Pulsa este botón para modificar los datos y el estado  de medida seleccionada.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar',
                popover: {
                    title: 'Eliminar medida',
                    description: 'Pulsa este botón para iniciar el proceso de eliminación de medida seleccionada.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        presentacion: [
            {
                element: '[data-bs-target="#modalRegistrarPresentacion"]',
                popover: {
                    title: 'Registrar presentación',
                    description: 'Pulsa este botón para abrir el formulario y registrar una nueva presentación de producto.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de presentaciones',
                    description: 'Aquí puedes consultar el código, el nombre y el estado de las presentaciones registradas.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar',
                popover: {
                    title: 'Editar presentación',
                    description: 'Pulsa este botón para modificar los datos y el estado de la presentación seleccionada.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar',
                popover: {
                    title: 'Eliminar presentación',
                    description: 'Pulsa este botón para iniciar el proceso de eliminación de la presentación seleccionada.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],



        unidad: [
            {
                element: '[data-bs-target="#modalRegistrarUnidad"]',
                popover: {
                    title: 'Registrar unidad',
                    description: 'Pulsa este botón para abrir el formulario y registrar una nueva unidad de producto, asociando su presentación y medida.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de unidades',
                    description: 'Aquí puedes consultar las unidades registradas, sus presentaciones, medidas y estados.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar',
                popover: {
                    title: 'Editar unidad',
                    description: 'Pulsa este botón para modificar el nombre, la presentación, la medida y el estado de la unidad seleccionada.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar',
                popover: {
                    title: 'Eliminar unidad',
                    description: 'Pulsa este botón para iniciar el proceso de eliminación de la unidad seleccionada.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        misdatos: [
            {
                element: '#tablacliente',
                popover: {
                    title: 'Perfil del usuario',
                    description: 'Aquí puedes consultar tus datos personales, como cédula, nombre, apellido, teléfono, dirección y correo electrónico.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#tablacliente .btn-editar',
                popover: {
                    title: 'Editar datos personales',
                    description: 'Pulsa este botón para abrir el formulario y modificar tu información personal.',
                    side: 'top',
                    align: 'center'
                }
            }
        ],

        misreservas: [
            {
                element: '#table1',
                popover: {
                    title: 'Mis reservas',
                    description: 'Aquí puedes consultar tus reservas, incluyendo el servicio, la fecha, la hora y el estado de cada una.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 tbody tr button[data-bs-target="#deleteModalReservas"]',
                popover: {
                    title: 'Cancelar reserva',
                    description: 'Pulsa este botón para iniciar la cancelación de una reserva activa. Antes de confirmar, podrás revisar la fecha de la reserva.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        reservacliente: [
            {
                element: '#calendar',
                popover: {
                    title: 'Calendario de reservas',
                    description: 'En este calendario puedes consultar las fechas y los horarios de las reservas registradas. y consultar las reservas existentes.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '.fc-header-toolbar',
                popover: {
                    title: 'Navegación del calendario',
                    description: 'Utiliza los botones Anterior, Siguiente y Hoy para desplazarte entre fechas. También puedes cambiar entre las vistas de día, semana y mes, según las opciones disponibles.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#calendar .fc-daygrid-day:not(.fc-day-other), #calendar .fc-timegrid-col',
                popover: {
                    title: 'Seleccionar una fecha',
                    description: 'Selecciona una fecha de hoy o futura para iniciar el proceso de registro de una reserva. No puedes seleccionar fechas anteriores a hoy.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#calendar .fc-event',
                popover: {
                    title: 'Reservas registradas',
                    description: 'Aquí puedes ver las reservas existentes. Pulsa una reserva para consultar sus detalles y revisar su información.',
                    side: 'top',
                    align: 'center'
                }
            }
        ],

       personal: [
            {
                element: '[data-bs-target="#modalRegistrarPersonal"]',
                popover: {
                    title: 'Registrar personal',
                    description: 'Pulsa este botón para abrir el formulario y registrar un nuevo miembro del personal.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de personal',
                    description: 'Aquí puedes consultar el personal registrado, sus datos de contacto y su estado actual.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar',
                popover: {
                    title: 'Editar personal',
                    description: 'Este botón permite modificar los datos o el estado del miembro del personal seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar',
                popover: {
                    title: 'Eliminar personal',
                    description: 'Este botón permite iniciar el proceso de eliminación del miembro del personal seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],
        pagos: [
            {
                element: '[data-bs-target="#modalRegistrarPago"]',
                popover: {
                    title: 'Registrar pago',
                    description: 'Pulsa este botón para registrar un pago. En el formulario podrás seleccionar el cliente y servicio, indicar el monto, adjuntar el comprobante y elegir la moneda y el tipo de pago.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de pagos',
                    description: 'Aquí puedes consultar los pagos registrados, sus montos, monedas, tipos de pago, comprobantes y estados.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 a.btn-outline-primary',
                popover: {
                    title: 'Ver comprobante',
                    description: 'Pulsa este botón para abrir el comprobante adjunto al pago.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-anular',
                popover: {
                    title: 'Anular pago',
                    description: 'Desde aquí puedes iniciar la anulación de un pago activo y confirmar la acción.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        pagospersonal: [
            {
                element: '[data-bs-target="#modalRegistrarPagoPersonal"]',
                popover: {
                    title: 'Registrar pago personal',
                    description: 'Pulsa este botón para registrar el pago de un especialista. El formulario permite seleccionar el servicio, indicar fecha, hora y porcentaje, y completar los datos del pago móvil.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#pagospersonalTable',
                popover: {
                    title: 'Tabla de pagos personales',
                    description: 'Aquí puedes consultar los pagos personales, el servicio, cliente, especialista, montos, fecha y estado.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#pagospersonalTable .btn-detalle-pago-personal',
                popover: {
                    title: 'Ver detalle del pago',
                    description: 'Pulsa este botón para consultar el detalle y el comprobante del pago personal seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#pagospersonalTable .btn-anular-personal',
                popover: {
                    title: 'Anular pago personal',
                    description: 'Desde aquí puedes iniciar la anulación de un pago personal activo y confirmar la acción.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        reportes: [],


        reporte_cliente: [
            {
                element: '#btnPDFCliente',
                popover: {
                    title: 'Generar reporte PDF',
                    description: 'Pulsa este botón para generar y abrir el reporte de clientes en formato PDF.',
                    side: 'bottom',
                    align: 'end'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Reporte de clientes',
                    description: 'Aquí puedes consultar la cédula, el nombre, el apellido, el teléfono, la dirección, el correo y el estado de los clientes registrados.',
                    side: 'top',
                    align: 'center'
                }
            }
        ],



        reporte_reserva: [
            {
                element: '#tab-activas',
                popover: {
                    title: 'Reservas',
                    description: 'En esta pestaña puedes consultar el reporte general de las reservas registradas.',
                    side: 'bottom',
                    align: 'start'
                }
            },

            {
                element: '#btnEstadisticasreservas',
                popover: {
                    title: 'Ir a estadísticas',
                    description: 'Pulsa este botón para acceder al reporte estadístico de las reservas y consultar sus estadísticas.',
                    side: 'bottom',
                    align: 'end'
                }
            },
            {
                element: '.btnReporte[data-reporte="Reporte General de Reservas"]',
                popover: {
                    title: 'Generar reporte PDF',
                    description: 'Pulsa este botón para generar y abrir el reporte general de reservas en formato PDF.',
                    side: 'bottom',
                    align: 'end'
                }
            },
            {
                element: 'form[action="/admin?ruta=reporte_reserva"] button[name="excel"]',
                popover: {
                    title: 'Generar reporte Excel',
                    description: 'Pulsa este botón para exportar el reporte general de reservas a un archivo Excel.',
                    side: 'bottom',
                    align: 'end'
                }
            },
            {
                element: '#fecha_inicio',
                popover: {
                    title: 'Fecha inicial',
                    description: 'Selecciona la fecha desde la que deseas consultar las reservas.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#fecha_fin',
                popover: {
                    title: 'Fecha final',
                    description: 'Selecciona la fecha hasta la que deseas consultar las reservas.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#btnFiltrarFecha',
                popover: {
                    title: 'Filtrar por fechas',
                    description: 'Pulsa este botón para generar el reporte PDF de las reservas dentro del período seleccionado.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#btnLimpiarFecha',
                popover: {
                    title: 'Limpiar fechas',
                    description: 'Pulsa este botón para limpiar las fechas seleccionadas.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: 'select[name="especialista"]',
                popover: {
                    title: 'Seleccionar especialista',
                    description: 'Selecciona un especialista para filtrar las reservas asociadas a él, o elige Todos para incluirlos a todos.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: 'button[name="pdfe"]',
                popover: {
                    title: 'Filtrar por especialista',
                    description: 'Pulsa este botón para generar el reporte PDF de las reservas del especialista seleccionado.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de reservas',
                    description: 'Aquí puedes consultar la cédula del cliente, su nombre, los servicios reservados, la fecha, la hora y el estado de cada reserva.',
                    side: 'top',
                    align: 'center'
                }
            }
        ],


        reporte_reserva_estadistico: [
            {
                element: '#btnEstadistiredevolver',
                popover: {
                    title: 'Volver al reporte de reservas',
                    description: 'Pulsa este botón para regresar al reporte general de reservas.',
                    side: 'bottom',
                    align: 'end'
                }
            },
            {
                element: '#formPDF button[type="submit"]',
                popover: {
                    title: 'Generar reporte PDF',
                    description: 'Pulsa este botón para exportar las estadísticas de reservas a un archivo PDF.',
                    side: 'bottom',
                    align: 'end'
                }
            },
            {
                element: '#formExcel button[type="submit"]',
                popover: {
                    title: 'Generar reporte Excel',
                    description: 'Pulsa este botón para exportar las estadísticas de reservas a un archivo Excel.',
                    side: 'bottom',
                    align: 'end'
                }
            },
            {
                element: '#especialista_reporte',
                popover: {
                    title: 'Seleccionar especialista',
                    description: 'Selecciona un especialista para consultar su reporte individual.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#formPDFEspecialista button[type="submit"]',
                popover: {
                    title: 'Reporte PDF por especialista',
                    description: 'Pulsa este botón para generar el PDF de las reservas del especialista seleccionado.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#cliente_reporte',
                popover: {
                    title: 'Seleccionar cliente',
                    description: 'Selecciona un cliente para consultar su reporte individual de reservas.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#formPDFCliente button[type="submit"]',
                popover: {
                    title: 'Reporte PDF por cliente',
                    description: 'Pulsa este botón para generar el PDF de las reservas del cliente seleccionado.',
                    side: 'bottom',
                    align: 'center'
                }
            },
            {
                element: '#tablaReservasServicio',
                popover: {
                    title: 'Reservas por servicio',
                    description: 'Aquí puedes consultar la cantidad de reservas registradas para cada servicio.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#tablaReservasEspecialista',
                popover: {
                    title: 'Reservas por especialista',
                    description: 'Aquí puedes consultar la cantidad de reservas que tiene registradas cada especialista.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#tablaTopClientes',
                popover: {
                    title: 'Top clientes',
                    description: 'Aquí puedes consultar los clientes que acumulan la mayor cantidad de reservas.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#tablaUltimasReservas',
                popover: {
                    title: 'Últimas reservas',
                    description: 'Aquí puedes consultar las reservas recientes, con sus clientes, especialistas, fechas, horarios y estados.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#graficoDias',
                popover: {
                    title: 'Reservas por día',
                    description: 'Este gráfico muestra cómo se distribuyen las reservas durante los días de la semana.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#graficoHorarios',
                popover: {
                    title: 'Horarios más solicitados',
                    description: 'Aquí puedes observar cuáles son los horarios que registran mayor demanda de reservas.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#graficoTendencia',
                popover: {
                    title: 'Tendencia mensual',
                    description: 'Este gráfico permite observar la evolución de las reservas a lo largo de los meses.',
                    side: 'top',
                    align: 'center'
                }
            }
        ],

        reporte_producto: [],

        reporte_pago: [],

        'rep-pagos-estadistico': [],


        empresa: [
           
            {
                element: '#contenedorEmpresas',
                popover: {
                    title: 'Gestión de empresa',
                    description: 'En esta sección puedes registrar tu empresa si todavía no existe, o consultar sus datos cuando ya está registrada.',
                    side: 'bottom',
                    align: 'center'
                }
            },

            // 2. REGISTRAR EMPRESA
            {
                element: '#btnCerrarModal',
                popover: {
                    title: 'Registrar empresa',
                    description: 'Pulsa este botón para abrir el formulario y registrar los datos de tu empresa.',
                    side: 'bottom',
                    align: 'center'
                }
            },

            // 3. EDITAR EMPRESA
            {
                element: '#contenedorEmpresas button[data-bs-target="#exampleModal"]',
                popover: {
                    title: 'Editar empresa',
                    description: 'Pulsa este botón para abrir el formulario y modificar los datos de la empresa registrada.',
                    side: 'top',
                    align: 'center'
                }
            }
        ],


        usuarios: [
            {
                element: '[data-bs-target="#primary"]',
                popover: {
                    title: 'Registrar usuarios',
                    description: 'Pulsa este botón para abrir el formulario y registrar un nuevo usuario del sistema.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de usuarios',
                    description: 'Aquí puedes consultar la cédula, el nombre de usuario, el rol y el estado de los usuarios registrados.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar',
                popover: {
                    title: 'Editar usuario',
                    description: 'Pulsa este botón para modificar los datos personales, el rol y el estado del usuario seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar',
                popover: {
                    title: 'Eliminar usuario',
                    description: 'Pulsa este botón para iniciar el proceso de eliminación del usuario seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],


        rol: [
            {
                element: '[data-bs-target="#Rol"]',
                popover: {
                    title: 'Registrar rol',
                    description: 'Pulsa este botón para abrir el formulario y registrar un nuevo rol en el sistema.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de roles',
                    description: 'Aquí puedes consultar los códigos, los nombres y los estados de los roles registrados.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar:not(:disabled)',
                popover: {
                    title: 'Editar rol',
                    description: 'Pulsa este botón para modificar los datos del rol seleccionado. El rol protegido no se puede editar.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar:not(:disabled)',
                popover: {
                    title: 'Eliminar rol',
                    description: 'Pulsa este botón para iniciar el proceso de eliminación del rol seleccionado. El rol protegido no se puede eliminar.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],



        permisos: [
            {
                element: '[data-bs-target="#modalPermisos"]',
                popover: {
                    title: 'Registrar permisos',
                    description: 'Pulsa este botón para abrir el formulario y asignar permisos a un usuario según su rol.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de permisos',
                    description: 'Aquí puedes consultar los usuarios, sus roles y el estado de los permisos asignados.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar',
                popover: {
                    title: 'Editar permisos',
                    description: 'Pulsa este botón para modificar los permisos y el estado de los permisos del usuario seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar',
                popover: {
                    title: 'Eliminar permisos',
                    description: 'Pulsa este botón para iniciar el proceso de eliminación de los permisos asignados al usuario seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        especialidad: [
            {
                element: '[data-bs-target="#primary"]',
                popover: {
                    title: 'Registrar especialista',
                    description: 'Pulsa este botón para abrir el formulario y registrar un nuevo especialista con su especialidad correspondiente.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de especialistas',
                    description: 'Aquí puedes consultar la cédula, la especialidad, el nombre, el apellido y el estado de cada especialista registrado.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar',
                popover: {
                    title: 'Editar especialista',
                    description: 'Pulsa este botón para modificar la especialidad y el estado del especialista seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar',
                popover: {
                    title: 'Eliminar especialista',
                    description: 'Pulsa este botón para iniciar el proceso de eliminación del especialista seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],


        tipopago: [
            {
                element: '[data-bs-target="#modalRegistrarTipoPago"]',
                popover: {
                    title: 'Registrar tipo de pago',
                    description: 'Pulsa este botón para abrir el formulario y registrar un nuevo tipo de pago.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de tipos de pago',
                    description: 'Aquí puedes consultar los tipos de pago registrados y sus datos.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar',
                popover: {
                    title: 'Editar tipo de pago',
                    description: 'Este botón permite modificar los datos del tipo de pago seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar',
                popover: {
                    title: 'Eliminar tipo de pago',
                    description: 'Este botón permite iniciar el proceso de eliminación del tipo de pago seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        moneda: [
             {
                element: '[data-bs-target="#modalRegistrarMoneda"]',
                popover: {
                    title: 'Registrar moneda',
                    description: 'Pulsa este botón para abrir el formulario y registrar una nueva moneda.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Tabla de monedas',
                    description: 'Aquí puedes consultar las monedas registradas y sus datos.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-editar',
                popover: {
                    title: 'Editar moneda',
                    description: 'Este botón permite modificar los datos de la moneda seleccionada.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-eliminar',
                popover: {
                    title: 'Eliminar moneda',
                    description: 'Este botón permite iniciar el proceso de eliminación de la moneda seleccionada.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        mantenimiento: [
            {
                element: '#btnCrearBackup',
                popover: {
                    title: 'Crear respaldo',
                    description: 'Pulsa este botón para generar un nuevo respaldo de la base de datos.',
                    side: 'bottom',
                    align: 'start'
                }
            },
            {
                element: '#table1',
                popover: {
                    title: 'Respaldos disponibles',
                    description: 'Aquí puedes consultar los respaldos guardados, su tamaño y fecha.',
                    side: 'top',
                    align: 'center'
                }
            },
            {
                element: '#table1 a.btn-primary',
                popover: {
                    title: 'Descargar respaldo',
                    description: 'Pulsa este botón para descargar el archivo de respaldo seleccionado.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 button[data-bs-target="#modalRestaurarBackup"]',
                popover: {
                    title: 'Restaurar respaldo',
                    description: 'Abre el formulario para seleccionar y restaurar un archivo de respaldo SQL.',
                    side: 'left',
                    align: 'center'
                }
            },
            {
                element: '#table1 .btn-limpiar',
                popover: {
                    title: 'Eliminar respaldo',
                    description: 'Inicia la eliminación del respaldo seleccionado. Confirma la acción en el cuadro que aparece.',
                    side: 'left',
                    align: 'center'
                }
            }
        ],

        bitacora: []
    };


    botonAyuda.addEventListener('click', function (event) {
        event.preventDefault();


        const empresaConfigurada =
            document.body.dataset.empresaConfigurada === 'true';

        const modulos = [...document.querySelectorAll('[data-modulo]')];

        const contenedorPagina = modulos.find(function (elemento) {
            return !['header', 'footer', 'primeravessistema'].includes(
                elemento.dataset.modulo
            );
        });

        let moduloActual;
        let listaPasos;

        if (!empresaConfigurada) {
            moduloActual = 'primeravessistema';
            listaPasos = pasos.primeravessistema;
        } else {
            moduloActual = contenedorPagina?.dataset.modulo || 'encabezado';
            listaPasos = pasos[moduloActual] || pasos.encabezado;
        }

        const pasosValidos = listaPasos.filter(function (paso) {
            const elemento = document.querySelector(paso.element);

            if (!elemento) return false;

            if (moduloActual === 'clientes' || moduloActual === 'reservas' || moduloActual === 'personal' || moduloActual === 'moneda' || moduloActual === 'tipopago' || moduloActual === 'pagos' || moduloActual === 'mantenimiento' || moduloActual === 'pagospersonal') {
                const selectorTabla = moduloActual === 'pagospersonal' ? '#pagospersonalTable' : '#table1';
                const tabla = document.querySelector(selectorTabla);
                const filas = tabla?.querySelectorAll('tbody tr') || [];

                if ((paso.element === '#table1' || paso.element === '#pagospersonalTable') && filas.length === 0) {
                    return false;
                }

                if (
                    paso.element.includes('.btn-editar') ||
                    paso.element.includes('.btn-eliminar') ||
                    paso.element.includes('.btn-anular') ||
                    paso.element.includes('a.btn-outline-primary') ||
                    paso.element.includes('a.btn-primary') ||
                    paso.element.includes('modalRestaurarBackup') ||
                    paso.element.includes('.btn-limpiar') ||
                    paso.element.includes('.btn-detalle-pago-personal') ||
                    paso.element.includes('.btn-anular-personal') ||
                    paso.element.includes('editModalReserva') ||
                    paso.element.includes('deleteModalReservas')
                ) {
                    return filas.length > 0;
                }
            }

            if (moduloActual === 'disponibilidad') {
                const tablaEstilistas = document.querySelector('#table1');
                const tablaManicuristas = document.querySelector('#table2');

                const filasEstilistas =
                    tablaEstilistas?.querySelectorAll('tbody tr') || [];

                const filasManicuristas =
                    tablaManicuristas?.querySelectorAll('tbody tr') || [];

                if (paso.element === '#table1') {
                    return filasEstilistas.length > 0;
                }

                if (paso.element === '#table2') {
                    return filasManicuristas.length > 0;
                }
            }

            if (moduloActual === 'unidadmedida') {
                const tabla = document.querySelector('#table1');
                const filas = tabla?.querySelectorAll('tbody tr') || [];

                if (paso.element === '#table1' && filas.length === 0) {
                    return false;
                }

                if (
                    paso.element.includes('.btn-editar') ||
                    paso.element.includes('.btn-eliminar')
                ) {
                    return filas.length > 0;
                }
            }

            if (moduloActual === 'presentacion') {
                const tabla = document.querySelector('#table1');
                const filas = tabla?.querySelectorAll('tbody tr') || [];

                if (paso.element === '#table1' && filas.length === 0) {
                    return false;
                }

                if (
                    paso.element.includes('.btn-editar') ||
                    paso.element.includes('.btn-eliminar')
                ) {
                    return filas.length > 0;
                }
            }

            if (moduloActual === 'unidad') {
                const tabla = document.querySelector('#table1');
                const filas = tabla?.querySelectorAll('tbody tr') || [];

                if (paso.element === '#table1' && filas.length === 0) {
                    return false;
                }

                if (
                    paso.element.includes('.btn-editar') ||
                    paso.element.includes('.btn-eliminar')
                ) {
                    return filas.length > 0;
                }
            }

            if (moduloActual === 'usuarios') {
                const tabla = document.querySelector('#table1');
                const filas = tabla?.querySelectorAll('tbody tr') || [];

                if (paso.element === '#table1' && filas.length === 0) {
                    return false;
                }

                if (
                    paso.element.includes('.btn-editar') ||
                    paso.element.includes('.btn-eliminar')
                ) {
                    return filas.length > 0;
                }
            }

            if (moduloActual === 'rol') {
                const tabla = document.querySelector('#table1');
                const filas = tabla?.querySelectorAll('tbody tr') || [];

                if (paso.element === '#table1' && filas.length === 0) {
                    return false;
                }

                if (
                    paso.element.includes('.btn-editar') ||
                    paso.element.includes('.btn-eliminar')
                ) {
                    return filas.length > 0 &&
                        tabla.querySelector(paso.element) !== null;
                }
            }

            if (moduloActual === 'permisos') {
                const tabla = document.querySelector('#table1');
                const filas = tabla?.querySelectorAll('tbody tr') || [];

                if (paso.element === '#table1' && filas.length === 0) {
                    return false;
                }

                if (
                    paso.element.includes('.btn-editar') ||
                    paso.element.includes('.btn-eliminar')
                ) {
                    return filas.length > 0;
                }
            }

            if (moduloActual === 'especialidad') {
                const tabla = document.querySelector('#table1');
                const filas = tabla?.querySelectorAll('tbody tr') || [];

                if (paso.element === '#table1' && filas.length === 0) {
                    return false;
                }

                if (
                    paso.element.includes('.btn-editar') ||
                    paso.element.includes('.btn-eliminar')
                ) {
                    return filas.length > 0;
                }
            }


            if (moduloActual === 'reporte_cliente') {
                const tabla = document.querySelector('#table1');
                const filas = tabla?.querySelectorAll('tbody tr') || [];

                if (paso.element === '#table1' && filas.length === 0) {
                    return false;
                }
            }
            if (moduloActual === 'reporte_reserva') {
                const tabla = document.querySelector('#table1');
                const filas = tabla?.querySelectorAll('tbody tr') || [];

                if (paso.element === '#table1' && filas.length === 0) {
                    return false;
                }
            }




            return true;
        });

        if (!pasosValidos.length) return;

        const manual = window.driver.js.driver({
            animate: true,
            smoothScroll: true,
            showProgress: true,
            allowClose: true,
            overlayClickNext: false,
            stagePadding: 8,
            stageRadius: 10,
            popoverOffset: 15,
            popoverClass: 'ayuda-personalizada',
            nextBtnText: 'Siguiente',
            prevBtnText: 'Anterior',
            doneBtnText: 'Finalizar',
            progressText: '{{current}} de {{total}}',
            steps: pasosValidos
        });

        manual.drive();
    });
});
