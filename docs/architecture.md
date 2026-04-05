# Architecture de l'application

Ce document décrit l'architecture de l'application, son organisation en modules et les interactions entre les différentes couches.

## Vue d'ensemble

L'application suit une **architecture en couches (Layered Architecture)** avec une séparation claire des responsabilités :

```
┌─────────────────────────────────────┐
│         Router (API Layer)          │  ← Endpoints HTTP / Validation
├─────────────────────────────────────┤
│         Services (Business)         │  ← Logique métier / Calculs
├─────────────────────────────────────┤
│      Repositories (Data Access)     │  ← Requêtes SQL / Filtres
├─────────────────────────────────────┤
│         Models (Database)           │  ← Modèles SQLAlchemy / Relations
└─────────────────────────────────────┘
```

### Principe de flux unidirectionnel

Les données circulent toujours dans le même sens :

- **Entrée** : HTTP Request → Router → Service → Repository → Database
- **Sortie** : Database → Repository → Service → Router → HTTP Response

Chaque couche ne communique qu'avec ses couches adjacentes, garantissant une séparation claire des responsabilités.

## Arborescence de l'application

```
test-backend-2/
├── app/                              # Application principale
│   ├── main.py                       # Point d'entrée FastAPI
│   │
│   ├── core/                         # Configuration et infrastructure
│   │   ├── config.py                 # Configuration (variables d'environnement)
│   │   └── logging.py                # Configuration du logging
│   │
│   ├── db/                           # Configuration base de données
│   │   └── database.py               # Engine SQLAlchemy, SessionLocal, Base
│   │
│   ├── models/                       # Modèles SQLAlchemy (ORM)
│   │   ├── __init__.py
│   │   ├── enum_types.py             # Types énumérés (DepartmentType, ToolStatus, etc.)
│   │   ├── tool.py                   # Modèle Tool
│   │   ├── category.py               # Modèle Category
│   │   ├── user.py                   # Modèle User
│   │   ├── usage_log.py              # Modèle UsageLog
│   │   ├── user_tool_access.py       # Modèle UserToolAccess
│   │   ├── access_request.py         # Modèle AccessRequest
│   │   └── cost_tracking.py          # Modèle CostTracking
│   │
│   ├── schemas/                      # Schémas Pydantic (validation)
│   │   ├── __init__.py
│   │   ├── common.py                 # Schémas communs (SortOrder, etc.)
│   │   ├── tool.py                    # Schémas pour les outils (Request/Response)
│   │   └── analytics.py              # Schémas pour les analytics
│   │
│   ├── repositories/                 # Couche d'accès aux données
│   │   ├── __init__.py
│   │   ├── tool_repository.py        # Repository pour les outils
│   │   └── analytics_repository.py   # Repository pour les analytics
│   │
│   ├── services/                     # Couche logique métier
│   │   ├── __init__.py
│   │   ├── tool_service.py           # Service pour les outils
│   │   └── analytics_service.py      # Service pour les analytics
│   │
│   └── router/                       # Couche API (endpoints)
│       ├── dependencies.py          # Dépendances FastAPI (DI)
│       ├── tool.py                   # Routes pour /tools
│       └── analytics.py              # Routes pour /analytics
│
├── tests/                            # Tests
│   ├── conftest.py                   # Fixtures partagées
│   ├── router/                       # Tests des endpoints
│   │   ├── tool/                     # Tests pour /tools
│   │   └── test_database_errors.py   # Tests erreurs DB
│   └── README.md                     # Documentation des tests
│
└── docs/                             # Documentation
    ├── architecture.md               # Ce fichier
    ├── erd.md                        # Modèle de données
    ├── erd.mermaid                   # Diagramme ERD
    └── analytics_queries.md          # Documentation des requêtes analytics
```

## Architecture en couches

### 1. Couche Router (API Layer)

**Localisation :** `app/router/`

**Responsabilités :**

- Définition des endpoints HTTP (GET, POST, PUT, DELETE)
- Validation des requêtes via Pydantic
- Gestion des dépendances FastAPI (Injection de dépendances)
- Transformation des réponses en JSON

**Fichiers :**

- `app/router/tool.py` : Définit les endpoints `/tools`
- `app/router/dependencies.py` : Définit les dépendances FastAPI (`get_tool_service`, `get_tool_repository`, `get_tool_filters`)

**Flux de données :**

```
Requête HTTP → Router → Service → Repository → Database
```

**Exemple :**

```python
@router.get("/tools")
async def get_tools(
    tool_service: ToolService = Depends(get_tool_service),
    filters: ToolFilters = Depends(get_tool_filters),
):
    return tool_service.list_tools(filters)
```

### 2. Couche Services (Business Logic Layer)

**Localisation :** `app/services/`

**Responsabilités :**

- Logique métier de l'application
- Orchestration des opérations complexes
- Calculs et transformations de données
- Gestion des erreurs métier (HTTPException)
- Validation des règles métier

**Fichiers :**

- `app/services/tool_service.py` : Service pour les outils

**Méthodes principales :**

- `list_tools()` : Liste les outils avec filtres, tri et pagination
- `get_tool()` : Récupère un outil avec ses métriques
- `create_tool()` : Crée un nouvel outil
- `update_tool()` : Met à jour un outil existant
- `get_tool_usage_metrics_last_days()` : Calcule les métriques d'utilisation
- `get_tool_total_monthly_cost()` : Calcule le coût total mensuel

**Dépendances :**

- Utilise `ToolRepository` pour accéder aux données
- Utilise les schémas Pydantic pour la validation

**Exemple :**

```python
class ToolService:
    def __init__(self, tool_repository: ToolRepository):
        self._repository = tool_repository

    def get_tool(self, tool_id: int) -> ToolDetailResponse:
        tool_model = self._repository.get_tool(tool_id)
        if not tool_model:
            raise HTTPException(status_code=404, detail="...")
        # Calculs métier...
        return ToolDetailResponse(...)
```

### 3. Couche Repositories (Data Access Layer)

**Localisation :** `app/repositories/`

**Responsabilités :**

- Accès direct à la base de données via SQLAlchemy
- Requêtes SQL complexes
- Filtrage, tri, pagination au niveau base de données
- Isolation de la logique d'accès aux données

**Fichiers :**

- `app/repositories/tool_repository.py` : Repository pour les outils

**Méthodes principales :**

- `list_tools()` : Requête avec filtres, tri et pagination
- `get_tool()` : Récupération par ID
- `create_tool()` : Création d'un outil
- `update_tool()` : Mise à jour d'un outil
- `count_all()` : Compte total
- `count_filtered()` : Compte avec filtres

**Dépendances :**

- Utilise `Session` SQLAlchemy pour les requêtes
- Utilise les modèles SQLAlchemy (`Tool`, `Category`, etc.)

**Exemple :**

```python
class ToolRepository:
    def __init__(self, session: Session):
        self._db = session

    def list_tools(self, filters: ToolFilters) -> List[ToolModel]:
        query = self._db.query(ToolModel).join(Category)
        query = self._apply_filters(query, filters)
        return query.all()
```

### 4. Couche Models (Database Layer)

**Localisation :** `app/models/`

**Responsabilités :**

- Définition des modèles SQLAlchemy (ORM)
- Relations entre entités
- Contraintes de base de données
- Types énumérés

**Fichiers :**

- `app/models/tool.py` : Modèle Tool
- `app/models/category.py` : Modèle Category
- `app/models/enum_types.py` : Types énumérés (DepartmentType, ToolStatus, etc.)

**Relations principales :**

- `Tool` ↔ `Category` (Many-to-One)
- `Tool` ↔ `UsageLog` (One-to-Many)
- `User` ↔ `UsageLog` (One-to-Many)
- `User` ↔ `UserToolAccess` (One-to-Many)

**Exemple :**

```python
class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="tools")
    usages = relationship("UsageLog", back_populates="tool")
```

### 5. Couche Schemas (Validation Layer)

**Localisation :** `app/schemas/`

**Responsabilités :**

- Validation des données d'entrée (Request)
- Sérialisation des données de sortie (Response)
- Transformation des données entre couches
- Validation des règles métier (field_validator)

**Fichiers :**

- `app/schemas/tool.py` : Schémas pour les outils
- `app/schemas/common.py` : Schémas communs

**Types de schémas :**

- **Request** : `ToolCreateRequest`, `ToolUpdateRequest`, `ToolFilters`
- **Response** : `ToolCreateResponse`, `ToolUpdateResponse`, `ToolDetailResponse`, `ToolsListResponse`
- **Common** : `SortOrder`, `SortToolField`, `PaginationInfo`

**Exemple :**

```python
class ToolCreateRequest(BaseModel):
    name: str
    vendor: str
    category_id: int
    monthly_cost: float
    owner_department: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Name is required and must be 2-100 characters")
        return v
```

### 6. Couche Core (Infrastructure)

**Localisation :** `app/core/`

**Responsabilités :**

- Configuration globale de l'application
- Gestion des exceptions globales
- Configuration du logging
- Variables d'environnement

**Fichiers :**

- `app/core/config.py` : Configuration (BaseSettings)
- `app/core/exceptions.py` : Gestionnaires d'exceptions
- `app/core/logging.py` : Configuration du logging

**Gestionnaires d'exceptions :**

- `validation_exception_handler` : Erreurs de validation (400)
- `pydantic_validation_exception_handler` : Erreurs Pydantic (400)
- `http_exception_handler` : Erreurs HTTP (404, etc.)
- `database_exception_handler` : Erreurs de base de données (500)

### 7. Couche Database (Configuration)

**Localisation :** `app/db/`

**Responsabilités :**

- Configuration de SQLAlchemy
- Création de l'engine et des sessions
- Définition de la classe Base pour les modèles

**Fichiers :**

- `app/db/database.py` : Configuration SQLAlchemy

## Diagrammes d'interaction

### Diagramme de séquence - GET /tools

```
Client          Router          Service         Repository      Database
  │               │               │                │              │
  │─ GET /tools ─>│               │                │              │
  │               │               │                │              │
  │               │─ list_tools() │                │              │
  │               │<──────────────│                │              │
  │               │               │                │              │
  │               │               │── list_tools() │              │
  │               │               │<───────────────│              │
  │               │               │                │              │
  │               │               │                │── SELECT ───>│
  │               │               │                │<── Results ──│
  │               │               │                │              │
  │               │               │<── List[Tool] ─│              │
  │               │               │                │              │
  │               │<── Response ──│                │              │
  │<── JSON ──────│               │                │              │
```

### Diagramme de séquence - POST /tools

```
Client          Router          Service         Repository      Database
  │               │               │                │              │
  │── POST /tools │               │                │              │
  │   {data} ────>│               │                │              │
  │               │               │                │              │
  │               │─ create_tool()│                │              │
  │               │<──────────────│                │              │
  │               │               │                │              │
  │               │               │── create_tool()│              │
  │               │               │<───────────────│              │
  │               │               │                │              │
  │               │               │                │── INSERT ───>│
  │               │               │                │<── Tool ─────│
  │               │               │                │              │
  │               │               │<── ToolModel ──│              │
  │               │               │                │              │
  │               │<── Response ──│                │              │
  │<── JSON ──────│               │                │              │
```

## Flux de données

### Flux de lecture (GET)

```
1. Client HTTP
   ↓
2. Router (app/router/tool.py)
   - Reçoit la requête HTTP
   - Valide les paramètres via Pydantic (ToolFilters)
   - Injecte les dépendances (ToolService)
   ↓
3. Service (app/services/tool_service.py)
   - Applique la logique métier
   - Calcule les métriques (usage, coût)
   - Gère les erreurs métier
   ↓
4. Repository (app/repositories/tool_repository.py)
   - Construit la requête SQLAlchemy
   - Applique filtres, tri, pagination
   - Exécute la requête
   ↓
5. Models (app/models/tool.py)
   - SQLAlchemy ORM mappe les résultats
   ↓
6. Repository retourne List[ToolModel]
   ↓
7. Service transforme en List[Tool] (Pydantic)
   ↓
8. Service retourne ToolsListResponse
   ↓
9. Router sérialise en JSON
   ↓
10. Client HTTP reçoit la réponse
```

### Flux d'écriture (POST/PUT)

```
1. Client HTTP envoie JSON
   ↓
2. Router (app/router/tool.py)
   - Valide le JSON via Pydantic (ToolCreateRequest/ToolUpdateRequest)
   - Injecte ToolService
   ↓
3. Service (app/services/tool_service.py)
   - Valide les règles métier
   - Convertit les enums (DepartmentType, ToolStatus)
   - Gère les erreurs (catégorie inexistante, etc.)
   ↓
4. Repository (app/repositories/tool_repository.py)
   - Crée/met à jour l'entité
   - Commit la transaction
   ↓
5. Database
   - Persiste les données
   ↓
6. Repository retourne ToolModel
   ↓
7. Service transforme en ToolCreateResponse/ToolUpdateResponse
   ↓
8. Router sérialise en JSON
   ↓
9. Client HTTP reçoit la réponse (201/200)
```

## Injection de dépendances (FastAPI)

L'application utilise le système d'injection de dépendances de FastAPI pour gérer les dépendances entre les couches :

```python
# app/router/dependencies.py
def get_tool_repository():
    db = SessionLocal()
    try:
        yield ToolRepository(session=db)
    finally:
        db.close()

def get_tool_service(tool_repository: ToolRepository = Depends(get_tool_repository)):
    yield ToolService(tool_repository=tool_repository)

# app/router/tool.py
@router.get("/tools")
async def get_tools(
    tool_service: ToolService = Depends(get_tool_service),
    filters: ToolFilters = Depends(get_tool_filters),
):
    return tool_service.list_tools(filters)
```

**Chaîne de dépendances :**

```
Router → Service → Repository → Database Session
```

## Gestion des erreurs

### Hiérarchie des exceptions

```
DatabaseError (SQLAlchemy)
    ↓
Repository → Laisse remonter
    ↓
Service → Lève HTTPException (404, etc.)
    ↓
Router → Laisse remonter
    ↓
Exception Handlers (app/core/exceptions.py)
    ↓
Réponse JSON formatée
```

### Formats d'erreur standardisés

- **400 Bad Request** : `{"error": "Validation failed", "details": {...}}`
- **404 Not Found** : `{"error": "Tool not found", "message": "..."}`
- **500 Internal Server Error** : `{"error": "Internal server error", "message": "Database connection failed"}`

## Articulations entre modules

### Dépendances entre modules

```
app/main.py
    ├── app/core/config.py          (Configuration)
    ├── app/core/exceptions.py      (Gestionnaires d'erreurs)
    └── app/router/tool.py          (Endpoints)

app/router/tool.py
    ├── app/router/dependencies.py  (Injection de dépendances)
    ├── app/services/tool_service.py
    └── app/schemas/tool.py         (Validation Request/Response)

app/services/tool_service.py
    ├── app/repositories/tool_repository.py
    ├── app/schemas/tool.py         (Transformation de données)
    └── app/models/enum_types.py    (Types énumérés)

app/repositories/tool_repository.py
    ├── app/models/tool.py          (Modèles SQLAlchemy)
    ├── app/models/category.py
    ├── app/models/usage_log.py
    └── app/schemas/tool.py         (Filtres)

app/models/*.py
    └── app/db/database.py          (Base SQLAlchemy)
```

### Matrice de dépendances

| Module         | Dépend de                                      |
| -------------- | ---------------------------------------------- |
| `router`       | `services`, `schemas`, `router.dependencies`   |
| `services`     | `repositories`, `schemas`, `models.enum_types` |
| `repositories` | `models`, `schemas` (pour les filtres)         |
| `models`       | `db.database`, `models.enum_types`             |
| `schemas`      | `models.enum_types`                            |
| `core`         | Aucune dépendance interne                      |
| `db`           | `core.config`                                  |

### Isolation des couches

Chaque couche est isolée et peut être testée indépendamment :

- **Router** : Testé avec `TestClient` (FastAPI)
- **Service** : Testé avec des mocks de Repository
- **Repository** : Testé avec une base de données de test (SQLite)
- **Models** : Testés via les fixtures de test

## Principes d'architecture

### 1. Séparation des responsabilités

Chaque couche a une responsabilité unique et bien définie :

- **Router** : Gestion HTTP uniquement
- **Service** : Logique métier uniquement
- **Repository** : Accès aux données uniquement
- **Models** : Structure des données uniquement

### 2. Inversion de dépendances

Les couches supérieures dépendent des abstractions des couches inférieures :

- Router dépend de Service (interface)
- Service dépend de Repository (interface)
- Repository dépend de Models (concrets)

### 3. Single Responsibility Principle

Chaque module/classe a une seule responsabilité :

- `ToolService` : Gestion des outils uniquement
- `ToolRepository` : Accès aux données des outils uniquement
- `Tool` : Représentation d'un outil uniquement

### 4. DRY (Don't Repeat Yourself)

- Validation centralisée dans les schémas Pydantic
- Gestion d'erreurs centralisée dans `app/core/exceptions.py`
- Fixtures partagées dans `tests/conftest.py`

## Extensibilité

### Ajouter un nouvel endpoint

1. **Router** : Ajouter la route dans `app/router/tool.py`
2. **Service** : Ajouter la méthode dans `app/services/tool_service.py`
3. **Repository** : Ajouter la méthode dans `app/repositories/tool_repository.py` (si nécessaire)
4. **Schemas** : Ajouter les schémas Request/Response dans `app/schemas/tool.py`

### Ajouter une nouvelle entité

1. **Models** : Créer le modèle dans `app/models/`
2. **Schemas** : Créer les schémas dans `app/schemas/`
3. **Repository** : Créer le repository dans `app/repositories/`
4. **Service** : Créer le service dans `app/services/`
5. **Router** : Créer le router dans `app/router/`
6. **Main** : Inclure le router dans `app/main.py`

## Technologies utilisées

- **FastAPI** : Framework web asynchrone
- **SQLAlchemy** : ORM pour la base de données
- **Pydantic** : Validation et sérialisation de données
- **PostgreSQL** : Base de données relationnelle
- **Pytest** : Framework de tests

## Structure des imports

### Exports principaux

**app/models/**init**.py** :

```python
from .tool import Tool
from .category import Category
from .user import User
# ...
```

**app/schemas/**init**.py** :

```python
from .tool import (
    Tool, ToolFilters, ToolsListResponse, ToolDetailResponse,
    ToolCreateRequest, ToolCreateResponse,
    ToolUpdateRequest, ToolUpdateResponse
)
from .common import SortOrder, SortToolField
```

**app/services/**init**.py** :

```python
from .tool_service import ToolService
```

**app/repositories/**init**.py** :

```python
from .tool_repository import ToolRepository
```

### Chaîne d'imports typique

```python
# Router
from app.services import ToolService          # Service
from app.schemas import ToolCreateRequest     # Schema

# Service
from app.repositories import ToolRepository   # Repository
from app.schemas import Tool, ToolCreateRequest  # Schemas

# Repository
from app.models import Tool as ToolModel      # Model
from app.schemas import ToolFilters           # Schema (pour filtres)
```

## Points d'attention

### Gestion des sessions de base de données

Les sessions sont créées et fermées automatiquement via les dépendances FastAPI :

- Création : `get_tool_repository()` crée une session
- Fermeture : `finally` garantit la fermeture même en cas d'erreur

### Validation à deux niveaux

1. **Pydantic** : Validation des types et formats (400)
2. **Service** : Validation des règles métier (404, etc.)

### Transactions

Les transactions sont gérées automatiquement par SQLAlchemy :

- `commit()` : Valide la transaction
- En cas d'exception : Rollback automatique
