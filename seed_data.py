"""
Database seeding script for testing

Run this after setting up the database to create sample data:
- Admin user
- Regular users
- Sample loans

Usage:
    python seed_data.py
"""

from app.database import SessionLocal, init_db
from app.models.user import User, UserRole
from app.models.wallet import Wallet
from app.auth.jwt import get_password_hash


def seed_database():
    """Seed database with sample data"""
    
    # Initialize database tables
    print("🗄️  Initializing database...")
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("⚠️  Database already contains users. Skipping seed.")
            return
        
        # Create admin user
        print("👤 Creating admin user...")
        admin = User(
            name="Admin User",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.flush()
        
        admin_wallet = Wallet(user_id=admin.id, balance=0)
        db.add(admin_wallet)
        
        # Create sample users
        print("👥 Creating sample users...")
        users_data = [
            ("John Doe", "john@example.com", "password123"),
            ("Jane Smith", "jane@example.com", "password123"),
            ("Bob Johnson", "bob@example.com", "password123"),
        ]
        
        for name, email, password in users_data:
            user = User(
                name=name,
                email=email,
                hashed_password=get_password_hash(password),
                role=UserRole.USER
            )
            db.add(user)
            db.flush()
            
            wallet = Wallet(user_id=user.id, balance=0)
            db.add(wallet)
        
        db.commit()
        
        print("✅ Database seeded successfully!")
        print("\n📝 Sample credentials:")
        print("   Admin: admin@example.com / admin123")
        print("   User:  john@example.com / password123")
        print("   User:  jane@example.com / password123")
        print("   User:  bob@example.com / password123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
