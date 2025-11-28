# Department Cost

Ce document analyse les jointures et requêtes nécessaires pour implémenter l'endpoint `GET /api/analytics/department-costs`.

## Données nécessaires

```bash
{
  "data": [
    {
      "department": "Engineering",
      "total_cost": 890.5,
      "tools_count": 12,
      "total_users": 45,
      "average_cost_per_tool": 74.21,
      "cost_percentage": 36.2
    },
    {
      "department": "Sales",
      "total_cost": 456.75,
      "tools_count": 6,
      "total_users": 18,
      "average_cost_per_tool": 76.13,
      "cost_percentage": 18.6
    }
  ],
  "summary": {
    "total_company_cost": 2450.8,
    "departments_count": 6,
    "most_expensive_department": "Engineering"
  }
}
```

## Jointures nécessaires

### Modèles de données impliqués

Les requêtes utilisent les relations entre ces tables :

- **`tools`** : Outils disponibles avec leur département propriétaire (`owner_department`)
- **`cost_tracking`** : Table de suivi des coûts mensuels par outil, contenant `total_monthly_cost` et `active_users_count`

### Choix de conception : `User.department` vs `Tool.owner_department`

**Décision : Utiliser `Tool.owner_department` avec `CostTracking`**

#### Modèle de coût : Utilisation de `CostTracking`

**Important** : Nous utilisons `CostTracking.total_monthly_cost` qui représente le **coût total mensuel pour l'entreprise** pour un outil donné.

- **`Tool.monthly_cost`** : Coût mensuel unitaire par utilisateur de l'outil (ex: Slack à 8€/utilisateur/mois)
- **`CostTracking.total_monthly_cost`** : Coût mensuel total pour l'entreprise = `monthly_cost × active_users_count`
- **`CostTracking.active_users_count`** : Nombre total d'utilisateurs actifs (déjà calculé dans `CostTracking`)

#### Exemple illustratif

Un outil "Slack Pro" :

- Coût unitaire : **8€/utilisateur/mois**
- 8 utilisateurs actifs au total
- **Coût total entreprise** : 8 × 8€ = 64€ (stocké dans `CostTracking.total_monthly_cost`)
- Propriétaire : Département **Engineering** (`Tool.owner_department`)

→ Engineering compte **64€** dans son `total_cost` pour Slack.

#### Jointures utilisées

1. **`users` → `user_tool_access` (INNER JOIN sur `users.id = user_tool_access.user_id`)** : Lie chaque utilisateur à ses accès aux outils

2. **`user_tool_access` → `tools` (INNER JOIN sur `user_tool_access.tool_id = tools.id`)** : Lie chaque accès à l'outil correspondant pour accéder au `monthly_cost`
