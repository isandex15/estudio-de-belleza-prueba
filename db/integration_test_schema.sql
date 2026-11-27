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

INSERT INTO usuario (cedula, status)
VALUES ('CI00000001', 1)
ON DUPLICATE KEY UPDATE status = VALUES(status);

INSERT INTO usuario (cedula, status)
VALUES ('4723317', 1)
ON DUPLICATE KEY UPDATE status = VALUES(status);

INSERT INTO rol (cod_rol, rol, status)
VALUES (1, 'administrador', 1)
ON DUPLICATE KEY UPDATE rol = VALUES(rol), status = VALUES(status);

INSERT INTO acciones (cod_accion, nombre_accion, status)
VALUES (1, 'registrar', 1)
ON DUPLICATE KEY UPDATE nombre_accion = VALUES(nombre_accion), status = VALUES(status);

INSERT INTO modulos (cod_modulo, nombre_modulo, status)
VALUES (1, 'compra', 1)
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
    PRIMARY KEY (cod_servicio)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_servicio (
    cod_detalle_servicio INT NOT NULL AUTO_INCREMENT,
    cod_tipo_servicio INT NOT NULL,
    PRIMARY KEY (cod_detalle_servicio)
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
VALUES (1, 'Servicio CI', 35.50, 1)
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
