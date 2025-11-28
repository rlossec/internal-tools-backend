# Endpoints Analytics - Guide des Requêtes

Ce dossier contient les analyses détaillées des endpoints analytics de l'application.

## Vue d'ensemble

| Endpoint                 | Objectif                                | Tables principales             | Documentation                                                      | Impl |
| ------------------------ | --------------------------------------- | ------------------------------ | ------------------------------------------------------------------ | ---- |
| **`/department-costs`**  | Coûts par département                   | users, user_tool_access, tools | [`1_department_cost.md`](./1_department_cost.md)                   | ✅   |
| **`/expensive-tools`**   | Outils les plus coûteux par utilisateur | tools, user_tool_access, users | [`2_expensive_tools_analysis.md`](./2_expensive_tools_analysis.md) | ❌   |
| **`/tools-by-category`** | Répartition par catégories              | tools, categories              | [`3_tools_by_category.md`](./3_tools_by_category.md)               | ❌   |
| **`/low-usage-tools`**   | Outils sous-utilisés                    | tools                          | [`4_low-usage-tools.md`](./4_low-usage-tools.md)                   | ❌   |
| **`/vendor-summary`**    | Analyse fournisseurs                    | tools                          | [`5_vendor-summary.md`](./5_vendor-summary.md)                     | ❌   |

## Endpoints disponibles

### 1. Department Costs

**Objectif** : Analyser la répartition des coûts des outils par département.

**Exemples** :

```
GET /api/analytics/department-costs
GET /api/analytics/department-costs?sort_by=department&order=asc
GET /api/analytics/department-costs?sort_by=total_cost&order=desc
```

**Exemple de Réponse** :

```json
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

**Tables impliquées** :

- `users` : Utilisateurs avec leur département
- `user_tool_access` : Table de jonction (many-to-many)
- `tools` : Outils avec leur coût mensuel

**📖 Analyse détaillée** : Voir [`1_department_cost_queries.md`](./1_department_cost.md)

### 2. Expensive Tools

**Objectif** : Identifier les outils les plus coûteux par utilisateur et analyser leur efficacité.

**Exemples** :

```
GET /api/analytics/expensive-tools?limit=10
GET /api/analytics/expensive-tools?min_cost=50&limit=5
```

**Réponse** :

```json
{
  "data": [
    {
      "id": 15,
      "name": "Enterprise CRM",
      "monthly_cost": 199.99,
      "active_users_count": 12,
      "cost_per_user": 16.67,
      "department": "Sales",
      "vendor": "BigCorp",
      "efficiency_rating": "low"
    }
  ],
  "analysis": {
    "total_tools_analyzed": 18,
    "avg_cost_per_user_company": 12.45,
    "potential_savings_identified": 345.5
  }
}
```

**Tables impliquées** :

- `tools` : Outils avec leur coût et nombre d'utilisateurs
- `user_tool_access` (optionnel) : Pour calcul dynamique du nombre d'utilisateurs
- `users` (optionnel) : Pour vérifier le statut des utilisateurs

**📖 Analyse détaillée** : Voir [`2_expensive_tools_analysis.md`](./2_expensive_tools_analysis.md)

### 3. Tool by Category

**Objectif** : Analyser la répartition des outils et coûts par catégorie.

**Exemples** :

```
GET /api/analytics/tools-by-category
```

**Réponse** :

```json
{
  "data": [
    {
      "category_name": "Development",
      "tools_count": 8,
      "total_cost": 650.0,
      "total_users": 67,
      "percentage_of_budget": 26.5,
      "average_cost_per_user": 9.7
    },
    {
      "category_name": "Communication",
      "tools_count": 5,
      "total_cost": 240.5,
      "total_users": 89,
      "percentage_of_budget": 9.8,
      "average_cost_per_user": 2.7
    }
  ],
  "insights": {
    "most_expensive_category": "Development",
    "most_efficient_category": "Communication"
  }
}
```

**Tables impliquées** :

- `tools` : Outils avec leur coût, nombre d'utilisateurs et catégorie
- `categories` : Catégories d'outils

**📖 Analyse détaillée** : Voir [`3_tools_by_category.md`](./3_tools_by_category.md)

### 4. Low Usage Tool

**Objectif** : Identifier les outils sous-utilisés et les opportunités d'économies.

**Exemples** :

```
GET /api/analytics/low-usage-tools
GET /api/analytics/low-usage-tools?max_users=5
```

**Réponse** :

```json
{
  "data": [
    {
      "id": 23,
      "name": "Specialized Analytics",
      "monthly_cost": 89.99,
      "active_users_count": 2,
      "cost_per_user": 45.0,
      "department": "Marketing",
      "vendor": "SmallVendor",
      "warning_level": "high",
      "potential_action": "Consider canceling or downgrading"
    }
  ],
  "savings_analysis": {
    "total_underutilized_tools": 5,
    "potential_monthly_savings": 287.5,
    "potential_annual_savings": 3450.0
  }
}
```

**Tables impliquées** :

- `tools` : Outils avec leur coût et nombre d'utilisateurs actifs

**📖 Analyse détaillée** : Voir [`4_low-usage-tools.md`](./4_low-usage-tools.md)

### 5. Vendor Summary

**Objectif** : Analyser les fournisseurs et optimiser les relations vendors.

**Exemples** :

```
GET /api/analytics/vendor-summary
```

**Réponse** :

```json
{
  "data": [
    {
      "vendor": "Google",
      "tools_count": 4,
      "total_monthly_cost": 234.5,
      "total_users": 67,
      "departments": "Engineering,Sales,Marketing",
      "average_cost_per_user": 3.5,
      "vendor_efficiency": "excellent"
    }
  ],
  "vendor_insights": {
    "most_expensive_vendor": "BigCorp",
    "most_efficient_vendor": "Google",
    "single_tool_vendors": 8
  }
}
```

**Tables impliquées** :

- `tools` : Outils avec leur fournisseur, coût et départements

**📖 Analyse détaillée** : Voir [`5_vendor-summary.md`](./5_vendor-summary.md)
