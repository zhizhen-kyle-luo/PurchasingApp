# debug_connection.py
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# Print what the app is seeing
print("=== Environment Variables ===")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
print(f"POSTGRES_PASSWORD: {'*' * len(str(os.getenv('POSTGRES_PASSWORD', ''))) if os.getenv('POSTGRES_PASSWORD') else 'None'}")
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")

# Test the exact connection your app would use
try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        database=os.getenv('POSTGRES_DB')
    )
    print("\n✅ Connection successful!")
    
    # Test basic query
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user;")
    result = cur.fetchone()
    print(f"Connected to database: {result[0]} as user: {result[1]}")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nTrying with 'postgres' database instead...")
    
    # Try connecting to postgres database as fallback
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database='postgres'
        )
        print("✅ Connection to 'postgres' database successful!")
        print("Issue: Your app is trying to connect to a database that doesn't exist")
        conn.close()
    except Exception as e2:
        print(f"❌ Still failed: {e2}")