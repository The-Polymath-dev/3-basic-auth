import mysql.connector
import bcrypt
import time

def create_connection():
    # Add retry logic for container startup
    max_retries = 30
    for _ in range(max_retries):
        try:
            connection = mysql.connector.connect(
                host='mysql',  # Docker service name
                user='root',
                password='mysecretpassword',
                database='auth_db'
            )
            print("Successfully connected to MySQL!")
            return connection
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            time.sleep(1)
    return None

def register(username, password):
    connection = create_connection()
    if not connection:
        return "Error: Could not connect to the database."

    try:
        cursor = connection.cursor()

        # Check if username exists
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return "Error: Username already taken."

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert new user
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        connection.commit()
        return "User registered successfully."

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return "Error: Could not register user."
    finally:
        cursor.close()
        connection.close()

def login(username, password):
    connection = create_connection()
    if not connection:
        return "Error: Could not connect to the database."

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            return "Error: Username not found."

        stored_hash = result[0]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return "Login successful!"
        return "Error: Invalid password."

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return "Error: Could not log in."
    finally:
        cursor.close()
        connection.close()

# Test the functionality
if __name__ == "__main__":
    # Wait for MySQL to be ready
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

        # Test registration
        print(register("testuser", "password123"))
        # Test login
        print(login("testuser", "password123"))
