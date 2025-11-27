# Tests des endpoints (Router)

Ce dossier contient les tests pour tous les endpoints de l'application. Chaque module de router a son propre sous-dossier.

## Structure

```
tests/router/
├── tool/                 # Tests pour les endpoints /tools
│   ├── list_tool.py      # Tests pour GET /tools
│   ├── get_tool.py       # Tests pour GET /tools/{tool_id} [À venir]
│   └── create_tool.py    # Tests pour POST /tools [À venir]
└── README.md             # Ce fichier
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
```
