# Wallet Project Tests

This directory contains comprehensive tests for the wallet project, organized by test type and following Domain Driven Design principles.

## Test Structure

```
tests/
├── conftest.py              # Common fixtures and test configuration
├── run_tests.py             # Test runner script
├── README.md               # This file
├── unit/                   # Unit tests (isolated components)
│   ├── test_wallet_entity.py
│   ├── test_transaction_entity.py
│   └── test_wallet_domain_service.py
├── functional/             # Functional tests (with database)
│   ├── test_wallet_repository.py
│   └── test_transaction_repository.py
└── integration/            # Integration tests (full flow)
    └── test_wallet_application_service.py
```

## Test Types

### Unit Tests (`unit/`)
- Test individual components in isolation
- Use mocks for dependencies
- Fast execution
- Test business logic and domain rules
- No database interaction

### Functional Tests (`functional/`)
- Test components with real database interaction
- Minimal mocking
- Test repository implementations
- Test data persistence and retrieval
- Use Django test database

### Integration Tests (`integration/`)
- Test full flow from application to domain to infrastructure
- Test complete use cases
- Test service interactions
- Test atomic transactions and rollbacks
- Use real database with transactions

## Running Tests

### Using the Test Runner Script

The `run_tests.py` script provides convenient commands to run different types of tests:

```bash
# Run unit tests only
python src/tests/run_tests.py unit

# Run functional tests only
python src/tests/run_tests.py functional

# Run integration tests only
python src/tests/run_tests.py integration

# Run all tests with coverage
python src/tests/run_tests.py all

# Run code linting
python src/tests/run_tests.py lint

# Run code formatting
python src/tests/run_tests.py format

# Run type checking
python src/tests/run_tests.py type-check

# Run full suite (lint + format + type-check + all tests)
python src/tests/run_tests.py full
```

### Using Pytest Directly

```bash
# Run all tests
pytest src/tests/

# Run specific test type
pytest src/tests/unit/
pytest src/tests/functional/
pytest src/tests/integration/

# Run with coverage
pytest src/tests/ --cov=src --cov-report=html

# Run specific test file
pytest src/tests/unit/test_wallet_entity.py

# Run specific test method
pytest src/tests/unit/test_wallet_entity.py::TestWalletEntity::test_wallet_creation_with_valid_data
```

### Using Django Test Commands

```bash
# Run tests using Django's test runner
python manage.py test src.tests

# Run with specific settings
python manage.py test src.tests --settings=config.settings.test
```

## Test Configuration

### Pytest Configuration
The pytest configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.dev"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=wallet_project",
    "--cov-report=term-missing",
    "--cov-report=html",
]
testpaths = ["src/tests"]
```

### Common Fixtures
The `conftest.py` file provides common fixtures for all tests:

- `sample_wallet_id`: Sample wallet ID
- `sample_transaction_id`: Sample transaction ID
- `sample_txid`: Sample transaction external ID
- `sample_money`: Sample money amount
- `sample_wallet`: Sample wallet entity
- `sample_transaction`: Sample transaction entity
- `sample_wallet_model`: Sample wallet Django model
- `sample_transaction_model`: Sample transaction Django model
- `DatabaseTestCase`: Base class for database-dependent tests

## Test Coverage

The tests cover:

### Domain Layer
- ✅ Wallet entity (creation, validation, business rules)
- ✅ Transaction entity (creation, validation, business rules)
- ✅ Domain services (business logic)
- ✅ Domain exceptions

### Application Layer
- ✅ Application services (use case orchestration)
- ✅ Commands and queries
- ✅ Use cases

### Infrastructure Layer
- ✅ Repository implementations
- ✅ Database models
- ✅ Data persistence and retrieval

### Integration
- ✅ Full application flow
- ✅ Atomic transactions
- ✅ Error handling and rollbacks
- ✅ Concurrent access handling

## Best Practices

### Writing Unit Tests
- Test one thing at a time
- Use descriptive test names
- Arrange-Act-Assert pattern
- Mock external dependencies
- Test both success and failure cases

### Writing Functional Tests
- Use real database
- Test data persistence
- Test query operations
- Test concurrent access
- Clean up test data

### Writing Integration Tests
- Test complete workflows
- Test service interactions
- Test transaction boundaries
- Test error scenarios
- Use realistic test data

### General Guidelines
- Keep tests fast and reliable
- Use meaningful assertions
- Test edge cases and error conditions
- Maintain test data isolation
- Document complex test scenarios

## Continuous Integration

The tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python src/tests/run_tests.py full
```

## Coverage Reports

After running tests with coverage, you can view the HTML report:

```bash
# Generate coverage report
pytest src/tests/ --cov=src --cov-report=html

# Open the report
open htmlcov/index.html
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure test database is configured
   - Check database settings in test configuration

2. **Import Errors**
   - Verify all dependencies are installed
   - Check import paths after refactoring

3. **Test Isolation Issues**
   - Use `DatabaseTestCase` for database tests
   - Clean up test data in `tearDown` methods

4. **Performance Issues**
   - Use database transactions for test isolation
   - Avoid creating unnecessary test data
   - Use appropriate test markers

### Debugging Tests

```bash
# Run tests with verbose output
pytest src/tests/ -v -s

# Run tests with debugger
pytest src/tests/ --pdb

# Run specific failing test
pytest src/tests/unit/test_wallet_entity.py::TestWalletEntity::test_wallet_creation_with_valid_data -v -s
```
