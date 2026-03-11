# PROPIG - Employee Profile Management API

A robust REST API for managing employee profiles with role-based access control (RBAC), JWT authentication, and comprehensive audit logging.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Quick Start](#quick-start)
5. [Installation](#installation)
6. [Project Structure](#project-structure)
7. [API Endpoints](#api-endpoints)
8. [Authentication & Roles](#authentication)
9. [Database](#database)
10. [Testing](#testing)
11. [Docker](#docker)
12. [Security Notes](#security-notes)
13. [Postman Integration](#api-testing-with-postman)



## Overview

PROPIG is a comprehensive employee profile management system designed to handle:

- User authentication with JWT tokens
- Department-based access control
- Employee profile CRUD operations
- Hierarchical permission system (SUPER, MANAGER, EMPLOYEE)
- Comprehensive audit trail for compliance
- RESTful API with OpenAPI documentation

This backend service provides a complete REST API for managing organizational structures and employee information with enterprise-grade security.

## Database Diagram

- [Db Diagram Link](https://dbdiagram.io/d/Propig-Case-Tecnico-db-69b015bc77d079431b4b124d)

![DB.DIAGRAM](img/Propig-Case-Tecnico-db.png)

## Features

Current features include:

- User authentication with JWT (HS256)
- Role-Based Access Control (RBAC) with three tiers
- Department management and organization
- Employee profile management with validation
- Search and filtering capabilities
- Complete audit logging for all operations
- Pagination support for list endpoints
- Comprehensive input validation with Pydantic
- Async/await support for high performance
- Automated unit and integration tests
- OpenAPI documentation with Swagger UI

## Tech Stack

### Backend

- **Python 3.11** - Core language
- **FastAPI 0.135.1** - Modern async web framework
- **Pydantic 2.12.5** - Data validation
- **SQLAlchemy 2.0.48** - ORM with async support
- **AsyncPG 0.31.0** - Async PostgreSQL driver
- **python-jose 3.5.0** - JWT handling
- **bcrypt 4.1.1** - Password hashing
- **Alembic 1.18.4** - Database migrations

### Database

- **PostgreSQL 15+** - Primary database with UUID support

### DevOps & Testing

- **Docker** - Container technology
- **Docker Compose** - Multi-container orchestration
- **Pytest 8.0.1** - Testing framework
- **pytest-asyncio 0.23.5** - Async test support

## Quick Start

### Prerequisites

Ensure you have installed:

- Docker - https://docs.docker.com/engine/install/
- Docker Compose - Bundled with Docker Desktop
- Git
- (Optional) Postman - For API testing

### Running the Application

1. Clone the repository:

```bash
git clone https://github.com/yourusername/propig-python-challenge.git
cd propig-python-challenge
```

2. Start the application with Docker Compose:

```bash
docker compose up -d
```

3. Access the API:

```
http://localhost:8000
```

4. View interactive API documentation:

```
http://localhost:8000/docs
```
5. (Optional) Ensure database is up to date:
```bash
docker compose exec app alembic upgrade head
```

6. Populate with test data:

```bash
docker compose exec app python -m scripts.seed_data
```

7. Run tests:

```bash
docker compose exec app pytest tests/ -v
```

Expected result: **20/20 tests passing**

The application will be ready once PostgreSQL is healthy and the FastAPI application starts.

---

## Installation

### Setup Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configure variables in `.env`:

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=propig_db
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/propig_db

# JWT Configuration
JWT_SECRET=your-secret-key-here-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Seed Credentials (Development Only - Change in Production)
SEED_SUPER_PASSWORD=super123
SEED_MANAGER_PASSWORD=manager123
SEED_EMPLOYEE_PASSWORD=employee123
```

### Development Setup (Local, No Docker)

1. Create and activate virtual environment:

```bash
python -m venv .venv

# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Setup PostgreSQL database and run migrations:

```bash
alembic upgrade head
```

4. Seed test data:

```bash
python -m scripts.seed_data
```

5. Run the application:

```bash
uvicorn app.main:app --reload
```

## Project Structure
<details>
<summary>Click to expand Project Structure</summary>

```
propig-python-challenge/
├── app/
│   ├── main.py                          # FastAPI application entry point
│   │
│   ├── core/
│   │   ├── config.py                    # Environment configuration
│   │   └── security.py                  # JWT and password hashing
│   │
│   ├── db/
│   │   ├── base.py                      # SQLAlchemy base configuration
│   │   └── session.py                   # Database session management
│   │
│   ├── models/
│   │   ├── user.py                      # User entity and UserRole enum
│   │   ├── department.py                # Department entity
│   │   └── audit_log.py                 # Audit trail entity
│   │
│   ├── schemas/
│   │   ├── user.py                      # User Pydantic models
│   │   ├── department.py                # Department Pydantic models
│   │   └── token.py                     # JWT token models
│   │
│   ├── services/
│   │   ├── user_service.py              # User business logic
│   │   ├── department_service.py        # Department business logic
│   │   └── audit_log_service.py         # Audit logging logic
│   │
│   └── routers/
│       ├── user_router.py               # User endpoints
│       └── department_router.py         # Department endpoints
│
├── tests/
│   ├── conftest.py                      # Pytest configuration and fixtures
│   ├── test_user_service.py             # UserService unit tests
│   ├── test_department_service.py       # DepartmentService unit tests
│   └── README.md                        # Testing documentation
│
├── scripts/
│   ├── seed_data.py                     # Populate database with test data
│
├── alembic/
│   ├── env.py                           # Alembic configuration
│   ├── versions/                        # Migration files
│   └── alembic.ini                      # Migration settings
│
├── .env.example                         # Environment variables template
├── .gitignore                           # Git ignore rules
├── docker-compose.yml                   # Docker Compose configuration
├── Dockerfile                           # Docker image definition
├── requirements.txt                     # Python dependencies
├── pytest.ini                           # Pytest configuration
└── README.md
```
</details>


## API Endpoints

### Authentication

```
POST   /users/login                 Login with username and password
```

### Users

```
POST   /users/register              Create new employee (SUPER, MANAGER only)
GET    /users                       List employees (with role-based filtering)
GET    /users/{user_id}             Get employee by ID (with authorization)
PUT    /users/{user_id}             Update employee (SUPER, MANAGER only)
DELETE /users/{user_id}             Delete employee (SUPER, MANAGER only)
```

### Departments

```
POST   /departments                 Create department (SUPER only)
GET    /departments                 List all departments
GET    /departments/{dept_id}       Get department by ID
PUT    /departments/{dept_id}       Update department (SUPER only)
DELETE /departments/{dept_id}       Delete department (SUPER only)
```

## Authentication

The API uses JWT (JSON Web Tokens) for stateless authentication.

### Request Header

Include the JWT token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Login Flow

1. User sends credentials to `POST /users/login`
2. Backend validates and returns JWT token
3. Include token in `Authorization: Bearer <token>` header
4. Token expires after configured duration (default: 60 minutes)

### Roles and Permissions

| Role | Login | Create User | View All | View Own Dept | Update Own Dept | Delete Own Dept | Manage Depts |
|------|-------|-------------|----------|---------------|-----------------|-----------------|--------------|
| SUPER | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| MANAGER | ✅ | ✅ * | ✅ * | ✅ | ✅ * | ✅ * | ❌ |
| EMPLOYEE | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

*Only within their department

## Database

The application uses PostgreSQL as the primary database.

### Database Initialization

Alembic automatically handles database migrations on application startup. Migrations are located in:

```
alembic/versions/
```

### Key Tables

- **users** - Employee accounts with authentication and roles
- **departments** - Organizational departments
- **audit_logs** - Complete history of all operations

## Testing

### Running Tests

Execute the test suite:

```bash
# Inside container
docker compose exec app pytest tests/ -v

# Or locally with virtual environment activated
pytest tests/ -v
```

### Test Coverage

- 12 UserService tests covering CRUD, search, and authentication
- 8 DepartmentService tests covering CRUD operations
- Total: 20 tests with 100% pass rate

### Running Specific Tests

```bash
# Test specific file
docker compose exec app pytest tests/test_user_service.py -v

# Test specific test case
docker compose exec app pytest tests/test_user_service.py::TestUserService::test_register_user -v

# With coverage report
docker compose exec app pytest tests/ --cov=app
```

## Docker

### Running with Docker Compose

Start all services:

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f app
docker compose logs -f db
```

Stop services:

```bash
docker compose down
```

Clean database and volumes:

```bash
docker compose down -v
```

### Docker Components

- **db** - PostgreSQL 15 database service
- **app** - FastAPI application service

Both services are configured with health checks and proper dependency ordering.

## Security Notes

### Credentials Management

- **Development**: Credentials are stored in `.env` file (NOT committed to Git)
- **Production**: Use environment variables from a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- Passwords are hashed with bcrypt (4 rounds minimum)
- JWT tokens use HS256 algorithm

### Best Practices

- Never commit `.env` file (in `.gitignore`)
- Rotate JWT_SECRET regularly
- Use strong passwords in production
- Change seed credentials before deploying
- All operations are logged in audit_logs table
- Use HTTPS in production
- Enable CORS only for trusted domains

### API Security

- All endpoints require authentication (except `/users/login`)
- Role-based access control on all protected endpoints
- Input validation with Pydantic
- SQL injection prevention through ORM
- CSRF protection via stateless JWT
- Rate limiting recommended for production

## API Testing with Postman

1. Import `PROPIG_Postman_Collection.json` into Postman
2. Set `{{base_url}}` to `http://localhost:8000`
3. Run login endpoint to get token
4. Token auto-populates in Authorization header
5. Test all endpoints with different roles

## Test Credentials (Development Only)

```
SUPER:       super / super123
MANAGER:     gerente_financeiro / manager123
EMPLOYEE:    funcionario_fin / employee123
```

> Change these credentials in `.env` before deploying to production.

## Seed Data Idempotency

The `seed_data.py` script includes idempotent checks:

- On first run: Creates tables and test data
- On subsequent runs: Detects existing data and aborts safely
- No support for multiple runs: Credentials stored in `.env` for security

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## Additional Documentation

- [PROPIG_Postman_Collection.json](./PROPIG_Postman_Collection.json) - Postman test collection

---
