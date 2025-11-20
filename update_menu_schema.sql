-- Update Items table to add description column
ALTER TABLE Items ADD COLUMN description TEXT DEFAULT NULL;

-- Create categories table to track custom categories
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    is_custom BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert existing categories as non-custom (built-in)
INSERT INTO categories (category_name, display_name, is_custom) VALUES 
('beverages', 'Beverages', FALSE),
('Snacks', 'Snacks', FALSE),
('Veg', 'Vegetarian', FALSE),
('Non-Veg', 'Non-Vegetarian', FALSE)
ON DUPLICATE KEY UPDATE display_name=display_name;
