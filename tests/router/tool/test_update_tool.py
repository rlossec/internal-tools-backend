"""Tests pour l'endpoint PUT /tools/{tool_id}."""
import pytest


class TestUpdateToolEndpoint:

    # 200 - Succès
    def test_update_tool_success(self, client, test_tools):
        """Test mise à jour réussie d'un outil avec données valides."""
        tool_id = test_tools[0].id
        update_data = {
            "monthly_cost": 7.00,
            "status": "deprecated",
            "description": "Updated description after renewal"
        }
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les champs ont été mis à jour
        assert data["id"] == tool_id
        assert data["monthly_cost"] == 7.0
        assert data["status"] == "deprecated"
        assert data["description"] == "Updated description after renewal"
        
        # Vérifier que les autres champs sont conservés
        assert data["name"] == test_tools[0].name
        assert data["vendor"] == test_tools[0].vendor
        assert data["category"] == test_tools[0].category.name
        assert data["owner_department"] == test_tools[0].owner_department.value
        assert data["active_users_count"] == test_tools[0].active_users_count
        
        # Vérifier que updated_at existe et est une date valide
        assert "updated_at" in data
        assert data["updated_at"] is not None
    
    def test_update_tool_partial_update(self, client, test_tools):
        """Test mise à jour partielle (un seul champ)."""
        tool_id = test_tools[0].id
        original_cost = float(test_tools[0].monthly_cost)
        original_status = test_tools[0].status.value
        
        update_data = {
            "monthly_cost": 15.50
        }
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que monthly_cost a été mis à jour
        assert data["monthly_cost"] == 15.5
        
        # Vérifier que les autres champs sont conservés
        assert data["status"] == original_status
        assert data["description"] == test_tools[0].description
    
    def test_update_tool_empty_body(self, client, test_tools):
        """Test mise à jour avec un body vide (aucun changement)."""
        tool_id = test_tools[0].id
        original_data = {
            "name": test_tools[0].name,
            "monthly_cost": float(test_tools[0].monthly_cost),
            "status": test_tools[0].status.value,
            "description": test_tools[0].description
        }
        
        update_data = {}
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que tous les champs sont conservés
        assert data["name"] == original_data["name"]
        assert data["monthly_cost"] == original_data["monthly_cost"]
        assert data["status"] == original_data["status"]
        assert data["description"] == original_data["description"]
    
    @pytest.mark.parametrize("status_value", [
        "active",
        "trial",
        "deprecated",
    ])
    def test_update_tool_different_status(self, client, test_tools, status_value):
        """Test mise à jour avec différents statuts."""
        tool_id = test_tools[0].id
        
        update_data = {
            "status": status_value
        }
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == status_value
    
    def test_update_tool_zero_cost(self, client, test_tools):
        """Test mise à jour avec un coût de 0."""
        tool_id = test_tools[0].id
        
        update_data = {
            "monthly_cost": 0.0
        }
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["monthly_cost"] == 0.0
    
    def test_update_tool_description_to_none(self, client, test_tools):
        """Test mise à jour de la description à None."""
        tool_id = test_tools[0].id
        
        update_data = {
            "description": None
        }
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] is None
    
    @pytest.mark.parametrize("field, value, expected_value, needs_categories", [
        ("name", "Updated Tool Name", "Updated Tool Name", False),
        ("vendor", "New Vendor", "New Vendor", False),
        ("website_url", "https://newwebsite.com", "https://newwebsite.com", False),
        ("owner_department", "Sales", "Sales", False),
        ("description", "New description", "New description", False),
        ("status", "trial", "trial", False),
        ("category_id", None, None, True),  # Sera remplacé dynamiquement
    ])

    def test_update_tool_individual_fields(self, client, test_tools, test_categories, field, value, expected_value, needs_categories):
        """Test paramétré pour la mise à jour de chaque champ individuellement."""
        tool_id = test_tools[0].id
        
        # Pour category_id, utiliser une catégorie différente
        if field == "category_id" and needs_categories:
            new_category_id = test_categories[1].id
            update_data = {field: new_category_id}
            expected_value = test_categories[1].name
        else:
            update_data = {field: value}
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Pour category_id, vérifier le nom de la catégorie dans la réponse
        if field == "category_id":
            assert data["category"] == expected_value
        else:
            assert data[field] == expected_value
    
    def test_update_tool_all_fields(self, client, test_tools, test_categories):
        """Test mise à jour de tous les champs en une fois."""
        tool_id = test_tools[0].id
        
        update_data = {
            "name": "Fully Updated Tool",
            "description": "Fully updated description",
            "vendor": "New Vendor Inc",
            "website_url": "https://newvendor.com",
            "category_id": test_categories[0].id,
            "monthly_cost": 25.99,
            "owner_department": "Marketing",
            "status": "trial"
        }
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Fully Updated Tool"
        assert data["description"] == "Fully updated description"
        assert data["vendor"] == "New Vendor Inc"
        assert data["website_url"] == "https://newvendor.com"
        assert data["category"] == test_categories[0].name
        assert data["monthly_cost"] == 25.99
        assert data["owner_department"] == "Marketing"
        assert data["status"] == "trial"
    
    def test_update_tool_response_structure(self, client, test_tools):
        """Test que la structure de la réponse est correcte."""
        tool_id = test_tools[0].id
        update_data = {
            "monthly_cost": 12.50,
            "status": "active",
            "description": "Test description"
        }
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier tous les champs requis
        required_fields = [
            "id", "name", "description", "vendor", "website_url",
            "category", "monthly_cost", "owner_department", "status",
            "active_users_count", "created_at", "updated_at"
        ]
        
        for field in required_fields:
            assert field in data, f"Le champ '{field}' est manquant dans la réponse"
        
        # Vérifier que l'ID est correct
        assert data["id"] == tool_id
        
        # Vérifier les dates
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    # 404 - Outil/catégorie inexistant(e)
    def test_update_tool_not_found(self, client, test_categories, test_tools):
        """Test avec un outil inexistant."""
        update_data = {
            "monthly_cost": 10.0
        }
        
        response = client.put("/tools/99999", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"] == "Tool not found"
        assert "message" in data
    
    def test_update_tool_invalid_category(self, client, test_tools):
        """Test avec une catégorie inexistante."""
        tool_id = test_tools[0].id
        
        update_data = {
            "category_id": 99999  # Catégorie inexistante
        }
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"] == "Category not found"
        assert "message" in data
        assert "Category with ID 99999 does not exist" in data["message"]
    

    # 422 - Validation errors
    @pytest.mark.parametrize("field, invalid_value, error_keyword", [
        ("name", "A", "2 et 100 caracteres"),  # Trop court
        ("name", "A" * 101, "2 et 100 caracteres"),  # Trop long
        ("vendor", "A", "2 et 100 caracteres"),  # Trop court
        ("vendor", "A" * 101, "2 et 100 caracteres"),  # Trop long
        ("category_id", 0, "entier positif"),
        ("category_id", -1, "entier positif"),
        ("monthly_cost", -10.0, "supérieur ou égal à 0"),
        ("monthly_cost", 10.123, "maximum 2 decimales"),
        ("owner_department", "InvalidDepartment", "owner_department"),
        ("status", "invalid_status", "status"),
        ("website_url", "invalid-url", "http:// ou https://"),
    ])
    def test_update_tool_validation_errors(self, client, test_tools, field, invalid_value, error_keyword):
        """Test des erreurs de validation."""
        tool_id = test_tools[0].id
        update_data = {
            field: invalid_value
        }
        
        response = client.put(f"/tools/{tool_id}", json=update_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"] == "Validation failed"
        assert "details" in data
        # Vérifier que le champ en erreur est dans les details
        assert field in data["details"] or error_keyword.lower() in str(data["details"]).lower()
    
    def test_update_tool_invalid_id_type(self, client, test_categories, test_tools):
        """Test avec un ID invalide (non numérique)."""
        update_data = {
            "monthly_cost": 10.0
        }
        
        response = client.put("/tools/abc", json=update_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"] == "Validation failed"
