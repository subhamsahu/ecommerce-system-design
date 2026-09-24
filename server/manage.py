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
"""

import sys
import os
from pathlib import Path

# Add the server directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import subprocess
import getpass
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import Base, engine
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
            existing = db.execute(select(User).where(User.username == username)).scalars().first()
            if existing:
                print(f"❌ User '{username}' already exists")
                continue
            break
        
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
            existing = db.execute(select(User).where(User.username == username)).scalars().first()
            if existing:
                print(f"❌ User '{username}' already exists")
                continue
            break
        
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
            existing = db.execute(select(RolePermissions).where(RolePermissions.role == role_enum)).scalars().first()
            
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
