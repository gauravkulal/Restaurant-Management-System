import mysql.connector

# Database connection
try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='restaurant_management'
    )
    cursor = connection.cursor()
    
    print("Connected to database successfully!")
    
    # Read and execute SQL file
    with open('update_menu_schema.sql', 'r') as file:
        sql_commands = file.read().split(';')
        
        for command in sql_commands:
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                    print(f"✓ Executed: {command[:50]}...")
                except mysql.connector.Error as err:
                    # Ignore if column already exists or table exists
                    if 'Duplicate column' in str(err) or 'already exists' in str(err):
                        print(f"⚠ Skipped (already exists): {command[:50]}...")
                    else:
                        print(f"✗ Error: {err}")
    
    connection.commit()
    print("\n" + "="*50)
    print("Database schema updated successfully!")
    print("="*50)
    
except mysql.connector.Error as err:
    print(f"Database error: {err}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
