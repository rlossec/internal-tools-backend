# Tests pour les endpoints `/tools`

Ce dossier contient les tests pour tous les endpoints liés aux outils (`/tools`).

## Structure des fichiers

```
tests/router/tool/
├── __init__.py
├── test_list_tool.py          # Tests pour GET /tools
├── test_get_tool.py           # Tests pour GET /tools/{tool_id}   [À venir]
├── test_create_tool.py        # Tests pour POST /tools (création) [À venir]
└── README.md                  # Ce fichier
```

## Exécution des tests

```bash
pytest tests/router/tool/
pytest tests/router/tool/list_tool.py   # Tests pour GET /tools
pytest tests/router/tool/get_tool.py    # Tests pour GET /tools/{tool_id}
pytest tests/router/tool/create_tool.py # Tests pour POST /tools
```

---

## GET /tools - Liste des outils

**Fichier :** `test_list_tool.py`

Tests pour l'endpoint `GET /tools` qui permet de récupérer la liste des outils avec filtres et tri.

### Tests des succès - 200

- `test_get_tools_without_filters` : Récupération sans filtres

#### Tests de filtrage

- `test_get_tools_filter_by_category` : Filtre par catégorie
- `test_get_tools_filter_by_vendor` : Filtre par vendeur
- `test_get_tools_filter_by_department` : Filtre par département
- `test_get_tools_filter_by_status` : Filtre par statut
- `test_get_tools_filter_by_min_cost` : Filtre par coût minimum
- `test_get_tools_filter_by_max_cost` : Filtre par coût maximum
- `test_get_tools_filter_by_cost_range` : Filtre par plage de coût
- `test_get_tools_multiple_filters` : Plusieurs filtres combinés

#### Tests des tri

- `test_get_tools_sorting` : Test paramétré pour le tri par différents champs
  - Tri par nom (asc/desc)
  - Tri par coût (asc/desc)
  - Tri par ID (asc/desc)
  - Tri par date de création (asc/desc)
  - **8 combinaisons testées** via `@pytest.mark.parametrize`

#### Tests de combinaisons filtres + tri

- `test_get_tools_filter_and_sort` : Test paramétré pour combiner filtres et tri
  - Filtres actifs + tri par coût
  - Filtres par département + tri par nom
  - Filtres par date + tri par date
  - **7 combinaisons testées** via `@pytest.mark.parametrize`

#### Tests de cas limites

- `test_get_tools_no_results` : Aucun résultat avec un filtre
- `test_get_tools_no_results_scenarios` : Test paramétré pour différents scénarios sans résultats (4 cas)
- `test_get_tools_invalid_department` : Département invalide (ignoré silencieusement)

### Tests de validation d'erreurs (422)

- [ ] Tests pour les erreurs de validation (coûts négatifs, plages invalides, etc.) [À venir]

## GET /tools/{tool_id} - Détail d'un outil

**Fichier :** `get_tool.py` [À venir]

Tests pour l'endpoint `GET /tools/{tool_id}` qui permet de récupérer les détails d'un outil spécifique.

### Tests à implémenter

- [ ] `test_get_tool_success` : Récupération réussie d'un outil existant
- [ ] `test_get_tool_not_found` : Outil inexistant (404)
- [ ] `test_get_tool_invalid_id` : ID invalide (non numérique)
- [ ] `test_get_tool_response_structure` : Vérification de la structure de la réponse
- [ ] `test_get_tool_with_usage_metrics` : Vérification des métriques d'utilisation
- [ ] `test_get_tool_with_cost_tracking` : Vérification du suivi des coûts

---

## POST /tools - Création d'un outil

**Fichier :** `create_tool.py` [À venir]

Tests pour l'endpoint `POST /tools` qui permet de créer un nouvel outil.

### Tests à implémenter

- [ ] `test_create_tool_success` : Création réussie avec données valides
- [ ] `test_create_tool_validation_errors` : Erreurs de validation (champs requis manquants)
- [ ] `test_create_tool_invalid_category` : Catégorie inexistante
- [ ] `test_create_tool_invalid_department` : Département invalide
- [ ] `test_create_tool_invalid_status` : Statut invalide
- [ ] `test_create_tool_duplicate_name` : Nom d'outil déjà existant (si applicable)
- [ ] `test_create_tool_negative_cost` : Coût négatif (validation)
- [ ] `test_create_tool_response_structure` : Vérification de la structure de la réponse

---

## Références

- **Fixtures** : Voir `tests/README.md` pour la documentation complète des fixtures
- **Données de test** : Voir `tests/README.md` pour la liste des données de test disponibles
- **Notes générales** : Voir `tests/README.md` pour les informations sur l'isolation et la configuration des tests
