# Full-Stack Application Base Template

A production-ready full-stack web application template with authentication, user management, and role-based permissions.  
Build your next application on top of this solid foundation with modern tech stack and best practices.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.14) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Migrations | Alembic |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt |
| Frontend | React 18 + TypeScript + Vite |
| State | Redux Toolkit |
| Styling | TailwindCSS + shadcn/ui |

---

## Core Features

| Module | Description |
|--------|-------------|
| **Authentication** | JWT-based authentication with secure password hashing |
| **User Management** | Admin-only user creation and role assignment |
| **Role-Based Permissions** | Per-role permission configuration (admin / staff / employee) |
| **Dashboard** | Minimal dashboard template ready for customization |
| **Settings** | App-level preferences and theme support |

---

## What's Included

**Backend (FastAPI):**
- ✅ JWT authentication system
- ✅ User CRUD operations with role-based access
- ✅ Dynamic permission system
- ✅ SQLAlchemy models with Alembic migrations
- ✅ Pydantic schemas for validation
- ✅ CORS configuration
- ✅ Environment-based configuration
- ✅ Database abstraction (SQLite for dev, PostgreSQL for prod)

**Frontend (React + TypeScript):**
- ✅ Modern React 18 with TypeScript
- ✅ Redux Toolkit for state management
- ✅ Protected routes with permission checks
- ✅ Responsive sidebar navigation
- ✅ Login/logout flow
- ✅ User management UI for admins
- ✅ Permission management UI
- ✅ Settings page
- ✅ Dark mode support
- ✅ shadcn/ui component library
- ✅ TailwindCSS for styling

---

## Project Structure

```
application-base/
├── .gitignore
├── README.md
│
├── server/                        # FastAPI backend
│   ├── app/
│   │   ├── main.py                # App entry point & router registration
│   │   ├── config.py              # Settings / env vars (pydantic-settings)
│   │   ├── database.py            # SQLAlchemy engine & session
│   │   ├── models.py              # ORM models (User, RolePermissions)
│   │   ├── schemas.py             # Pydantic schemas
│   │   ├── auth.py                # JWT helpers & dependency guards
│   │   └── routers/
│   │       ├── auth.py            # POST /auth/login
│   │       ├── users.py           # /users (CRUD)
│   │       └── permissions.py     # /permissions (role management)
│   ├── migrations/                # Alembic migration scripts
│   ├── manage.py                  # Django-style management commands
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── client/                        # React + Vite frontend
    └── src/
        ├── api/client.ts          # Axios instance + API helpers
        ├── components/            # Shared UI components (sidebar, nav, etc.)
        │   ├── ui/                # shadcn/ui components
        │   ├── app-sidebar.tsx    # Main navigation
        │   ├── login-form.tsx     # Login component
        │   ├── ProtectedRoute.tsx # Route guard
        │   └── ...
        ├── context/               # Theme & settings context
        ├── hooks/                 # usePermissions,  use-mobile
        ├── layout/                # App shell layout
        ├── pages/
        │   ├── Dashboard.tsx      # Main dashboard
        │   ├── Login.tsx          # Login page
        │   ├── UserManagement.tsx # User CRUD (admin only)
        │   ├── Permissions.tsx    # Role permissions (admin only)
        │   ├── Settings.tsx       # App settings
        │   ├── Forbidden.tsx      # 403 page  
        │   └── NotFound.tsx       # 404 page
        ├── routes/index.tsx       # React Router config
        ├── store/                 # Redux slices (auth, permissions)
        └── types.ts               # Shared TypeScript types
```

---

## Getting Started

### 1. Backend Setup (Server)

#### Local Development (SQLite — zero config)

```bash
cd server

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Seed initial data (role permissions)
python manage.py seed

# Create the first admin user (interactive)
python manage.py createsuperuser

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API docs will be available at: **http://localhost:8000/docs**

#### Production (PostgreSQL)

1. Create a `.env` file in `server/`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/app_db
SECRET_KEY=replace-with-a-long-random-secret-at-least-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

2. Uncomment `psycopg2-binary` in `requirements.txt`
3. Run the same commands as above

#### Using Docker

```bash
cd server
docker compose up --build
```

### 2. Frontend Setup (Client)

```bash
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

The Vite dev server automatically proxies API requests to `http://localhost:8000` (configured in `vite.config.ts`).

### 3. Default Login

After running `python manage.py createsuperuser`, use those credentials to login.  
Default: username `admin`, password of your choice.

---

## Management Commands

The `manage.py` script provides Django-style management commands for common tasks:

### Database Migrations

```bash
# Create a new migration after modifying models
python manage.py makemigrations "description of changes"

# Run pending migrations
python manage.py migrate

# Show migration history
python manage.py history

# Show current database version
python manage.py current

# Rollback last migration
python manage.py downgrade

# Rollback to specific revision
python manage.py downgrade abc123
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

## Core API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/login` | Authenticate user, returns JWT token |

### Users (Admin Only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users` | List all users |
| `POST` | `/users` | Create a new user |
| `PATCH` | `/users/{id}` | Update user role or password |
| `DELETE` | `/users/{id}` | Delete a user |

### Permissions (Admin Only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/permissions` | Get all role permissions |
| `PUT` | `/permissions/{role}` | Update permissions for a specific role |

---

## Built-In Roles & Permissions

| Permission | Admin | Staff | Employee |
|-----------|-------|-------|----------|
| View Dashboard | ✅ | ✅ | ✅ |
| View User Management | ✅ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ❌ |
| View Settings | ✅ | ✅ | ✅ |

> Admin permissions are always full and cannot be changed.  
> Staff and Employee permissions can be configured via the Permissions page.

---

## Customization Guide

### Adding New Features

#### 1. Backend (Add a New Model & Router)

**Step 1:** Add your model in `server/app/models.py`

```python
class YourModel(Base):
    __tablename__ = "your_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Step 2:** Add schemas in `server/app/schemas.py`

```python
class YourModelCreate(BaseModel):
    name: str

class YourModelResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

**Step 3:** Create a router in `server/app/routers/your_feature.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/your-feature", tags=["Your Feature"])

@router.get("", response_model=list[schemas.YourModelResponse])
def list_items(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    items = db.query(models.YourModel).all()
    return items
```

**Step 4:** Register router in `server/app/main.py`

```python
from app.routers import auth, users, permissions, your_feature

app.include_router(your_feature.router)
```

**Step 5:** Create and run migration

```bash
cd server
python manage.py makemigrations "add your_model"
python manage.py migrate
```

#### 2. Frontend (Add a New Page)

**Step 1:** Create page in `client/src/pages/YourFeature.tsx`

```tsx
export default function YourFeature() {
  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <h1 className="text-2xl font-bold">Your Feature</h1>
      {/* Your content here */}
    </div>
  )
}
```

**Step 2:** Add route in `client/src/routes/index.tsx`

```tsx
import YourFeature from '@/pages/YourFeature'

// In the children array:
{
  path: 'your-feature',
  element: (
    <ProtectedRoute requirePermission="canViewYourFeature">
      <YourFeature />
    </ProtectedRoute>
  ),
}
```

**Step 3:** Add navigation item in `client/src/components/app-sidebar.tsx`

```tsx
...(perms.canViewYourFeature
  ? [{
    title: "Your Feature",
    url: "/your-feature",
    icon: YourIcon,
    items: [{ title: "Overview", url: "/your-feature" }],
  }]
  : []),
```

**Step 4:** Add permission to `server/app/models.py`

```python
DEFAULT_ROLE_PERMISSIONS: dict = {
    "staff": {
        "canViewDashboard": True,
        "canViewYourFeature": True,  # Add this
        # ...
    },
}
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | DB connection string | `sqlite:///./app.db` |
| `SECRET_KEY` | JWT signing secret | *(must change in prod)* |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL | `1440` (24 hours) |

---

## Deployment

### Backend (Render / Railway / Fly.io)

1. Set environment variables (DATABASE_URL, SECRET_KEY)
2. Ensure `psycopg2-binary` is uncommented in `requirements.txt`
3. Set build command: `pip install -r requirements.txt && alembic upgrade head`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Netlify / Vercel / Cloudflare Pages)

1. Build command: `npm run build`
2. Publish directory: `dist`
3. Set environment variable: `VITE_API_URL=https://your-backend-url.com`

---

## Tech Stack Details

**Backend:**
- **FastAPI**: Modern Python web framework, auto-generated docs
- **SQLAlchemy 2.0**: ORM with async support
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **python-jose**: JWT token generation and verification
- **bcrypt**: Password hashing

**Frontend:**
- **React 18**: Latest React with concurrent features
- **TypeScript**: Type-safe JavaScript
- **Vite**: Lightning-fast build tool and dev server
- **Redux Toolkit**: State management with less boilerplate
- **React Router**: Client-side routing
- **TailwindCSS**: Utility-first CSS framework
- **shadcn/ui**: Beautiful, accessible component library
- **Lucide React**: Modern icon library

---

## License

This template is free to use for any purpose. No attribution required.

---

## Next Steps

1. **Customize branding**: Update app name in sidebar, page titles, etc.
2. **Add your features**: Follow the customization guide above
3. **Configure permissions**: Add your own permissions in DEFAULT_ROLE_PERMISSIONS
4. **Set up production database**: Switch to PostgreSQL for production
5. **Deploy**: Deploy backend and frontend to your preferred hosting
6. **Secure your app**: Change SECRET_KEY, enable HTTPS, configure CORS properly

---

## Support

This is a template/starting point. Feel free to modify, extend, or completely restructure it to fit your needs.

**What's included:**
- ✅ Authentication & authorization
- ✅ User management
- ✅ Role-based permissions
- ✅ Responsive UI with dark mode
- ✅ Protected routes
- ✅ Redux state management
- ✅ Database migrations
- ✅ Docker support

**What you need to add:**
- Your business logic and models
- Your custom pages and features
- Your API endpoints
- Your database schema
- Production deployment configuration

---

Happy building! 🚀

