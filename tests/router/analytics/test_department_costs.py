"""Tests pour l'endpoint GET /api/analytics/department-costs."""
import pytest

from app.schemas import SortDepartmentCostField, SortOrder


class TestGetDepartmentCostsEndpoint:
    """Tests pour l'endpoint GET /api/analytics/department-costs."""
    
    def test_get_department_costs_success(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test récupération des coûts par département avec succès."""
        response = client.get("/analytics/department-costs")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier la structure de la réponse
        assert "data" in data
        assert "summary" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        
        # Vérifier la structure de chaque item
        for dept_item in data["data"]:
            assert "department" in dept_item
            assert "total_cost" in dept_item
            assert "tools_count" in dept_item
            assert "total_users" in dept_item
            assert "average_cost_per_tool" in dept_item
            assert "cost_percentage" in dept_item
        
        # Vérifier la structure du summary
        summary = data["summary"]
        assert "total_company_cost" in summary
        assert "departments_count" in summary
        assert "most_expensive_department" in summary
    
    def test_get_department_costs_calculates_totals_correctly(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les totaux sont calculés correctement."""
        response = client.get("/analytics/department-costs")
        
        assert response.status_code == 200
        data = response.json()
        
        # Engineering: GitHub (100) + Jira (100) = 200
        engineering = next((d for d in data["data"] if d["department"] == "Engineering"), None)
        assert engineering is not None
        assert engineering["total_cost"] == 200.0
        assert engineering["tools_count"] == 2
        assert engineering["total_users"] == 3
        
        # Marketing: Slack (225) = 225
        marketing = next((d for d in data["data"] if d["department"] == "Marketing"), None)
        assert marketing is not None
        assert marketing["total_cost"] == 225.0
        assert marketing["tools_count"] == 1
        assert marketing["total_users"] == 3
        
        # Design: Figma (30) = 30
        design = next((d for d in data["data"] if d["department"] == "Design"), None)
        assert design is not None
        assert design["total_cost"] == 30.0
        assert design["tools_count"] == 1
        assert design["total_users"] == 1
    
    def test_get_department_costs_calculates_averages_correctly(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les moyennes sont calculées correctement."""
        response = client.get("/analytics/department-costs")
        
        assert response.status_code == 200
        data = response.json()
        
        # Engineering: 200 / 2 outils = 100
        engineering = next((d for d in data["data"] if d["department"] == "Engineering"), None)
        assert engineering is not None
        assert engineering["average_cost_per_tool"] == 100.0
        
        # Marketing: 225 / 1 outil = 225
        marketing = next((d for d in data["data"] if d["department"] == "Marketing"), None)
        assert marketing is not None
        assert marketing["average_cost_per_tool"] == 225.0
    
    def test_get_department_costs_summary_is_correct(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que le résumé est correct."""
        response = client.get("/analytics/department-costs")
        
        assert response.status_code == 200
        data = response.json()
        
        summary = data["summary"]
        assert summary["total_company_cost"] > 0
        assert summary["departments_count"] > 0
        assert summary["most_expensive_department"] is not None
        assert summary["most_expensive_department"] != ""
        
        # Le total devrait être la somme des coûts des départements
        calculated_total = sum(d["total_cost"] for d in data["data"])
        assert abs(summary["total_company_cost"] - calculated_total) < 0.01
        
        # Le nombre de départements devrait correspondre
        assert summary["departments_count"] == len(data["data"])
    
    def test_get_department_costs_sorts_by_total_cost_desc(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que le tri par coût total décroissant fonctionne."""
        response = client.get("/analytics/department-costs?sort_by=total_cost&order=desc")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les coûts sont triés en ordre décroissant
        costs = [d["total_cost"] for d in data["data"]]
        assert costs == sorted(costs, reverse=True)
    
    def test_get_department_costs_sorts_by_total_cost_asc(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que le tri par coût total croissant fonctionne."""
        response = client.get("/analytics/department-costs?sort_by=total_cost&order=asc")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les coûts sont triés en ordre croissant
        costs = [d["total_cost"] for d in data["data"] if d["total_cost"] > 0]
        assert costs == sorted(costs)
    
    def test_get_department_costs_sorts_by_department_name(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que le tri par nom de département fonctionne."""
        response = client.get("/analytics/department-costs?sort_by=department&order=asc")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les départements sont triés alphabétiquement
        departments = [d["department"] for d in data["data"]]
        assert departments == sorted(departments)
    
    def test_get_department_costs_default_sort(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que le tri par défaut (total_cost DESC) fonctionne."""
        response = client.get("/analytics/department-costs")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les coûts sont triés en ordre décroissant par défaut
        costs = [d["total_cost"] for d in data["data"]]
        assert costs == sorted(costs, reverse=True)
    
    def test_get_department_costs_percentage_sums_to_100(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les pourcentages s'additionnent à ~100%."""
        response = client.get("/analytics/department-costs")
        
        assert response.status_code == 200
        data = response.json()
        
        # Calculer la somme des pourcentages des départements avec coûts > 0
        total_percentage = sum(
            d["cost_percentage"] for d in data["data"] if d["total_cost"] > 0
        )
        
        # Avec les arrondis, ça devrait être proche de 100%
        assert 99.0 <= total_percentage <= 101.0, \
            f"Les pourcentages devraient totaliser ~100%, mais totalisent {total_percentage}%"
    
    def test_get_department_costs_empty_data_returns_empty_response(
        self,
        client
    ):
        """Test que sans données, une réponse vide est retournée."""
        response = client.get("/analytics/department-costs")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["data"] == []
        assert data["summary"]["total_company_cost"] == 0.0
        assert data["summary"]["departments_count"] == 0
        assert data["summary"]["most_expensive_department"] == ""
    
    # 400 - Validation errors
    def test_get_department_costs_invalid_sort_field(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les paramètres de tri invalides retournent une erreur 400."""
        response = client.get("/analytics/department-costs?sort_by=invalid&order=desc")
        
        assert response.status_code == 400
    
    def test_get_department_costs_invalid_order(
        self,
        client,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les paramètres d'ordre invalides retournent une erreur 400."""
        response = client.get("/analytics/department-costs?sort_by=total_cost&order=invalid")
        
        assert response.status_code == 400

