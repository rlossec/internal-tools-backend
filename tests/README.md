# Tests

Ce dossier contient tous les tests de l'application. La structure des tests suit la même organisation que le code de l'application dans `app/`.

## Structure

```
tests/
├── conftest.py           # Fixtures partagées pour tous les tests
├── router/               # Tests pour les endpoints (routes)
│   └── tool/             # Tests pour les endpoints /tools
└── README.md             # Ce fichier
```

## Fixtures partagées

Les fixtures sont définies dans `conftest.py` à la racine du dossier `tests/` et sont disponibles pour tous les tests :

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

### Fixtures d'application

- **`client`** : Client FastAPI de test
  - Permet d'effectuer des requêtes HTTP vers l'application
  - Les dépendances FastAPI sont surchargées pour utiliser la base de données de test

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
