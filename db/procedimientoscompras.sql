/* Objetos de compras, catalogos y auditoria.
   Ejecutar despues de crear las bases sac y seguridad. */

USE sac;

/* Indices de busqueda */
DROP INDEX IF EXISTS idx_tipo_servicio_nombre ON tipo_servicio;
DROP INDEX IF EXISTS idx_tipo_producto_nombre ON tipo_producto;
DROP INDEX IF EXISTS idx_categoria_nombre ON categoria;
DROP INDEX IF EXISTS idx_compra_fecha_proveedor ON compra;
CREATE INDEX idx_tipo_servicio_nombre ON tipo_servicio (nombre_servicio);
CREATE INDEX idx_tipo_producto_nombre ON tipo_producto (nombre_tipo_producto);
CREATE INDEX idx_categoria_nombre ON categoria (nombre_categoria);
CREATE INDEX idx_compra_fecha_proveedor ON compra (fecha_compra, cod_proveedor);

/* Vistas de consulta */
DROP VIEW IF EXISTS v_compras_detalladas;
CREATE VIEW v_compras_detalladas AS
SELECT
    c.cod_compra,
    c.fecha_compra,
    c.total,
    c.status,
    c.cod_proveedor,
    CONCAT(p.nombre, ' ', p.apellido) AS proveedor,
    dc.cod_detalle_compra,
    dc.cod_producto,
    pr.nombre_producto,
    dc.cantidad,
    dc.precio_unitario,
    dc.cantidad * dc.precio_unitario AS subtotal
FROM compra AS c
INNER JOIN proveedor AS p ON p.cod_proveedor = c.cod_proveedor
LEFT JOIN detalle_compra AS dc ON dc.cod_compra = c.cod_compra
LEFT JOIN producto AS pr ON pr.cod_producto = dc.cod_producto;

DROP VIEW IF EXISTS v_productos_categoria_marca;
CREATE VIEW v_productos_categoria_marca AS
SELECT
    pr.cod_producto,
    pr.nombre_producto,
    pr.precio_producto,
    pr.stock,
    pr.status,
    ca.cod_categoria,
    ca.nombre_categoria,
    ma.cod_marca,
    ma.nombre_marca,
    (
        SELECT tp.nombre_tipo_producto
        FROM detalle_producto AS dp
        INNER JOIN tipo_producto AS tp
            ON tp.cod_tipo_producto = dp.cod_tipo_producto
        WHERE dp.cod_producto = pr.cod_producto
        ORDER BY dp.cod_detalle_producto
        LIMIT 1
    ) AS nombre_tipo_producto
FROM producto AS pr
LEFT JOIN categoria AS ca ON ca.cod_categoria = pr.cod_categoria
LEFT JOIN marca AS ma ON ma.cod_marca = pr.cod_marca;

DROP VIEW IF EXISTS v_tipos_servicios_activos;
CREATE VIEW v_tipos_servicios_activos AS
SELECT cod_tipo_servicio, nombre_servicio, precio
FROM tipo_servicio
WHERE status = 1;

/* Funciones */
DROP FUNCTION IF EXISTS fn_calcular_total_compra;
DELIMITER //
CREATE FUNCTION fn_calcular_total_compra(p_cod_compra INT)
RETURNS DECIMAL(12,2)
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(12,2);

    SELECT COALESCE(SUM(cantidad * precio_unitario), 0)
      INTO v_total
      FROM detalle_compra
     WHERE cod_compra = p_cod_compra;

    RETURN v_total;
END //
DELIMITER ;

DROP FUNCTION IF EXISTS fn_obtener_stock_producto;
DELIMITER //
CREATE FUNCTION fn_obtener_stock_producto(p_cod_producto INT)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_stock INT;

    SELECT stock INTO v_stock
      FROM producto
     WHERE cod_producto = p_cod_producto;

    RETURN COALESCE(v_stock, 0);
END //
DELIMITER ;

/* Procedimientos basicos */
DROP PROCEDURE IF EXISTS sp_actualizar_producto;
DELIMITER //
CREATE PROCEDURE sp_actualizar_producto(
    IN p_cod_producto INT,
    IN p_cantidad INT
)
BEGIN
    IF p_cantidad = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cantidad no puede ser cero.';
    END IF;

    UPDATE producto
       SET stock = stock + p_cantidad
     WHERE cod_producto = p_cod_producto
       AND status = 1;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El producto no existe o esta inactivo.';
    END IF;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_registrar_bitacora;
DELIMITER //
CREATE PROCEDURE sp_registrar_bitacora(
    IN p_cedula VARCHAR(12),
    IN p_movimiento VARCHAR(250)
)
BEGIN
    INSERT INTO seguridad.bitacora (fecha, hora, cedula, status, movimiento)
    VALUES (CURRENT_DATE, CURRENT_TIME, p_cedula, 1, p_movimiento);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_registrar_compra;
DELIMITER //
CREATE PROCEDURE sp_registrar_compra(
    IN p_fecha_compra DATE,
    IN p_cod_proveedor INT,
    IN p_total DECIMAL(12,2),
    OUT p_cod_compra INT
)
BEGIN
    IF p_fecha_compra IS NULL OR p_cod_proveedor IS NULL OR p_total <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Datos de compra invalidos.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM proveedor
         WHERE cod_proveedor = p_cod_proveedor AND status = 1
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El proveedor no existe o esta inactivo.';
    END IF;

    INSERT INTO compra (fecha_compra, total, cod_proveedor, status)
    VALUES (p_fecha_compra, p_total, p_cod_proveedor, 1);

    SET p_cod_compra = LAST_INSERT_ID();
END //
DELIMITER ;

/* Trigger de stock: las compras nuevas actualizan stock una sola vez. */
DROP TRIGGER IF EXISTS tg_actualizar_stock_compra;
DELIMITER //
CREATE TRIGGER tg_actualizar_stock_compra
AFTER INSERT ON detalle_compra
FOR EACH ROW
BEGIN
    CALL sp_actualizar_producto(NEW.cod_producto, NEW.cantidad);
END //
DELIMITER ;

/* Auditoria de compras y productos */
DROP TRIGGER IF EXISTS tg_bitacora_compra;
DELIMITER //
CREATE TRIGGER tg_bitacora_compra
AFTER INSERT ON compra
FOR EACH ROW
BEGIN
    CALL sp_registrar_bitacora(
        COALESCE(@cedula_usuario, 'SISTEMA'),
        CONCAT('Registro de compra #', NEW.cod_compra)
    );
END //
DELIMITER ;

DROP TRIGGER IF EXISTS tg_bitacora_producto;
DELIMITER //
CREATE TRIGGER tg_bitacora_producto
AFTER UPDATE ON producto
FOR EACH ROW
BEGIN
    IF NOT (OLD.stock <=> NEW.stock) THEN
        CALL sp_registrar_bitacora(
            COALESCE(@cedula_usuario, 'SISTEMA'),
            CONCAT('Actualizacion de stock del producto #', NEW.cod_producto,
                   ': ', OLD.stock, ' -> ', NEW.stock)
        );
    END IF;
END //
DELIMITER ;

/* Compra completa atomica. p_detalles: JSON [{"cod_producto":1,"cantidad":2,"precio_unitario":10}] */
DROP PROCEDURE IF EXISTS sp_registrar_compra_completa;
DELIMITER //
CREATE PROCEDURE sp_registrar_compra_completa(
    IN p_fecha_compra DATE,
    IN p_cod_proveedor INT,
    IN p_detalles JSON,
    IN p_cedula VARCHAR(12),
    OUT p_cod_compra INT
)
BEGIN
    DECLARE v_total DECIMAL(12,2) DEFAULT 0;
    DECLARE v_cantidad INT DEFAULT 0;
    DECLARE v_precio DECIMAL(12,2) DEFAULT 0;
    DECLARE v_cod_producto INT DEFAULT 0;
    DECLARE v_pos INT DEFAULT 0;
    DECLARE v_total_detalles INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_detalles IS NULL OR JSON_TYPE(p_detalles) <> 'ARRAY' OR JSON_LENGTH(p_detalles) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La compra debe tener productos.';
    END IF;

    IF p_cedula IS NULL OR NOT EXISTS (
        SELECT 1 FROM seguridad.usuario
         WHERE cedula = p_cedula AND status = 1
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La sesion no tiene un usuario valido para la bitacora.';
    END IF;

    SET v_total_detalles = JSON_LENGTH(p_detalles);
    SET @cedula_usuario = p_cedula;
    START TRANSACTION;

    CALL sp_registrar_compra(p_fecha_compra, p_cod_proveedor, 0.01, p_cod_compra);

    WHILE v_pos < v_total_detalles DO
        SET v_cod_producto = CAST(JSON_UNQUOTE(JSON_EXTRACT(p_detalles, CONCAT('$[', v_pos, '].cod_producto'))) AS UNSIGNED);
        SET v_cantidad = CAST(JSON_UNQUOTE(JSON_EXTRACT(p_detalles, CONCAT('$[', v_pos, '].cantidad'))) AS UNSIGNED);
        SET v_precio = CAST(JSON_UNQUOTE(JSON_EXTRACT(p_detalles, CONCAT('$[', v_pos, '].precio_unitario'))) AS DECIMAL(12,2));

        IF v_cod_producto <= 0 OR v_cantidad <= 0 OR v_precio <= 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Detalle de compra invalido.';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM producto WHERE cod_producto = v_cod_producto AND status = 1) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Uno de los productos no existe o esta inactivo.';
        END IF;

        INSERT INTO detalle_compra (cod_compra, cod_producto, cantidad, precio_unitario)
        VALUES (p_cod_compra, v_cod_producto, v_cantidad, v_precio);

        SET v_total = v_total + (v_cantidad * v_precio);
        SET v_pos = v_pos + 1;
    END WHILE;

    UPDATE compra SET total = v_total WHERE cod_compra = p_cod_compra;
    COMMIT;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_cancelar_compra;
DELIMITER //
CREATE PROCEDURE sp_cancelar_compra(
    IN p_cod_compra INT,
    IN p_cedula VARCHAR(12)
)
BEGIN
    DECLARE v_status TINYINT DEFAULT NULL;
    DECLARE v_cod_producto INT;
    DECLARE v_cantidad INT;
    DECLARE v_fin INT DEFAULT 0;
    DECLARE v_detalles CURSOR FOR
        SELECT cod_producto, cantidad
        FROM detalle_compra
        WHERE cod_compra = p_cod_compra
        ORDER BY cod_producto;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fin = 1;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    SELECT status INTO v_status FROM compra WHERE cod_compra = p_cod_compra FOR UPDATE;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La compra no existe.';
    ELSEIF v_status = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La compra ya esta cancelada.';
    END IF;

    IF p_cedula IS NULL OR NOT EXISTS (
        SELECT 1 FROM seguridad.usuario
         WHERE cedula = p_cedula AND status = 1
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La sesion no tiene un usuario valido para la bitacora.';
    END IF;

    SET @cedula_usuario = p_cedula;
    OPEN v_detalles;
    ciclo: LOOP
        FETCH v_detalles INTO v_cod_producto, v_cantidad;
        IF v_fin = 1 THEN LEAVE ciclo; END IF;
        CALL sp_actualizar_producto(v_cod_producto, -v_cantidad);
    END LOOP;
    CLOSE v_detalles;

    UPDATE compra SET status = 0 WHERE cod_compra = p_cod_compra;
    CALL sp_registrar_bitacora(@cedula_usuario, CONCAT('Cancelacion de compra #', p_cod_compra));
    COMMIT;
END //
DELIMITER ;

/* Consultas con subconsultas solicitadas */
DROP PROCEDURE IF EXISTS sp_productos_por_categoria;
DELIMITER //
CREATE PROCEDURE sp_productos_por_categoria(IN p_cod_categoria INT)
BEGIN
    SELECT * FROM v_productos_categoria_marca
     WHERE cod_categoria = p_cod_categoria
       AND status = 1;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_compras_por_proveedor;
DELIMITER //
CREATE PROCEDURE sp_compras_por_proveedor(IN p_cod_proveedor INT)
BEGIN
    SELECT * FROM v_compras_detalladas
     WHERE cod_proveedor = p_cod_proveedor
       AND status = 1;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_productos_por_marca;
DELIMITER //
CREATE PROCEDURE sp_productos_por_marca(IN p_cod_marca INT)
BEGIN
    SELECT * FROM v_productos_categoria_marca
     WHERE cod_marca = p_cod_marca
       AND status = 1;
END //
DELIMITER ;
