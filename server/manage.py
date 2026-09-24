#!/usr/bin/env python3
"""
Management script for the application - similar to Django's manage.py
Provides commands for database migrations, user creation, and other admin tasks.

Usage:
    python manage.py makemigrations "description"  # Create a new migration
    python manage.py migrate                       # Run pending migrations
    python manage.py createsuperuser              # Create an admin user interactively
    python manage.py createuser                   # Create a regular user
    python manage.py shell                        # Open interactive shell with DB session
    python manage.py dbshell                      # Open database shell
    python manage.py reset_db                     # Reset database (WARNING: deletes all data)
    python manage.py seed                         # Seed initial data (permissions)
    python manage.py seed_fake --count 1000       # Seed repeatable fake users/products/stock/carts
"""

import sys
import os
from pathlib import Path

# Add the server directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import subprocess
import getpass
from decimal import Decimal
from sqlalchemy import select
from sqlmodel import Session
from app.core.database import Base, engine
from app import models
from app.models import User, UserRole, RolePermissions, DEFAULT_ROLE_PERMISSIONS
from app.auth import hash_password

def makemigrations(message: str = "auto migration"):
    """Create a new Alembic migration"""
    print(f"📝 Creating migration: {message}")
    try:
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("❌ Error:", result.stderr)
            return False
        print("✅ Migration created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        return False


def migrate():
    """Run pending database migrations"""
    print("🔄 Running database migrations...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("❌ Error:", result.stderr)
            return False
        print("✅ Migrations applied successfully")
        return True
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False


def downgrade(revision: str = "-1"):
    """Downgrade database migration"""
    print(f"⏪ Downgrading database to: {revision}")
    try:
        result = subprocess.run(
            ["alembic", "downgrade", revision],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("❌ Error:", result.stderr)
            return False
        print("✅ Downgrade completed")
        return True
    except Exception as e:
        print(f"❌ Error downgrading: {e}")
        return False


def createsuperuser():
    """Create an admin user interactively"""
    print("👤 Create Admin User")
    print("-" * 50)
    
    db = Session(engine)
    try:
        # Get username
        while True:
            username = input("Username: ").strip()
            if not username:
                print("❌ Username cannot be empty")
                continue
            
            # Check if user exists
            existing = db.exec(select(User).where(User.username == username)).first()
            if existing:
                print(f"❌ User '{username}' already exists")
                continue
            break

        email = input("Email: ").strip().lower()
        full_name = input("Full name: ").strip()
        if not email or not full_name:
            print("❌ Email and full name are required")
            return False
        if db.exec(select(User).where(User.email == email)).first():
            print(f"❌ Email '{email}' already exists")
            return False
        
        # Get password
        while True:
            password = getpass.getpass("Password: ")
            if len(password) < 8:
                print("❌ Password must be at least 8 characters")
                continue
            
            password_confirm = getpass.getpass("Password (again): ")
            if password != password_confirm:
                print("❌ Passwords don't match")
                continue
            break
        
        # Create admin user
        hashed_password = hash_password(password)
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=UserRole.admin
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Admin user '{username}' created successfully (ID: {user.id})")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating user: {e}")
        return False
    finally:
        db.close()


def createuser():
    """Create a regular user interactively"""
    print("👤 Create User")
    print("-" * 50)
    
    db = Session(engine)
    try:
        # Get username
        while True:
            username = input("Username: ").strip()
            if not username:
                print("❌ Username cannot be empty")
                continue
            
            # Check if user exists
            existing = db.exec(select(User).where(User.username == username)).first()
            if existing:
                print(f"❌ User '{username}' already exists")
                continue
            break

        email = input("Email: ").strip().lower()
        full_name = input("Full name: ").strip()
        if not email or not full_name:
            print("❌ Email and full name are required")
            return False
        if db.exec(select(User).where(User.email == email)).first():
            print(f"❌ Email '{email}' already exists")
            return False
        
        # Get password
        while True:
            password = getpass.getpass("Password: ")
            if len(password) < 8:
                print("❌ Password must be at least 8 characters")
                continue
            
            password_confirm = getpass.getpass("Password (again): ")
            if password != password_confirm:
                print("❌ Passwords don't match")
                continue
            break
        
        # Get role
        print("\nSelect role:")
        print("1. Customer")
        print("2. Staff")
        print("3. Employee")
        while True:
            role_choice = input("Choice [1]: ").strip() or "1"
            if role_choice == "1":
                role = UserRole.customer
                break
            elif role_choice == "2":
                role = UserRole.staff
                break
            elif role_choice == "3":
                role = UserRole.employee
                break
            else:
                print("❌ Invalid choice. Please enter 1 or 2")
        
        # Create user
        hashed_password = hash_password(password)
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ User '{username}' created successfully (ID: {user.id}, Role: {role.value})")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating user: {e}")
        return False
    finally:
        db.close()


def seed():
    """Seed initial data (role permissions)"""
    print("🌱 Seeding initial data...")
    
    db = Session(engine)
    try:
        # Seed role permissions
        for role_name, perms in DEFAULT_ROLE_PERMISSIONS.items():
            role_enum = UserRole[role_name]
            existing = db.exec(select(RolePermissions).where(RolePermissions.role == role_enum)).first()
            
            if existing:
                print(f"ℹ️  Role permissions for '{role_name}' already exist, skipping...")
                continue
            
            role_perms = RolePermissions(
                role=role_enum,
                permissions=perms
            )
            db.add(role_perms)
            print(f"✅ Created permissions for role: {role_name}")
        
        db.commit()
        print("✅ Seeding completed")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        return False
    finally:
        db.close()


def seed_fake(count: int = 100):
    """Create repeatable, duplicate-safe fake data for local/load testing.

    ``count`` is the target number for each primary fixture group: customers,
    products, inventory records, and carts. Existing seed identifiers are
    reused, so rerunning the command does not create duplicates.
    """
    if count < 1 or count > 1_000_000:
        raise ValueError("count must be between 1 and 1,000,000")

    print(f"🌱 Seeding up to {count} fake customers, products, inventory records, and carts...")
    db = Session(engine)
    batch_size = 200
    try:
        category_names = ["Electronics", "Home", "Books", "Apparel", "Sports"]
        categories = []
        for name in category_names:
            category = db.query(models.Category).filter(models.Category.name == name).first()
            if not category:
                slug = name.lower().replace(" ", "-")
                category = models.Category(name=name, slug=slug, description=f"Seed category: {name}")
                db.add(category)
                db.flush()
            categories.append(category)

        # One hash is intentional: these are non-production test accounts.
        seeded_password = hash_password("TestPassword123!")
        created_users = created_products = created_inventory = created_carts = 0
        for start in range(1, count + 1, batch_size):
            end = min(start + batch_size, count + 1)
            for index in range(start, end):
                username = f"seed_user_{index:06d}"
                user = db.query(User).filter(User.username == username).first()
                if not user:
                    user = User(
                        username=username,
                        email=f"{username}@example.test",
                        full_name=f"Seed User {index:06d}",
                        hashed_password=seeded_password,
                        role=UserRole.customer,
                    )
                    db.add(user)
                    db.flush()
                    created_users += 1

                sku = f"SEED-{index:06d}"
                product = db.query(models.Product).filter(models.Product.sku == sku).first()
                if not product:
                    product = models.Product(
                        category_id=categories[(index - 1) % len(categories)].id,
                        name=f"Seed Product {index:06d}",
                        sku=sku,
                        description="Generated test product",
                        price=Decimal(str(10 + (index % 500))),
                        currency="INR",
                        is_published=True,
                    )
                    db.add(product)
                    db.flush()
                    created_products += 1

                inventory = db.query(models.Inventory).filter(models.Inventory.product_id == product.id).first()
                if not inventory:
                    inventory = models.Inventory(product_id=product.id, quantity=100, low_stock_threshold=10)
                    db.add(inventory)
                    db.add(models.InventoryMovement(
                        product_id=product.id,
                        quantity_delta=100,
                        reason="Fake data seed",
                        reference_type="seed",
                        reference_id=sku,
                    ))
                    created_inventory += 1

                if not db.query(models.Cart).filter(models.Cart.user_id == user.id).first():
                    db.add(models.Cart(user_id=user.id))
                    created_carts += 1

            db.commit()

        print(
            "✅ Seed complete: "
            f"{created_users} users, {created_products} products, "
            f"{created_inventory} inventory records, {created_carts} carts created."
        )
        print("🔐 Seed user password: TestPassword123!")
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def shell():
    """Open interactive Python shell with database session"""
    print("🐍 Starting interactive shell...")
    print("Available objects: db (database session), User, UserRole, RolePermissions")
    print("Type 'exit()' to quit\n")
    
    db = Session(engine)
    
    # Import common models
    from app.models import User, UserRole, RolePermissions
    
    import code
    code.interact(local={
        'db': db,
        'User': User,
        'UserRole': UserRole,
        'RolePermissions': RolePermissions,
    })
    
    db.close()


def dbshell():
    """Open database shell"""
    from app.core.config import get_settings
    settings = get_settings()
    
    db_url = settings.database_url
    
    if db_url.startswith("sqlite"):
        # Extract SQLite database file path
        db_file = db_url.replace("sqlite:///", "").replace("sqlite://", "")
        print(f"📊 Opening SQLite database: {db_file}")
        try:
            subprocess.run(["sqlite3", db_file])
        except FileNotFoundError:
            print("❌ sqlite3 command not found. Please install SQLite.")
    elif db_url.startswith("postgresql"):
        print(f"📊 Opening PostgreSQL database...")
        print("💡 Use: psql {database_url}")
        print(f"   {db_url}")
    else:
        print("❌ Unsupported database type")


def reset_db():
    """Reset database (WARNING: deletes all data)"""
    print("⚠️  WARNING: This will delete ALL data in the database!")
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Operation cancelled")
        return False
    
    print("🗑️  Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
        
        print("📋 Creating fresh tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created")
        
        # Seed initial data
        seed()
        
        return True
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False


def show_migration_history():
    """Show migration history"""
    print("📜 Migration History:")
    try:
        result = subprocess.run(
            ["alembic", "history"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("❌ Error:", result.stderr)
    except Exception as e:
        print(f"❌ Error: {e}")


def show_current_revision():
    """Show current database revision"""
    print("📍 Current Database Revision:")
    try:
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("❌ Error:", result.stderr)
    except Exception as e:
        print(f"❌ Error: {e}")


def show_help():
    """Show help message"""
    print(__doc__)


def requested_seed_count() -> int:
    args = sys.argv[2:]
    if not args:
        return 100
    if len(args) == 1 and not args[0].startswith("--"):
        return int(args[0])
    if len(args) == 2 and args[0] == "--count":
        return int(args[1])
    if len(args) == 1 and args[0].startswith("--count="):
        return int(args[0].split("=", 1)[1])
    raise ValueError("Usage: python manage.py seed_fake --count 1000")


def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    commands = {
        'makemigrations': lambda: makemigrations(sys.argv[2] if len(sys.argv) > 2 else "auto migration"),
        'migrate': migrate,
        'downgrade': lambda: downgrade(sys.argv[2] if len(sys.argv) > 2 else "-1"),
        'createsuperuser': createsuperuser,
        'createuser': createuser,
        'seed': seed,
        'seed_fake': lambda: seed_fake(requested_seed_count()),
        'shell': shell,
        'dbshell': dbshell,
        'reset_db': reset_db,
        'history': show_migration_history,
        'current': show_current_revision,
        'help': show_help,
        '--help': show_help,
        '-h': show_help,
    }
    
    if command not in commands:
        print(f"❌ Unknown command: {command}")
        print("Run 'python manage.py help' for available commands")
        sys.exit(1)
    
    try:
        commands[command]()
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
