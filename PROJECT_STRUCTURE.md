# Wallet Project - Complete DDD Architecture

This document provides a comprehensive overview of the Django project designed with Domain Driven Design (DDD) and SOLID principles.

## Project Overview

The project implements a wallet and transaction management system with the following key features:

- **Wallet Management**: Create, update, and deactivate wallets with soft delete functionality
- **Transaction Management**: Handle transactions with atomic balance updates and concurrency safety
- **RESTful API**: Versioned API endpoints with proper error handling
- **Domain-Driven Design**: Clean separation of concerns with pure domain logic
- **SOLID Principles**: Strict adherence to single responsibility, dependency inversion, and separation of concerns

## Architecture Layers

### 1. Domain Layer (`domain/`)

**Pure business logic with no framework dependencies**

#### Shared Domain (`domain/shared/`)
- `exceptions.py`: Domain-specific exceptions
- `types.py`: Type aliases for better type safety

#### Wallet Domain (`domain/wallets/`)
- `entities.py`: Wallet domain entity with business logic
- `repositories.py`: Abstract wallet repository interface
- `services.py`: Wallet domain services for business operations
- `tests/`: Unit tests for domain logic

#### Transaction Domain (`domain/transactions/`)
- `entities.py`: Transaction domain entity with business logic
- `repositories.py`: Abstract transaction repository interface
- `services.py`: Transaction domain services for business operations
- `tests/`: Unit tests for domain logic

### 2. Application Layer (`application/`)

**Use cases and coordination between domain services**

#### Wallet Application (`application/wallets/`)
- `commands.py`: Write operations (update label, deactivate)
- `queries.py`: Read operations (get wallet, get wallets by IDs)

#### Transaction Application (`application/transactions/`)
- `queries.py`: Read operations (search transactions by wallet IDs)

#### Application Services (`application/services.py`)
- `WalletApplicationService`: Coordinates between wallet and transaction domains

### 3. Infrastructure Layer (`infrastructure/`)

**Django ORM models and repository implementations**

#### Wallet Infrastructure (`infrastructure/wallets/`)
- `models.py`: Django Wallet model
- `repositories.py`: Django implementation of WalletRepository
- `migrations/`: Database migrations

#### Transaction Infrastructure (`infrastructure/transactions/`)
- `models.py`: Django Transaction model
- `repositories.py`: Django implementation of TransactionRepository with atomic operations
- `migrations/`: Database migrations

### 4. Interface Layer (`interfaces/`)

**API endpoints, serializers, and external interfaces**

#### API (`interfaces/api/`)
- `urls.py`: Main API routing
- `wallets/`: Wallet API endpoints
  - `serializers.py`: Request/response serializers
  - `views.py`: API views with proper error handling
  - `urls.py`: Wallet URL patterns
- `transactions/`: Transaction API endpoints
  - `serializers.py`: Request/response serializers
  - `views.py`: API views with proper error handling
  - `urls.py`: Transaction URL patterns

#### Admin Interface (`interfaces/admin.py`)
- Django admin configuration for models

## Key Features Implemented

### 1. Soft Delete Functionality
- Both Wallet and Transaction models support soft delete using `is_active` and `deactivated_at` fields
- When a wallet is deactivated, all related transactions are also soft-deactivated atomically

### 2. Concurrency Safety
- Database locking with `select_for_update()` for wallet balance updates
- Atomic transactions for all balance-affecting operations
- Proper handling of race conditions

### 3. API Endpoints
- `PATCH /api/v1/wallets/{id}/`: Update wallet label only
- `POST /api/v1/wallets/{id}/deactivate/`: Deactivate wallet and all transactions
- `POST /api/v1/transactions/search/`: Search transactions by wallet IDs

### 4. Domain Logic
- Pure business logic in domain entities (no Django imports)
- Business rules enforced at domain level
- Proper validation and error handling

### 5. Dependency Injection
- Repository interfaces in domain layer
- Concrete implementations in infrastructure layer
- Easy to test and mock dependencies

## Database Schema

### Wallet Model
```sql
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label VARCHAR(255) NOT NULL,
    balance DECIMAL(18,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    deactivated_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transaction Model
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id UUID REFERENCES wallets(id) ON DELETE CASCADE,
    txid VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(18,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    deactivated_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Development Setup

### Prerequisites
- Python 3.11+
- Poetry for dependency management
- PostgreSQL (or SQLite for development)

### Installation
1. Clone the repository
2. Install dependencies: `poetry install`
3. Copy environment file: `cp env.example .env`
4. Run migrations: `poetry run python manage.py migrate`
5. Start development server: `poetry run python manage.py runserver`

### Docker Setup
```bash
docker-compose up --build
```

## Testing

### Running Tests
```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=wallet_project

# Specific test file
poetry run pytest domain/wallets/tests/test_entities.py
```

### Test Structure
- Domain tests: `domain/*/tests/`
- API tests: `interfaces/api/*/tests/`
- Integration tests: `infrastructure/tests/`

## Code Quality

### Linting and Formatting
```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check .
poetry run ruff check . --fix
```

### Type Checking
```bash
poetry run mypy .
```

## API Examples

### Update Wallet Label
```bash
curl -X PATCH http://localhost:8000/api/v1/wallets/{wallet-id}/ \
  -H "Content-Type: application/json" \
  -d '{"label": "New Wallet Label"}'
```

### Deactivate Wallet
```bash
curl -X POST http://localhost:8000/api/v1/wallets/{wallet-id}/deactivate/
```

### Search Transactions
```bash
curl -X POST http://localhost:8000/api/v1/transactions/search/ \
  -H "Content-Type: application/json" \
  -d '{"wallet_ids": ["uuid1", "uuid2"]}'
```

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)
- Each class has a single, well-defined responsibility
- Domain entities handle business logic only
- Repositories handle data access only
- Use cases handle application logic only

### Open/Closed Principle (OCP)
- Domain entities are open for extension through inheritance
- Repository interfaces allow different implementations
- New use cases can be added without modifying existing code

### Liskov Substitution Principle (LSP)
- Repository implementations can be substituted without breaking code
- Domain entities maintain consistent behavior

### Interface Segregation Principle (ISP)
- Repository interfaces are specific to their domain
- No forced dependencies on unused methods

### Dependency Inversion Principle (DIP)
- Domain layer depends on abstractions (repository interfaces)
- Infrastructure layer implements these abstractions
- High-level modules don't depend on low-level modules

## Future Enhancements

1. **Event Sourcing**: Implement domain events for audit trails
2. **CQRS**: Separate read and write models for better performance
3. **Microservices**: Split into separate services for wallets and transactions
4. **Authentication**: Add JWT-based authentication
5. **Rate Limiting**: Implement API rate limiting
6. **Monitoring**: Add health checks and metrics
7. **Caching**: Implement Redis caching for frequently accessed data
8. **Background Jobs**: Add Celery for async task processing

## Conclusion

This project demonstrates a well-structured Django application following DDD and SOLID principles. The clean architecture makes it easy to maintain, test, and extend while ensuring business logic is properly encapsulated and protected from external dependencies.
