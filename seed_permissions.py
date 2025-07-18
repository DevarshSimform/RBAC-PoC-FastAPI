#!/usr/bin/env python3
"""
Permission Seeding Script

This script handles:
1. Initial seeding of superadmin user, role, and permissions for all existing tables
2. Detection of new tables and creation of permissions for them
3. Detection of removed tables and cleanup of their permissions
4. Assignment of all permissions to superadmin role

Usage:
    python seed_permissions.py

The script is idempotent - it can be run multiple times safely.
"""

import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")  # Adjust as needed


def get_db_session():
    """Create database session"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def seed_initial_data(session):
    """Seed basic actions, superadmin role, and superadmin user"""
    print("🌱 Seeding initial data...")

    # Seed actions if they don't exist
    actions_data = [
        {"name": "create"},
        {"name": "read"},
        {"name": "update"},
        {"name": "delete"},
    ]

    for action_data in actions_data:
        result = session.execute(
            text("SELECT id FROM actions WHERE name = :name"),
            {"name": action_data["name"]},
        )
        if not result.fetchone():
            session.execute(
                text("INSERT INTO actions (name) VALUES (:name)"), action_data
            )
            print(f"   ✅ Created action: {action_data['name']}")

    # Seed superadmin role if it doesn't exist
    result = session.execute(text("SELECT id FROM roles WHERE name = 'superadmin'"))
    superadmin_role = result.fetchone()

    if not superadmin_role:
        session.execute(text("INSERT INTO roles (name) VALUES ('superadmin')"))
        print("   ✅ Created superadmin role")
        result = session.execute(text("SELECT id FROM roles WHERE name = 'superadmin'"))
        superadmin_role = result.fetchone()

    superadmin_role_id = superadmin_role[0]

    # Seed superadmin user if it doesn't exist
    result = session.execute(
        text("SELECT id FROM users WHERE email = 'superadmin@gmail.com'")
    )
    superadmin_user = result.fetchone()

    if not superadmin_user:
        session.execute(
            text(
                """
                INSERT INTO users (firstname, lastname, email, password_hash)
                VALUES ('superadmin', 'superadmin', 'superadmin@gmail.com', 'Admin@123')
            """
            )
        )
        print("   ✅ Created superadmin user")
        result = session.execute(
            text("SELECT id FROM users WHERE email = 'superadmin@gmail.com'")
        )
        superadmin_user = result.fetchone()

    superadmin_user_id = superadmin_user[0]

    # Create user-role relationship if it doesn't exist
    result = session.execute(
        text(
            "SELECT id FROM user_roles WHERE user_id = :user_id AND role_id = :role_id"
        ),
        {"user_id": superadmin_user_id, "role_id": superadmin_role_id},
    )

    if not result.fetchone():
        session.execute(
            text(
                "INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"
            ),
            {"user_id": superadmin_user_id, "role_id": superadmin_role_id},
        )
        print("   ✅ Assigned superadmin role to superadmin user")

    return superadmin_role_id


def get_all_tables(session):
    """Get all tables from the database"""
    tables_query = text(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        AND name NOT IN ('alembic_version')
    """
    )
    return {row[0] for row in session.execute(tables_query).fetchall()}


def get_existing_modules(session):
    """Get existing modules from the database"""
    return {
        row[0] for row in session.execute(text("SELECT name FROM modules")).fetchall()
    }


def create_module_and_permissions(session, table_name, superadmin_role_id):
    """Create module and permissions for a table"""
    print(f"   📁 Processing table: {table_name}")

    # Create module for the table
    session.execute(
        text("INSERT INTO modules (name) VALUES (:name)"), {"name": table_name}
    )
    result = session.execute(
        text("SELECT id FROM modules WHERE name = :name"), {"name": table_name}
    )
    module = result.fetchone()
    module_id = module[0]
    print(f"      ✅ Created module: {table_name}")

    # Get all actions
    actions = session.execute(text("SELECT id, name FROM actions")).fetchall()

    # Create permissions for each action for the module
    for action_row in actions:
        action_id, action_name = action_row
        permission_name = f"{action_name}:{table_name}"

        # Create permission if it doesn't exist
        result = session.execute(
            text("SELECT id FROM permissions WHERE name = :name"),
            {"name": permission_name},
        )
        permission = result.fetchone()

        if not permission:
            session.execute(
                text(
                    """
                    INSERT INTO permissions (name, module_id, action_id)
                    VALUES (:name, :module_id, :action_id)
                """
                ),
                {
                    "name": permission_name,
                    "module_id": module_id,
                    "action_id": action_id,
                },
            )
            result = session.execute(
                text("SELECT id FROM permissions WHERE name = :name"),
                {"name": permission_name},
            )
            permission = result.fetchone()
            print(f"      ✅ Created permission: {permission_name}")

        permission_id = permission[0]

        # Create role-permission relationship for superadmin if it doesn't exist
        result = session.execute(
            text(
                """
                SELECT id FROM role_permissions
                WHERE role_id = :role_id AND permission_id = :permission_id
            """
            ),
            {"role_id": superadmin_role_id, "permission_id": permission_id},
        )

        if not result.fetchone():
            session.execute(
                text(
                    """
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES (:role_id, :permission_id)
                """
                ),
                {"role_id": superadmin_role_id, "permission_id": permission_id},
            )
            print(f"      ✅ Assigned {permission_name} to superadmin role")


def remove_module_and_permissions(session, module_name):
    """Remove module and its associated permissions"""
    print(f"   🗑️  Removing module: {module_name}")

    # Get module ID
    result = session.execute(
        text("SELECT id FROM modules WHERE name = :name"), {"name": module_name}
    )
    module = result.fetchone()

    if not module:
        print(f"      ⚠️  Module {module_name} not found")
        return

    module_id = module[0]

    # Get all permissions for this module
    permissions = session.execute(
        text("SELECT id, name FROM permissions WHERE module_id = :module_id"),
        {"module_id": module_id},
    ).fetchall()

    for permission_row in permissions:
        permission_id, permission_name = permission_row

        # Remove role-permission relationships
        session.execute(
            text("DELETE FROM role_permissions WHERE permission_id = :permission_id"),
            {"permission_id": permission_id},
        )
        print(f"      ✅ Removed role assignments for permission: {permission_name}")

        # Remove permission
        session.execute(
            text("DELETE FROM permissions WHERE id = :permission_id"),
            {"permission_id": permission_id},
        )
        print(f"      ✅ Removed permission: {permission_name}")

    # Remove module
    session.execute(
        text("DELETE FROM modules WHERE id = :module_id"), {"module_id": module_id}
    )
    print(f"      ✅ Removed module: {module_name}")


def sync_permissions(session, superadmin_role_id):
    """Sync permissions for new tables and remove permissions for deleted tables"""
    print("🔄 Syncing permissions...")

    # Get all tables and existing modules
    all_tables = get_all_tables(session)
    existing_modules = get_existing_modules(session)

    # Identify new tables (tables not in modules)
    new_tables = all_tables - existing_modules

    # Identify removed tables (modules without corresponding tables)
    removed_tables = existing_modules - all_tables

    # Handle removed tables
    if removed_tables:
        print(
            f"   📉 Found {len(removed_tables)} removed tables: {', '.join(removed_tables)}"
        )
        for table_name in removed_tables:
            remove_module_and_permissions(session, table_name)
    else:
        print("   ℹ️  No removed tables found")

    # Handle new tables
    if new_tables:
        print(f"   📊 Found {len(new_tables)} new tables: {', '.join(new_tables)}")
        for table_name in new_tables:
            create_module_and_permissions(session, table_name, superadmin_role_id)
    else:
        print("   ℹ️  No new tables found")

    return len(new_tables), len(removed_tables)


def is_initial_run(session):
    """Check if this is the initial run (no modules exist)"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM modules")).scalar()
        return result == 0
    except Exception:
        # If modules table doesn't exist, it's definitely initial run
        return True


def display_statistics(session):
    """Display final statistics"""
    print("\n📊 Final Statistics:")
    try:
        actions_count = session.execute(text("SELECT COUNT(*) FROM actions")).scalar()
        modules_count = session.execute(text("SELECT COUNT(*) FROM modules")).scalar()
        permissions_count = session.execute(
            text("SELECT COUNT(*) FROM permissions")
        ).scalar()
        roles_count = session.execute(text("SELECT COUNT(*) FROM roles")).scalar()
        users_count = session.execute(text("SELECT COUNT(*) FROM users")).scalar()

        print(f"   Actions: {actions_count}")
        print(f"   Modules: {modules_count}")
        print(f"   Permissions: {permissions_count}")
        print(f"   Roles: {roles_count}")
        print(f"   Users: {users_count}")
    except Exception as e:
        print(f"   ⚠️  Could not fetch statistics: {e}")


def main():
    """Main function"""
    print("🚀 Starting Permission Seeding Script")
    print("=" * 50)

    session = get_db_session()

    try:
        # Check if this is initial run
        initial_run = is_initial_run(session)

        if initial_run:
            print("🆕 Initial run detected - setting up base data")
        else:
            print("🔄 Subsequent run detected - syncing new tables")

        # Seed initial data (actions, superadmin role, superadmin user)
        superadmin_role_id = seed_initial_data(session)

        # Sync permissions for all tables (new and existing)
        if initial_run:
            print("🏗️  Creating modules and permissions for all existing tables...")
            all_tables = get_all_tables(session)
            processed_count = 0
            for table_name in all_tables:
                create_module_and_permissions(session, table_name, superadmin_role_id)
                processed_count += 1
            print(f"   ✅ Processed {processed_count} tables")
        else:
            # Only sync new tables and remove deleted tables
            new_tables_count, removed_tables_count = sync_permissions(
                session, superadmin_role_id
            )
            if new_tables_count > 0:
                print(f"   ✅ Processed {new_tables_count} new tables")
            if removed_tables_count > 0:
                print(f"   ✅ Cleaned up {removed_tables_count} removed tables")

        # Commit all changes
        session.commit()

        print("\n🎉 Permission seeding completed successfully!")

        # Display statistics
        display_statistics(session)

    except Exception as e:
        print(f"\n❌ Error during permission seeding: {e}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
