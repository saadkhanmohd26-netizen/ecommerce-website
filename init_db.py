"""
Database initialization script
Run this to create or reset the database
"""
from app import app, db

if __name__ == '__main__':
    with app.app_context():
        print("Resetting database...")
        # Drop all tables
        print("  Dropping existing tables...")
        db.drop_all()
        
        # Create all tables with new schema
        print("  Creating tables with new schema...")
        db.create_all()
        print("✓ Database reset successfully!")
        print("\nDatabase is ready. You can now run the app.")

