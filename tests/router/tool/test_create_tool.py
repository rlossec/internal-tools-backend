"""Tests pour l'endpoint POST /tools."""
import pytest


class TestCreateToolEndpoint:

    # 201 - Succès
    def test_create_tool_success(self, client):
        """Test création réussie d'un outil avec données valides."""
        tool_data = {
            "name": "Linear",
            "description": "Issue tracking and project management",
            "vendor": "Linear",
            "website_url": "https://linear.app",
            "category_id": 1,  # Development
            "monthly_cost": 8.00,
            "owner_department": "Engineering"
        }
        
        response = client.post("/tools", json=tool_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Vérifier la structure de la réponse
        assert "id" in data
        assert data["name"] == "Linear"
        assert data["description"] == "Issue tracking and project management"
        assert data["vendor"] == "Linear"
        assert data["website_url"] == "https://linear.app"
        assert data["category"] == "Development"
        assert data["monthly_cost"] == 8.0
        assert data["owner_department"] == "Engineering"
        assert data["status"] == "active"  # Par défaut
        assert data["active_users_count"] == 0  # Par défaut pour un nouvel outil
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_tool_with_status(self, client):
        """Test création - le statut est toujours 'active' par défaut."""
        tool_data = {
            "name": "New Tool",
            "description": "Test tool",
            "vendor": "Test Vendor",
            "category_id": 1,
            "monthly_cost": 10.0,
            "owner_department": "Engineering"
        }
        
        response = client.post("/tools", json=tool_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "active"  # Toujours 'active' par défaut
    
    def test_create_tool_minimal_data(self, client):
        """Test création avec données minimales (champs optionnels omis)."""
        tool_data = {
            "name": "Minimal Tool",
            "vendor": "Minimal Vendor",
            "category_id": 1,
            "monthly_cost": 5.0,
            "owner_department": "Engineering"
        }
        
        response = client.post("/tools", json=tool_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Tool"
        assert data["vendor"] == "Minimal Vendor"
        assert data["description"] is None or data["description"] == ""
        assert data["website_url"] is None or data["website_url"] == ""
        assert data["status"] == "active"  # Par défaut
    
    @pytest.mark.parametrize("department", [
        "Engineering",
        "Sales",
        "Marketing",
        "HR",
        "Finance",
        "Operations",
        "Design",
    ])
    def test_create_tool_different_departments(self, client, department):
        """Test création avec différents départements."""
        tool_data = {
            "name": f"Tool for {department}",
            "vendor": "Test Vendor",
            "category_id": 1,
            "monthly_cost": 10.0,
            "owner_department": department
        }
        
        response = client.post("/tools", json=tool_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["owner_department"] == department
    
    def test_create_tool_status_always_active(self, client):
        """Test que le statut est toujours 'active' lors de la création."""
        tool_data = {
            "name": "New Tool",
            "vendor": "Test Vendor",
            "category_id": 1,
            "monthly_cost": 10.0,
            "owner_department": "Engineering"
        }
        
        response = client.post("/tools", json=tool_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "active"  # Toujours 'active' par défaut
    
    def test_create_tool_zero_cost(self, client):
        """Test création avec un coût de 0 (gratuit)."""
        tool_data = {
            "name": "Free Tool",
            "vendor": "Free Vendor",
            "category_id": 1,
            "monthly_cost": 0.0,
            "owner_department": "Engineering"
        }
        
        response = client.post("/tools", json=tool_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["monthly_cost"] == 0.0
    
    # 422 - Validation errors
    @pytest.mark.parametrize("field, invalid_value, error_keyword", [
        ("name", None, "name"),
        ("vendor", None, "vendor"),
        ("category_id", None, "category_id"),
        ("monthly_cost", None, "monthly_cost"),
        ("owner_department", None, "owner_department"),
        ("monthly_cost", -10.0, "supérieur ou égal à 0"),
        ("owner_department", "InvalidDepartment", "owner_department"),
    ])
    def test_create_tool_validation_errors(self, client, field, invalid_value, error_keyword):
        """Test des erreurs de validation."""
        tool_data = {
            "name": "Test Tool",
            "vendor": "Test Vendor",
            "category_id": 1,
            "monthly_cost": 10.0,
            "owner_department": "Engineering"
        }
        
        if invalid_value is None:
            tool_data.pop(field)
        else:
            tool_data[field] = invalid_value
        
        response = client.post("/tools", json=tool_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"] == "Validation failed"
        assert "details" in data
        # Vérifier que le champ en erreur est dans les details
        assert field in data["details"] or error_keyword.lower() in str(data["details"]).lower()
    
    # 404 - Category not found
    def test_create_tool_invalid_category(self, client):
        """Test avec une catégorie inexistante."""
        tool_data = {
            "name": "Test Tool",
            "vendor": "Test Vendor",
            "category_id": 999,  # Catégorie inexistante
            "monthly_cost": 10.0,
            "owner_department": "Engineering"
        }
        
        response = client.post("/tools", json=tool_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"] == "Category not found"
        assert "message" in data
        assert "Category with ID 999 does not exist" in data["message"]
    
    def test_create_tool_response_structure(self, client):
        """Test que la structure de la réponse est correcte."""
        tool_data = {
            "name": "Structure Test",
            "description": "Test description",
            "vendor": "Test Vendor",
            "website_url": "https://test.com",
            "category_id": 1,
            "monthly_cost": 15.0,
            "owner_department": "Engineering"
        }
        
        response = client.post("/tools", json=tool_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Vérifier tous les champs requis
        required_fields = [
            "id", "name", "description", "vendor", "website_url",
            "category", "monthly_cost", "owner_department", "status",
            "active_users_count", "created_at", "updated_at"
        ]
        
        for field in required_fields:
            assert field in data, f"Le champ '{field}' est manquant dans la réponse"
        
        # Vérifier que l'ID est généré
        assert isinstance(data["id"], int)
        assert data["id"] > 0
        
        # Vérifier les dates
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

