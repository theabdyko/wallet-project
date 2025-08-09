# Wallet Project

A Django project designed with Domain Driven Design (DDD) and SOLID principles for Wallet and Transaction management.

## Architecture

This project follows Domain Driven Design (DDD) principles with a clean architecture approach:

- **Domain Layer**: Pure business logic and entities (no Django imports)
- **Application Layer**: Use cases and commands/queries
- **Infrastructure Layer**: Django ORM models, migrations, and repository implementations
- **Interface Layer**: API serializers, views, routers, and versioning

## Features

- Wallet management with soft delete functionality
- Transaction management with atomic balance updates
- RESTful API with versioning (/api/v1/)
- Concurrency-safe operations using database locking
- Comprehensive test coverage
- Docker and Docker Compose support

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository
2. Run the application:
   ```bash
   docker-compose up --build
   ```
3. Access the API at http://localhost:8000

### Local Development

1. Install Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   # Option 1: Use the setup script (recommended)
   python setup_env.py
   
   # Option 2: Copy the example file
   cp env.example .env
   # Edit .env with your configuration
   
   # Option 3: Copy the template file
   cp env.template .env
   # Edit .env with your configuration
   
   # Option 4: Create .env manually (all variables are optional for development)
   touch .env
   ```

4. Run migrations:
   ```bash
   poetry run python manage.py migrate
   ```

5. Start the development server:
   ```bash
   poetry run python manage.py runserver
   ```

## API Endpoints

### Wallets
- `PATCH /api/v1/wallets/{id}/` - Update wallet label
- `POST /api/v1/wallets/{id}/deactivate/` - Deactivate wallet and related transactions

### Transactions
- `POST /api/v1/transactions/search/` - Search transactions by wallet IDs

## Environment Variables

The application uses environment variables for configuration. All variables are optional for development mode with sensible defaults.

### Quick Setup

1. **For Local Development**: You can run the app without creating a `.env` file - all variables have sensible defaults
2. **For Custom Configuration**: Copy `env.template` to `.env` and customize as needed
3. **For Docker**: Environment variables are automatically loaded from `.env` file

### Key Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `django-insecure-change-me-in-production` | Django secret key |
| `DEBUG` | `True` | Enable debug mode |
| `DB_NAME` | `wallet_db` | Database name |
| `DB_USER` | `wallet_user` | Database user |
| `DB_PASSWORD` | `wallet_password` | Database password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |
| `USE_SQLITE_FALLBACK` | `True` | Use SQLite for local development |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Allowed CORS origins |

### Docker Environment Variables

When running with Docker Compose, the following additional variables are available:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_DB` | `wallet_db` | PostgreSQL database name |
| `POSTGRES_USER` | `wallet_user` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `wallet_password` | PostgreSQL password |
| `POSTGRES_HOST` | `db` | PostgreSQL host (Docker service name) |
| `DOCKER_WEB_PORT` | `8000` | Web service port |
| `DOCKER_DB_PORT` | `5432` | Database service port |

## Development

- **Ruff**: Code formatting and linting
- **Black**: Code formatting
- **Pytest**: Testing framework
- **Coverage**: Test coverage reporting

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=wallet_project

# Run specific test file
poetry run pytest domain/wallets/tests/
```

### Code Formatting

```bash
# Format code with Black
poetry run black .

# Lint with Ruff
poetry run ruff check .
poetry run ruff check . --fix
```

## Project Structure

```
wallet_project/
├── domain/                 # Pure business logic
│   ├── wallets/
│   ├── transactions/
│   └── shared/
├── application/            # Use cases and commands/queries
│   ├── wallets/
│   ├── transactions/
│   └── services.py
├── infrastructure/         # Django ORM and repositories
│   ├── wallets/
│   ├── transactions/
│   └── migrations/
├── interfaces/             # API layer
│   ├── api/
│   └── admin.py
└── config/                 # Django configuration
    ├── settings/
    ├── urls.py
    └── wsgi.py
```

## Contributing

1. Follow the existing code style and architecture patterns
2. Write tests for new features
3. Ensure all tests pass before submitting
4. Use type hints and docstrings
5. Follow SOLID principles

## License

This project is licensed under the MIT License.
