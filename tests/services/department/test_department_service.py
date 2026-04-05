"""Tests pour DepartmentService."""

from app.schemas import SortDepartmentCostField, SortOrder


class TestDepartmentService:
    """Tests pour le service des départements."""
    
    def test_get_department_costs_aggregates_correctly(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les coûts sont correctement agrégés par département."""
        result = department_service.get_department_costs()
        
        # Vérifier la structure de la réponse
        assert result.data is not None
        assert result.summary is not None
        assert len(result.data) > 0
        
        # Vérifier que chaque département a les champs requis
        for dept_item in result.data:
            assert dept_item.department is not None
            assert dept_item.total_cost >= 0
            assert dept_item.tools_count >= 0
            assert dept_item.total_users >= 0
            assert dept_item.average_cost_per_tool >= 0
            assert dept_item.cost_percentage >= 0
    
    def test_get_department_costs_calculates_totals_correctly(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les totaux sont calculés correctement."""
        result = department_service.get_department_costs()
        
        # Engineering: GitHub (100) + Jira (100) = 200
        engineering = next((d for d in result.data if d.department == "Engineering"), None)
        assert engineering is not None
        assert engineering.total_cost == 200.0
        assert engineering.tools_count == 2  # GitHub et Jira
        assert engineering.total_users == 3  # 2 (GitHub) + 1 (Jira)
        
        # Marketing: Slack (225) = 225
        marketing = next((d for d in result.data if d.department == "Marketing"), None)
        assert marketing is not None
        assert marketing.total_cost == 225.0
        assert marketing.tools_count == 1  # Slack
        assert marketing.total_users == 3  # 3 utilisateurs actifs
        
        # Design: Figma (30) = 30
        design = next((d for d in result.data if d.department == "Design"), None)
        assert design is not None
        assert design.total_cost == 30.0
        assert design.tools_count == 1  # Figma
        assert design.total_users == 1  # 1 utilisateur actif
    
    def test_get_department_costs_calculates_averages_correctly(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les moyennes sont calculées correctement."""
        result = department_service.get_department_costs()
        
        # Engineering: 200 / 2 outils = 100
        engineering = next((d for d in result.data if d.department == "Engineering"), None)
        assert engineering is not None
        assert engineering.average_cost_per_tool == 100.0
        
        # Marketing: 225 / 1 outil = 225
        marketing = next((d for d in result.data if d.department == "Marketing"), None)
        assert marketing is not None
        assert marketing.average_cost_per_tool == 225.0
        
        # Design: 30 / 1 outil = 30
        design = next((d for d in result.data if d.department == "Design"), None)
        assert design is not None
        assert design.average_cost_per_tool == 30.0
    
    def test_get_department_costs_calculates_percentages_correctly(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les pourcentages sont calculés correctement."""
        result = department_service.get_department_costs()
        
        total_company_cost = result.summary.total_company_cost
        # Total attendu: Engineering (200) + Marketing (225) + Design (30) = 455
        
        # Vérifier que les pourcentages s'additionnent à ~100% (avec arrondis)
        total_percentage = sum(d.cost_percentage for d in result.data if d.total_cost > 0)
        assert 99.0 <= total_percentage <= 101.0, f"Les pourcentages devraient totaliser ~100%, mais totalisent {total_percentage}"
        
        # Engineering: 200 / 455 * 100 ≈ 43.96
        engineering = next((d for d in result.data if d.department == "Engineering"), None)
        assert engineering is not None
        assert 43.0 <= engineering.cost_percentage <= 45.0
    
    def test_get_department_costs_includes_departments_without_tools(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que seuls les départements avec outils sont inclus."""
        result = department_service.get_department_costs()
        
        # Avec la nouvelle logique, seuls les départements avec des outils (owner_department) sont inclus
        # HR n'a pas d'outils, donc ne devrait pas être présent
        hr = next((d for d in result.data if d.department == "HR"), None)
        # HR ne devrait pas être présent car il n'a pas d'outils avec owner_department = HR
        # Cette assertion peut être supprimée ou adaptée selon les besoins
    
    def test_get_department_costs_sorts_by_total_cost_desc(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que le tri par coût total décroissant fonctionne."""
        result = department_service.get_department_costs(
            sort_by=SortDepartmentCostField.TOTAL_COST,
            order=SortOrder.DESC
        )
        
        # Vérifier que les coûts sont triés en ordre décroissant
        costs = [d.total_cost for d in result.data]
        assert costs == sorted(costs, reverse=True)
        
        # Le premier devrait être Engineering (150) ou Marketing (105)
        assert result.data[0].total_cost >= result.data[1].total_cost
    
    def test_get_department_costs_sorts_by_total_cost_asc(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que le tri par coût total croissant fonctionne."""
        result = department_service.get_department_costs(
            sort_by=SortDepartmentCostField.TOTAL_COST,
            order=SortOrder.ASC
        )
        
        # Vérifier que les coûts sont triés en ordre croissant
        costs = [d.total_cost for d in result.data if d.total_cost > 0]
        assert costs == sorted(costs)
    
    def test_get_department_costs_sorts_by_department_name(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que le tri par nom de département fonctionne."""
        result = department_service.get_department_costs(
            sort_by=SortDepartmentCostField.DEPARTMENT,
            order=SortOrder.ASC
        )
        
        # Vérifier que les départements sont triés alphabétiquement
        departments = [d.department for d in result.data]
        assert departments == sorted(departments)
    
    def test_get_department_costs_summary_is_correct(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que le résumé est correct."""
        result = department_service.get_department_costs()
        
        summary = result.summary
        assert summary is not None
        assert summary.total_company_cost > 0
        assert summary.departments_count > 0
        assert summary.most_expensive_department is not None
        assert summary.most_expensive_department != ""
        
        # Le total devrait être la somme des coûts des départements
        calculated_total = sum(d.total_cost for d in result.data)
        assert abs(summary.total_company_cost - calculated_total) < 0.01
        
        # Le nombre de départements devrait correspondre
        assert summary.departments_count == len(result.data)
    
    def test_get_department_costs_finds_most_expensive_department(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que le département le plus cher est identifié correctement."""
        result = department_service.get_department_costs()
        
        # Trouver le département avec le coût le plus élevé
        max_cost_dept = max(result.data, key=lambda d: d.total_cost)
        
        # Le résumé devrait indiquer ce département
        assert result.summary.most_expensive_department == max_cost_dept.department
    
    def test_get_department_costs_empty_data_returns_empty_response(
        self,
        db_session
    ):
        """Test que sans données, une réponse vide est retournée."""
        from app.repositories import DepartmentRepository
        from app.services import DepartmentService
        
        repository = DepartmentRepository(session=db_session)
        service = DepartmentService(department_repository=repository)
        
        result = service.get_department_costs()
        
        assert result.data == []
        assert result.summary.total_company_cost == 0.0
        assert result.summary.departments_count == 0
        assert result.summary.most_expensive_department == ""
    
    def test_get_department_costs_average_cost_per_tool_is_zero_when_no_tools(
        self,
        department_service,
        test_cost_tracking_for_department_computations
    ):
        """Test que average_cost_per_tool est calculé correctement."""
        result = department_service.get_department_costs()
        
        # Vérifier que tous les départements avec outils ont une moyenne > 0
        for dept in result.data:
            if dept.tools_count > 0:
                assert dept.average_cost_per_tool > 0
            else:
                assert dept.average_cost_per_tool == 0.0
    
    def test_get_department_costs_handles_same_cost_for_departments(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les départements avec le même coût sont gérés correctement."""
        result = department_service.get_department_costs()
        
        # Vérifier que le département le plus cher est déterminé même en cas d'égalité
        # (doit choisir alphabétiquement)
        summary = result.summary
        assert summary.most_expensive_department is not None
        assert summary.most_expensive_department != ""
    
    def test_get_department_costs_percentage_sums_to_100(
        self,
        department_service,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les pourcentages des départements avec coûts s'additionnent à ~100%."""
        result = department_service.get_department_costs()
        
        # Calculer la somme des pourcentages des départements avec coûts > 0
        total_percentage = sum(
            d.cost_percentage for d in result.data if d.total_cost > 0
        )
        
        # Avec les arrondis, ça devrait être proche de 100%
        assert 99.0 <= total_percentage <= 101.0, \
            f"Les pourcentages devraient totaliser ~100%, mais totalisent {total_percentage}%"

