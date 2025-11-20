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
    with open('table_orders_schema.sql', 'r') as file:
        sql_commands = file.read().split(';')
        
        for command in sql_commands:
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                    print(f"✓ Executed: {command[:60]}...")
                except mysql.connector.Error as err:
                    # Ignore if already exists
                    if 'already exists' in str(err) or 'Duplicate' in str(err):
                        print(f"⚠ Skipped (already exists): {command[:60]}...")
                    else:
                        print(f"✗ Error: {err}")
    
    connection.commit()
    print("\n" + "="*50)
    print("Table orders schema created successfully!")
    print("✓ Default 6 tables created")
    print("="*50)
    
except mysql.connector.Error as err:
    print(f"Database error: {err}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
