# 2 Expensive Tools

`GET /api/analytics/expensive-tools`.

## Données nécessaires

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

## Approche d'implémentation

### Simplification : Aucune jointure nécessaire

Cet endpoint **n'utilise aucune jointure** car toutes les données nécessaires sont déjà présentes dans la table `tools` :

- `monthly_cost` : Coût mensuel de l'outil
- `active_users_count` : Nombre d'utilisateurs actifs
- `owner_department` : Département propriétaire
- `vendor` : Fournisseur

### Architecture

#### Repository (`ToolRepository`)

**Méthode réutilisée** :

- `list_tools(filters)` : Récupère les outils avec filtres, tri et pagination
  - Filtre par `min_cost` si fourni
  - Tri par `monthly_cost` en ordre décroissant
  - Limite le nombre de résultats si `limit` est fourni

**Nouvelle méthode** :

- `get_company_cost_statistics()` : Calcule les statistiques globales
  - Retourne `(total_monthly_cost, total_active_users)` pour tous les outils avec `active_users_count > 0`
  - Utilise `func.sum()` de SQLAlchemy pour une requête efficace
  - Exclut automatiquement les outils à 0 utilisateurs

#### Service (`ToolService`)

**Méthode principale** : `get_expensive_tools(min_cost, limit)`

**Logique métier** :

1. **Récupération des outils** :
   - Utilise `list_tools()` avec filtres appropriés (min_cost, tri DESC par monthly_cost, limit)
   - Récupère également tous les outils (sans limit) pour l'analyse complète

2. **Calcul des statistiques globales** :
   - Appelle `get_company_cost_statistics()` pour obtenir les totaux
   - Calcule `avg_cost_per_user_company` = `total_monthly_cost / total_active_users`
   - Gestion de la division par zéro

3. **Calcul par outil** :
   - `cost_per_user` = `monthly_cost / active_users_count` (gestion division par zéro)
   - `efficiency_rating` basé sur la comparaison avec `avg_cost_per_user_company` :
     - **"excellent"** : < 50% de la moyenne
     - **"good"** : 50%-80% de la moyenne
     - **"average"** : 80%-120% de la moyenne
     - **"low"** : > 120% de la moyenne

4. **Calcul des économies potentielles** :
   - Parcourt **tous les outils** (pas seulement ceux limités)
   - Somme les `monthly_cost` des outils avec `efficiency_rating = "low"`

### Table utilisée

- **`tools`** : Table principale contenant toutes les données nécessaires
  - Pas besoin de jointure avec `categories` (déjà fait dans `list_tools()` si nécessaire)
  - Pas besoin de `cost_tracking` (les données sont dans `tools`)
