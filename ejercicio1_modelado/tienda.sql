-- EJERCICIO 1: Modelo fisico de la tienda online (MySQL)

CREATE DATABASE IF NOT EXISTS tienda_online;
USE tienda_online;

CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    telefono VARCHAR(15),
    direccion VARCHAR(200) NOT NULL,
    fecha_registro DATE NOT NULL
);

CREATE TABLE categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
);

CREATE TABLE proveedor (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(100)
);

CREATE TABLE producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    stock_minimo INT NOT NULL DEFAULT 5,
    id_categoria INT NOT NULL,
    id_proveedor INT NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria),
    FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor)
);

CREATE TABLE pedido (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha_pedido DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('pendiente', 'enviado', 'entregado', 'cancelado') NOT NULL DEFAULT 'pendiente',
    total DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
);

CREATE TABLE detalle_pedido (
    id_pedido INT,
    id_producto INT,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_pedido, id_producto),
    FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

-- Datos de prueba
INSERT INTO cliente (nombre, apellidos, email, telefono, direccion, fecha_registro) VALUES
('Laura', 'Martinez Soler', 'laura@gmail.com', '611223344', 'C/ Mallorca 120, Barcelona', '2026-01-15'),
('Pablo', 'Ruiz Gomez', 'pablo@gmail.com', '622334455', 'Av. Diagonal 45, Barcelona', '2026-03-02');

INSERT INTO categoria (nombre, descripcion) VALUES
('Electronica', 'Moviles, portatiles y accesorios'),
('Hogar', 'Productos para la casa');

INSERT INTO proveedor (nombre, telefono, email) VALUES
('TechDistribucion S.L.', '931112233', 'ventas@techdist.com'),
('CasaPlus S.A.', '932223344', 'pedidos@casaplus.com');

INSERT INTO producto (nombre, descripcion, precio, stock, stock_minimo, id_categoria, id_proveedor) VALUES
('Raton inalambrico', 'Raton bluetooth', 19.99, 50, 10, 1, 1),
('Auriculares', 'Auriculares con cancelacion de ruido', 89.90, 3, 5, 1, 1),
('Lampara LED', 'Lampara de escritorio', 25.50, 20, 5, 2, 2);

INSERT INTO pedido (id_cliente, estado, total) VALUES
(1, 'enviado', 129.88),
(2, 'pendiente', 25.50);

INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario) VALUES
(1, 1, 2, 19.99),
(1, 2, 1, 89.90),
(2, 3, 1, 25.50);

-- Consulta de prueba: productos con el stock por debajo del minimo (para reponer)
SELECT p.nombre, p.stock, p.stock_minimo, pr.nombre AS proveedor
FROM producto p
JOIN proveedor pr ON p.id_proveedor = pr.id_proveedor
WHERE p.stock < p.stock_minimo;

-- Consulta de prueba: pedidos con el cliente y lo que ha comprado
SELECT pe.id_pedido, c.nombre, c.apellidos, pr.nombre AS producto, d.cantidad, d.precio_unitario
FROM pedido pe
JOIN cliente c ON pe.id_cliente = c.id_cliente
JOIN detalle_pedido d ON pe.id_pedido = d.id_pedido
JOIN producto pr ON d.id_producto = pr.id_producto;
