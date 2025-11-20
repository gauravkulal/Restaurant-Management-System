-- Create tables for offline restaurant table management

-- Restaurant tables
CREATE TABLE IF NOT EXISTS restaurant_tables (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    table_number INT UNIQUE NOT NULL,
    table_name VARCHAR(50),
    seats INT DEFAULT 4,
    status ENUM('available', 'occupied', 'reserved') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table orders (offline orders for restaurant tables)
CREATE TABLE IF NOT EXISTS table_orders (
    table_order_id INT AUTO_INCREMENT PRIMARY KEY,
    table_id INT NOT NULL,
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (table_id) REFERENCES restaurant_tables(table_id) ON DELETE CASCADE
);

-- Table order items
CREATE TABLE IF NOT EXISTS table_order_items (
    item_order_id INT AUTO_INCREMENT PRIMARY KEY,
    table_order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (table_order_id) REFERENCES table_orders(table_order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE RESTRICT
);

-- Insert default 6 tables
INSERT INTO restaurant_tables (table_number, table_name, seats) VALUES
(1, 'Table 1', 4),
(2, 'Table 2', 4),
(3, 'Table 3', 6),
(4, 'Table 4', 4),
(5, 'Table 5', 2),
(6, 'Table 6', 6)
ON DUPLICATE KEY UPDATE table_number=table_number;
