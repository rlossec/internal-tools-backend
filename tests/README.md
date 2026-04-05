# Tests

This folder contains all application tests. The test layout mirrors the `app/` package structure.

## Structure

```
tests/
├── conftest.py                    # Fixtures communes partagées
├── factories/                     # Factories pour créer des données de test
│   ├── __init__.py                # FactoryManager + fixture
│   ├── base.py                    # BaseFactory
│   ├── category_factory.py
│   ├── cost_tracking_factory.py
│   ├── tool_factory.py
│   ├── user_factory.py
│   ├── user_tool_access_factory.py
│   └── usage_log_factory.py
├── fixtures/                      # Fixtures spécifiques par domaine
│   ├── __init__.py
│   ├── data.py                    # Fixtures de données (catégories, outils, etc.)
│   └── department/              # Fixtures départements (données + services)
│       ├── data.py
│       └── services.py
├── repositories/                  # Tests des repositories
│   └── department_repository/
│       └── test_get_department_costs_data.py
├── services/                      # Tests des services
│   └── department/
│       └── test_department_service.py
├── router/                        # Tests pour les endpoints
│   ├── analytics/               # Tests des routes analytics
│   └── tool/                    # Tests pour les endpoints /tools
└── README.md                      # Ce fichier
```

## Organisation des fixtures

### Fixtures communes (`tests/conftest.py`)

Les fixtures définies dans `conftest.py` à la racine sont disponibles pour **tous les tests** et contiennent les éléments communs :

- Configuration de la base de données
- Données de base (catégories, outils de base)
- Repositories et services généraux
- Client FastAPI de test

### Fixtures spécifiques (`tests/fixtures/`)

Les fixtures spécifiques à un domaine fonctionnel sont organisées dans le dossier `fixtures/` :

- **`tests/fixtures/department/data.py`** et **`tests/fixtures/department/services.py`** : données et services pour les tests liés aux départements (coûts, agrégations, etc.)

Ces modules sont chargés automatiquement via `pytest_plugins` dans le `conftest.py` principal.

## Fixtures communes disponibles

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

- **`tool_repository`** : Repository pour les outils
- **`tool_service`** : Service pour les outils
- **`client`** : Client FastAPI de test
  - Permet d'effectuer des requêtes HTTP vers l'application
  - Les dépendances FastAPI sont surchargées pour utiliser la base de données de test

## Fixtures spécifiques - Départements

Les fixtures liées aux départements sont définies sous `tests/fixtures/department/` et chargées via `pytest_plugins` dans le `conftest.py` principal :

- **`test_users_for_department_computations`** : crée plusieurs utilisateurs dans différents départements (admin, Engineering, Sales, Marketing, HR, etc.)
- **`test_user_tool_access_for_department_computations`** : accès utilisateur-outil pour les scénarios de coûts par département
- **`test_cost_tracking_for_department_computations`** : données de suivi des coûts pour ces tests
- **`department_repository`** : `DepartmentRepository` de test
- **`department_service`** : service départements de test

## Factories pour créer des données de test

Les **factories** permettent de créer facilement des données de test avec des valeurs par défaut intelligentes.

### Fixture `factories`

La fixture `factories` donne accès à un `FactoryManager` qui regroupe toutes les factories disponibles :

```python
def test_example(factories):
    # Créer une catégorie
    category = factories.category.create_development()

    # Créer un outil
    tool = factories.tool.create_github(category_id=category.id)

    # Créer un utilisateur
    user = factories.user.create_engineer(name="John")

    # Commiter toutes les créations
    factories.commit()
```

### Factories disponibles

- **`factories.category`** : Créer des catégories
  - `create_development()`, `create_marketing()`, etc.
  - `create(name="...", description="...")` avec valeurs personnalisées
- **`factories.tool`** : Créer des outils
  - `create_github(category_id)`, `create_slack(category_id)`, etc.
  - `create(category_id, name="...", monthly_cost=...)` avec valeurs personnalisées
- **`factories.user`** : Créer des utilisateurs
  - `create_engineer()`, `create_sales()`, `create_admin()`, etc.
  - `create(name="...", department=...)` avec valeurs personnalisées
- **`factories.user_tool_access`** : Créer des accès
  - `create_active(user_id, tool_id, granted_by)`
  - `grant_access_to_multiple_tools(...)`
- **`factories.usage_log`** : Créer des logs d'utilisation
  - `create_recent(user_id, tool_id, days_ago=5)`
  - `create_old(user_id, tool_id, days_ago=40)`

### Exemple complet

```python
def test_department_costs_with_factories(factories):
    """Exemple : données créées via factories puis appel au repository."""
    dev_category = factories.category.create_development()
    design_category = factories.category.create_design()

    github = factories.tool.create_github(category_id=dev_category.id)
    slack = factories.tool.create_slack(category_id=design_category.id)

    admin = factories.user.create_admin()
    engineer1 = factories.user.create_engineer(name="Engineer 1")
    engineer2 = factories.user.create_engineer(name="Engineer 2")

    factories.user_tool_access.create_active(engineer1.id, github.id, admin.id)
    factories.user_tool_access.create_active(engineer2.id, github.id, admin.id)

    factories.commit()

    from app.repositories import DepartmentRepository
    repository = DepartmentRepository(session=factories.db)
    results = repository.get_department_costs_data()
    # ...
```

Voir `tests/factories/test_factories_example.py` pour plus d'exemples.

## Données de test

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
pytest tests/router/analytics/

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
