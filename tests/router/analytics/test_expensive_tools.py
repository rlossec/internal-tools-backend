"""Tests pour l'endpoint GET /api/analytics/expensive-tools."""


class TestGetExpensiveToolsEndpoint:
    # 200 - Success
    def test_get_expensive_tools_success(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test récupération des outils coûteux avec succès."""
        response = client.get("/analytics/expensive-tools")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier la structure de la réponse
        assert "data" in data
        assert "analysis" in data
        assert isinstance(data["data"], list)
        
        # Vérifier la structure de chaque item
        for tool_item in data["data"]:
            assert "id" in tool_item
            assert "name" in tool_item
            assert "monthly_cost" in tool_item
            assert "active_users_count" in tool_item
            assert "cost_per_user" in tool_item
            assert "department" in tool_item
            assert "vendor" in tool_item
            assert "efficiency_rating" in tool_item
            assert tool_item["efficiency_rating"] in ["excellent", "good", "average", "low"]
        
        # Vérifier la structure de l'analyse
        analysis = data["analysis"]
        assert "total_tools_analyzed" in analysis
        assert "avg_cost_per_user_company" in analysis
        assert "potential_savings_identified" in analysis
    
    def test_get_expensive_tools_calculates_cost_per_user_correctly(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que cost_per_user est calculé correctement."""
        response = client.get("/analytics/expensive-tools")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que cost_per_user = monthly_cost / active_users_count
        for tool_item in data["data"]:
            if tool_item["active_users_count"] > 0:
                expected_cost_per_user = tool_item["monthly_cost"] / tool_item["active_users_count"]
                assert abs(tool_item["cost_per_user"] - expected_cost_per_user) < 0.01
            else:
                # Si active_users_count = 0, cost_per_user devrait être 0
                assert tool_item["cost_per_user"] == 0.0
    
    def test_get_expensive_tools_sorted_by_cost_desc(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que les outils sont triés par coût décroissant."""
        response = client.get("/analytics/expensive-tools")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les coûts sont triés en ordre décroissant
        costs = [tool["monthly_cost"] for tool in data["data"]]
        assert costs == sorted(costs, reverse=True)
    
    def test_get_expensive_tools_with_limit(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que le paramètre limit fonctionne."""
        response = client.get("/analytics/expensive-tools?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier qu'on a au maximum 2 outils
        assert len(data["data"]) <= 2
        
        # Vérifier que ce sont les 2 plus chers
        if len(data["data"]) == 2:
            assert data["data"][0]["monthly_cost"] >= data["data"][1]["monthly_cost"]
    
    def test_get_expensive_tools_with_min_cost(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que le paramètre min_cost fonctionne."""
        response = client.get("/analytics/expensive-tools?min_cost=50")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que tous les outils ont un coût >= 50
        for tool_item in data["data"]:
            assert tool_item["monthly_cost"] >= 50
    
    def test_get_expensive_tools_with_min_cost_and_limit(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que les paramètres min_cost et limit fonctionnent ensemble."""
        response = client.get("/analytics/expensive-tools?min_cost=50&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que tous les outils ont un coût >= 50
        for tool_item in data["data"]:
            assert tool_item["monthly_cost"] >= 50
        
        # Vérifier qu'on a au maximum 2 outils
        assert len(data["data"]) <= 2
    
    def test_get_expensive_tools_calculates_avg_cost_per_user_company(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que avg_cost_per_user_company est calculé correctement."""
        response = client.get("/analytics/expensive-tools")
        
        assert response.status_code == 200
        data = response.json()
        
        analysis = data["analysis"]
        
        # Calculer manuellement la moyenne attendue
        # Somme de tous les monthly_cost / Somme de tous les active_users_count
        # (outils à 0 utilisateurs exclus)
        total_cost = sum(
            float(tool.monthly_cost) for tool in test_tools 
            if tool.active_users_count > 0
        )
        total_users = sum(
            tool.active_users_count for tool in test_tools 
            if tool.active_users_count > 0
        )
        
        if total_users > 0:
            expected_avg = total_cost / total_users
            assert abs(analysis["avg_cost_per_user_company"] - expected_avg) < 0.01
        else:
            assert analysis["avg_cost_per_user_company"] == 0.0
    
    def test_get_expensive_tools_calculates_efficiency_rating(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que efficiency_rating est calculé correctement."""
        response = client.get("/analytics/expensive-tools")
        
        assert response.status_code == 200
        data = response.json()
        
        analysis = data["analysis"]
        avg_cost_per_user = analysis["avg_cost_per_user_company"]
        
        # Vérifier que les ratings sont cohérents avec la moyenne
        for tool_item in data["data"]:
            if tool_item["active_users_count"] > 0 and avg_cost_per_user > 0:
                cost_per_user = tool_item["cost_per_user"]
                ratio = cost_per_user / avg_cost_per_user
                
                rating = tool_item["efficiency_rating"]
                if ratio < 0.5:
                    assert rating == "excellent"
                elif ratio < 0.8:
                    assert rating == "good"
                elif ratio <= 1.2:
                    assert rating == "average"
                else:
                    assert rating == "low"
    
    def test_get_expensive_tools_calculates_potential_savings(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que potential_savings_identified est calculé correctement."""
        response = client.get("/analytics/expensive-tools")
        
        assert response.status_code == 200
        data = response.json()
        
        analysis = data["analysis"]
        
        # Calculer manuellement les économies potentielles
        # Somme des monthly_cost des outils avec efficiency_rating = "low"
        expected_savings = sum(
            tool["monthly_cost"] for tool in data["data"]
            if tool["efficiency_rating"] == "low"
        )
        
        # Mais attention : potential_savings est calculé sur TOUS les outils, pas seulement ceux retournés
        # On vérifie juste que c'est >= aux économies des outils retournés
        assert analysis["potential_savings_identified"] >= expected_savings
    
    def test_get_expensive_tools_total_tools_analyzed(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que total_tools_analyzed correspond au nombre total d'outils."""
        response = client.get("/analytics/expensive-tools?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        
        # total_tools_analyzed devrait être le nombre total d'outils (pas limité)
        analysis = data["analysis"]
        assert analysis["total_tools_analyzed"] == len(test_tools)
        # Même si on limite à 2, total_tools_analyzed devrait être le total
    
    # 200 Cas limite
    def test_get_expensive_tools_handles_zero_users(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que les outils avec 0 utilisateurs sont gérés correctement."""
        response = client.get("/analytics/expensive-tools")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les outils avec 0 utilisateurs ont cost_per_user = 0
        for tool_item in data["data"]:
            if tool_item["active_users_count"] == 0:
                assert tool_item["cost_per_user"] == 0.0


    def test_get_expensive_tools_all_tools_with_zero_users(
        self,
        client,
        db_session,
        test_categories
    ):
        """Test avec des outils qui ont tous 0 utilisateurs."""
        from datetime import datetime
        from app.models import Tool
        from app.models.enum_types import DepartmentType, ToolStatus
        
        # Créer un outil avec 0 utilisateurs
        tool = Tool(
            name="Tool Zero Users",
            description="Test",
            vendor="Test Vendor",
            category_id=test_categories[0].id,
            monthly_cost=100.00,
            active_users_count=0,
            owner_department=DepartmentType.Engineering,
            status=ToolStatus.active,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(tool)
        db_session.commit()
        db_session.refresh(tool)
        
        response = client.get("/analytics/expensive-tools")
        
        assert response.status_code == 200
        data = response.json()
        
        # avg_cost_per_user_company devrait être 0 car aucun outil avec utilisateurs
        assert data["analysis"]["avg_cost_per_user_company"] == 0.0

    def test_get_expensive_tools_empty_data(
        self,
        client
    ):
        """Test que sans données, une réponse vide est retournée."""
        response = client.get("/analytics/expensive-tools")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["data"] == []
        assert data["analysis"]["total_tools_analyzed"] == 0
        assert data["analysis"]["avg_cost_per_user_company"] == 0.0
        assert data["analysis"]["potential_savings_identified"] == 0.0

    # 400 - Validation errors
    def test_get_expensive_tools_invalid_limit(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que les valeurs invalides de limit retournent une erreur 400."""
        # Limit négatif
        response = client.get("/analytics/expensive-tools?limit=-1")
        assert response.status_code == 400
        
        # Limit trop grand
        response = client.get("/analytics/expensive-tools?limit=101")
        assert response.status_code == 400
    
    def test_get_expensive_tools_invalid_min_cost(
        self,
        client,
        test_categories,
        test_tools
    ):
        """Test que les valeurs invalides de min_cost retournent une erreur 400."""
        # Min_cost négatif
        response = client.get("/analytics/expensive-tools?min_cost=-1")
        assert response.status_code == 400
    