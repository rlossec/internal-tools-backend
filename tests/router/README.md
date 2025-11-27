# Tests des endpoints

Ce dossier contient les tests pour tous les endpoints de l'application.
Chaque module de router a son propre sous-dossier.

## Structure

```
tests/router/
├── tool/                      # Tests pour les endpoints /tools
│   ├── test_list_tool.py      # Tests pour GET /tools
│   ├── test_retrieve_tool.py  # Tests pour GET /tools/{tool_id}
│   ├── test_create_tool.py    # Tests pour POST /tools
│   ├── test_update_tool.py    # Tests pour PUT /tools/{tool_id}
│   └── README.md              # Documentation des tests /tools
└── README.md
```

## Organisation

La structure des tests suit exactement la structure du code de l'application :

- `app/router/tool.py` → `tests/router/tool/`
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
```

## Tests paramétrés

Certains tests utilisent `pytest.mark.parametrize` pour tester plusieurs scénarios avec le même code de test. Cela permet de réduire la duplication de code et d'améliorer la maintenabilité.

Exemples :

- **`test_list_tool.py`** : Tests de tri avec différentes combinaisons (champ + ordre)
- **`test_create_tool.py`** : Tests avec différents départements (7 cas)
- **`test_update_tool.py`** : Tests de validation avec différents champs invalides (10 cas)
- **`test_update_tool.py`** : Tests avec différents statuts (active, trial, deprecated)

## Statistiques des tests

**Total : 139 tests** pour les endpoints `/tools` :

- `GET /tools` : 65 tests
- `GET /tools/{tool_id}` : 22 tests
- `POST /tools` : 21 tests
- `PUT /tools/{tool_id}` : 32 tests

Voir `tests/router/tool/README.md` pour la documentation détaillée de chaque endpoint.
