# Backend - FastAPI Server

FastAPI backend with SQLAlchemy, Alembic migrations, and JWT authentication.  
Part of the full-stack application base template.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- pip
- Virtual environment tool (venv, virtualenv, or conda)

### Installation & Development

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Seed initial data (role permissions)
python manage.py seed

# Create repeatable fake customers, products, inventory, and carts
python manage.py seed_fake --count 1000

# Create admin user (interactive)
python manage.py createsuperuser

# Start development server
uvicorn app.main:app --reload --port 8000
```

API will be available at **http://localhost:8000**  
Interactive API docs at **http://localhost:8000/docs**

---

## Project Structure

```
server/
├── app/
│   ├── auth/                # Registration, login, JWT dependencies
│   ├── users/               # Profiles and administrator user management
│   ├── products/            # Categories and published catalog
│   ├── inventory/           # Stock adjustments and movement history
│   ├── cart/                # Authenticated customer carts
│   ├── orders/              # Checkout, snapshots, status, cancellation
│   ├── payments/            # Local success/failure/timeout simulator
│   ├── core/                # Shared pagination, schemas, and utilities
│   ├── main.py              # FastAPI app and router registration
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   └── database.py      # SQLModel engine and session
│   └── models.py            # Relational model registry
├── migrations/
│   ├── env.py               # Alembic environment
│   ├── script.py.mako       # Migration template
│   └── versions/            # Migration files
├── .env                     # Environment variables (not in git)
├── .env.example             # Example environment file
├── alembic.ini              # Alembic configuration
├── manage.py                # Django-style management commands
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image configuration
└── server.py                # Alternative entry point
```

---

## 🛠 Tech Stack

| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Modern Python web framework |
| **SQLModel** | ORM (SQLAlchemy 2.0 wrapper) |
| **Alembic** | Database migrations |
| **Pydantic** | Data validation & settings |
| **python-jose** | JWT token creation/validation |
| **bcrypt** | Password hashing |
| **SQLite** | Development database |
| **PostgreSQL** | Production database |
| **Uvicorn** | ASGI server |

---

## 📋 Management Commands

The `manage.py` script provides Django-style commands for common tasks.

### Database Migrations

```bash
# Create a new migration after modifying models
python manage.py makemigrations "add user profile fields"

# Apply pending migrations
python manage.py migrate

# Show migration history
python manage.py history

# Show current database version
python manage.py current

# Rollback last migration
python manage.py downgrade

# Rollback to specific revision
python manage.py downgrade abc123def456
```

### User Management

```bash
# Create an admin user (interactive)
python manage.py createsuperuser

# Create a regular user (interactive - staff or employee)
python manage.py createuser
```

### Data Management

```bash
# Seed initial data (role permissions)
python manage.py seed

# Reset database (WARNING: deletes all data)
python manage.py reset_db
```

### Development Tools

```bash
# Open interactive Python shell with database session
python manage.py shell

# Open database shell (sqlite3 or psql)
python manage.py dbshell

# Show all available commands
python manage.py help
```

---

## API Endpoints

Business endpoints use the `/api/v1` prefix. The Phase 0 flow is:

1. `POST /api/v1/auth/register` and `POST /api/v1/auth/login`
2. Admin creates a product, publishes it, and adjusts inventory
3. Customer uses `/api/v1/products` and `/api/v1/cart`
4. Customer calls `POST /api/v1/orders` with an `Idempotency-Key`
5. Customer calls `/api/v1/payments/{order_id}/attempt` with an outcome of `success`, `failure`, or `timeout`
6. Customer cancels eligible orders through `/api/v1/orders/{order_id}/cancellation`

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/login` | Login with username/password, returns JWT token | No |

**Request:**
```json
{
  "username": "admin",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "created_at": "2026-01-15T10:30:00Z"
  }
}
```

### Users (Admin Only)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/users` | List all users | Admin |
| `POST` | `/users` | Create a new user | Admin |
| `PATCH` | `/users/{id}` | Update user role or password | Admin |
| `DELETE` | `/users/{id}` | Delete a user | Admin |

**Create User Request:**
```json
{
  "username": "newuser",
  "password": "secure-password",
  "role": "staff"
}
```

### Permissions (Admin Only)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/permissions` | Get all role permissions | Admin |
| `PUT` | `/permissions/{role}` | Update permissions for a role | Admin |

**Update Permissions Request:**
```json
{
  "permissions": {
    "canViewDashboard": true,
    "canViewUserManagement": false,
    "canManageUsers": false,
    "canViewSettings": true
  }
}
```

---

## 🔐 Authentication Flow

### JWT Token Authentication

1. User sends `POST /auth/login` with username and password
2. Server validates credentials and returns JWT token
3. Client stores token and includes it in subsequent requests:
   ```
   Authorization: Bearer <token>
   ```
4. Server validates token on each protected endpoint
5. Token expires after 24 hours (configurable)

### Password Security

- Passwords are hashed using bcrypt before storage
- Plain passwords are never stored in the database
- Password hashing uses unique salt per password

---

## 📦 Database Models

### User

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.staff, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### RolePermissions

```python
class RolePermissions(Base):
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum(UserRole), unique=True, nullable=False)
    permissions = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
```

---

## ⚙️ Configuration

Environment variables are managed via `.env` file and `app/config.py`.

### Available Settings

```env
# Database
DATABASE_URL=sqlite:///./app.db                    # SQLite (dev)
# DATABASE_URL=postgresql://user:pass@localhost/db  # PostgreSQL (prod)

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Switching to PostgreSQL

1. Update `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/your_db
   ```

2. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

---

## 🐳 Docker Setup

### Using Docker Compose (PostgreSQL + API)

```bash
# Start services
docker compose up --build

# Run in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

The `docker-compose.yml` includes:
- PostgreSQL database container
- FastAPI application container
- Network configuration
- Volume persistence for database

### Environment Variables in Docker

Update `docker-compose.yml` or create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:password@db:5432/app_db
SECRET_KEY=your-production-secret-key
```

---

## 🔧 Adding New Features

### 1. Create a New Model

Add your model in `app/models.py`:

```python
class YourModel(Base):
    __tablename__ = "your_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### 2. Create Pydantic Schemas

Add schemas in the owning domain package, such as `app/auth/schemas.py`:

```python
class YourModelCreate(BaseModel):
    name: str
    description: str | None = None

class YourModelResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

### 3. Create a Router

Create `app/routers/your_router.py`:

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_db
from app.auth import get_current_user
from app.models import User, YourModel
from app.auth.schemas import YourModelCreate, YourModelResponse

router = APIRouter(prefix="/your-endpoint", tags=["Your Feature"])

@router.get("", response_model=list[YourModelResponse])
def list_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.exec(select(YourModel)).all()

@router.post("", response_model=YourModelResponse, status_code=201)
def create_item(
    payload: YourModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = YourModel(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
```

### 4. Register Router

In `app/main.py`:

```python
from app.routers import your_router

app.include_router(your_router.router)
```

### 5. Create Migration

```bash
python manage.py makemigrations "add your_table"
python manage.py migrate
```

---

## 🧪 Testing

### Manual Testing with Interactive Docs

1. Start the server: `uvicorn app.main:app --reload`
2. Open **http://localhost:8000/docs**
3. Test endpoints directly in the Swagger UI

### Using curl

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# List users (with token)
curl http://localhost:8000/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🔒 Security Best Practices

### Production Checklist

- ✅ Change `SECRET_KEY` to a strong random value (32+ characters)
- ✅ Use PostgreSQL instead of SQLite
- ✅ Enable HTTPS/TLS
- ✅ Set proper CORS origins (not `*`)
- ✅ Use environment variables for secrets (never commit `.env`)
- ✅ Implement rate limiting
- ✅ Enable logging and monitoring
- ✅ Regular security updates for dependencies

### CORS Configuration

Update allowed origins in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Change from ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Database Migrations

### Creating Migrations

```bash
# After modifying models in app/models.py
python manage.py makemigrations "describe your changes"
```

### Applying Migrations

```bash
# Apply all pending migrations
python manage.py migrate

# Or use alembic directly
alembic upgrade head
```

### Migration Best Practices

- Always review auto-generated migrations before applying
- Test migrations on a development database first
- Create migrations for each logical change
- Use descriptive migration messages
- Never edit migrations after they've been committed to version control

---

## 🚀 Deployment

### Production Server

```bash
# Install production server
pip install gunicorn

# Run with gunicorn (recommended for production)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Systemd Service (Linux)

Create `/etc/systemd/system/fastapi-app.service`:

```ini
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/server
Environment="PATH=/path/to/server/.venv/bin"
ExecStart=/path/to/server/.venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable fastapi-app
sudo systemctl start fastapi-app
```

---

## 📖 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Pydantic Documentation](https://docs.pydantic.dev)

---

## 🤝 Contributing

This is a base template - feel free to modify and extend it for your specific needs!

---

**Part of the Full-Stack Application Base Template**  
See the [main README](../README.md) for complete setup instructions and architecture overview.
