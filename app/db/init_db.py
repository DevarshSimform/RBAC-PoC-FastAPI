from datetime import datetime

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models import Action, Module, Permission, Role, RolePermission, User, UserRole
from app.utils.hashing import get_password_hash


def get_or_create(db: Session, model, defaults=None, **kwargs):
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    params = {**kwargs, **(defaults or {})}
    instance = model(**params)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance, True


def seed_initial_data():
    db = SessionLocal()
    now = datetime.utcnow()

    # 1. Create SuperAdmin user
    superadmin_user, _ = get_or_create(
        db,
        User,
        email="superadmin@example.com",
        defaults={
            "firstname": "Super",
            "lastname": "Admin",
            "password_hash": get_password_hash("SuperAdmin123"),
            "last_login": None,
            "created_at": now,
            "updated_at": now,
        },
    )

    # 2. Create CRUD actions
    action_objs = {}
    for action_name in ["create", "read", "update", "delete"]:
        action, _ = get_or_create(
            db,
            Action,
            name=action_name,
            defaults={"created_by": superadmin_user.id, "created_at": now},
        )
        action_objs[action_name] = action

    # 3. Create modules including join-tables
    module_names = [
        "user",
        "role",
        "permission",
        "module",
        "action",
        "user_role",
        "role_permission",
    ]
    module_objs = {}
    for module_name in module_names:
        module, _ = get_or_create(
            db,
            Module,
            name=module_name,
            defaults={"created_by": superadmin_user.id, "created_at": now},
        )
        module_objs[module_name] = module

    # 4. Create permissions (action × module)
    permission_objs = []
    for module in module_objs.values():
        for action in action_objs.values():
            permission_name = f"{module.name}:{action.name}"
            permission, _ = get_or_create(
                db,
                Permission,
                name=permission_name,
                module_id=module.id,
                action_id=action.id,
                defaults={
                    "description": f"{action.name} {module.name}",
                    "created_by": superadmin_user.id,
                    "created_at": now,
                },
            )
            permission_objs.append(permission)

    # 5. Create SuperAdmin role
    superadmin_role, _ = get_or_create(
        db,
        Role,
        name="SuperAdmin",
        defaults={
            "description": "System SuperAdmin with all permissions",
            "created_by": superadmin_user.id,
            "created_at": now,
        },
    )

    # 6. Assign all permissions to SuperAdmin role
    for perm in permission_objs:
        get_or_create(
            db,
            RolePermission,
            role_id=superadmin_role.id,
            permission_id=perm.id,
            defaults={"granted_by": superadmin_user.id, "granted_at": now},
        )

    # 7. Assign SuperAdmin role to SuperAdmin user
    get_or_create(
        db,
        UserRole,
        user_id=superadmin_user.id,
        role_id=superadmin_role.id,
        defaults={"assigned_by": superadmin_user.id, "assigned_at": now},
    )

    print("✅ Seeded SuperAdmin user, actions, modules, permissions, and role.")


if __name__ == "__main__":
    seed_initial_data()
