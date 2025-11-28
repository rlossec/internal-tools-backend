"""Tests pour vérifier que tous les endpoints retournent 500 quand la base de données est indisponible."""
import pytest
from unittest.mock import patch
from sqlalchemy.exc import OperationalError


class TestDatabaseErrors:
    """Tests pour vérifier la gestion des erreurs de base de données sur tous les endpoints."""
    
    @pytest.mark.parametrize("method,url,data", [
        ("GET", "/tools", None),
        ("GET", "/tools/1", None),
        ("POST", "/tools", {
            "name": "Test Tool",
            "vendor": "Test Vendor",
            "category_id": 1,
            "monthly_cost": 50.0,
            "owner_department": "Engineering"
        }),
        ("PUT", "/tools/1", {
            "monthly_cost": 60.0
        }),
        ("GET", "/analytics/department-costs", None),
        ("GET", "/analytics/expensive-tools", None),
    ])
    def test_endpoints_return_500_when_database_unavailable(self, client, method, url, data):
        """Test que tous les endpoints retournent 500 quand la base de données est indisponible."""
        # Mock pour simuler une erreur de base de données
        # On mock la méthode appropriée selon l'endpoint
        if method == "GET" and url == "/tools":
            # GET /tools utilise list_tools
            with patch('app.services.tool_service.ToolRepository.list_tools', side_effect=OperationalError("Connection failed", None, None)):
                response = client.get(url)
        elif method == "GET" and url.startswith("/tools/"):
            # GET /tools/{id} utilise get_tool
            with patch('app.services.tool_service.ToolRepository.get_tool', side_effect=OperationalError("Connection failed", None, None)):
                response = client.get(url)
        elif method == "POST":
            # POST /tools utilise create_tool
            with patch('app.services.tool_service.ToolRepository.create_tool', side_effect=OperationalError("Connection failed", None, None)):
                response = client.post(url, json=data)
        elif method == "PUT":
            # PUT /tools/{id} utilise update_tool
            with patch('app.services.tool_service.ToolRepository.update_tool', side_effect=OperationalError("Connection failed", None, None)):
                response = client.put(url, json=data)
        elif method == "GET" and url == "/analytics/department-costs":
            # GET /analytics/department-costs utilise get_department_costs
            with patch('app.services.department.department_service.DepartmentRepository.get_department_costs_data', side_effect=OperationalError("Connection failed", None, None)):
                response = client.get(url)
        elif method == "GET" and url == "/analytics/expensive-tools":
            # GET /analytics/expensive-tools utilise get_expensive_tools
            with patch('app.services.tool_service.ToolRepository.list_tools', side_effect=OperationalError("Connection failed", None, None)):
                response = client.get(url)
        else:
            pytest.fail(f"Method {method} not supported")
        
        assert response.status_code == 500
        data_response = response.json()
        assert data_response["error"] == "Internal server error"
        assert data_response["message"] == "Database connection failed"

