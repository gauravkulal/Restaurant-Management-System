import mysql.connector
from werkzeug.security import generate_password_hash

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'restaurant_management'
}

try:
    # Connect to database
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    
    print("Connected to database successfully!")
    
    # Step 1: Add is_admin column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
        db.commit()
        print("✓ Added is_admin column to user table")
    except mysql.connector.Error as e:
        if "Duplicate column name" in str(e):
            print("✓ is_admin column already exists")
        else:
            print(f"Error adding column: {e}")
    
    # Step 2: Check if admin user exists
    cursor.execute("SELECT user_id FROM user WHERE username = 'gaurav'")
    existing_user = cursor.fetchone()
    
    if existing_user:
        # Update existing user to be admin
        cursor.execute("UPDATE user SET is_admin = TRUE WHERE username = 'gaurav'")
        db.commit()
        print("✓ Updated existing user 'gaurav' to admin")
    else:
        # Create new admin user
        hashed_password = generate_password_hash('1234')
        cursor.execute(
            "INSERT INTO user (username, email, password, is_admin) VALUES (%s, %s, %s, %s)",
            ('gaurav', 'admin@chaiosa.com', hashed_password, True)
        )
        db.commit()
        print("✓ Created new admin user 'gaurav' with password '1234'")
    
    print("\n" + "="*50)
    print("Admin setup completed successfully!")
    print("="*50)
    print("\nAdmin Credentials:")
    print("  Username: gaurav")
    print("  Password: 1234")
    print("\nYou can now login with these credentials to access the admin dashboard.")
    print("="*50)
    
except mysql.connector.Error as err:
    print(f"Database Error: {err}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'db' in locals() and db.is_connected():
        db.close()
