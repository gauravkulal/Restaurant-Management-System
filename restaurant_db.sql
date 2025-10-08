-- To Create a database for the restaurant management system
CREATE DATABASE restaurant_management;


USE restaurant_management;

--create sign up table
CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- item table
CREATE TABLE Items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100),
    price DECIMAL(6,2),
    category VARCHAR(50)
);


-- Beverages
INSERT INTO Items (item_id, item_name, price, category) VALUES (1, 'Coffee', 30, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (2, 'Black Coffee', 60, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (3, 'Cappuccino', 90, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (4, 'Tea', 30, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (5, 'Green Tea', 35, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (6, 'Iced Tea', 60, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (7, 'Lemonade', 50, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (8, 'Orange Juice', 80, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (9, 'Sugarcane Juice', 60, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (10, 'Berry Juice', 60, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (11, 'Pineapple Juice', 80, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (12, 'Pomegranate Shake', 100, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (13, 'Grape Juice', 80, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (14, 'Watermelon Juice', 80, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (15, 'Hot chocolate', 130, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (16, 'Hazelnut hot chocolate', 150, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (17, 'Iced Coffee', 60, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (18, 'Caramel cold coffee', 180, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (19, 'Lotus biscoff coffee', 165, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (20, 'Oreo milkshake', 180, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (21, 'Chocolate Devil Shake', 175, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (22, 'Brownie Milkshake', 170, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (23, 'Mango Lassi', 90, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (24, 'Mango smoothie', 85, 'beverages');
INSERT INTO Items (item_id, item_name, price, category) VALUES (25, 'Strawberry Smoothie', 85, 'beverages');

-- Snacks and Other Items
INSERT INTO Items (item_id, item_name, price, category) VALUES (26, 'Samosa', 30, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (27, 'Kachori', 40, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (28, 'Pani Puri', 35, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (29, 'Veg Puff', 20, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (30, 'Egg Puff', 30, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (31, 'Cutlet', 35, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (32, 'French Fries', 60, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (33, 'Peri Peri Fries', 85, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (34, 'Chicken Loaded Fries', 175, 'Non-Veg Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (35, 'Vada Pav', 50, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (36, 'Bhel Puri', 50, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (37, 'Veg Sandwich', 75, 'Sandwiches');
INSERT INTO Items (item_id, item_name, price, category) VALUES (38, 'Pav Bhaji', 95, 'Meals');
INSERT INTO Items (item_id, item_name, price, category) VALUES (39, 'Paneer Roll', 100, 'Rolls');
INSERT INTO Items (item_id, item_name, price, category) VALUES (40, 'Sabudana Vada', 65, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (41, 'Corn Cheese Balls', 80, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (42, 'Potato Nuggets', 80, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (43, 'Paneer Momos', 120, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (44, 'Cheese Nachos', 110, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (45, 'Spring Roll', 199, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (46, 'Chocolate Donut', 55, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (47, 'Brownie with Ice Cream', 140, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (48, 'Chocolate Tart', 135, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (49, 'Triple Chocolate Cupcake', 85, 'Snacks');
INSERT INTO Items (item_id, item_name, price, category) VALUES (50, 'Belgian Waffle', 149, 'Snacks');
-- Veg Soups
INSERT INTO Items (item_id, item_name, price, category) VALUES (51, 'Manchow Soup', 195, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (52, 'Hot & Sour Soup', 185, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (53, 'Tomato Ginger Soup', 195, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (54, 'Cream of Mushroom Soup', 195, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (55, 'Sweet Corn Soup', 185, 'Veg');

-- Veg Starters
INSERT INTO Items (item_id, item_name, price, category) VALUES (56, 'Gobi 65', 270, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (57, 'Paneer 65', 370, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (58, 'Paneer Tikka', 399, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (59, 'Crispy Fried Veg', 268, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (60, 'Baby Corn Pepper Fry', 316, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (61, 'Dragon Paneer', 319, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (62, 'Honey Chilli Potato', 250, 'Veg');

-- Veg Main Course
INSERT INTO Items (item_id, item_name, price, category) VALUES (63, 'South Indian Meals', 250, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (64, 'North Indian Meals', 345, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (65, 'Sambar Rice', 150, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (66, 'Curd Rice', 150, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (67, 'Veg Fried Rice', 299, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (68, 'Veg Noodles', 299, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (69, 'Jeera Rice', 250, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (70, 'Veg Biriyani', 350, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (71, 'Paneer Biriyani', 400, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (72, 'Kashmiri Pulao', 380, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (73, 'Hyderabadi Paneer Biriyani', 400, 'Veg');

-- Tiffin
INSERT INTO Items (item_id, item_name, price, category) VALUES (74, 'Plain Dosa', 100, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (75, 'Idly', 60, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (76, 'Pongal', 80, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (77, 'Vada', 60, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (78, 'Poori', 80, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (79, 'Masala Dosa', 120, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (80, 'Onion Uttapam', 130, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (81, 'Rava Dosa', 140, 'Veg');

-- Indian Breads
INSERT INTO Items (item_id, item_name, price, category) VALUES (82, 'Plain Naan', 55, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (83, 'Plain Roti', 50, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (84, 'Plain Kulcha', 55, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (85, 'Butter Naan', 66, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (86, 'Stuffed Naan', 90, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (87, 'Chappathi', 50, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (88, 'Parotta', 60, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (89, 'Paneer Kulcha', 110, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (90, 'Masala Kulcha', 100, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (91, 'Aloo Paratha', 85, 'Veg');

-- Veg CurriIs
INSERT INTO Items (item_id, item_name, price, category) VALUES (92, 'Mixed Veg Curry', 230, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (93, 'Paneer Butter Masala', 310, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (94, 'Kadai Paneer', 300, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (95, 'Dal Fry', 220, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (96, 'Malai Koftha', 365, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (97, 'Kadai Vegetables', 340, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (98, 'Mushroom Masala', 299, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (99, 'Dum Aloo', 289, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (100, 'Chana Masala', 250, 'Veg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (101, 'Chicken 65', 250, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (102, 'Mutton Seekh Kebab', 300, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (103, 'Tandoori Chicken', 350, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (104, 'Fish Tikka', 280, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (105, 'Prawn Masala Fry', 320, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (106, 'Chilli Fish Dry', 320, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (107, 'Fish 65', 320, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (108, 'Crab Lollipop', 280, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (109, 'Chicken Lolipop', 390, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (110, 'Dragon Chicken', 367, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (111, 'Chilli Chicken Dry', 254, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (112, 'Mutton Tikka', 319, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (113, 'Chicken Kebab', 345, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (114, 'Spicy Prawn Fry', 350, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (115, 'Prawn Ghee Roast', 345, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (116, 'Chicken Milagu Soup', 140, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (117, 'Mutton Milagu Soup', 150, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (118, 'Hot And Sour Chicken Soup', 185, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (119, 'Sweet Corn Chicken Soup', 178, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (120, 'Butter Chicken', 320, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (121, 'Rogan Josh', 400, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (122, 'Chicken Chettinad', 380, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (123, 'Mutton Korma', 249, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (124, 'Fish Curry', 210, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (125, 'Chicken Biriyani', 270, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (126, 'Fish Biriyani', 210, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (127, 'Mutton Biriyani', 290, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (128, 'Prawn Biriyani', 252, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (129, 'Hydrabadi Chicken Dum Biriyani', 300, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (130, 'Hydrabadi Mutton Dum Biriyani', 280, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (131, 'Naidu Mutton Biryani', 186, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (132, 'Boneless Chicken 65 Biryani', 280, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (133, 'Mutton Kola Biryani', 272, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (134, 'Egg Biryani', 235, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (135, 'Boneless Chicken Ghee Rice', 180, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (136, 'Pepper Fish Ghee Rice', 264, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (137, 'Egg Fried Rice', 230, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (138, 'Bucket Chicken Biryani', 3659, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (139, 'Bucket Mutton Biryani', 3587, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (140, 'Prawn 65 Biriyani', 365, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (141, 'Chicken Noodles', 300, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (142, 'Chicken Biriyani (served With Salan & Raita)', 323, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (143, 'Chicken Schezwan Rice', 289, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (144, 'Mutton Boneless Roll', 199, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (145, 'Chicken Boneless Roll', 199, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (146, 'Mutton Shami Kebab Roll', 199, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (147, 'Chicken Special Boneless Roll', 199, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (148, 'Mutton Sheek Kebab Roll', 169, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (149, 'Egg Roll', 188, 'nonveg');
INSERT INTO Items (item_id, item_name, price, category) VALUES (150, 'Egg Cheese Chicken Wrap Roll', 198, 'nonveg');


CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    bill_amt INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);
CREATE TABLE order_details (
    order_id INT,
    item_id INT,
    quantity INT,
    total_price INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
CREATE TABLE customer (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone_no VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    delivery_option VARCHAR(50),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);