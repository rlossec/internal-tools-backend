# 5 Vendor Summary

Ce document analyse les jointures et requêtes nécessaires pour implémenter l'endpoint `GET /api/analytics/vendor-summary`.

## Analyse des données nécessaires

### Champs de la réponse `data`

| Champ                   | Source         | Type    | Calcul                                                      |
| ----------------------- | -------------- | ------- | ----------------------------------------------------------- |
| `vendor`                | `tools.vendor` | String  | Direct (agrégation)                                         |
| `tools_count`           | Calculé        | Integer | COUNT(DISTINCT `tools.id`) par vendor                       |
| `total_monthly_cost`    | Calculé        | Decimal | SUM(`tools.monthly_cost`) par vendor                        |
| `total_users`           | Calculé        | Integer | SUM(`tools.active_users_count`) par vendor                  |
| `departments`           | Calculé        | String  | Concaténation des départements uniques (ordre alphabétique) |
| `average_cost_per_user` | Calculé        | Decimal | `total_monthly_cost / total_users`                          |
| `vendor_efficiency`     | Calculé        | String  | Basé sur `average_cost_per_user`                            |

### Champs de la réponse `vendor_insights`

| Champ                   | Calcul                                   | Description                                                                     |
| ----------------------- | ---------------------------------------- | ------------------------------------------------------------------------------- |
| `most_expensive_vendor` | MAX(`total_monthly_cost`)                | Vendor avec le coût total mensuel le plus élevé                                 |
| `most_efficient_vendor` | MIN(`average_cost_per_user`)             | Vendor avec le plus bas `average_cost_per_user` (ordre alphabétique si égalité) |
| `single_tool_vendors`   | COUNT des vendors avec `tools_count = 1` | Nombre de vendors qui fournissent exactement 1 outil actif                      |

## Jointures nécessaires

### Modèles de données impliqués

Les requêtes utilisent uniquement la table :

- **`tools`** : Outils disponibles avec leur fournisseur, coût mensuel, nombre d'utilisateurs et départements

### Requête principale : `get_vendor_summary()`

#### Objectif

Récupérer, pour chaque vendor, le nombre d'outils, le coût total mensuel, le nombre total d'utilisateurs, les départements concernés, le coût moyen par utilisateur et l'efficacité du vendor.

#### Jointures utilisées

**Aucune jointure nécessaire** - Cette requête utilise uniquement la table `tools` avec agrégation par `vendor`.

#### Requête SQL équivalente

```sql
SELECT
    tools.vendor,
    COUNT(DISTINCT tools.id) AS tools_count,
    SUM(tools.monthly_cost) AS total_monthly_cost,
    SUM(tools.active_users_count) AS total_users,
    CASE
        WHEN SUM(tools.active_users_count) > 0
        THEN SUM(tools.monthly_cost) / SUM(tools.active_users_count)
        ELSE NULL
    END AS average_cost_per_user
FROM
    tools
WHERE
    tools.status = 'active'
    AND tools.vendor IS NOT NULL
GROUP BY
    tools.vendor
ORDER BY
    total_monthly_cost DESC
```

#### Code Python

```python
query = (
    db.query(
        Tool.vendor,
        func.count(func.distinct(Tool.id)).label('tools_count'),
        func.sum(Tool.monthly_cost).label('total_monthly_cost'),
        func.sum(Tool.active_users_count).label('total_users'),
        case(
            (func.sum(Tool.active_users_count) > 0,
             func.sum(Tool.monthly_cost) / func.sum(Tool.active_users_count)),
            else_=None
        ).label('average_cost_per_user')
    )
    .filter(Tool.status == ToolStatus.active)
    .filter(Tool.vendor.isnot(None))
    .group_by(Tool.vendor)
    .order_by(func.sum(Tool.monthly_cost).desc())
)

vendors_data = query.all()
```

## Calcul des champs supplémentaires

### 1. `departments`

Concaténation des départements uniques pour chaque vendor, triés par ordre alphabétique.

```python
for vendor in vendors_data:
    # Récupérer les départements distincts pour ce vendor
    departments_query = (
        db.query(Tool.owner_department)
        .filter(Tool.vendor == vendor.vendor)
        .filter(Tool.status == ToolStatus.active)
        .distinct()
        .order_by(Tool.owner_department)
    )

    departments = [dept[0] for dept in departments_query.all()]
    vendor.departments = ",".join(departments)
```

### 2. `vendor_efficiency`

Classification basée sur `average_cost_per_user`.

```python
def calculate_vendor_efficiency(average_cost_per_user: float) -> str:
    """Calcule l'efficacité du vendor basée sur le coût moyen par utilisateur."""
    if average_cost_per_user is None:
        return "poor"

    if average_cost_per_user < 5:
        return "excellent"
    elif average_cost_per_user < 15:
        return "good"
    elif average_cost_per_user < 25:
        return "average"
    else:
        return "poor"
```

## Calcul de l'analyse (`vendor_insights`)

### 1. `most_expensive_vendor`

Identifie le vendor avec le coût total mensuel le plus élevé.

```python
most_expensive_vendor = max(
    vendors_data,
    key=lambda x: x.total_monthly_cost
).vendor
```

### 2. `most_efficient_vendor`

Identifie le vendor avec le plus bas `average_cost_per_user`. En cas d'égalité, ordre alphabétique. Exclut les vendors sans utilisateurs actifs.

```python
# Filtrer les vendors avec utilisateurs actifs
vendors_with_users = [
    vendor for vendor in vendors_data
    if vendor.total_users > 0
]

if vendors_with_users:
    most_efficient_vendor = min(
        vendors_with_users,
        key=lambda x: (x.average_cost_per_user, x.vendor)
    ).vendor
else:
    most_efficient_vendor = None
```

### 3. `single_tool_vendors`

Compte le nombre de vendors qui fournissent exactement 1 outil actif.

```sql
SELECT COUNT(*) AS single_tool_vendors
FROM (
    SELECT tools.vendor
    FROM tools
    WHERE tools.status = 'active'
        AND tools.vendor IS NOT NULL
    GROUP BY tools.vendor
    HAVING COUNT(DISTINCT tools.id) = 1
) AS single_vendors
```

```python
single_tool_vendors = sum(
    1 for vendor in vendors_data
    if vendor.tools_count == 1
)
```

## Cas particuliers à gérer

### 1. Vendors sans outils actifs

- Ces vendors ne doivent pas apparaître dans les résultats
- Le filtre `tools.status = 'active'` les exclut automatiquement

### 2. Vendors sans utilisateurs (`total_users = 0`)

- `average_cost_per_user` = `NULL`
- `vendor_efficiency` = "poor"
- Ces vendors sont exclus du calcul de `most_efficient_vendor`

### 3. Vendors avec `vendor IS NULL`

- Exclus des résultats avec le filtre `tools.vendor IS NOT NULL`

### 4. Concaténation des départements

- Départements uniques uniquement (pas de doublons)
- Ordre alphabétique : "Engineering,Marketing,Sales"
- Séparateur : virgule

### 5. Tri des résultats

- Trier par `total_monthly_cost DESC` par défaut (vendors les plus chers en premier)
- En cas d'égalité, trier par `vendor ASC`

## Références

- **Modèle Tool** : `app/models/tool.py`
- **Router Analytics** : `app/router/analytics.py`
- **Documentation similaire** : [`3_tools_by_category.md`](./3_tools_by_category.md)
