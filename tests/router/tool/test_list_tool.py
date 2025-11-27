"""Tests pour l'endpoint GET /tools."""
import pytest


class TestGetToolsEndpoint:
    """Tests pour l'endpoint GET /tools."""
    
    # 200
    # Filters
    def test_get_tools_without_filters(self, client):
        """Test récupération de tous les outils sans filtres."""
        response = client.get("/tools")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "filtered" in data
        assert "filters_applied" in data
        assert len(data["data"]) == 5
        assert data["total"] == 5
        assert data["filtered"] == 5
    
    def test_get_tools_filter_by_category(self, client):
        """Test filtrage par catégorie."""
        response = client.get("/tools?category=Development")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "GitHub"
        assert data["filtered"] == 1
    
    def test_get_tools_filter_by_vendor(self, client):
        """Test filtrage par vendeur."""
        response = client.get("/tools?vendor=GitHub")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "GitHub"
        assert data["filtered"] == 1
    
    def test_get_tools_filter_by_department(self, client):
        """Test filtrage par département."""
        response = client.get("/tools?department=Engineering")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2  # GitHub et Jira
        assert all(tool["owner_department"] == "Engineering" for tool in data["data"])
        assert data["filtered"] == 2
    
    def test_get_tools_filter_by_status(self, client):
        """Test filtrage par statut."""
        response = client.get("/tools?status=active")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3  # GitHub, Slack, Figma
        assert all(tool["status"] == "active" for tool in data["data"])
        assert data["filtered"] == 3
    
    def test_get_tools_filter_by_min_cost(self, client):
        """Test filtrage par coût minimum."""
        response = client.get("/tools?min_cost=50")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3  # GitHub (50), Slack (75), Jira (100)
        assert all(tool["monthly_cost"] >= 50 for tool in data["data"])
        assert data["filtered"] == 3
    
    def test_get_tools_filter_by_max_cost(self, client):
        """Test filtrage par coût maximum."""
        response = client.get("/tools?max_cost=50")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3  # GitHub (50), Figma (30), Deprecated (20)
        assert all(tool["monthly_cost"] <= 50 for tool in data["data"])
        assert data["filtered"] == 3
    
    def test_get_tools_filter_by_cost_range(self, client):
        """Test filtrage par plage de coût."""
        response = client.get("/tools?min_cost=30&max_cost=75")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3  # GitHub (50), Slack (75), Figma (30)
        assert all(30 <= tool["monthly_cost"] <= 75 for tool in data["data"])
        assert data["filtered"] == 3
    
    def test_get_tools_partial_vendor_match(self, client):
        """Test que le filtre de vendeur accepte des correspondances partielles."""
        response = client.get("/tools?vendor=Tech")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Slack"
    
    @pytest.mark.parametrize("query_params, expected_count, expected_names", [
        # Test 1: Engineering + active + min_cost 50
        ("department=Engineering&status=active&min_cost=50", 1, ["GitHub"]),
        # Test 2: Marketing + active
        ("department=Marketing&status=active", 1, ["Slack"]),
        # Test 3: Engineering + trial
        ("department=Engineering&status=trial", 1, ["Jira"]),
        # Test 4: Design + active
        ("department=Design&status=active", 1, ["Figma"]),
        # Test 5: active + max_cost 50
        ("status=active&max_cost=50", 2, ["GitHub", "Figma"]),
        # Test 6: active + min_cost 75
        ("status=active&min_cost=75", 1, ["Slack"]),
        # Test 7: Engineering + min_cost 50 + max_cost 100
        ("department=Engineering&min_cost=50&max_cost=100", 2, ["GitHub", "Jira"]),
        # Test 8: active + cost range 30-75
        ("status=active&min_cost=30&max_cost=75", 3, ["GitHub", "Slack", "Figma"]),
        # Test 9: department Engineering + status active + cost range
        ("department=Engineering&status=active&min_cost=40&max_cost=60", 1, ["GitHub"]),
        # Test 10: Multiple departments (via category filtering)
        ("category=Development&status=active", 1, ["GitHub"]),
    ])
    def test_get_tools_multiple_filters(self, client, query_params, expected_count, expected_names):
        """Test avec plusieurs combinaisons de filtres."""
        response = client.get(f"/tools?{query_params}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == expected_count
        actual_names = [tool["name"] for tool in data["data"]]
        assert set(actual_names) == set(expected_names)
        assert data["filtered"] == expected_count

    # Sorting
    @pytest.mark.parametrize("sort_by, sort_order, expected_first_name, check_field", [
        # Tri par nom
        ("name", "asc", "Deprecated Tool", "name"),
        ("name", "desc", "Slack", "name"),
        # Tri par coût
        ("monthly_cost", "asc", "Deprecated Tool", "monthly_cost"),  # 20.0
        ("monthly_cost", "desc", "Jira", "monthly_cost"),  # 100.0
        # Tri par ID
        ("id", "asc", "GitHub", "id"),  # 1
        ("id", "desc", "Deprecated Tool", "id"),  # 5
        # Tri par date de création
        ("created_at", "asc", "Deprecated Tool", "created_at"),  # 2023-01-01 (le plus ancien)
        ("created_at", "desc", "Figma", "created_at"),  # 2024-04-01 (le plus récent)
    ])
    def test_get_tools_sorting(self, client, sort_by, sort_order, expected_first_name, check_field):
        """Test tri des outils par différents champs et ordres."""
        response = client.get(f"/tools?sort_by={sort_by}&sort_order={sort_order}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que tous les outils sont présents
        assert len(data["data"]) == 5
        
        # Vérifier le tri sur le champ approprié
        from datetime import datetime
        
        if check_field == "created_at":
            # Pour les dates, convertir les strings ISO en datetime pour la comparaison
            def parse_date(date_value):
                if isinstance(date_value, str):
                    # Gérer les formats ISO avec ou sans timezone
                    date_str = date_value.replace("Z", "+00:00")
                    try:
                        return datetime.fromisoformat(date_str)
                    except ValueError:
                        # Fallback pour d'autres formats
                        return datetime.fromisoformat(date_str.split("+")[0].split(".")[0])
                return date_value
            
            values = [parse_date(tool[check_field]) for tool in data["data"]]
        else:
            values = [tool[check_field] for tool in data["data"]]
        
        if sort_order == "asc":
            assert values == sorted(values), f"Les valeurs ne sont pas triées en ordre croissant: {values}"
        else:
            assert values == sorted(values, reverse=True), f"Les valeurs ne sont pas triées en ordre décroissant: {values}"
        
        # Vérifier le premier élément par son nom (plus lisible)
        assert data["data"][0]["name"] == expected_first_name, \
            f"Le premier élément devrait être '{expected_first_name}', mais c'est '{data['data'][0]['name']}'"
    
    def test_get_tools_default_sort(self, client):
        """Test que le tri par défaut est par ID croissant."""
        response = client.get("/tools")
        
        assert response.status_code == 200
        data = response.json()
        ids = [tool["id"] for tool in data["data"]]
        assert ids == sorted(ids)

    @pytest.mark.parametrize("query_params, sort_by, sort_order, expected_first_name, expected_first_value, check_field", [
        # Test 1: active + tri par coût décroissant
        ("status=active&sort_by=monthly_cost&sort_order=desc", "monthly_cost", "desc", "Slack", 75.0, "monthly_cost"),
        # Test 2: active + tri par coût croissant
        ("status=active&sort_by=monthly_cost&sort_order=asc", "monthly_cost", "asc", "Figma", 30.0, "monthly_cost"),
        # Test 3: Engineering + tri par nom croissant
        ("department=Engineering&sort_by=name&sort_order=asc", "name", "asc", "GitHub", "GitHub", "name"),
        # Test 4: Engineering + tri par nom décroissant
        ("department=Engineering&sort_by=name&sort_order=desc", "name", "desc", "Jira", "Jira", "name"),
        # Test 5: active + tri par date croissante
        ("status=active&sort_by=created_at&sort_order=asc", "created_at", "asc", "GitHub", None, "created_at"),
        # Test 6: cost range + tri par coût décroissant
        ("min_cost=30&max_cost=75&sort_by=monthly_cost&sort_order=desc", "monthly_cost", "desc", "Slack", 75.0, "monthly_cost"),
        # Test 7: department + status + tri par coût
        ("department=Engineering&status=active&sort_by=monthly_cost&sort_order=asc", "monthly_cost", "asc", "GitHub", 50.0, "monthly_cost"),
    ])
    def test_get_tools_filter_and_sort(self, client, query_params, sort_by, sort_order, expected_first_name, expected_first_value, check_field):
        """Test combinaison de filtres et tri avec différentes options."""
        response = client.get(f"/tools?{query_params}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier le tri sur le champ approprié
        from datetime import datetime
        
        if check_field == "created_at":
            # Pour les dates, convertir les strings ISO en datetime pour la comparaison
            def parse_date(date_value):
                if isinstance(date_value, str):
                    date_str = date_value.replace("Z", "+00:00")
                    try:
                        return datetime.fromisoformat(date_str)
                    except ValueError:
                        return datetime.fromisoformat(date_str.split("+")[0].split(".")[0])
                return date_value
            
            values = [parse_date(tool[check_field]) for tool in data["data"]]
        else:
            values = [tool[check_field] for tool in data["data"]]
        
        # Vérifier que le tri est correct
        if sort_order == "asc":
            assert values == sorted(values), f"Les valeurs ne sont pas triées en ordre croissant: {values}"
        else:
            assert values == sorted(values, reverse=True), f"Les valeurs ne sont pas triées en ordre décroissant: {values}"
        
        # Vérifier le premier élément par son nom
        assert data["data"][0]["name"] == expected_first_name, \
            f"Le premier élément devrait être '{expected_first_name}', mais c'est '{data['data'][0]['name']}'"
        
        # Vérifier la valeur du premier élément si spécifiée
        if expected_first_value is not None:
            assert data["data"][0][check_field] == expected_first_value, \
                f"La valeur du champ '{check_field}' devrait être {expected_first_value}, mais c'est {data['data'][0][check_field]}"

    # No results
    def test_get_tools_no_results(self, client):
        """Test avec des filtres qui ne retournent aucun résultat."""
        response = client.get("/tools?vendor=NonExistentVendor")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "No results found"
    
    # Ignored invalid filters
    @pytest.mark.parametrize("query_params, filter_type", [
        ("department=InvalidDepartment", "department"),
        ("status=invalid_status", "status"),
    ])
    def test_get_tools_invalid_filters_ignored(self, client, query_params, filter_type):
        """Test que les filtres invalides sont ignorés silencieusement."""
        response = client.get(f"/tools?{query_params}")
        
        assert response.status_code == 200
        data = response.json()
        # Le filtre invalide est ignoré, donc tous les outils sont retournés
        assert len(data["data"]) == 5

    # No results
    @pytest.mark.parametrize("query_params, expected_count", [
        # Test 1: Filtre qui retourne aucun résultat
        ("vendor=NonExistentVendor", 0),
        # Test 2: Combinaison qui retourne aucun résultat
        ("department=Engineering&status=deprecated", 0),
        # Test 3: Plage de coût qui ne correspond à rien
        ("min_cost=200&max_cost=300", 0),
        # Test 4: Catégorie inexistante
        ("category=NonExistentCategory", 0),
    ])
    def test_get_tools_no_results_scenarios(self, client, query_params, expected_count):
        """Test de différents scénarios qui retournent aucun résultat."""
        response = client.get(f"/tools?{query_params}")
        
        assert response.status_code == 200
        if expected_count == 0:
            data = response.json()
            assert "message" in data
            assert data["message"] == "No results found"
        else:
            data = response.json()
            assert len(data["data"]) == expected_count

    # 422 - Validation errors
    @pytest.mark.parametrize("query_params, error_keyword, error_field", [
        # Coûts négatifs - validation FastAPI Query
        ("min_cost=-10", "greater than or equal to 0", "min_cost"),
        ("max_cost=-5", "greater than or equal to 0", "max_cost"),
        # Enums invalides - validation FastAPI Query
        ("sort_by=invalid_field", None, "sort_by"),
        ("sort_order=invalid", None, "sort_order"),
    ])
    def test_get_tools_query_validation_errors(self, client, query_params, error_keyword, error_field):
        """Test des erreurs de validation FastAPI Query (paramètres de requête invalides)."""
        response = client.get(f"/tools?{query_params}")
        
        assert response.status_code == 422, f"Expected 422, got {response.status_code}. Response: {response.text}"
        
        data = response.json()
        assert "detail" in data, f"Response should contain 'detail' field: {data}"
        
        # Vérifier le message d'erreur si spécifié
        if error_keyword:
            error_text = str(data).lower()
            assert error_keyword.lower() in error_text, f"Expected '{error_keyword}' in error message, got: {data}"
        
        # Vérifier le champ en erreur si spécifié
        if error_field and "errors" in data:
            error_fields = [err.get("field", "") for err in data.get("errors", [])]
            assert any(error_field in field for field in error_fields), \
                f"Expected field '{error_field}' in errors: {error_fields}"
    
    def test_get_tools_pydantic_validation_error(self, client):
        """Test des erreurs de validation Pydantic (logique métier, ex: min_cost > max_cost)."""
        response = client.get("/tools?min_cost=100&max_cost=50")
        
        assert response.status_code == 422, f"Expected 422, got {response.status_code}. Response: {response.text}"
        
        data = response.json()
        assert "detail" in data, f"Response should contain 'detail' field: {data}"
        
        # La structure est {'detail': {'detail': '...', 'errors': [...]}}
        detail = data["detail"]
        if isinstance(detail, dict):
            assert "errors" in detail, f"Response should contain 'errors' field for Pydantic validation: {data}"
            assert len(detail["errors"]) > 0, "Errors array should not be empty"
            
            # Vérifier que le message d'erreur contient la validation métier
            error_text = str(detail).lower()
            assert "min_cost ne peut pas être supérieur à max_cost" in error_text or \
                   ("min_cost" in error_text and "max_cost" in error_text), \
                   f"Expected validation error message, got: {data}"
    
    # Response structure
    def test_get_tools_filters_applied_in_response(self, client):
        """Test que les filtres appliqués sont retournés dans la réponse."""
        response = client.get("/tools?category=Development&vendor=GitHub&sort_by=name")
        
        assert response.status_code == 200
        data = response.json()
        assert "filters_applied" in data
        filters = data["filters_applied"]
        assert filters["category"] == "Development"
        assert filters["vendor"] == "GitHub"
        assert filters["sort_by"] == "name"
    
    @pytest.mark.parametrize("query_params, expected_count", [
        # Test 1: Tous les filtres vides
        ("category=&vendor=&department=&status=", 5),
        # Test 2: Certains filtres vides, d'autres non
        ("category=&vendor=GitHub&department=&status=", 1),
        # Test 3: Filtres vides avec tri
        ("category=&vendor=&department=&status=&sort_by=name&sort_order=asc", 5),
        # Test 4: Filtres None (pas de paramètres)
        ("", 5),
    ])
    def test_get_tools_empty_filters(self, client, query_params, expected_count):
        """Test avec différents scénarios de filtres vides."""
        url = f"/tools?{query_params}" if query_params else "/tools"
        response = client.get(url)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == expected_count