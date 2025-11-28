# Tests des endpoints

Ce dossier contient les tests pour tous les endpoints de l'application.
Chaque module de router a son propre sous-dossier.

## Structure

```
tests/router/
├── tool/                      # Tests pour les endpoints /tools
│   ├── test_list_tool.py      # Tests pour GET /tools
│   ├── test_retrieve_tool.py   # Tests pour GET /tools/{tool_id}
│   ├── test_create_tool.py    # Tests pour POST /tools
│   ├── test_update_tool.py    # Tests pour PUT /tools/{tool_id}
│   └── README.md              # Documentation des tests /tools
├── analytics/                 # Tests pour les endpoints /analytics
│   ├── test_department_costs.py    # Tests pour GET /analytics/department-costs
│   ├── test_expensive_tools.py     # Tests pour GET /analytics/expensive-tools
│   └── README.md                   # Documentation des tests /analytics
├── test_database_errors.py    # Tests pour les erreurs de base de données (tous endpoints)
└── README.md
```

## Organisation

La structure des tests suit exactement la structure du code de l'application :

- `app/router/tool.py` → `tests/router/tool/`
- `app/router/analytics.py` → `tests/router/analytics/`
- Chaque endpoint a son propre fichier de test
- Les noms de fichiers correspondent aux fonctionnalités testées

## Fixtures disponibles

Toutes les fixtures définies dans `tests/conftest.py` sont disponibles :

- `db_session` : Session de base de données de test
- `test_categories` : Catégories de test
- `test_tools` : Outils de test
- `client` : Client FastAPI de test

Voir `tests/README.md` pour plus de détails sur les fixtures.

## Exécution des tests

### Tous les tests des routers

```bash
pytest tests/router/
```

### Tests d'un module spécifique

```bash
# Tests pour les endpoints /tools
pytest tests/router/tool/

# Tests pour les endpoints /analytics
pytest tests/router/analytics/
```

### Tests d'un endpoint spécifique

```bash
# Tests pour GET /tools
pytest tests/router/tool/test_list_tool.py

# Tests pour GET /tools/{tool_id}
pytest tests/router/tool/test_retrieve_tool.py

# Tests pour POST /tools
pytest tests/router/tool/test_create_tool.py

# Tests pour PUT /tools/{tool_id}
pytest tests/router/tool/test_update_tool.py

# Tests pour GET /analytics/department-costs
pytest tests/router/analytics/test_department_costs.py

# Tests pour GET /analytics/expensive-tools
pytest tests/router/analytics/test_expensive_tools.py

# Tests pour les erreurs de base de données (tous endpoints)
pytest tests/router/test_database_errors.py
```

## Tests paramétrés

Certains tests utilisent `pytest.mark.parametrize` pour tester plusieurs scénarios avec le même code de test. Cela permet de réduire la duplication de code et d'améliorer la maintenabilité.

Exemples :

- **`test_list_tool.py`** : Tests de tri avec différentes combinaisons (champ + ordre)
- **`test_create_tool.py`** : Tests avec différents départements (7 cas)
- **`test_update_tool.py`** : Tests de validation avec différents champs invalides (10 cas)
- **`test_update_tool.py`** : Tests avec différents statuts (active, trial, deprecated)

## Tests d'erreurs de base de données

**Fichier :** `test_database_errors.py`

Tests pour vérifier que tous les endpoints retournent HTTP 500 avec le format standardisé lorsque la base de données est indisponible.

### Fonctionnalités

- Test paramétré qui passe en revue tous les endpoints disponibles
- Vérifie que chaque endpoint retourne :
  - Statut HTTP 500
  - Format de réponse : `{"error": "Internal server error", "message": "Database connection failed"}`

### Endpoints testés

- `GET /tools` : Liste des outils
- `GET /tools/{tool_id}` : Détail d'un outil
- `POST /tools` : Création d'un outil
- `PUT /tools/{tool_id}` : Mise à jour d'un outil
- `GET /analytics/department-costs` : Coûts par département
- `GET /analytics/expensive-tools` : Outils les plus coûteux

**Total : 6 tests** (1 fonction paramétrée testant les 6 endpoints)

## Statistiques des tests

**Total : 171 tests** pour tous les endpoints :

### Endpoints `/tools` : 143 tests

- `GET /tools` : 65 tests
- `GET /tools/{tool_id}` : 22 tests
- `POST /tools` : 21 tests
- `PUT /tools/{tool_id}` : 31 tests

### Endpoints `/analytics` : 28 tests

- `GET /analytics/department-costs` : 13 tests
- `GET /analytics/expensive-tools` : 15 tests

### Erreurs de base de données

- **Erreurs de base de données** : 6 tests (tous endpoints)

Voir `tests/router/tool/README.md` pour la documentation détaillée des endpoints `/tools`.  
Voir `tests/router/analytics/README.md` pour la documentation détaillée des endpoints `/analytics`.
