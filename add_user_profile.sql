-- Add user profile fields to existing user table
USE restaurant_management;

-- Add profile fields to user table
ALTER TABLE user 
ADD COLUMN full_name VARCHAR(100) AFTER email,
ADD COLUMN phone VARCHAR(20) AFTER full_name,
ADD COLUMN address TEXT AFTER phone;

-- Check the updated structure
DESCRIBE user;
