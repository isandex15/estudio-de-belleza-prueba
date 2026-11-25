-- Indices  
-- usuarios y pagos. 

DROP INDEX IF EXISTS idx_usuario_cedula_cod_rol ON seguridad.usuario;
ALTER TABLE seguridad.usuario 
    ADD INDEX idx_usuario_cedula_cod_rol (cedula, cod_rol); 

DROP INDEX IF EXISTS idx_pago_fecha_cod_servicio ON pago;
ALTER TABLE pago 
    ADD INDEX idx_pago_fecha_cod_servicio (fecha_pago, cod_servicio); 
 
 
 
 
--PROCEDIMIENTOS ALMACENADOS!!! 
 
--Procedimiento Almacenado para registrar pago completo (modulo pagos) 
 
DELIMITER // 
 
DROP PROCEDURE IF EXISTS sp_registrar_pago_completo // 

CREATE PROCEDURE sp_registrar_pago_completo( 
    IN p_monto FLOAT, 
    IN p_comprobante VARCHAR(300), 
    IN p_cod_servicio INT, 
    IN p_cod_tipo_pago INT, 
    IN p_cod_moneda INT, 
    IN p_cantidad VARCHAR(250) 
) 
BEGIN 
    DECLARE v_cod_pago INT; 
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN 
        ROLLBACK; 
    END; 
 
    START TRANSACTION; 
        INSERT INTO pago (fecha_pago, monto, comprobante_pago, status, cod_servicio) 
        VALUES (CURDATE(), p_monto, p_comprobante, 1, p_cod_servicio); 
         
        SET v_cod_pago = LAST_INSERT_ID(); 
         
        INSERT INTO detalle_pago (cantidad, cod_pago, cod_tipo_pago, cod_moneda) 
        VALUES (p_cantidad, v_cod_pago, p_cod_tipo_pago, p_cod_moneda); 
    COMMIT; 
END // 
 
DELIMITER ; 
 
-- Procedimiento almacenado para guardar un pago personal 
DELIMITER // 

DROP PROCEDURE IF EXISTS sp_guardar_pago_personal // 

CREATE PROCEDURE sp_guardar_pago_personal( 
    IN p_fecha_pago DATE, 
    IN p_hora_pago TIME, 
    IN p_porcentaje INT, 
    IN p_status TINYINT, 
    IN p_cod_servicio INT, 
    IN p_comprobante VARCHAR(250), 
    IN p_cod_banco INT 
) 
BEGIN 
    IF NOT EXISTS ( 
        SELECT 1 
        FROM servicio 
        WHERE cod_servicio = p_cod_servicio 
          AND status = 1 
    ) THEN 
        SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'El servicio no existe o está inactivo.'; 
    END IF; 
 
    IF EXISTS ( 
        SELECT 1 
        FROM pago_personal 
        WHERE cod_servicio = p_cod_servicio 
          AND status = 1 
    ) THEN 
        SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'El servicio ya tiene un pago personal activo.'; 
    END IF; 
 
    INSERT INTO pago_personal ( 
        fecha_pago, hora_pago, porcentaje, status, cod_servicio, 
        comprobante, cod_banco 
    ) VALUES ( 
        p_fecha_pago, p_hora_pago, p_porcentaje, p_status, p_cod_servicio, 
        p_comprobante, p_cod_banco 
    ); 
END // 
 
DELIMITER ; 
 
-- Procedimiento transaccional para procesar la nómina de un personal 
DELIMITER // 
DELIMITER //

DROP PROCEDURE IF EXISTS sp_procesar_nomina_personal //

CREATE PROCEDURE sp_procesar_nomina_personal(  
    IN p_fecha_pago DATE,  
    IN p_hora_pago TIME,  
    IN p_porcentaje INT,  
    IN p_status TINYINT,  
    IN p_cod_servicio INT  
)  
BEGIN  
    DECLARE v_servicio INT DEFAULT NULL;  
    DECLARE v_pago_activo INT DEFAULT 0;  
  
    DECLARE EXIT HANDLER FOR SQLEXCEPTION  
    BEGIN  
        ROLLBACK;  
        RESIGNAL;  
    END;  
  
    START TRANSACTION;  
  
    SELECT cod_servicio  
    INTO v_servicio  
    FROM servicio  
    WHERE cod_servicio = p_cod_servicio  
      AND status = 1  
    FOR UPDATE;  
  
    IF v_servicio IS NULL THEN  
        SIGNAL SQLSTATE '45000'  
            SET MESSAGE_TEXT = 'El servicio no existe o está inactivo.';  
    END IF;  
  
    SELECT COUNT(*)  
    INTO v_pago_activo  
    FROM pago_personal  
    WHERE cod_servicio = p_cod_servicio  
      AND status = 1;  
  
    IF v_pago_activo > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El servicio ya tiene una nómina activa.';
    END IF;
  
    INSERT INTO pago_personal (  
        fecha_pago, hora_pago, porcentaje, status, cod_servicio  
    ) VALUES (  
        p_fecha_pago, p_hora_pago, p_porcentaje, p_status, p_cod_servicio  
    );  
  
    COMMIT;  
END //

DELIMITER ;
-- Procedimiento almacenado para respaldar mantenimiento en seguridad.mantenimiento 
DELIMITER // 

DROP PROCEDURE IF EXISTS sp_respaldar_mantenimiento // 

CREATE PROCEDURE sp_respaldar_mantenimiento( 
    IN p_nombre_archivo VARCHAR(250), 
    IN p_tamano VARCHAR(20), 
    IN p_fecha DATE, 
    IN p_hora TIME, 
    IN p_cedula_usuario VARCHAR(12) 
) 
BEGIN 
    INSERT INTO seguridad.mantenimiento ( 
        nombre_archivo, 
        tamano, 
        fecha, 
        hora, 
        cedula_usuario 
    ) 
    VALUES ( 
        p_nombre_archivo, 
        p_tamano, 
        p_fecha, 
        p_hora, 
        p_cedula_usuario 
    ); 
END // 
 
DELIMITER ; 
 
 
-- FUNCIONES!!! 
 
-- Función para obtener la última tasa registrada de una moneda 
DELIMITER // 

DROP FUNCTION IF EXISTS fn_obtener_tasa_moneda // 
 
CREATE FUNCTION fn_obtener_tasa_moneda(p_cod_moneda INT) 
RETURNS FLOAT 
READS SQL DATA 
BEGIN 
    DECLARE v_tasa FLOAT DEFAULT 0; 
 
    SELECT COALESCE(c.valor, 0) 
    INTO v_tasa 
    FROM cambio c 
    WHERE c.cod_moneda = p_cod_moneda 
    ORDER BY c.fecha DESC, c.cod_cambio DESC 
    LIMIT 1; 
 
    RETURN COALESCE(v_tasa, 0); 
END // 
 
DELIMITER ; 
 
 
-- Función para calcular la comisión del servicio basada en un porcentaje del monto del servicio 
DELIMITER // 
 
DROP FUNCTION IF EXISTS fn_calcular_comision_servicio // 
 
CREATE FUNCTION fn_calcular_comision_servicio(p_monto_servicio FLOAT, p_porcentaje_especialista INT)  
RETURNS FLOAT 
READS SQL DATA 
BEGIN 
    DECLARE v_pago_final FLOAT; 
    SET v_pago_final = (p_monto_servicio * p_porcentaje_especialista) / 100; 
    RETURN v_pago_final; 
END // 
 
DELIMITER ; 
 
 
-- Función para calcular el total de comisiones del personal por especialista y día 
DELIMITER // 
 
DROP FUNCTION IF EXISTS fn_calcular_total_pago_personal // 
 
CREATE FUNCTION fn_calcular_total_pago_personal( 
    p_cedula_especialista VARCHAR(12), 
    p_fecha_pago DATE 
) 
RETURNS FLOAT 
READS SQL DATA 
BEGIN 
    DECLARE v_total_pago FLOAT DEFAULT 0; 
 
    SELECT COALESCE(SUM(comision), 0) 
    INTO v_total_pago 
    FROM ( 
        SELECT 
            pp.cod_pago_personal, 
            pp.porcentaje, 
            fn_calcular_comision_servicio( 
                COALESCE( 
                    ( 
                        SELECT SUM(GREATEST(CAST(ds.cantidad_servicio AS DECIMAL(10,2)), 1) * ts.precio) 
                        FROM detalle_servicio ds 
                        LEFT JOIN tipo_servicio ts ON ts.cod_tipo_servicio = ds.cod_tipo_servicio 
                        WHERE ds.cod_servicio = s.cod_servicio 
                    ), 
                    0 
                ), 
                pp.porcentaje 
            ) AS comision 
        FROM pago_personal pp 
        INNER JOIN servicio s ON s.cod_servicio = pp.cod_servicio 
        WHERE s.cedula_especialista = p_cedula_especialista 
          AND pp.fecha_pago = p_fecha_pago 
          AND pp.status = 1 
    ) AS pagos_del_dia; 
 
    RETURN v_total_pago; 
END // 
 
DELIMITER ; 
 
 
-- cada tipo de servicio seleccionado equivale a una unidad 
UPDATE detalle_servicio 
SET cantidad_servicio = '1' 
WHERE CAST(cantidad_servicio AS DECIMAL(10,2)) <= 0; 
 
 
-- Asegurar existencia de un usuario 'sistema' para registros desde triggers 
DELIMITER // 

DROP PROCEDURE IF EXISTS sp_asegurar_usuario_sistema // 

CREATE PROCEDURE sp_asegurar_usuario_sistema() 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM seguridad.usuario WHERE cedula = '00000000000') THEN 
        INSERT INTO seguridad.usuario ( 
            cedula, nombre_usuario, apellido_usuario, password, telefono, direccion, correo, status, cod_rol, intentos_fallidos, ultimo_acceso, fecha_registro 
        ) 
        SELECT '00000000000', 'Sistema', 'Automático', '', '0000000000', '', '', 1, 1, 0, CURDATE(), CURDATE(); 
    END IF; 
END // 
 
DELIMITER ; 
 
-- Ejecutar aseguramiento del usuario (al importar este SQL, importante, KLEY) 
CALL sp_asegurar_usuario_sistema(); 
 
 
-- TRIGGERS !!! 
-- Trigger para guardar precio moneda al registrar un nuevo cambio  
DELIMITER // 

DROP TRIGGER IF EXISTS tg_guardar_precio_moneda_reg // 

CREATE TRIGGER tg_guardar_precio_moneda_reg 
AFTER INSERT ON cambio 
FOR EACH ROW 
BEGIN 
    INSERT INTO seguridad.bitacora (cedula, movimiento, fecha, hora, status) 
    VALUES ( 
        '00000000000', 
        CONCAT('cambio: cod_moneda=', NEW.cod_moneda, ',valor=', NEW.valor), 
        CURDATE(), 
        CURTIME(), 
        1 
    ); 
END // 
 
DELIMITER ; 
 
 
-- Trigger para guardar precio moneda al actualizar un cambio  
DELIMITER // 

DROP TRIGGER IF EXISTS tg_guardar_precio_moneda_act // 

CREATE TRIGGER tg_guardar_precio_moneda_act 
AFTER UPDATE ON cambio 
FOR EACH ROW 
BEGIN 
    INSERT INTO seguridad.bitacora (cedula, movimiento, fecha, hora, status) 
    VALUES ( 
        '00000000000', 
        CONCAT('cambio UPDATE: cod_moneda=', NEW.cod_moneda, ',valor_old=', OLD.valor, ',valor_new=', NEW.valor), 
        CURDATE(), 
        CURTIME(), 
        1 
    ); 
END // 
 
DELIMITER ; 
 
-- VISTAS 

DROP VIEW IF EXISTS v_usuarios_personal;
CREATE VIEW v_usuarios_personal AS 
SELECT u.cedula, u.nombre_usuario, u.apellido_usuario, u.telefono, 
       u.direccion, u.correo, u.status, u.cod_rol, r.rol 
FROM seguridad.usuario u 
INNER JOIN seguridad.rol r ON r.cod_rol = u.cod_rol 
WHERE r.rol IN ('gerente', 'empleado') AND u.status IN (0, 1); 
 
DROP VIEW IF EXISTS v_pagos_detallados;
CREATE VIEW v_pagos_detallados AS 
SELECT p.cod_pago, p.fecha_pago, p.monto, p.status, 
       u.cedula, u.nombre_usuario AS nombre_cliente, s.cod_servicio, 
       ( 
         SELECT tp.nombre_tipo_pago 
         FROM detalle_pago dp 
         INNER JOIN tipo_pago tp ON tp.cod_tipo_pago = dp.cod_tipo_pago 
         WHERE dp.cod_pago = p.cod_pago 
         LIMIT 1 
       ) AS nombre_tipo_pago, 
       ( 
         SELECT m.nombre_moneda 
         FROM detalle_pago dp 
         INNER JOIN moneda m ON m.cod_moneda = dp.cod_moneda 
         WHERE dp.cod_pago = p.cod_pago 
         LIMIT 1 
       ) AS nombre_moneda, 
       p.comprobante_pago 
FROM pago p 
INNER JOIN servicio s ON s.cod_servicio = p.cod_servicio 
INNER JOIN seguridad.usuario u ON u.cedula = s.cedula; 
 
DROP VIEW IF EXISTS v_cambios_monedas_todos;
CREATE VIEW v_cambios_monedas_todos AS 
SELECT m.cod_moneda, m.nombre_moneda, m.status, 
       c.valor AS valor_cambio, c.fecha AS fecha_cambio 
FROM moneda m 
LEFT JOIN cambio c ON c.cod_cambio = ( 
  SELECT c2.cod_cambio 
  FROM cambio c2 
  WHERE c2.cod_moneda = m.cod_moneda 
  ORDER BY c2.fecha DESC, c2.cod_cambio DESC 
  LIMIT 1 
); 