# Tests

Ce dossier contient tous les tests de l'application. La structure des tests suit la même organisation que le code de l'application dans `app/`.

## Structure

```
tests/
├── conftest.py                    # Fixtures communes partagées
├── factories/                     # Factories pour créer des données de test
│   ├── __init__.py                # FactoryManager + fixture
│   ├── base.py                    # BaseFactory
│   ├── category_factory.py
│   ├── tool_factory.py
│   ├── user_factory.py
│   ├── user_tool_access_factory.py
│   └── usage_log_factory.py
├── fixtures/                      # Fixtures spécifiques par domaine
│   ├── __init__.py
│   ├── data.py                   # Fixtures de données (catégories, outils, etc.)
│   └── analytics.py              # Fixtures spécifiques aux analytics
├── repositories/                  # Tests des repositories
│   └── analytics_repository/
│       └── test_analytics_repository.py
├── services/                      # Tests des services
│   └── analytics_service/
│       └── test_analytics_service.py
├── router/                        # Tests pour les endpoints
│   └── tool/                     # Tests pour les endpoints /tools
└── README.md                     # Ce fichier
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

- **`tests/fixtures/analytics.py`** : Fixtures spécifiques aux tests analytics
  - Utilisateurs multiples pour les tests analytics
  - Accès utilisateur-outil pour les tests analytics
  - Repository et service analytics

Ces fixtures sont chargées automatiquement via `pytest_plugins` dans le `conftest.py` principal.

## Fixtures communes disponibles

### Fixtures de base de données

- **`db_session`** : Session de base de données de test (SQLite en mémoire)
  - Scope: `function` (une nouvelle session par test)
  - Crée et supprime automatiquement les tables avant/après chaque test
  - Garantit l'isolation complète entre les tests

### Fixtures de données

- **`test_categories`** : Crée 5 catégories de test

  - Development, Design, Marketing, Operations, Finance

- **`test_tools`** : Crée 5 outils de test avec différentes caractéristiques
  - Voir la section [Données de test](#données-de-test) ci-dessous
- **`test_user`** : Crée un utilisateur de test pour les logs d'utilisation
  - Utilisé pour tester les métriques d'utilisation des outils
- **`test_usage_logs`** : Crée des logs d'utilisation de test
  - 5 logs avec différentes dates (récents et anciens)
  - Utilisé pour tester le calcul des métriques d'utilisation

### Fixtures d'application

- **`tool_repository`** : Repository pour les outils
- **`tool_service`** : Service pour les outils
- **`client`** : Client FastAPI de test
  - Permet d'effectuer des requêtes HTTP vers l'application
  - Les dépendances FastAPI sont surchargées pour utiliser la base de données de test

## Fixtures spécifiques - Analytics

Les fixtures spécifiques aux tests analytics sont définies dans `tests/fixtures/analytics.py` et chargées automatiquement via `pytest_plugins` dans le `conftest.py` principal :

- **`test_users_for_analytics`** : Crée 8 utilisateurs dans différents départements
  - 1 admin (Engineering)
  - 3 utilisateurs Engineering (2 actifs, 1 inactif)
  - 2 utilisateurs Sales (actifs)
  - 1 utilisateur Marketing (actif)
  - 1 utilisateur HR (actif, sans outils)
- **`test_user_tool_access_for_analytics`** : Crée des accès utilisateur-outil

  - Engineering : accès à GitHub et Jira
  - Sales : accès à Slack
  - Marketing : accès à Slack et Figma
  - Inclut des accès révoqués et inactifs pour tester le filtrage

- **`analytics_repository`** : Repository analytics de test
- **`analytics_service`** : Service analytics de test

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
def test_analytics_with_factories(factories):
    """Test analytics en créant des données avec factories."""
    # Créer catégories
    dev_category = factories.category.create_development()
    design_category = factories.category.create_design()

    # Créer outils
    github = factories.tool.create_github(category_id=dev_category.id)
    slack = factories.tool.create_slack(category_id=design_category.id)

    # Créer utilisateurs
    admin = factories.user.create_admin()
    engineer1 = factories.user.create_engineer(name="Engineer 1")
    engineer2 = factories.user.create_engineer(name="Engineer 2")

    # Créer accès
    factories.user_tool_access.create_active(engineer1.id, github.id, admin.id)
    factories.user_tool_access.create_active(engineer2.id, github.id, admin.id)

    factories.commit()  # Tout est prêt pour les tests

    # Tester maintenant...
    repository = AnalyticsRepository(session=factories.db)
    results = repository.get_department_costs_data()
    # ...
```

Voir `tests/factories/test_factories_example.py` pour plus d'exemples.

## Données de test

Les fixtures créent 5 outils de test avec différentes caractéristiques pour couvrir tous les scénarios de test :

1. **GitHub**

   - Catégorie: Development
   - Département: Engineering
   - Statut: active
   - Coût: 50€
   - Vendeur: GitHub Inc.

2. **Slack**

   - Catégorie: Design
   - Département: Marketing
   - Statut: active
   - Coût: 75€
   - Vendeur: Slack Technologies

3. **Jira**

   - Catégorie: Marketing
   - Département: Engineering
   - Statut: trial
   - Coût: 100€
   - Vendeur: Atlassian

4. **Figma**

   - Catégorie: Operations
   - Département: Design
   - Statut: active
   - Coût: 30€
   - Vendeur: Figma Inc.

5. **Deprecated Tool**
   - Catégorie: Finance
   - Département: Operations
   - Statut: deprecated
   - Coût: 20€
   - Vendeur: Old Vendor

Ces données permettent de tester tous les scénarios de filtrage, tri, validation et cas limites.

## Exécution des tests

### Tous les tests

```bash
pytest
```

### Tests avec sortie détaillée

```bash
pytest -v
```

### Tests avec couverture de code

```bash
pytest --cov=app --cov-report=html
```

### Tests spécifiques

```bash
# Tous les tests d'un module
pytest tests/router/tool/

# Un fichier de test spécifique
pytest tests/router/tool/test_list_tool.py

# Un test spécifique
pytest tests/router/tool/test_list_tool.py::TestGetToolsEndpoint::test_get_tools_without_filters
```

## Notes importantes

### Isolation des tests

- Les tests utilisent une base de données SQLite en mémoire pour l'isolation complète
- Chaque test a sa propre session de base de données (fixture `db_session` avec scope `function`)
- Les fixtures sont automatiquement nettoyées après chaque test
- Aucun test ne peut affecter un autre test

### Surcharge des dépendances

- Les dépendances FastAPI sont surchargées pour utiliser la base de données de test
- Cela permet de tester les endpoints sans affecter la base de données de développement
- Voir `conftest.py` pour les détails d'implémentation

### Structure des tests

- Chaque module de router a son propre dossier dans `tests/router/`
- Chaque endpoint a son propre fichier de test (ex: `test_list_tool.py`, `test_get_tool.py`)
- Les tests suivent la même structure que le code de l'application
- Utilisation de `@pytest.mark.parametrize` pour tester plusieurs combinaisons efficacement

### Tests paramétrés

Les tests utilisent `@pytest.mark.parametrize` pour éviter la duplication et tester de nombreuses combinaisons

Chaque combinaison est exécutée comme un test séparé, facilitant l'identification des problèmes.
