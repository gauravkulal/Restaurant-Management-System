import mysql.connector
from werkzeug.security import generate_password_hash

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'restaurant_management'
}

def ensure_admin(cursor, username, email, password):
    """Ensure the given user exists and has admin privileges."""
    cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.execute("UPDATE user SET is_admin = TRUE WHERE username = %s", (username,))
        print(f"✓ Updated existing user '{username}' to admin")
    else:
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO user (username, email, password, is_admin) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_password, True)
        )
        print(f"✓ Created new admin user '{username}' with password '{password}'")


try:
    # Connect to database
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(buffered=True)
    
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
    
    # Step 2: Ensure required admin accounts exist
    ensure_admin(cursor, 'gaurav', 'admin@chaiosa.com', '1234')
    db.commit()
    ensure_admin(cursor, 'aryan', 'aryan@gmail.com', '1234')
    db.commit()

    print("\n" + "="*50)
    print("Admin setup completed successfully!")
    print("="*50)
    print("\nAdmin Credentials Updated:")
    print("  Username: gaurav | Password: 1234")
    print("  Username: aryan  | Password: 1234")
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
