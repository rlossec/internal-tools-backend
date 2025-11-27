# Tests pour les endpoints `/tools`

Ce dossier contient les tests pour tous les endpoints liés aux outils (`/tools`).

## Structure des fichiers

```
tests/router/tool/
├── __init__.py
├── test_list_tool.py          # Tests pour GET /tools
├── test_retrieve_tool.py      # Tests pour GET /tools/{tool_id}
├── test_create_tool.py        # Tests pour POST /tools (création) [À venir]
└── README.md                  # Ce fichier
```

## Exécution des tests

```bash
pytest tests/router/tool/
pytest tests/router/tool/test_list_tool.py   # Tests pour GET /tools
pytest tests/router/tool/test_retrieve_tool.py    # Tests pour GET /tools/{tool_id}
pytest tests/router/tool/test_create_tool.py # Tests pour POST /tools
```

---

## GET /tools - Liste des outils

**Fichier :** `test_list_tool.py`

Tests pour l'endpoint `GET /tools` qui permet de récupérer la liste des outils avec filtres, tri et pagination.

### Fonctionnalités

L'endpoint supporte :

- **Filtrage** : par catégorie, vendeur, département, statut, coût (min/max)
- **Tri** : par nom, coût, ID, date de création (asc/desc)
- **Pagination** : paramètres `page` et `limit` optionnels
  - `page` : numéro de page (≥ 1)
  - `limit` : nombre d'éléments par page (1-100)
  - Les métadonnées de pagination sont incluses uniquement si les deux paramètres sont fournis

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
- `test_get_tools_invalid_filters_ignored` : Test paramétré pour les filtres invalides (département, statut) ignorés silencieusement
- `test_get_tools_empty_filters` : Test paramétré pour différents scénarios de filtres vides (4 cas)
- `test_get_tools_filters_applied_in_response` : Vérification que les filtres appliqués sont retournés dans la réponse
- `test_get_tools_default_sort` : Vérification que le tri par défaut est par ID croissant

#### Tests de pagination

- `test_get_tools_pagination_first_page` : Pagination - première page
- `test_get_tools_pagination_middle_page` : Pagination - page du milieu
- `test_get_tools_pagination_last_page` : Pagination - dernière page
- `test_get_tools_pagination_without_pagination_params` : Sans page/limit, pas de métadonnées de pagination
- `test_get_tools_pagination_with_filters` : Pagination combinée avec des filtres
- `test_get_tools_pagination_with_sorting` : Pagination combinée avec tri
- `test_get_tools_pagination_validation_errors` : Test paramétré pour les erreurs de validation de pagination
  - `page < 1` (6 cas testés)
- `test_get_tools_pagination_page_out_of_range` : Page hors limites (retourne NoResultsFoundResponse)

**Paramètres de pagination :**

- `page` : Numéro de page (commence à 1, optionnel)
- `limit` : Nombre d'éléments par page (1-100, optionnel)
- Les métadonnées de pagination (`pagination`) ne sont incluses que si `page` et `limit` sont fournis

### Tests de validation d'erreurs (422)

- `test_get_tools_query_validation_errors` : Test paramétré pour les erreurs de validation FastAPI Query
  - Coûts négatifs (`min_cost`, `max_cost`)
  - Enums invalides (`sort_by`, `sort_order`)
  - **4 cas testés** via `@pytest.mark.parametrize`
- `test_get_tools_pydantic_validation_error` : Erreur de validation Pydantic (logique métier)
  - `min_cost > max_cost` (validation métier)

## GET /tools/{tool_id} - Détail d'un outil

**Fichier :** `test_retrieve_tool.py`

Tests pour l'endpoint `GET /tools/{tool_id}` qui permet de récupérer les détails d'un outil spécifique.

**Total : 23 tests** couvrant tous les cas d'usage, les métriques d'utilisation et les cas limites.

### Fonctionnalités

L'endpoint retourne :

- **Informations de base** : id, name, description, vendor, website_url, category, monthly_cost, owner_department, status, active_users_count
- **Coût total mensuel** : calculé automatiquement (`monthly_cost * active_users_count`)
- **Métriques d'utilisation** : statistiques des 30 derniers jours (total_sessions, avg_session_minutes)
- **Dates** : created_at, updated_at

### Tests des succès - 200

- `test_get_tool_success` : Récupération réussie d'un outil existant avec vérification de tous les champs
- `test_get_tool_total_monthly_cost_calculation` : Vérification du calcul du coût total mensuel
- `test_get_tool_different_tools` : Test paramétré pour différents outils avec leurs coûts calculés
  - **5 outils testés** via `@pytest.mark.parametrize` (GitHub, Slack, Jira, Figma, Deprecated Tool)
- `test_get_tool_response_fields` : Vérification que tous les champs requis sont présents

#### Tests des métriques d'utilisation

- `test_get_tool_usage_metrics_structure` : Vérification de la structure des métriques d'utilisation
- `test_get_tool_usage_metrics_without_logs` : Métriques retournent 0 quand il n'y a pas de logs
- `test_get_tool_usage_metrics_with_logs` : Calcul correct des métriques avec des logs réels
  - Vérifie le calcul de `total_sessions` et `avg_session_minutes`
- `test_get_tool_usage_metrics_filters_old_logs` : Les logs de plus de 30 jours sont exclus
- `test_get_tool_usage_metrics_different_tools` : Isolation des métriques par outil
- `test_get_tool_usage_metrics_single_session` : Calcul correct avec une seule session
- `test_get_tool_usage_metrics_zero_minutes` : Gestion des sessions avec 0 minutes (cas limite)

### Tests Not Found - 200 (NotFoundResponse)

- `test_get_tool_not_found` : Outil inexistant retourne NotFoundResponse
- `test_get_tool_not_found_scenarios` : Test paramétré pour différents IDs inexistants
  - **3 scénarios testés** via `@pytest.mark.parametrize` (0, -1, 999999)

### Tests de validation d'erreurs (422)

- `test_get_tool_invalid_id_type` : Test paramétré pour IDs invalides (non numériques)
  - IDs non numériques : "not_a_number", "abc", "1.5"
  - Chaîne vide : redirige vers `/tools` (307)
  - **4 cas testés** via `@pytest.mark.parametrize`

---

## POST /tools - Création d'un outil

**Fichier :** `test_create_tool.py` [À venir]

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
