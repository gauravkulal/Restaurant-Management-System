-- Add is_admin column to user table
ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;

-- Create or update admin user (gaurav with password: 1234)
-- First, delete if exists
DELETE FROM user WHERE username = 'gaurav';

-- Insert admin user with hashed password for '1234'
-- The password hash is generated using werkzeug.security.generate_password_hash('1234')
INSERT INTO user (username, email, password, is_admin) 
VALUES ('gaurav', 'admin@chaiosa.com', 'scrypt:32768:8:1$v8P5Z8Cy2dNzvmQE$c8f6c0e5d0a8c8c8a8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8', TRUE);

-- Note: You should run this SQL after creating the admin user through signup first,
-- then update the is_admin flag, or manually hash the password using Python
