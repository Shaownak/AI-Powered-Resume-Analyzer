import sys

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database():
    """Create the resume_screener database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        connection = psycopg2.connect(host="localhost", user="postgres", password="shaownak", port="5432")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'resume_screener'")
        exists = cursor.fetchone()

        if exists:
            print("✅ Database 'resume_screener' already exists")
        else:
            # Create database
            cursor.execute("CREATE DATABASE resume_screener")
            print("✅ Database 'resume_screener' created successfully")

        cursor.close()
        connection.close()
        return True

    except psycopg2.Error as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        print("\nPossible solutions:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if username/password is correct")
        print("3. Verify PostgreSQL is listening on localhost:5432")
        return False


if __name__ == "__main__":
    create_database()
