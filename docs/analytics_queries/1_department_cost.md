# Department Cost

This document analyzes the joins and queries required to implement the `GET /api/analytics/department-costs` endpoint.

## Required data

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

## Required joins

### Data models involved

Queries use relationships between these tables:

- **`tools`**: Available tools with their owning department (`owner_department`)
- **`cost_tracking`**: Monthly cost tracking per tool, containing `total_monthly_cost` and `active_users_count`

### Design choice: `User.department` vs `Tool.owner_department`

**Decision: Use `Tool.owner_department` with `CostTracking`**

#### Cost model: using `CostTracking`

**Important**: We use `CostTracking.total_monthly_cost`, which represents the **total monthly cost to the company** for a given tool.

- **`Tool.monthly_cost`**: Per-user monthly cost for the tool (e.g. Slack at €8/user/month)
- **`CostTracking.total_monthly_cost`**: Total monthly cost to the company = `monthly_cost × active_users_count`
- **`CostTracking.active_users_count`**: Total active users (already stored in `CostTracking`)

#### Illustrative example

A "Slack Pro" tool:

- Unit cost: **€8/user/month**
- 8 active users in total
- **Total company cost**: 8 × €8 = €64 (stored in `CostTracking.total_monthly_cost`)
- Owner: **Engineering** department (`Tool.owner_department`)

→ Engineering counts **€64** toward its `total_cost` for Slack.

#### Joins used

1. **`users` → `user_tool_access` (INNER JOIN on `users.id = user_tool_access.user_id`)**: Links each user to their tool access records

2. **`user_tool_access` → `tools` (INNER JOIN on `user_tool_access.tool_id = tools.id`)**: Links each access row to the corresponding tool to read `monthly_cost`
