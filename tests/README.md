# Tests

This folder contains all application tests. The test layout mirrors the `app/` package structure.

## Structure

```
tests/
├── conftest.py           # Shared fixtures for all tests
├── router/               # Endpoint tests
│   └── tool/             # Tests for /tools endpoints
└── README.md             # This file
```

## Shared fixtures

Fixtures are defined in `conftest.py` at the `tests/` root and are available to every test:

### Database fixtures

- **`db_session`**: Test database session (in-memory SQLite)
  - Scope: `function` (new session per test)
  - Creates and drops tables automatically before/after each test
  - Ensures full isolation between tests

### Data fixtures

- **`test_categories`**: Creates 5 test categories

  - Development, Design, Marketing, Operations, Finance

- **`test_tools`**: Creates 5 test tools with different attributes
  - See [Test data](#test-data) below
- **`test_user`**: Creates a test user for usage logs
  - Used to exercise tool usage metrics
- **`test_usage_logs`**: Creates sample usage logs
  - 5 logs with different dates (recent and older)
  - Used to test usage metric calculations

### Application fixtures

- **`client`**: FastAPI test client
  - Sends HTTP requests to the app
  - FastAPI dependencies are overridden to use the test database

## Test data

The fixtures create five tools with varied attributes to cover test scenarios:

1. **GitHub**

   - Category: Development
   - Department: Engineering
   - Status: active
   - Cost: €50
   - Vendor: GitHub Inc.

2. **Slack**

   - Category: Design
   - Department: Marketing
   - Status: active
   - Cost: €75
   - Vendor: Slack Technologies

3. **Jira**

   - Category: Marketing
   - Department: Engineering
   - Status: trial
   - Cost: €100
   - Vendor: Atlassian

4. **Figma**

   - Category: Operations
   - Department: Design
   - Status: active
   - Cost: €30
   - Vendor: Figma Inc.

5. **Deprecated Tool**
   - Category: Finance
   - Department: Operations
   - Status: deprecated
   - Cost: €20
   - Vendor: Old Vendor

These records support filtering, sorting, validation, and edge-case tests.

## Running tests

### All tests

```bash
pytest
```

### Verbose output

```bash
pytest -v
```

### Code coverage

```bash
pytest --cov=app --cov-report=html
```

### Specific tests

```bash
# All tests in a module
pytest tests/router/tool/

# A single test file
pytest tests/router/tool/test_list_tool.py

# A single test
pytest tests/router/tool/test_list_tool.py::TestGetToolsEndpoint::test_get_tools_without_filters
```

## Important notes

### Test isolation

- Tests use an in-memory SQLite database for isolation
- Each test gets its own DB session (`db_session`, scope `function`)
- Fixtures are cleaned up after each test
- Tests cannot affect one another

### Dependency overrides

- FastAPI dependencies are overridden to use the test database
- Endpoints can be tested without touching the development database
- See `conftest.py` for implementation details

### Test organization

- Each router module has its own folder under `tests/router/`
- Each endpoint has its own test file (e.g. `test_list_tool.py`, `test_get_tool.py`)
- Tests mirror the application layout
- `@pytest.mark.parametrize` is used to cover many combinations efficiently

### Parametrized tests

Tests use `@pytest.mark.parametrize` to avoid duplication and cover many combinations.

Each combination runs as its own test, which makes failures easier to pinpoint.
