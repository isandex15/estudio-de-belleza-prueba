SET @especialista_index_exists = (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'usuario'
      AND index_name = 'idx_especialista_nombre'
);
SET @especialista_index_sql = IF(
    @especialista_index_exists = 0,
    'ALTER TABLE usuario ADD INDEX idx_especialista_nombre (nombre_usuario)',
    'SELECT 1'
);
PREPARE especialista_index_stmt FROM @especialista_index_sql;
EXECUTE especialista_index_stmt;
DEALLOCATE PREPARE especialista_index_stmt;

DELIMITER // 

DROP PROCEDURE IF EXISTS sp_registrar_rol//

CREATE PROCEDURE sp_registrar_rol( 
    IN p_rol VARCHAR(50) 
) 
BEGIN 
    INSERT INTO seguridad.rol (rol, status) 
    VALUES (p_rol, 1); 
END // 

DELIMITER ; 


DELIMITER // 

DROP PROCEDURE IF EXISTS sp_guardar_especialista//

CREATE PROCEDURE sp_guardar_especialista( 
    IN p_especialista VARCHAR(50), 
    IN p_cedula_especialista VARCHAR(12) 
) 
BEGIN 

    INSERT INTO sac.especialista ( 
        especialista, 
        cedula_especialista, 
        status 
    ) 
    VALUES ( 
        p_especialista, 
        p_cedula_especialista, 
        1 
    ); 

END // 

DELIMITER ; 


DELIMITER // 

DROP PROCEDURE IF EXISTS sac.sp_procesar_reservas_8pm//

CREATE PROCEDURE sac.sp_procesar_reservas_8pm() 
BEGIN 

    DECLARE v_fin INT DEFAULT 0; 
    DECLARE v_cod_servicio INT; 
    DECLARE v_fecha DATE; 
    DECLARE v_hora VARCHAR(20); 
    DECLARE v_cedula_especialista VARCHAR(12); 

    /* ========================================================== 
       CURSOR DE RESERVAS ACTIVAS DE HOY 
       ========================================================== */ 

    DECLARE cur_reservas CURSOR FOR 
        SELECT 
            cod_servicio, 
            fecha, 
            hora, 
            cedula_especialista 
        FROM sac.servicio 
        WHERE fecha = CURDATE() 
          AND status = 1; 

    /* ========================================================== 
       FIN DEL CURSOR 
       ========================================================== */ 

    DECLARE CONTINUE HANDLER FOR NOT FOUND 
        SET v_fin = 1; 

    /* ========================================================== 
       MANEJO DE ERRORES 
       ========================================================== */ 

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN 

        ROLLBACK; 

        RESIGNAL; 

    END; 

    /* ========================================================== 
       INICIAR TRANSACCIÓN 
       ========================================================== */ 

    START TRANSACTION; 

    OPEN cur_reservas; 

    /* ========================================================== 
       RECORRER RESERVAS 
       ========================================================== */ 

    leer_reservas: LOOP 

        FETCH cur_reservas 
        INTO 
            v_cod_servicio, 
            v_fecha, 
            v_hora, 
            v_cedula_especialista; 

        IF v_fin = 1 THEN 

            LEAVE leer_reservas; 

        END IF; 

        /* ====================================================== 
           VERIFICAR SI TIENE PAGO ACTIVO 
           ====================================================== */ 

        IF NOT EXISTS ( 

            SELECT 1 
            FROM sac.pago 
            WHERE cod_servicio = v_cod_servicio 
              AND status = 1 

        ) THEN 

            /* ================================================== 
               CANCELAR RESERVA 
               ================================================== */ 

            UPDATE sac.servicio 
            SET status = 0 
            WHERE cod_servicio = v_cod_servicio 
              AND status = 1; 


            /* ================================================== 
               LIBERAR DISPONIBILIDAD DEL ESPECIALISTA 
               ================================================== */ 

            UPDATE sac.disponibilidad_especialista 
            SET status = 0 
            WHERE fecha_disponibilidad = v_fecha 
              AND hora_disponibilidad = v_hora 
              AND cedula_especialista = v_cedula_especialista 
              AND status = 1; 

        END IF; 

    END LOOP; 

    CLOSE cur_reservas; 

    /* ========================================================== 
       CONFIRMAR TRANSACCIÓN 
       ========================================================== */ 

    COMMIT; 

END// 

DELIMITER ; 


DELIMITER // 

DROP PROCEDURE IF EXISTS sac.sp_registrar_reserva//

CREATE PROCEDURE sac.sp_registrar_reserva( 
    IN p_cedula VARCHAR(12), 
    IN p_cod_tipos_servicio VARCHAR(250), 
    IN p_fecha DATE, 
    IN p_hora VARCHAR(20), 
    IN p_cedula_especialista VARCHAR(12), 
    IN p_cod_promo INT, 
    IN p_cod_productos VARCHAR(500), 
    IN p_cantidades VARCHAR(500), 
    IN p_descripcion VARCHAR(500) 
) 
BEGIN 

    /* ===== VARIABLES ===== */ 

    DECLARE v_cod_servicio INT DEFAULT NULL; 

    DECLARE v_nombre_cliente VARCHAR(50); 
    DECLARE v_apellido_cliente VARCHAR(50); 
    DECLARE v_especialista VARCHAR(100); 

    DECLARE v_tipo_actual INT DEFAULT NULL; 
    DECLARE v_pos_tipo INT DEFAULT 1; 
    DECLARE v_total_tipos INT DEFAULT 0; 

    DECLARE v_producto_actual INT DEFAULT NULL; 
    DECLARE v_cantidad_actual INT DEFAULT NULL; 

    DECLARE v_pos_producto INT DEFAULT 1; 
    DECLARE v_total_productos INT DEFAULT 0; 

    /* ===== VALIDAR STOCK ===== */ 

    DECLARE v_stock INT DEFAULT NULL; 

    /* ===== CODIGOS DE CONTEO ===== */ 

    DECLARE v_cod_conteo INT DEFAULT NULL; 
    DECLARE v_cod_conteos VARCHAR(500) DEFAULT ''; 

    /* ===== MANEJO DE ERRORES ===== */ 

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN 

        ROLLBACK; 

        RESIGNAL; 

    END; 

    /* ===== INICIAR TRANSACCION ===== */ 

    START TRANSACTION; 

    /* ===== VALIDAR CLIENTE ===== */ 

    SELECT 
        nombre_usuario, 
        apellido_usuario 
    INTO 
        v_nombre_cliente, 
        v_apellido_cliente 
    FROM seguridad.usuario 
    WHERE cedula = p_cedula 
    LIMIT 1; 

    IF v_nombre_cliente IS NULL THEN 

        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 
        'Debe ingresar la cedula de un cliente existente.'; 

    END IF; 

    /* ===== VALIDAR ESPECIALISTA ===== */ 

    SELECT 
        especialista 
    INTO 
        v_especialista 
    FROM sac.especialista 
    WHERE cedula_especialista = p_cedula_especialista 
      AND status = 1 
    LIMIT 1; 

    IF v_especialista IS NULL THEN 

        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 
        'Debe seleccionar un especialista existente.'; 

    END IF; 

    /* ===== VALIDAR RESERVA DEL ESPECIALISTA ===== */ 

    IF EXISTS ( 
        SELECT 1 
        FROM sac.servicio 
        WHERE cedula_especialista = p_cedula_especialista 
          AND fecha = p_fecha 
          AND hora = p_hora 
          AND status = 1 
    ) THEN 

        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 
        'El especialista ya tiene una reserva en esa fecha y hora.'; 

    END IF; 

    /* ===== VALIDAR RESERVA DEL CLIENTE ===== */ 

    IF EXISTS ( 
        SELECT 1 
        FROM sac.servicio 
        WHERE cedula = p_cedula 
          AND fecha = p_fecha 
          AND hora = p_hora 
          AND cedula_especialista = p_cedula_especialista 
          AND status = 1 
    ) THEN 

        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 
        'El cliente ya tiene una reserva con ese especialista en esa fecha y hora.'; 

    END IF; 

    /* ===== VALIDAR TIPOS DE SERVICIO ===== */ 

    IF p_cod_tipos_servicio IS NULL 
       OR TRIM(p_cod_tipos_servicio) = '' THEN 

        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 
        'Debe seleccionar al menos un tipo de servicio.'; 

    END IF; 

    /* ===== VALIDAR PRODUCTOS ===== */ 

    IF p_cod_productos IS NULL 
       OR TRIM(p_cod_productos) = '' THEN 

        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 
        'Debe seleccionar productos.'; 

    END IF; 

    /* ===== VALIDAR CANTIDADES ===== */ 

    IF p_cantidades IS NULL 
       OR TRIM(p_cantidades) = '' THEN 

        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 
        'Debe indicar las cantidades de los productos.'; 

    END IF; 

    /* ===== CONTAR TIPOS ===== */ 

    SET v_total_tipos = 
        LENGTH(p_cod_tipos_servicio) 
        - LENGTH(REPLACE(p_cod_tipos_servicio, ',', '')) 
        + 1; 

    /* ===== CONTAR PRODUCTOS ===== */ 

    SET v_total_productos = 
        LENGTH(p_cod_productos) 
        - LENGTH(REPLACE(p_cod_productos, ',', '')) 
        + 1; 

    /* ===== VALIDAR CANTIDADES ===== */ 

    IF ( 
        LENGTH(p_cantidades) 
        - LENGTH(REPLACE(p_cantidades, ',', '')) 
        + 1 
    ) <> v_total_productos THEN 

        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 
        'La cantidad de productos no coincide con las cantidades indicadas.'; 

    END IF; 

    /* ===== CREAR RESERVA ===== */ 

    INSERT INTO sac.servicio( 
        cod_promo, 
        cedula, 
        descripcion, 
        fecha, 
        hora, 
        status, 
        cedula_especialista 
    ) 
    VALUES( 
        p_cod_promo, 
        p_cedula, 
        p_descripcion, 
        p_fecha, 
        p_hora, 
        1, 
        p_cedula_especialista 
    ); 

    SET v_cod_servicio = LAST_INSERT_ID(); 

    /* ===== REGISTRAR PRODUCTOS Y CONTEO STOCK ===== */ 

    SET v_pos_producto = 1; 

    WHILE v_pos_producto <= v_total_productos DO 

        /* ===== OBTENER PRODUCTO ACTUAL ===== */ 

        SET v_producto_actual = 
            CAST( 
                SUBSTRING_INDEX( 
                    SUBSTRING_INDEX( 
                        p_cod_productos, 
                        ',', 
                        v_pos_producto 
                    ), 
                    ',', 
                    -1 
                ) 
                AS UNSIGNED 
            ); 

        /* ===== OBTENER CANTIDAD ACTUAL ===== */ 

        SET v_cantidad_actual = 
            CAST( 
                SUBSTRING_INDEX( 
                    SUBSTRING_INDEX( 
                        p_cantidades, 
                        ',', 
                        v_pos_producto 
                    ), 
                    ',', 
                    -1 
                ) 
                AS UNSIGNED 
            ); 

        /* ===== VALIDAR CANTIDAD ===== */ 

        IF v_cantidad_actual IS NULL 
           OR v_cantidad_actual <= 0 THEN 

            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 
            'La cantidad del producto debe ser mayor que cero.'; 

        END IF; 

        /* ===== VALIDAR STOCK ===== */ 

        SELECT 
            stock 
        INTO 
            v_stock 
        FROM sac.producto 
        WHERE cod_producto = v_producto_actual 
          AND status = 1 
        FOR UPDATE; 

        IF v_stock IS NULL THEN 

            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 
            'Producto no encontrado o inactivo.'; 

        END IF; 

        IF v_stock < v_cantidad_actual THEN 

            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 
            'Stock insuficiente para uno de los productos seleccionados.'; 

        END IF; 

        /* ===== CREAR CONTEO STOCK ===== */ 

        INSERT INTO sac.conteo_stock( 
            conteo, 
            status, 
            cod_producto 
        ) 
        VALUES( 
            v_cantidad_actual, 
            1, 
            v_producto_actual 
        ); 

        /* ===== OBTENER CODIGO DEL CONTEO ===== */ 

        SET v_cod_conteo = LAST_INSERT_ID(); 

        /* ===== GUARDAR CODIGOS DE CONTEO ===== */ 

        SET v_cod_conteos = CONCAT( 
            v_cod_conteos, 
            CASE 
                WHEN v_cod_conteos = '' THEN '' 
                ELSE ',' 
            END, 
            v_cod_conteo 
        ); 

        SET v_pos_producto = 
            v_pos_producto + 1; 

    END WHILE; 

    /* ===== CREAR DETALLES ===== */ 

    SET v_pos_tipo = 1; 

    WHILE v_pos_tipo <= v_total_tipos DO 

        /* ===== OBTENER TIPO DE SERVICIO ===== */ 

        SET v_tipo_actual = 
            CAST( 
                SUBSTRING_INDEX( 
                    SUBSTRING_INDEX( 
                        p_cod_tipos_servicio, 
                        ',', 
                        v_pos_tipo 
                    ), 
                    ',', 
                    -1 
                ) 
                AS UNSIGNED 
            ); 

        SET v_pos_producto = 1; 

        WHILE v_pos_producto <= v_total_productos DO 

            /* ===== OBTENER PRODUCTO ACTUAL ===== */ 

            SET v_producto_actual = 
                CAST( 
                    SUBSTRING_INDEX( 
                        SUBSTRING_INDEX( 
                            p_cod_productos, 
                            ',', 
                            v_pos_producto 
                        ), 
                        ',', 
                        -1 
                    ) 
                    AS UNSIGNED 
                ); 

            INSERT INTO sac.detalle_servicio( 
                cantidad_servicio, 
                cod_servicio, 
                cod_tipo_servicio, 
                cod_producto 
            ) 
            VALUES( 
                1, 
                v_cod_servicio, 
                v_tipo_actual, 
                v_producto_actual 
            ); 

            SET v_pos_producto = 
                v_pos_producto + 1; 

        END WHILE; 

        SET v_pos_tipo = 
            v_pos_tipo + 1; 

    END WHILE; 

    /* ===== REGISTRAR DISPONIBILIDAD ===== */ 

    INSERT INTO sac.disponibilidad_especialista( 
        fecha_disponibilidad, 
        hora_disponibilidad, 
        status, 
        cedula_especialista 
    ) 
    VALUES( 
        p_fecha, 
        p_hora, 
        1, 
        p_cedula_especialista 
    ); 

    /* ===== CONFIRMAR TRANSACCION ===== */ 

    COMMIT; 

    /* ===== DEVOLVER RESULTADO ===== */ 

    SELECT 
        v_cod_servicio AS cod_servicio, 
        v_nombre_cliente AS nombre_cliente, 
        v_apellido_cliente AS apellido_cliente, 
        v_especialista AS especialista, 
        p_fecha AS fecha, 
        p_hora AS hora, 
        v_cod_conteos AS cod_conteos; 

END// 

DELIMITER ; 


DELIMITER // 

DROP TRIGGER IF EXISTS sac.tg_registrar_conteo_stock//

CREATE TRIGGER sac.tg_registrar_conteo_stock 
AFTER INSERT ON sac.detalle_servicio 
FOR EACH ROW 
BEGIN 

    DECLARE v_conteo INT DEFAULT NULL; 


    IF NEW.cod_producto IS NOT NULL THEN 


        SELECT 
            conteo 
        INTO 
            v_conteo 
        FROM sac.conteo_stock 
        WHERE cod_producto = NEW.cod_producto 
          AND status = 1 
        ORDER BY cod_conteo DESC 
        LIMIT 1; 


        IF v_conteo IS NULL THEN 

            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 
            'No existe un conteo de stock para el producto de la reserva.'; 

        END IF; 


        IF v_conteo <= 0 THEN 

            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 
            'La cantidad registrada en conteo_stock no es válida.'; 

        END IF; 

    END IF; 

END// 

DELIMITER ; 


DELIMITER // 

DROP TRIGGER IF EXISTS sac.tg_descontar_stock//

CREATE TRIGGER sac.tg_descontar_stock 
AFTER INSERT ON sac.detalle_servicio 
FOR EACH ROW 
BEGIN 

    DECLARE v_stock INT DEFAULT NULL; 
    DECLARE v_conteo INT DEFAULT NULL; 
    DECLARE v_cantidad_detalles INT DEFAULT 0; 


    IF NEW.cod_producto IS NOT NULL THEN 


        SELECT 
            COUNT(*) 
        INTO 
            v_cantidad_detalles 
        FROM sac.detalle_servicio 
        WHERE cod_servicio = NEW.cod_servicio 
          AND cod_producto = NEW.cod_producto; 


        IF v_cantidad_detalles = 1 THEN 


            SELECT 
                conteo 
            INTO 
                v_conteo 
            FROM sac.conteo_stock 
            WHERE cod_producto = NEW.cod_producto 
              AND status = 1 
            ORDER BY cod_conteo DESC 
            LIMIT 1; 


            IF v_conteo IS NULL 
               OR v_conteo <= 0 THEN 

                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 
                'No existe una cantidad válida en conteo_stock.'; 

            END IF; 


            SELECT 
                stock 
            INTO 
                v_stock 
            FROM sac.producto 
            WHERE cod_producto = NEW.cod_producto 
              AND status = 1 
            FOR UPDATE; 


            IF v_stock IS NULL THEN 

                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 
                'Producto no encontrado o inactivo.'; 

            END IF; 


            IF v_stock < v_conteo THEN 

                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 
                'Stock insuficiente.'; 

            END IF; 


            UPDATE sac.producto 
            SET stock = stock - v_conteo 
            WHERE cod_producto = NEW.cod_producto; 


        END IF; 

    END IF; 

END// 

DELIMITER ; 


DROP VIEW IF EXISTS vista_clientes_activos; 

CREATE VIEW vista_clientes_activos AS 
SELECT 
    COUNT(*) AS total_clientes_activos 
FROM usuario 
WHERE cod_rol = 3 
  AND status = 1; 


DROP VIEW IF EXISTS vista_reservas_por_dia; 

CREATE VIEW vista_reservas_por_dia AS 
SELECT 
    DATE_ADD( 
        DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY), 
        INTERVAL d.num DAY 
    ) AS fecha, 
    CASE d.num 
        WHEN 0 THEN 'Lunes' 
        WHEN 1 THEN 'Martes' 
        WHEN 2 THEN 'Miércoles' 
        WHEN 3 THEN 'Jueves' 
        WHEN 4 THEN 'Viernes' 
        WHEN 5 THEN 'Sábado' 
        WHEN 6 THEN 'Domingo' 
    END AS dia_semana, 
    CASE d.num 
        WHEN 0 THEN 'Lunes' 
        WHEN 1 THEN 'Martes' 
        WHEN 2 THEN 'Miércoles' 
        WHEN 3 THEN 'Jueves' 
        WHEN 4 THEN 'Viernes' 
        WHEN 5 THEN 'Sábado' 
        WHEN 6 THEN 'Domingo' 
    END AS dia, 
    COUNT(s.cod_servicio) AS total_reservas 
FROM 
( 
    SELECT 0 AS num 
    UNION ALL SELECT 1 
    UNION ALL SELECT 2 
    UNION ALL SELECT 3 
    UNION ALL SELECT 4 
    UNION ALL SELECT 5 
    UNION ALL SELECT 6 
) d 
LEFT JOIN servicio s 
    ON s.fecha = DATE_ADD( 
        DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY), 
        INTERVAL d.num DAY 
    ) 
    AND s.status = 1 
GROUP BY 
    d.num, 
    fecha, 
    dia_semana, 
    dia 
ORDER BY 
    d.num; 


DROP VIEW IF EXISTS vista_reservas_por_mes; 

CREATE VIEW vista_reservas_por_mes AS 
SELECT 
    m.num, 
    m.mes, 
    COUNT(s.cod_servicio) AS total_reservas 
FROM 
( 
    SELECT 1 AS num, 'Enero' AS mes 
    UNION ALL SELECT 2, 'Febrero' 
    UNION ALL SELECT 3, 'Marzo' 
    UNION ALL SELECT 4, 'Abril' 
    UNION ALL SELECT 5, 'Mayo' 
    UNION ALL SELECT 6, 'Junio' 
    UNION ALL SELECT 7, 'Julio' 
    UNION ALL SELECT 8, 'Agosto' 
    UNION ALL SELECT 9, 'Septiembre' 
    UNION ALL SELECT 10, 'Octubre' 
    UNION ALL SELECT 11, 'Noviembre' 
    UNION ALL SELECT 12, 'Diciembre' 
) m 
LEFT JOIN servicio s 
    ON MONTH(s.fecha) = m.num 
    AND YEAR(s.fecha) = YEAR(CURDATE()) 
    AND s.status = 1 
GROUP BY 
    m.num, 
    m.mes 
ORDER BY 
    m.num; 


DROP VIEW IF EXISTS vista_reservas_por_hora; 

CREATE VIEW vista_reservas_por_hora AS 
SELECT 
    s.hora, 
    COUNT(s.cod_servicio) AS total_reservas 
FROM servicio s 
WHERE 
    s.status = 1 
    AND YEAR(s.fecha) = YEAR(CURDATE()) 
GROUP BY 
    s.hora 
ORDER BY 
    total_reservas DESC; 


DROP VIEW IF EXISTS vista_ingresos_dia; 

CREATE VIEW vista_ingresos_dia AS 
SELECT 
    DATE_ADD( 
        DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY), 
        INTERVAL d.num DAY 
    ) AS fecha, 
    CASE d.num 
        WHEN 0 THEN 'Lunes' 
        WHEN 1 THEN 'Martes' 
        WHEN 2 THEN 'Miércoles' 
        WHEN 3 THEN 'Jueves' 
        WHEN 4 THEN 'Viernes' 
        WHEN 5 THEN 'Sábado' 
        WHEN 6 THEN 'Domingo' 
    END AS dia_semana, 
    CASE d.num 
        WHEN 0 THEN 'Lunes' 
        WHEN 1 THEN 'Martes' 
        WHEN 2 THEN 'Miércoles' 
        WHEN 3 THEN 'Jueves' 
        WHEN 4 THEN 'Viernes' 
        WHEN 5 THEN 'Sábado' 
        WHEN 6 THEN 'Domingo' 
    END AS dia, 
    COALESCE(SUM(p.monto), 0) AS total_ingresos 
FROM 
( 
    SELECT 0 AS num 
    UNION ALL SELECT 1 
    UNION ALL SELECT 2 
    UNION ALL SELECT 3 
    UNION ALL SELECT 4 
    UNION ALL SELECT 5 
    UNION ALL SELECT 6 
) d 
LEFT JOIN pago p 
    ON p.fecha_pago = DATE_ADD( 
        DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY), 
        INTERVAL d.num DAY 
    ) 
    AND p.status = 1 
GROUP BY 
    d.num, 
    fecha, 
    dia_semana, 
    dia 
ORDER BY 
    d.num; 


DROP VIEW IF EXISTS vista_ingresos_mes; 

CREATE VIEW vista_ingresos_mes AS 
SELECT 
    m.num, 
    m.mes, 
    COALESCE(SUM(p.monto), 0) AS total_ingresos 
FROM 
( 
    SELECT 1 AS num, 'Enero' AS mes 
    UNION ALL SELECT 2, 'Febrero' 
    UNION ALL SELECT 3, 'Marzo' 
    UNION ALL SELECT 4, 'Abril' 
    UNION ALL SELECT 5, 'Mayo' 
    UNION ALL SELECT 6, 'Junio' 
    UNION ALL SELECT 7, 'Julio' 
    UNION ALL SELECT 8, 'Agosto' 
    UNION ALL SELECT 9, 'Septiembre' 
    UNION ALL SELECT 10, 'Octubre' 
    UNION ALL SELECT 11, 'Noviembre' 
    UNION ALL SELECT 12, 'Diciembre' 
) m 
LEFT JOIN pago p 
    ON MONTH(p.fecha_pago) = m.num 
    AND YEAR(p.fecha_pago) = YEAR(CURDATE()) 
    AND p.status = 1 
GROUP BY 
    m.num, 
    m.mes 
ORDER BY 
    m.num; 


DROP VIEW IF EXISTS vista_total_reservas_activas; 

CREATE VIEW vista_total_reservas_activas AS 
SELECT 
    COUNT(*) AS total_reservas_activas 
FROM servicio 
WHERE 
    status = 1 
    AND YEAR(fecha) = YEAR(CURDATE()); 