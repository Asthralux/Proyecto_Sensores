-- Creación de la base de datos
CREATE DATABASE Sensor;
USE Sensor;
CREATE TABLE Datos(
	id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    voltaje FLOAT NOT NULL,
    corriente FLOAT NOT NULL,
    potencia_activa FLOAT,
    potencia_reactiva FLOAT,
    factor_de_potencia FLOAT,
    frecuencia FLOAT NOT NULL DEFAULT 0 
);
-- Aquí termina la creación de la base de datos
-- Asignación de permisos especiales al usuario que se está usando
SHOW GRANTS FOR 'daniel'@'localhost';
CREATE USER 'daniel'@'localhost' IDENTIFIED BY '123';
GRANT ALL PRIVILEGES ON Sensor.* TO 'daniel'@'localhost';
FLUSH PRIVILEGES;
DROP USER 'daniel'@'192.68.1.110';
DROP USER 'daniel'@'%';
FLUSH PRIVILEGES;
CREATE USER 'daniel'@'%' IDENTIFIED BY '123';
GRANT ALL PRIVILEGES ON *.* TO 'daniel'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SHOW GRANTS FOR 'daniel'@'%';
SELECT * FROM mysql.user WHERE User = 'daniel';
-- Aquí terminan las asignaciónes de permisos especiales de usuario
-- Este comando muestra todas las bases de datos existentes en el sistema
SELECT User, Host FROM mysql.user;
SHOW DATABASES;
-- Aquí termina el comando que muestra todas las bases de datos en el equipo
-- Este comando lo que hace es mostrar todos los datos de la base de datos
USE sensor;
SELECT * FROM Datos;
-- Aquí termina el comando que muestra los datos de la base de datos

-- Este código es para borrar los datos de la base de datos
USE sensor;
SELECT * FROM Datos;
SET SQL_SAFE_UPDATES = 0;
DELETE FROM Datos;
ALTER TABLE Datos AUTO_INCREMENT = 1;
SET SQL_SAFE_UPDATES = 1;
-- Aquí termina el código para borrar los datos de la base de datos

-- Este comando lo que hace es decirme el peso de la base de datos
SELECT
	-- table_name AS "Tabla",
    ROUND(SUM((data_length + index_length) / 1024 / 1024), 2) AS "Tamaño en MB"
FROM information_schema.TABLES
WHERE table_schema = "sensor"
	-- AND table_name = "Datos";
-- Aquí termina el comando para checar el peso de la DB
