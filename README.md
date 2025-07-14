# 🔐 FastAPI Role-Based Access Control (RBAC) PoC

This is a **production-ready Role-Based Access Control (RBAC)** system built using **FastAPI**. It supports:

- Role-based access (with role hierarchies)
- Object-level permissions
- Dynamic permission generation using modules and actions
- Multi-role assignment per user
- Audit logs for sensitive operations
- Clean separation of layers (API, services, repository, database)
- Future-ready for multitenant support

---

## 🛠️ Installation & Setup

### 1️⃣ Install Dependencies

Make sure you're using Python 3.11 or higher. This project uses `uv` for dependency management.

Create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 2️⃣ Run Alembic Migrations

To apply the database schema:

```bash
alembic upgrade head
```

This will create all necessary tables in the connected PostgreSQL database.

> Make sure your database connection is correctly configured using environment variables (see `.env.examples`).

### 3️⃣ Seed Initial Data

Seed the system with:

- One SuperAdmin user
- Base Actions: create, read, update, delete
- Base Modules: e.g., Post, Invoice etc.

Run the seed script:

uv run python app/db/init_db.py

This will:

- Create system actions that are reusable across all modules
- Add foundational modules to the system
- Create a SuperAdmin user with full access
- Generate permissions for each action + module combination
- Assign all permissions to the SuperAdmin role
- Assign the SuperAdmin role to the seeded user

#### 🧪 SuperAdmin User Credentials

After running the seed script, the SuperAdmin user is created with the following default values:

- **Email**: superadmin@example.com
- **Password**: SuperAdmin123

> ⚠️ Change these credentials in `init_db.py` or immediately after login in your environment.

---

## 📋 API Documentation

Once the server is running, you can explore the API via Swagger UI:

http://localhost:8000/docs

It includes endpoints for:

- Authentication (login)
- User and role management
- Module and action management
- Permission and object-permission assignment
- Audit log inspection

---

## 🧠 Core Concepts

- **Roles** represent collections of permissions
- **Permissions** are generated from action + module
- **Modules** represent high-level resources (like Post, Invoice etc.)
- **Actions** represent operations (like create, read, update, delete)
- **Object Permissions** allow assigning permissions on a specific record/resource
- **Audit Logs** capture user actions like role assignments and permission changes

---

## ✅ What’s Included

- Clean, modular FastAPI codebase
- RBAC system with extensibility for:
  - Role hierarchy
  - Object/resource-based permission assignment
  - Permission grouping by module + action
  - Audit trails