-- Complete the category_id migration
-- Run this after the initial migration script has already added the category_id column
USE restaurant_management;

-- Step 1: Remap legacy category names to existing categories
UPDATE Items SET category = 'Non-Veg' WHERE category IN ('Non-Veg Snacks');
UPDATE Items SET category = 'Snacks'  WHERE category IN ('Sandwiches','Rolls');
UPDATE Items SET category = 'Veg'     WHERE category = 'Meals';

-- Step 2: Back-fill category_id using normalized matching
UPDATE Items i
JOIN categories c ON REPLACE(REPLACE(REPLACE(LOWER(c.category_name), '-', ''), ' ', ''), '_', '')
                  = REPLACE(REPLACE(REPLACE(LOWER(i.category), '-', ''), ' ', ''), '_', '')
SET i.category_id = c.category_id
WHERE i.category_id IS NULL;

-- Step 2b: Fallback match against display_name
UPDATE Items i
JOIN categories c ON i.category_id IS NULL
                 AND REPLACE(REPLACE(REPLACE(LOWER(c.display_name), '-', ''), ' ', ''), '_', '')
                     = REPLACE(REPLACE(REPLACE(LOWER(i.category), '-', ''), ' ', ''), '_', '')
SET i.category_id = c.category_id;

-- Step 3: Verify no unmapped items remain
SELECT item_id, item_name, category
FROM Items
WHERE category_id IS NULL;

-- Step 4: Enforce NOT NULL constraint
ALTER TABLE Items MODIFY category_id INT NOT NULL;

-- Step 5: Add foreign key constraint
ALTER TABLE Items
  ADD CONSTRAINT fk_items_category
    FOREIGN KEY (category_id)
    REFERENCES categories(category_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;

-- Step 6: Create index for performance
CREATE INDEX idx_items_category_id ON Items(category_id);

-- Step 7: Verification - show item counts per category
SELECT c.category_name, COUNT(i.item_id) AS item_count
FROM categories c
LEFT JOIN Items i ON i.category_id = c.category_id
GROUP BY c.category_id, c.category_name
ORDER BY c.category_name;
