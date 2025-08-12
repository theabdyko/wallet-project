# Wallet Project

A modern Django project designed with Domain Driven Design (DDD) and SOLID principles for Wallet and Transaction management. Features a clean architecture, comprehensive testing, and production-ready Docker deployment.

## 🏗️ Architecture

This project follows **Domain Driven Design (DDD)** principles with a clean architecture approach:

- **Domain Layer**: Pure business logic and entities (no framework dependencies)
- **Application Layer**: Use cases, commands, and queries with orchestration services
- **Infrastructure Layer**: Django ORM models, migrations, and repository implementations
- **Interface Layer**: REST API with versioning, serializers, and comprehensive error handling

### Key Design Principles
- **SOLID Principles**: Single responsibility, dependency inversion, and interface segregation
- **Clean Architecture**: Clear separation of concerns and dependency direction
- **Repository Pattern**: Abstract data access with concrete implementations
- **CQRS**: Command Query Responsibility Segregation for write/read operations

## ✨ Features

### Core Functionality
- **Wallet Management**: Create, update, deactivate with soft delete
- **Transaction Management**: Atomic balance updates with database locking
- **Concurrency Safety**: Database-level locking for race condition prevention
- **Soft Delete**: Maintains data integrity while allowing deactivation

### API & Development
- **RESTful API**: Versioned endpoints (`/api/v1/`) with JSON:API compliance
- **Comprehensive Testing**: Unit, integration, and functional tests with pytest
- **Modern Python**: Python 3.11+ with type hints and union types
- **Code Quality**: Ruff linting, and comprehensive coverage

### Deployment & DevOps
- **Docker Support**: Multi-stage Dockerfile with development and production targets
- **Docker Compose**: Complete development environment with PostgreSQL
- **CI/CD Pipeline**: GitHub Actions with automated testing and Docker builds
- **Health Checks**: Built-in health endpoints for container orchestration

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wallet-project
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the API**
   - API: http://localhost:8000/api/v1/
   - Documentation: http://localhost:8000/docs/swagger/


## 🔌 API Endpoints

### Wallets
- `GET /api/v1/wallets/list/` - List wallets with filtering and pagination
- `POST /api/v1/wallets/create/` - Create new wallet
- `PATCH /api/v1/wallets/{id}/update-label/` - Update wallet label
- `POST /api/v1/wallets/{id}/deactivate/` - Deactivate wallet and transactions

### Transactions
- `GET /api/v1/transactions/list/` - List transactions with filtering and pagination
- `POST /api/v1/transactions/create/` - Create new transaction
- `GET /api/v1/transactions/by-txid/{txid}/` - Get transaction by external ID

### System
- `GET /docs/` - API documentation (Swagger/OpenAPI)

## ⚙️ Environment Configuration

### Quick Setup
- **Development**: Run without `.env` file - all variables have sensible defaults
- **Custom**: Copy `env.template` to `.env` and customize as needed
- **Docker**: Environment variables automatically loaded from `.env`

### Key Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `django-insecure-change-me-in-production` | Django secret key |
| `DEBUG` | `True` | Enable debug mode |
| `ENVIRONMENT` | `dev` | Environment mode (dev/prod) |
| `DB_NAME` | `wallet_db` | Database name |
| `DB_USER` | `wallet_user` | Database user |
| `DB_PASSWORD` | `wallet_password` | Database password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Allowed CORS origins |

### Docker Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_DB` | `wallet_db` | PostgreSQL database name |
| `POSTGRES_USER` | `wallet_user` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `wallet_password` | PostgreSQL password |
| `POSTGRES_HOST` | `db` | PostgreSQL host (Docker service) |
| `DOCKER_WEB_PORT` | `8000` | Web service port |
| `DOCKER_DB_PORT` | `5432` | Database service port |

## 🧪 Development & Testing

### Code Quality Tools
- **Ruff**: Fast Python linter and formatter
- **Black**: Uncompromising code formatter
- **Pytest**: Testing framework with comprehensive fixtures
- **Coverage**: Test coverage reporting and analysis

### Running Tests

```bash
# Run all tests (within the docker container)
poetry run pytest

# Run with verbose output and colors (within the docker container)
poetry run pytest -s -vv --color=yes ./src/tests

# Run specific test categories (within the docker container)
poetry run pytest src/tests/unit/          # Unit tests
poetry run pytest src/tests/integration/   # Integration tests
poetry run pytest src/tests/functional/    # Functional tests
```

### Code Quality Commands

```bash
# Lint with Ruff (within the docker container)
poetry run ruff check .
poetry run ruff check . --fix
```

## 🐳 Docker & Deployment

### Docker Targets
- **`develop`**: Development environment with hot reload
- **`production`**: Production-ready with Gunicorn and security hardening

### Docker Compose Services
- **`web`**: Django application with entrypoint script
- **`db`**: PostgreSQL 15 with optimized configuration
- **Health checks** and **automatic restart** policies

### Production Features
- **Gunicorn**: Production WSGI server with worker processes
- **Entrypoint Script**: Environment-aware startup with database readiness checks
- **Security**: Non-root user execution and resource limits
- **Monitoring**: Built-in health endpoints for container orchestration

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
The project includes a comprehensive CI/CD pipeline that runs on every push to `main` and `develop` branches:

1. **Build Stage**: Docker image building with caching
2. **Test Stage**: Comprehensive testing in containerized environment
3. **Quality Gates**: Syntax validation, linting, and test coverage

### Pipeline Features
- **Docker Build**: Multi-stage builds with layer caching
- **Automated Testing**: Full test suite execution in isolated containers
- **Artifact Management**: Docker images and test results storage
- **Branch Protection**: Separate workflows for main and develop branches

## 📁 Project Structure

```
wallet-project/
├── .github/                          # GitHub configuration
│   └── workflows/                    # CI/CD pipeline configuration
│       └── ci.yml                    # GitHub Actions workflow
├── config/                           # Django configuration
│   ├── settings/                     # Environment-specific settings
│   │   ├── base.py                   # Base settings with common configuration
│   │   ├── dev.py                    # Development environment settings
│   │   ├── prod.py                   # Production environment settings
│   │   └── test.py                   # Test environment settings (SQLite)
│   ├── urls.py                       # Main URL routing and health endpoint
│   └── wsgi.py                       # WSGI application entry point
├── src/                              # Source code (main application)
│   ├── api/                          # API layer (interfaces)
│   │   ├── base.py                   # Base API ViewSet with common functionality
│   │   ├── exceptions.py             # API exception handling
│   │   ├── pagination.py             # JSON:API compliant pagination
│   │   ├── urls.py                   # Main API routing
│   │   ├── wallets/                  # Wallet API endpoints
│   │   └── transactions/             # Transaction API endpoints
│   ├── application/                  # Application layer (use cases)
│   │   ├── services.py               # Application orchestration services
│   │   ├── wallets/                  # Wallet use cases
│   │   └── transactions/             # Transaction use cases
│   ├── containers/                   # Dependency injection container
│   │   ├── repositories.py           # Repository bindings
│   │   ├── services.py               # Service bindings
│   │   └── use_cases.py              # Use case bindings
│   ├── domain/                       # Domain layer (business logic)
│   │   ├── shared/                   # Common domain elements
│   │   ├── wallets/                  # Wallet domain
│   │   └── transactions/             # Transaction domain
│   ├── infrastructure/               # Infrastructure layer (data access)
│   │   ├── database/                 # Database utilities
│   │   ├── wallets/                  # Wallet infrastructure
│   │   └── transactions/             # Transaction infrastructure
│   └── tests/                        # Comprehensive test suite
│       ├── conftest.py               # Pytest configuration and fixtures
│       ├── test_basic.py             # Basic test setup verification
│       ├── test_pagination.py        # Pagination functionality tests
│       ├── test_refactored_views.py  # Refactored API view tests
│       ├── run_tests.py              # Test runner script
│       ├── README.md                 # Testing documentation
│       ├── unit/                     # Unit tests for business logic
│       ├── integration/              # Integration tests for services
│       └── functional/               # Functional tests for API endpoints
├── entrypoints/                      # Docker entrypoint scripts
│   └── entrypoint.sh                 # Environment-aware startup script
├── postgres-init/                     # PostgreSQL initialization
│   └── 01-init.sql                   # Database setup and extensions
├── docker-compose.yml                # Development environment setup
├── Dockerfile                        # Multi-stage Docker build
├── pyproject.toml                    # Python dependencies and tooling
├── poetry.lock                       # Locked dependency versions
├── manage.py                         # Django management script
├── env.template                      # Environment variables template
├── .gitignore                        # Git ignore patterns
├── PROJECT_STRUCTURE.md              # Detailed project structure documentation
├── REFACTORING_SUMMARY.md            # Refactoring changes documentation
├── POSTGRESQL_REFACTORING_SUMMARY.md # PostgreSQL changes documentation
└── README.md                         # This file
```

### **Architecture Layers**

- **🏗️ Domain Layer** (`src/domain/`): Pure business logic, entities, and business rules
- **⚙️ Application Layer** (`src/application/`): Use cases, commands, queries, and orchestration
- **🏗️ Infrastructure Layer** (`src/infrastructure/`): Data access, Django ORM, and external services
- **🌐 Interface Layer** (`src/api/`): REST API, serializers, and request/response handling

### **Key Directories**

- **`config/`**: Django configuration with environment-specific settings
- **`src/`**: Main application code following clean architecture principles
- **`tests/`**: Comprehensive test suite with unit, integration, and functional tests
- **`entrypoints/`**: Docker container startup scripts
- **`postgres-init/`**: Database initialization and configuration

## 🤝 Contributing

### Development Guidelines
1. **Follow DDD Principles**: Keep domain logic pure and framework-agnostic
2. **Write Tests**: Ensure comprehensive test coverage for new features
3. **Code Quality**: Use type hints, docstrings, and follow PEP 8
4. **SOLID Principles**: Maintain single responsibility and dependency inversion
5. **Git Workflow**: Use feature branches and ensure CI passes before merging

### Code Standards
- **Python 3.11+**: Modern Python features and type hints
- **Type Safety**: Comprehensive type annotations throughout
- **Documentation**: Clear docstrings and API documentation
- **Error Handling**: Proper exception chaining and user-friendly messages

## 📊 Project Status

- **✅ Core Features**: Wallet and transaction management complete
- **✅ API Layer**: RESTful endpoints with comprehensive validation
- **✅ Testing**: Unit, integration, and functional test coverage
- **✅ Docker**: Production-ready containerization
- **✅ CI/CD**: Automated testing and deployment pipeline
- **✅ Documentation**: Comprehensive API and development docs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions, issues, or contributions:
1. Check the existing documentation and API docs
2. Review the test suite for usage examples
3. Open an issue with detailed description and reproduction steps
4. Submit pull requests with comprehensive test coverage
