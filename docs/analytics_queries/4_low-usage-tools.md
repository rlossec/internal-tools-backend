# Analyse de l'endpoint `/api/analytics/low-usage-tools`

Ce document analyse les jointures et requêtes nécessaires pour implémenter l'endpoint `GET /api/analytics/low-usage-tools`.

## Analyse des données nécessaires

### Champs de la réponse `data`

| Champ                | Source                     | Type                  | Calcul                              |
| -------------------- | -------------------------- | --------------------- | ----------------------------------- |
| `id`                 | `tools.id`                 | Integer               | Direct                              |
| `name`               | `tools.name`               | String                | Direct                              |
| `monthly_cost`       | `tools.monthly_cost`       | Decimal               | Direct                              |
| `active_users_count` | `tools.active_users_count` | Integer               | Direct                              |
| `cost_per_user`      | Calculé                    | Decimal               | `monthly_cost / active_users_count` |
| `department`         | `tools.owner_department`   | Enum (DepartmentType) | Direct                              |
| `vendor`             | `tools.vendor`             | String                | Direct                              |
| `warning_level`      | Calculé                    | String                | Basé sur `cost_per_user`            |
| `potential_action`   | Calculé                    | String                | Basé sur `warning_level`            |

### Champs de la réponse `savings_analysis`

| Champ                       | Calcul                                                  | Description                              |
| --------------------------- | ------------------------------------------------------- | ---------------------------------------- |
| `total_underutilized_tools` | COUNT des outils avec `active_users_count <= max_users` | Nombre d'outils sous-utilisés identifiés |
| `potential_monthly_savings` | SUM(`monthly_cost`) des outils "high" + "medium"        | Économies potentielles mensuelles        |
| `potential_annual_savings`  | `potential_monthly_savings * 12`                        | Économies potentielles annuelles         |

## Jointures nécessaires

### Modèles de données impliqués

Les requêtes utilisent uniquement la table :

- **`tools`** : Outils disponibles avec leur coût mensuel et nombre d'utilisateurs actifs

### Requête principale : `get_low_usage_tools()`

#### Objectif

Identifier les outils avec un nombre d'utilisateurs actifs inférieur ou égal au seuil (`max_users`, défaut: 5) et calculer leur niveau d'alerte et les actions recommandées.

#### Jointures utilisées

**Aucune jointure nécessaire** - Cette requête utilise uniquement la table `tools`.

#### Requête SQL équivalente

```sql
SELECT
    tools.id,
    tools.name,
    tools.monthly_cost,
    tools.active_users_count,
    CASE
        WHEN tools.active_users_count > 0
        THEN tools.monthly_cost / tools.active_users_count
        ELSE NULL
    END AS cost_per_user,
    tools.owner_department AS department,
    tools.vendor
FROM
    tools
WHERE
    tools.status = 'active'
    AND tools.active_users_count <= :max_users
ORDER BY
    cost_per_user DESC NULLS LAST,
    tools.monthly_cost DESC
```

#### Code Python

```python
max_users = max_users or 5  # Défaut: 5

query = (
    db.query(
        Tool.id,
        Tool.name,
        Tool.monthly_cost,
        Tool.active_users_count,
        case(
            (Tool.active_users_count > 0,
             Tool.monthly_cost / Tool.active_users_count),
            else_=None
        ).label('cost_per_user'),
        Tool.owner_department.label('department'),
        Tool.vendor
    )
    .filter(Tool.status == ToolStatus.active)
    .filter(Tool.active_users_count <= max_users)
    .order_by(
        func.coalesce(
            case(
                (Tool.active_users_count > 0,
                 Tool.monthly_cost / Tool.active_users_count),
                else_=None
            ),
            0
        ).desc(),
        Tool.monthly_cost.desc()
    )
)

low_usage_tools = query.all()
```

## Calcul de `warning_level` et `potential_action`

### Logique de calcul

```python
def calculate_warning_level(cost_per_user: float, active_users_count: int) -> str:
    """Calcule le niveau d'alerte basé sur le coût par utilisateur."""
    if active_users_count == 0:
        return "high"

    if cost_per_user is None:
        return "high"

    if cost_per_user < 20:
        return "low"
    elif cost_per_user <= 50:
        return "medium"
    else:
        return "high"

def get_potential_action(warning_level: str) -> str:
    """Retourne l'action recommandée selon le niveau d'alerte."""
    actions = {
        "high": "Consider canceling or downgrading",
        "medium": "Review usage and consider optimization",
        "low": "Monitor usage trends"
    }
    return actions.get(warning_level, "Monitor usage trends")
```

## Calcul de l'analyse (`savings_analysis`)

### 1. `total_underutilized_tools`

Compte le nombre d'outils avec `active_users_count <= max_users`.

```sql
SELECT COUNT(*) AS total_underutilized_tools
FROM tools
WHERE
    tools.status = 'active'
    AND tools.active_users_count <= :max_users
```

### 2. `potential_monthly_savings`

Somme des `monthly_cost` des outils avec `warning_level` = "high" ou "medium".

```python
potential_monthly_savings = sum(
    tool.monthly_cost
    for tool in low_usage_tools
    if tool.warning_level in ["high", "medium"]
)
```

### 3. `potential_annual_savings`

Calcul : `potential_monthly_savings * 12`

```python
potential_annual_savings = potential_monthly_savings * 12
```

## Cas particuliers à gérer

### 1. Outils sans utilisateurs (`active_users_count = 0`)

- Toujours inclus dans les résultats (même si `max_users = 0`)
- `cost_per_user` = `NULL`
- `warning_level` = "high" automatiquement
- `potential_action` = "Consider canceling or downgrading"

### 2. Paramètre `max_users` non fourni

- Valeur par défaut : 5 utilisateurs
- Les outils avec 0 utilisateurs sont toujours inclus

### 3. Tri des résultats

- Trier par `cost_per_user DESC` (outils les plus chers par utilisateur en premier)
- En cas d'égalité, trier par `monthly_cost DESC`
- Gérer les valeurs `NULL` (les placer en dernier)

### 4. Calcul des économies

- Seuls les outils avec `warning_level` = "high" ou "medium" contribuent aux économies
- Les outils avec `warning_level` = "low" ne sont pas comptés dans les économies potentielles

## Références

- **Modèle Tool** : `app/models/tool.py`
- **Router Analytics** : `app/router/analytics.py`
- **Documentation similaire** : [`2_expensive_tools_analysis.md`](./2_expensive_tools_analysis.md)
