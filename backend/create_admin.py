"""
Script to create an admin user for the Pollution Management System
Run this script to create your first admin account
"""

from werkzeug.security import generate_password_hash
from db import get_db_connection

def create_admin():
    print("=== Create Admin User ===\n")
    
    name = input("Enter admin name: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    
    if not name or not email or not password:
        print("Error: All fields are required!")
        return
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"\nError: User with email '{email}' already exists!")
            cursor.close()
            conn.close()
            return
        
        # Hash password and create admin
        hashed_password = generate_password_hash(password)
        
        query = """
        INSERT INTO users (name, email, password, role)
        VALUES (%s, %s, %s, 'ADMIN')
        """
        cursor.execute(query, (name, email, hashed_password))
        conn.commit()
        
        print(f"\n✓ Admin user created successfully!")
        print(f"  Name: {name}")
        print(f"  Email: {email}")
        print(f"  Role: ADMIN")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nMake sure:")
        print("1. MySQL is running")
        print("2. Database 'pollution_db' exists")
        print("3. Run the schema.sql file first")

if __name__ == "__main__":
    create_admin()
