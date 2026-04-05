# Analyse de l'endpoint `/api/analytics/tools-by-category`

Ce document analyse les jointures et requêtes nécessaires pour implémenter l'endpoint `GET /api/analytics/tools-by-category`.

## Analyse des données nécessaires

### Champs de la réponse `data`

| Champ                   | Source            | Type    | Calcul                                                         |
| ----------------------- | ----------------- | ------- | -------------------------------------------------------------- |
| `category_name`         | `categories.name` | String  | Direct (agrégation)                                            |
| `tools_count`           | Calculé           | Integer | COUNT(DISTINCT `tools.id`) par catégorie                       |
| `total_cost`            | Calculé           | Decimal | SUM(`tools.monthly_cost`) par catégorie                        |
| `total_users`           | Calculé           | Integer | SUM(`tools.active_users_count`) par catégorie (pas dédupliqué) |
| `percentage_of_budget`  | Calculé           | Decimal | `(total_cost / total_company_cost) * 100`                      |
| `average_cost_per_user` | Calculé           | Decimal | `total_cost / total_users`                                     |

### Champs de la réponse `insights`

| Champ                     | Calcul                       | Description                                                                        |
| ------------------------- | ---------------------------- | ---------------------------------------------------------------------------------- |
| `most_expensive_category` | MAX(`total_cost`)            | Catégorie avec le coût total le plus élevé                                         |
| `most_efficient_category` | MIN(`average_cost_per_user`) | Catégorie avec le plus bas `average_cost_per_user` (ordre alphabétique si égalité) |

## Jointures nécessaires

### Modèles de données impliqués

Les requêtes utilisent les relations entre ces tables :

- **`tools`** : Outils disponibles avec leur coût mensuel, nombre d'utilisateurs et catégorie
- **`categories`** : Catégories d'outils

### Requête principale : `get_tools_by_category()`

#### Objectif

Récupérer, pour chaque catégorie, le nombre d'outils, le coût total, le nombre total d'utilisateurs, le pourcentage du budget et le coût moyen par utilisateur.

#### Jointures utilisées

1. **`tools` → `categories` (INNER JOIN sur `tools.category_id = categories.id`)** : Lie chaque outil à sa catégorie

#### Requête SQL équivalente

```sql
SELECT
    categories.name AS category_name,
    COUNT(DISTINCT tools.id) AS tools_count,
    SUM(tools.monthly_cost) AS total_cost,
    SUM(tools.active_users_count) AS total_users,
    CASE
        WHEN SUM(tools.active_users_count) > 0
        THEN SUM(tools.monthly_cost) / SUM(tools.active_users_count)
        ELSE NULL
    END AS average_cost_per_user
FROM
    tools
INNER JOIN
    categories ON tools.category_id = categories.id
WHERE
    tools.status = 'active'
GROUP BY
    categories.id,
    categories.name
ORDER BY
    total_cost DESC
```

#### Code Python

```python
query = (
    db.query(
        Category.name.label('category_name'),
        func.count(func.distinct(Tool.id)).label('tools_count'),
        func.sum(Tool.monthly_cost).label('total_cost'),
        func.sum(Tool.active_users_count).label('total_users'),
        case(
            (func.sum(Tool.active_users_count) > 0,
             func.sum(Tool.monthly_cost) / func.sum(Tool.active_users_count)),
            else_=None
        ).label('average_cost_per_user')
    )
    .join(Category, Tool.category_id == Category.id)
    .filter(Tool.status == ToolStatus.active)
    .group_by(Category.id, Category.name)
    .order_by(func.sum(Tool.monthly_cost).desc())
)

categories_data = query.all()
```

## Calcul de l'analyse (`insights`)

### 1. `percentage_of_budget`

Calcule le pourcentage du budget total de l'entreprise pour chaque catégorie.

```python
total_company_cost = sum(cat.total_cost for cat in categories_data)

for category in categories_data:
    category.percentage_of_budget = (
        (category.total_cost / total_company_cost * 100)
        if total_company_cost > 0 else 0
    )
```

### 2. `most_expensive_category`

Identifie la catégorie avec le coût total le plus élevé.

```python
most_expensive_category = max(
    categories_data,
    key=lambda x: x.total_cost
).category_name
```

### 3. `most_efficient_category`

Identifie la catégorie avec le plus bas `average_cost_per_user`. En cas d'égalité, ordre alphabétique.

```python
# Filtrer les catégories sans utilisateurs
categories_with_users = [
    cat for cat in categories_data
    if cat.total_users > 0
]

if categories_with_users:
    most_efficient_category = min(
        categories_with_users,
        key=lambda x: (x.average_cost_per_user, x.category_name)
    ).category_name
else:
    most_efficient_category = None
```

## Cas particuliers à gérer

### 1. Catégories sans outils actifs

- Ces catégories ne doivent pas apparaître dans les résultats
- Le filtre `tools.status = 'active'` les exclut automatiquement

### 2. Catégories sans utilisateurs (`total_users = 0`)

- `average_cost_per_user` doit être `NULL`
- Ces catégories sont exclues du calcul de `most_efficient_category`

### 3. Pourcentage du budget

- Les pourcentages doivent additionner à 100% (±0.1% de tolérance)
- Arrondi à 1 décimale maximum

### 4. Tri des résultats

- Trier par `total_cost DESC` par défaut (catégories les plus chères en premier)
- En cas d'égalité, trier par `category_name ASC`

## Références

- **Modèle Tool** : `app/models/tool.py`
- **Modèle Category** : `app/models/category.py`
- **Router Analytics** : `app/router/analytics.py`
- **Documentation similaire** : [`1_department_cost.md`](./1_department_cost.md)
