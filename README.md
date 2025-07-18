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

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- [uv](https://docs.astral.sh/uv/) package manager

### 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd fastapi-rbac-poc
```

### 2️⃣ Install Dependencies

This project uses `uv` for dependency management. Create a virtual environment and install dependencies:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies from pyproject.toml
uv sync
```

### 3️⃣ Environment Configuration

Create a `.env` file based on the provided `.env.example`:

```bash
cp .env.example .env
```

Configure your database connection and other environment variables in the `.env` file.

### 4️⃣ Database Setup & Migrations

This project uses a custom Django-style migration management script with Alembic.

#### Initialize Database Schema

Run the initial migration to create all necessary tables:

```bash
python manage.py migrate
```

#### Migration Management Commands

The project includes a custom migration management script with the following commands:

**Create New Migration:**
```bash
python manage.py makemigrations -m "migration message"
```

**Apply Migrations:**
```bash
python manage.py migrate
```

**Seed Permissions:**
```bash
python manage.py seed_permissions
```

**Show Help:**
```bash
python manage.py help
```

**Examples:**
```bash
# Create a new migration
python manage.py makemigrations -m "add user table"

# Apply all pending migrations
python manage.py migrate

# Seed permissions only
python manage.py seed_permissions
```

### 5️⃣ Seed Initial Data

Seed the system with foundational data:
To seed initial data you need to create initial migration to create db_schema then you can run migrate command to seed all required initial data.
If there is no migration inside migrations/versions, migrate will not work


#### 🧪 superadmin User Credentials

After running the seed script or migrate command, the superadmin user is created with the following default credentials:

- **Email**: superadmin@gmail.com
- **Password**: Admin@123

> ⚠️ **Security Note**: Change these credentials in `seed_permissions.py` or immediately after login in your production environment.

### 6️⃣ Run the Application

Start the FastAPI development server:

```bash
uv run uvicorn app.main:app --reload
```

The application will be available at: `http://localhost:8000`

---

## 📋 API Documentation

Once the server is running, you can explore the API via Swagger UI:

**Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
**ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Available Endpoints

The API includes endpoints for:

- **Authentication** (login/logout)
- **User Management** (CRUD operations)
- **Role Management** (create, assign, manage roles)
- **Module Management** (manage system modules)
- **Action Management** (manage system actions)
- **Permission Management** (assign/revoke permissions)
- **Object-Level Permissions** (resource-specific permissions)
- **Audit Log Inspection** (track user actions)

---

## 🧠 Core Concepts

### System Components

- **Roles**: Collections of permissions that can be assigned to users
- **Permissions**: Generated from action + module combinations
- **Modules**: High-level resources (e.g., Post, Invoice, User)
- **Actions**: Operations that can be performed (e.g., create, read, update, delete)
- **Object Permissions**: Allow assigning permissions on specific records/resources
- **Audit Logs**: Capture user actions like role assignments and permission changes

### Permission Model

The system uses a hierarchical permission model:

```
Permission = Module + Action
Example: "Post:create", "Invoice:read", "User:update"
```

### Role Hierarchy

Roles can be organized in hierarchies, allowing inheritance of permissions from parent roles.

---

## 🗂️ Project Structure

```
fastapi-rbac-poc/
├── app/
│   ├── api/                 # API endpoints
│   ├── core/                # Core configuration
│   ├── db/                  # Database models and setup
│   ├── services/            # Business logic layer
│   ├── repositories/        # Data access layer
│   └── main.py             # FastAPI application
├── alembic/                 # Database migrations
├── manage.py               # Custom migration management script
├── pyproject.toml          # Project dependencies and configuration
├── .env.example            # Environment variables template
└── README.md              # This file
```

---

## 🔧 Development

### Adding New Migrations

When you make changes to your database models:

```bash
# Create a new migration
python manage.py makemigrations -m "describe your changes"

# Apply the migration
python manage.py migrate
```

### Adding New Modules

1. Define your module in the system
2. Create associated actions if needed
3. The system will automatically generate permissions
4. Assign permissions to appropriate roles

### Adding New Actions

1. Define new actions in the system
2. The system will generate permissions for existing modules
3. Assign new permissions to roles as needed

---

## ✅ Features

### Core Features

- **Clean, modular FastAPI codebase**
- **RBAC system with extensibility for:**
  - Role hierarchy
  - Object/resource-based permission assignment
  - Permission grouping by module + action
  - Audit trails
- **Production-ready architecture**
- **Comprehensive API documentation**
- **Database migration management**
- **Flexible permission system**

### Advanced Features

- **Multi-role assignment per user**
- **Object-level permissions**
- **Dynamic permission generation**
- **Audit logging for security**
- **Future-ready for multitenant support**

---

## 🧪 Testing

Run the test suite:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=app
```

---

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**: Update all environment variables for production
2. **Database**: Set up production PostgreSQL database
3. **Security**: Change default superadmin credentials
4. **Migrations**: Run all migrations in production
5. **Logging**: Configure appropriate logging levels
6. **Monitoring**: Set up application monitoring

### Docker Deployment

```bash
# Build the Docker image
docker build -t fastapi-rbac .

# Run the container
docker run -p 8000:8000 fastapi-rbac
```

---

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## 🔄 Migration History

To view migration history:

```bash
# Show current migration status
alembic current

# Show migration history
alembic history

# Show specific migration details
alembic show <revision_id>
```