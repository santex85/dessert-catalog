"""
Script for initializing production database structure only (no test data)
"""
from app.database import SessionLocal, engine, Base

def init_prod_db():
    """Create database tables without any test data"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully.")
        print("✓ Database is ready for production use.")
        print("\n⚠️  IMPORTANT: Create an admin user using:")
        print("   python create_admin.py <username> <email> <password>")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_prod_db()

