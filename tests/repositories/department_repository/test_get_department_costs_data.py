"""Tests pour la méthode get_department_costs_data du DepartmentRepository."""


class TestGetDepartmentCostsData:
    """Tests pour get_department_costs_data."""
    
    def test_get_department_costs_data_with_valid_data(
        self,
        department_repository,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test récupération des données de coûts par département avec des données valides."""
        results = department_repository.get_department_costs_data()
        
        # Vérifier que les résultats sont une liste
        assert isinstance(results, list)
        
        # Vérifier qu'on a des résultats
        assert len(results) > 0
        
        # Vérifier la structure de chaque résultat
        for row in results:
            assert 'department' in row
            assert 'tool_id' in row
            assert 'monthly_cost' in row
            assert 'active_users_count' in row
            assert isinstance(row['monthly_cost'], float)
            assert isinstance(row['active_users_count'], int)
    
    def test_get_department_costs_data_uses_owner_department(
        self,
        department_repository,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les données utilisent owner_department et non user.department."""
        results = department_repository.get_department_costs_data()
        
        # Trouver l'entrée pour Engineering + GitHub
        engineering_github = [
            r for r in results
            if r['department'] == 'Engineering' and r['tool_id'] == test_tools[0].id
        ]
        
        # La ligne doit être présente
        assert len(engineering_github) == 1
        assert engineering_github[0]['monthly_cost'] == 100.0
        assert engineering_github[0]['active_users_count'] == 2
    
    def test_get_department_costs_data_aggregates_by_department_and_tool(
        self,
        department_repository,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les données sont correctement agrégées par département et outil."""
        results = department_repository.get_department_costs_data()
        
        # Engineering devrait avoir 2 entrées (GitHub et Jira)
        engineering_results = [r for r in results if r['department'] == 'Engineering']
        assert len(engineering_results) == 2
        
        # Marketing devrait avoir 1 entrée (Slack - owner_department)
        marketing_results = [r for r in results if r['department'] == 'Marketing']
        assert len(marketing_results) == 1
        
        # Design devrait avoir 1 entrée (Figma)
        design_results = [r for r in results if r['department'] == 'Design']
        assert len(design_results) == 1
    
    def test_get_department_costs_data_monthly_costs_are_correct(
        self,
        department_repository,
        test_categories,
        test_tools,
        test_cost_tracking_for_department_computations
    ):
        """Test que les coûts mensuels totaux sont corrects depuis CostTracking."""
        results = department_repository.get_department_costs_data()
        
        # Trouver GitHub (coût total 100.00)
        github_results = [r for r in results if r['tool_id'] == test_tools[0].id]
        for result in github_results:
            assert result['monthly_cost'] == 100.0
            assert result['active_users_count'] == 2
        
        # Trouver Slack (coût total 225.00)
        slack_results = [r for r in results if r['tool_id'] == test_tools[1].id]
        for result in slack_results:
            assert result['monthly_cost'] == 225.0
            assert result['active_users_count'] == 3
        
        # Trouver Jira (coût total 100.00)
        jira_results = [r for r in results if r['tool_id'] == test_tools[2].id]
        for result in jira_results:
            assert result['monthly_cost'] == 100.0
            assert result['active_users_count'] == 1
        
        # Trouver Figma (coût total 30.00)
        figma_results = [r for r in results if r['tool_id'] == test_tools[3].id]
        for result in figma_results:
            assert result['monthly_cost'] == 30.0
            assert result['active_users_count'] == 1
    
    def test_get_department_costs_data_no_data_returns_empty_list(
        self,
        department_repository
    ):
        """Test que sans données, get_department_costs_data retourne une liste vide."""
        results = department_repository.get_department_costs_data()
        
        assert isinstance(results, list)
        assert len(results) == 0

