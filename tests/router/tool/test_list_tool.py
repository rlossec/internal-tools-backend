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
    
    # Ignored invalid department
    def test_get_tools_invalid_department(self, client):
        """Test avec un département invalide (doit être ignoré)."""
        response = client.get("/tools?department=InvalidDepartment")
        
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

    # 422