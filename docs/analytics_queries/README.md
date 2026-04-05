# Analytics endpoints — Query guide

This folder contains detailed analyses of the application’s analytics endpoints.

## Overview

| Endpoint                 | Purpose                                      | Main tables                    | Documentation                                                      | Impl |
| ------------------------ | -------------------------------------------- | ------------------------------ | ------------------------------------------------------------------ | ---- |
| **`/department-costs`**  | Costs by department                          | users, user_tool_access, tools | [`1_department_cost.md`](./1_department_cost.md)                   | ✅   |
| **`/expensive-tools`**   | Most expensive tools per user                | tools, user_tool_access, users | [`2_expensive_tools_analysis.md`](./2_expensive_tools_analysis.md) | ❌   |
| **`/tools-by-category`** | Breakdown by category                        | tools, categories              | [`3_tools_by_category.md`](./3_tools_by_category.md)               | ❌   |
| **`/low-usage-tools`**   | Underused tools                              | tools                          | [`4_low-usage-tools.md`](./4_low-usage-tools.md)                   | ❌   |
| **`/vendor-summary`**    | Vendor analysis                              | tools                          | [`5_vendor-summary.md`](./5_vendor-summary.md)                     | ❌   |

## Available endpoints

### 1. Department Costs

**Purpose**: Analyze how tool costs are distributed across departments.

**Examples**:

```
GET /api/analytics/department-costs
GET /api/analytics/department-costs?sort_by=department&order=asc
GET /api/analytics/department-costs?sort_by=total_cost&order=desc
```

**Sample response**:

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

**Tables involved**:

- `users`: Users and their department
- `user_tool_access`: Junction table (many-to-many)
- `tools`: Tools and their monthly cost

**📖 Detailed analysis**: See [`1_department_cost.md`](./1_department_cost.md)

### 2. Expensive Tools

**Purpose**: Identify the most expensive tools per user and analyze their efficiency.

**Examples**:

```
GET /api/analytics/expensive-tools?limit=10
GET /api/analytics/expensive-tools?min_cost=50&limit=5
```

**Response**:

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

**Tables involved**:

- `tools`: Tools with cost and user counts
- `user_tool_access` (optional): For dynamic active user counts
- `users` (optional): To verify user status

**📖 Detailed analysis**: See [`2_expensive_tools_analysis.md`](./2_expensive_tools_analysis.md)

### 3. Tool by Category

**Purpose**: Analyze tool and cost distribution by category.

**Examples**:

```
GET /api/analytics/tools-by-category
```

**Response**:

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

**Tables involved**:

- `tools`: Tools with cost, user count, and category
- `categories`: Tool categories

**📖 Detailed analysis**: See [`3_tools_by_category.md`](./3_tools_by_category.md)

### 4. Low Usage Tool

**Purpose**: Identify underused tools and savings opportunities.

**Examples**:

```
GET /api/analytics/low-usage-tools
GET /api/analytics/low-usage-tools?max_users=5
```

**Response**:

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

**Tables involved**:

- `tools`: Tools with cost and active user count

**📖 Detailed analysis**: See [`4_low-usage-tools.md`](./4_low-usage-tools.md)

### 5. Vendor Summary

**Purpose**: Analyze vendors and optimize vendor relationships.

**Examples**:

```
GET /api/analytics/vendor-summary
```

**Response**:

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

**Tables involved**:

- `tools`: Tools with vendor, cost, and departments

**📖 Detailed analysis**: See [`5_vendor-summary.md`](./5_vendor-summary.md)
