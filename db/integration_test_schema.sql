-- Esquema minimo y datos ficticios para pytest/test/pruebas de integracion.
-- Cargar solamente en una instancia MySQL dedicada a pruebas.

CREATE DATABASE IF NOT EXISTS sac
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS seguridad
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

ALTER DATABASE sac
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
ALTER DATABASE seguridad
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE seguridad;

CREATE TABLE IF NOT EXISTS usuario (
    cedula VARCHAR(12) NOT NULL,
    nombre_usuario VARCHAR(50) NOT NULL DEFAULT 'Usuario',
    apellido_usuario VARCHAR(50) NOT NULL DEFAULT 'Pruebas',
    password VARCHAR(250) NOT NULL DEFAULT '',
    telefono VARCHAR(12) NOT NULL DEFAULT '',
    direccion VARCHAR(200) NOT NULL DEFAULT '',
    correo VARCHAR(100) NOT NULL DEFAULT '',
    status TINYINT(1) NOT NULL,
    cod_rol INT NOT NULL DEFAULT 1,
    intentos_fallidos INT DEFAULT 0,
    ultimo_acceso DATETIME DEFAULT NULL,
    fecha_registro DATE DEFAULT NULL,
    PRIMARY KEY (cedula)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS rol (
    cod_rol INT NOT NULL,
    rol VARCHAR(50) NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_rol)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS acciones (
    cod_accion INT NOT NULL,
    nombre_accion VARCHAR(50) NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_accion)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS modulos (
    cod_modulo INT NOT NULL,
    nombre_modulo VARCHAR(50) NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_modulo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS permiso (
    cod_permiso INT NOT NULL,
    status TINYINT(1) NOT NULL,
    cod_modulo INT NOT NULL,
    cod_accion INT NOT NULL,
    PRIMARY KEY (cod_permiso)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS rol_permiso (
    cod_rol_permiso INT NOT NULL,
    cor_rol INT NOT NULL,
    cod_permiso INT NOT NULL,
    PRIMARY KEY (cod_rol_permiso)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS bitacora (
    cod_bitacora INT NOT NULL AUTO_INCREMENT,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    cedula VARCHAR(12) NOT NULL,
    status TINYINT(1) NOT NULL,
    movimiento VARCHAR(250) DEFAULT NULL,
    PRIMARY KEY (cod_bitacora)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mantenimiento (
    cod_mantenimiento INT NOT NULL AUTO_INCREMENT,
    nombre_archivo VARCHAR(250) NOT NULL,
    tamano VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    cedula_usuario VARCHAR(12) NOT NULL,
    PRIMARY KEY (cod_mantenimiento),
    UNIQUE KEY uq_ci_mantenimiento_archivo (nombre_archivo)
) ENGINE=InnoDB;

INSERT INTO usuario (cedula, status)
VALUES ('CI00000001', 1)
ON DUPLICATE KEY UPDATE status = VALUES(status);

INSERT INTO usuario (cedula, status)
VALUES ('4723317', 1)
ON DUPLICATE KEY UPDATE status = VALUES(status);

INSERT INTO usuario (cedula, nombre_usuario, apellido_usuario, status, cod_rol)
VALUES
    ('3123446', 'Especialista', 'CI', 1, 2),
    ('3196486', 'Cliente', 'CI', 1, 3)
ON DUPLICATE KEY UPDATE
    nombre_usuario = VALUES(nombre_usuario),
    apellido_usuario = VALUES(apellido_usuario),
    status = VALUES(status),
    cod_rol = VALUES(cod_rol);

INSERT INTO rol (cod_rol, rol, status)
VALUES
    (1, 'administrador', 1),
    (2, 'empleado', 1),
    (3, 'cliente', 1)
ON DUPLICATE KEY UPDATE rol = VALUES(rol), status = VALUES(status);

INSERT INTO acciones (cod_accion, nombre_accion, status)
VALUES
    (1, 'registrar', 1),
    (2, 'editar', 1)
ON DUPLICATE KEY UPDATE nombre_accion = VALUES(nombre_accion), status = VALUES(status);

INSERT INTO modulos (cod_modulo, nombre_modulo, status)
VALUES
    (1, 'compra', 1),
    (2, 'servicio', 1),
    (3, 'producto', 1)
ON DUPLICATE KEY UPDATE nombre_modulo = VALUES(nombre_modulo), status = VALUES(status);

INSERT INTO permiso (cod_permiso, status, cod_modulo, cod_accion)
VALUES (1, 1, 1, 1)
ON DUPLICATE KEY UPDATE status = VALUES(status), cod_modulo = VALUES(cod_modulo), cod_accion = VALUES(cod_accion);

INSERT INTO rol_permiso (cod_rol_permiso, cor_rol, cod_permiso)
VALUES (1, 1, 1)
ON DUPLICATE KEY UPDATE cor_rol = VALUES(cor_rol), cod_permiso = VALUES(cod_permiso);

USE sac;

CREATE TABLE IF NOT EXISTS empresa (
    nombre VARCHAR(200) NOT NULL,
    direccion VARCHAR(250) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    descripcion_empresa VARCHAR(250) NOT NULL,
    logo VARCHAR(250) DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categoria (
    cod_categoria INT NOT NULL AUTO_INCREMENT,
    nombre_categoria VARCHAR(50) NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_categoria)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS marca (
    cod_marca INT NOT NULL AUTO_INCREMENT,
    nombre_marca VARCHAR(100) NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_marca)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tipo_producto (
    cod_tipo_producto INT NOT NULL AUTO_INCREMENT,
    nombre_tipo_producto VARCHAR(50) NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_tipo_producto)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tipo_servicio (
    cod_tipo_servicio INT NOT NULL AUTO_INCREMENT,
    nombre_servicio VARCHAR(50) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_tipo_servicio)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS presentacion (
    cod_presentacion INT NOT NULL AUTO_INCREMENT,
    presentacion VARCHAR(100) NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_presentacion)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS medida (
    cod_medida INT NOT NULL AUTO_INCREMENT,
    medida VARCHAR(50) NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_medida)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS unidad (
    cod_unidad INT NOT NULL AUTO_INCREMENT,
    nombre_unidad VARCHAR(100) NOT NULL,
    cod_presentacion INT NOT NULL,
    status TINYINT(1) NOT NULL,
    cod_medida INT NOT NULL,
    PRIMARY KEY (cod_unidad),
    CONSTRAINT fk_ci_unidad_presentacion
        FOREIGN KEY (cod_presentacion) REFERENCES presentacion (cod_presentacion),
    CONSTRAINT fk_ci_unidad_medida
        FOREIGN KEY (cod_medida) REFERENCES medida (cod_medida)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS proveedor (
    cod_proveedor INT NOT NULL AUTO_INCREMENT,
    cedula VARCHAR(12) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    rif VARCHAR(50) NOT NULL,
    telefono VARCHAR(12) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_proveedor),
    UNIQUE KEY uq_ci_proveedor_cedula (cedula)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS producto (
    cod_producto INT NOT NULL AUTO_INCREMENT,
    nombre_producto VARCHAR(50) NOT NULL,
    precio_producto DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    cod_categoria INT NOT NULL,
    cod_marca INT NOT NULL,
    cod_unidad INT NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_producto),
    CONSTRAINT fk_ci_producto_categoria
        FOREIGN KEY (cod_categoria) REFERENCES categoria (cod_categoria),
    CONSTRAINT fk_ci_producto_marca
        FOREIGN KEY (cod_marca) REFERENCES marca (cod_marca),
    CONSTRAINT fk_ci_producto_unidad
        FOREIGN KEY (cod_unidad) REFERENCES unidad (cod_unidad)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_producto (
    cod_detalle_producto INT NOT NULL AUTO_INCREMENT,
    fecha_vencimiento DATE NOT NULL,
    cod_producto INT NOT NULL,
    cod_tipo_producto INT NOT NULL,
    PRIMARY KEY (cod_detalle_producto),
    UNIQUE KEY uq_ci_detalle_producto_producto (cod_producto),
    CONSTRAINT fk_ci_detalle_producto_producto
        FOREIGN KEY (cod_producto) REFERENCES producto (cod_producto)
        ON DELETE CASCADE,
    CONSTRAINT fk_ci_detalle_producto_tipo
        FOREIGN KEY (cod_tipo_producto) REFERENCES tipo_producto (cod_tipo_producto)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS promocion (
    cod_promo INT NOT NULL AUTO_INCREMENT,
    descuento INT NOT NULL,
    nombre_promo VARCHAR(100) NOT NULL,
    descripcion_promo VARCHAR(250) NOT NULL,
    imagen_promo VARCHAR(250) DEFAULT NULL,
    inicio_promo DATE NOT NULL,
    fin_promo DATE NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_promo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS servicio (
    cod_servicio INT NOT NULL AUTO_INCREMENT,
    cod_promo INT DEFAULT NULL,
    cedula VARCHAR(12) NOT NULL,
    descripcion VARCHAR(500) DEFAULT NULL,
    fecha DATE NOT NULL,
    hora VARCHAR(20) NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 1,
    cedula_especialista VARCHAR(12) NOT NULL,
    PRIMARY KEY (cod_servicio)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS especialista (
    cedula_especialista VARCHAR(12) NOT NULL,
    especialista VARCHAR(100) NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (cedula_especialista)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS disponibilidad_especialista (
    cod_disponibilidad INT NOT NULL AUTO_INCREMENT,
    fecha_disponibilidad DATE NOT NULL,
    hora_disponibilidad VARCHAR(20) NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 1,
    cedula_especialista VARCHAR(12) NOT NULL,
    PRIMARY KEY (cod_disponibilidad)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS conteo_stock (
    cod_conteo INT NOT NULL AUTO_INCREMENT,
    conteo INT NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 1,
    cod_producto INT NOT NULL,
    PRIMARY KEY (cod_conteo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_servicio (
    cod_detalle_servicio INT NOT NULL AUTO_INCREMENT,
    cantidad_servicio VARCHAR(20) NOT NULL DEFAULT '1',
    cod_servicio INT NOT NULL,
    cod_tipo_servicio INT NOT NULL,
    cod_producto INT DEFAULT NULL,
    PRIMARY KEY (cod_detalle_servicio)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pago (
    cod_pago INT NOT NULL AUTO_INCREMENT,
    fecha_pago DATE NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    comprobante_pago VARCHAR(300) NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 1,
    cod_servicio INT NOT NULL,
    PRIMARY KEY (cod_pago)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tipo_pago (
    cod_tipo_pago INT NOT NULL AUTO_INCREMENT,
    nombre_tipo_pago VARCHAR(100) NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (cod_tipo_pago)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS moneda (
    cod_moneda INT NOT NULL AUTO_INCREMENT,
    nombre_moneda VARCHAR(100) NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (cod_moneda)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cambio (
    cod_cambio INT NOT NULL AUTO_INCREMENT,
    valor DECIMAL(12,4) NOT NULL,
    fecha DATE NOT NULL,
    cod_moneda INT NOT NULL,
    PRIMARY KEY (cod_cambio)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_pago (
    cod_detalle_pago INT NOT NULL AUTO_INCREMENT,
    cantidad VARCHAR(250) NOT NULL,
    cod_pago INT NOT NULL,
    cod_tipo_pago INT NOT NULL,
    cod_moneda INT NOT NULL,
    PRIMARY KEY (cod_detalle_pago)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS banco (
    cod_banco INT NOT NULL AUTO_INCREMENT,
    nombre_banco VARCHAR(100) NOT NULL,
    PRIMARY KEY (cod_banco)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pago_personal (
    cod_pago_personal INT NOT NULL AUTO_INCREMENT,
    fecha_pago DATE NOT NULL,
    hora_pago TIME NOT NULL,
    porcentaje INT NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 1,
    cod_servicio INT NOT NULL,
    comprobante VARCHAR(250) DEFAULT NULL,
    cod_banco INT DEFAULT NULL,
    referencia_pago VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (cod_pago_personal),
    UNIQUE KEY uq_ci_pago_personal_referencia (referencia_pago)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS compra (
    cod_compra INT NOT NULL AUTO_INCREMENT,
    fecha_compra DATE NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    cod_proveedor INT NOT NULL,
    status TINYINT(1) NOT NULL,
    PRIMARY KEY (cod_compra),
    CONSTRAINT fk_ci_compra_proveedor
        FOREIGN KEY (cod_proveedor) REFERENCES proveedor (cod_proveedor)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_compra (
    cod_detalle_compra INT NOT NULL AUTO_INCREMENT,
    cod_compra INT NOT NULL,
    cod_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (cod_detalle_compra),
    CONSTRAINT fk_ci_detalle_compra_compra
        FOREIGN KEY (cod_compra) REFERENCES compra (cod_compra),
    CONSTRAINT fk_ci_detalle_compra_producto
        FOREIGN KEY (cod_producto) REFERENCES producto (cod_producto)
) ENGINE=InnoDB;

INSERT INTO categoria (cod_categoria, nombre_categoria, status)
VALUES (1, 'Categoria CI', 1)
ON DUPLICATE KEY UPDATE nombre_categoria = VALUES(nombre_categoria), status = VALUES(status);

INSERT INTO marca (cod_marca, nombre_marca, status)
VALUES (1, 'Marca CI', 1)
ON DUPLICATE KEY UPDATE nombre_marca = VALUES(nombre_marca), status = VALUES(status);

INSERT INTO tipo_producto (cod_tipo_producto, nombre_tipo_producto, status)
VALUES (1, 'Tipo CI', 1)
ON DUPLICATE KEY UPDATE nombre_tipo_producto = VALUES(nombre_tipo_producto), status = VALUES(status);

INSERT INTO tipo_servicio (cod_tipo_servicio, nombre_servicio, precio, status)
VALUES
    (1, 'Servicio CI', 35.50, 1),
    (2, 'Servicio CI 2', 25.00, 1),
    (3, 'Servicio CI 3', 15.00, 1)
ON DUPLICATE KEY UPDATE nombre_servicio = VALUES(nombre_servicio), precio = VALUES(precio), status = VALUES(status);

INSERT INTO presentacion (cod_presentacion, presentacion, status)
VALUES (1, 'Unidad CI', 1)
ON DUPLICATE KEY UPDATE presentacion = VALUES(presentacion), status = VALUES(status);

INSERT INTO medida (cod_medida, medida, status)
VALUES (1, 'Unidad CI', 1)
ON DUPLICATE KEY UPDATE medida = VALUES(medida), status = VALUES(status);

INSERT INTO unidad (cod_unidad, nombre_unidad, cod_presentacion, status, cod_medida)
VALUES (1, 'Unidad CI', 1, 1, 1)
ON DUPLICATE KEY UPDATE nombre_unidad = VALUES(nombre_unidad), status = VALUES(status);

INSERT INTO proveedor (cod_proveedor, cedula, nombre, apellido, rif, telefono, correo, status)
VALUES (1, 'CI00000002', 'Proveedor', 'Pruebas', 'J-CI-0002', '04120000002', 'proveedor-ci@example.test', 1)
ON DUPLICATE KEY UPDATE status = VALUES(status);

INSERT INTO producto (
    cod_producto,
    nombre_producto,
    precio_producto,
    stock,
    cod_categoria,
    cod_marca,
    cod_unidad,
    status
)
VALUES (1, 'Producto CI', 10.00, 10, 1, 1, 1, 1)
ON DUPLICATE KEY UPDATE status = VALUES(status);

INSERT INTO detalle_producto (
    fecha_vencimiento,
    cod_producto,
    cod_tipo_producto
)
VALUES ('2030-01-01', 1, 1)
ON DUPLICATE KEY UPDATE cod_tipo_producto = VALUES(cod_tipo_producto);

INSERT INTO especialista (cedula_especialista, especialista, status)
VALUES ('3123446', 'Especialista CI', 1)
ON DUPLICATE KEY UPDATE especialista = VALUES(especialista), status = VALUES(status);

INSERT INTO conteo_stock (conteo, status, cod_producto)
VALUES (1, 1, 1);

INSERT INTO servicio (
    cod_servicio, cedula, descripcion, fecha, hora, status, cedula_especialista
)
VALUES (
    1, '3196486', 'Reserva CI', CURRENT_DATE, '08:00 AM', 1, '3123446'
);

INSERT INTO detalle_servicio (
    cantidad_servicio, cod_servicio, cod_tipo_servicio, cod_producto
)
VALUES ('1', 1, 1, NULL);

INSERT INTO disponibilidad_especialista (
    fecha_disponibilidad, hora_disponibilidad, status, cedula_especialista
)
VALUES (CURRENT_DATE, '08:00 AM', 1, '3123446');

INSERT INTO tipo_pago (cod_tipo_pago, nombre_tipo_pago, status)
VALUES (1, 'Efectivo CI', 1)
ON DUPLICATE KEY UPDATE nombre_tipo_pago = VALUES(nombre_tipo_pago), status = VALUES(status);

INSERT INTO moneda (cod_moneda, nombre_moneda, status)
VALUES (1, 'Dolar CI', 1)
ON DUPLICATE KEY UPDATE nombre_moneda = VALUES(nombre_moneda), status = VALUES(status);
