"""Tests pour l'endpoint GET /tools/{tool_id}."""
import pytest
from datetime import datetime


class TestRetrieveToolEndpoint:
    """Tests pour l'endpoint GET /tools/{tool_id}."""
    
    # 200 - Succès
    def test_get_tool_success(self, client):
        """Test récupération réussie d'un outil existant."""
        response = client.get("/tools/1")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier la structure de base
        assert "id" in data
        assert "name" in data
        assert "description" in data
        assert "vendor" in data
        assert "website_url" in data
        assert "category" in data
        assert "monthly_cost" in data
        assert "owner_department" in data
        assert "status" in data
        assert "active_users_count" in data
        assert "total_monthly_cost" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "usage_metrics" in data
        
        # Vérifier les valeurs spécifiques pour l'outil ID 1 (GitHub)
        assert data["id"] == 1
        assert data["name"] == "GitHub"
        assert data["vendor"] == "GitHub Inc."
        assert data["monthly_cost"] == 50.0
        assert data["active_users_count"] == 10
        assert data["owner_department"] == "Engineering"
        assert data["status"] == "active"
        assert data["category"] == "Development"
    
    def test_get_tool_total_monthly_cost_calculation(self, client):
        """Test que le coût total mensuel est correctement calculé."""
        # GitHub : monthly_cost=50, active_users_count=10 => total=500
        response = client.get("/tools/1")
        
        assert response.status_code == 200
        data = response.json()
        expected_total = data["monthly_cost"] * data["active_users_count"]
        assert data["total_monthly_cost"] == expected_total
        assert data["total_monthly_cost"] == 500.0
    
    @pytest.mark.parametrize("tool_id, expected_name, expected_total_cost", [
        (1, "GitHub", 500.0),  # 50 * 10
        (2, "Slack", 1875.0),  # 75 * 25
        (3, "Jira", 1500.0),   # 100 * 15
        (4, "Figma", 240.0),   # 30 * 8
        (5, "Deprecated Tool", 0.0),  # 20 * 0
    ])
    def test_get_tool_different_tools(self, client, tool_id, expected_name, expected_total_cost):
        """Test récupération de différents outils avec calculs corrects."""
        response = client.get(f"/tools/{tool_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == tool_id
        assert data["name"] == expected_name
        assert data["total_monthly_cost"] == expected_total_cost
    
    def test_get_tool_usage_metrics_structure(self, client):
        """Test que les métriques d'utilisation ont la bonne structure."""
        response = client.get("/tools/1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "usage_metrics" in data
        usage_metrics = data["usage_metrics"]
        assert "last_30_days" in usage_metrics
        
        last_30_days = usage_metrics["last_30_days"]
        assert "total_sessions" in last_30_days
        assert "avg_session_minutes" in last_30_days
        
        # Vérifier que ce sont des entiers
        assert isinstance(last_30_days["total_sessions"], int)
        assert isinstance(last_30_days["avg_session_minutes"], int)
    
    def test_get_tool_usage_metrics_without_logs(self, client):
        """Test que les métriques retournent 0 quand il n'y a pas de logs."""
        response = client.get("/tools/1")
        
        assert response.status_code == 200
        data = response.json()
        
        # Sans logs d'utilisation, les métriques doivent être à 0
        usage_metrics = data["usage_metrics"]["last_30_days"]
        assert usage_metrics["total_sessions"] == 0
        assert usage_metrics["avg_session_minutes"] == 0
    
    def test_get_tool_usage_metrics_with_logs(self, client, test_usage_logs):
        """Test que les métriques sont correctement calculées avec des logs réels."""
        # GitHub (tool_id=1) a 3 logs dans les 30 derniers jours :
        # - 120 minutes (5 jours)
        # - 90 minutes (10 jours)
        # - 60 minutes (15 jours)
        # Total: 3 sessions, 270 minutes, moyenne: 90 minutes
        response = client.get("/tools/1")
        
        assert response.status_code == 200
        data = response.json()
        
        usage_metrics = data["usage_metrics"]["last_30_days"]
        assert usage_metrics["total_sessions"] == 3
        assert usage_metrics["avg_session_minutes"] == 90  # (120 + 90 + 60) / 3
    
    def test_get_tool_usage_metrics_filters_old_logs(self, client, test_usage_logs):
        """Test que les logs de plus de 30 jours sont exclus des métriques."""
        # GitHub a 4 logs au total, mais 1 est de plus de 30 jours
        # Seuls les 3 logs récents doivent être comptés
        response = client.get("/tools/1")
        
        assert response.status_code == 200
        data = response.json()
        
        usage_metrics = data["usage_metrics"]["last_30_days"]
        # Vérifier qu'on n'a que 3 sessions (pas 4)
        assert usage_metrics["total_sessions"] == 3
        # Les 200 minutes du log ancien ne doivent pas être inclus
        assert usage_metrics["avg_session_minutes"] == 90
    
    def test_get_tool_usage_metrics_different_tools(self, client, test_usage_logs):
        """Test que les métriques sont calculées par outil (isolation)."""
        # Slack (tool_id=2) a 1 log dans les 30 derniers jours
        response = client.get("/tools/2")
        
        assert response.status_code == 200
        data = response.json()
        
        usage_metrics = data["usage_metrics"]["last_30_days"]
        assert usage_metrics["total_sessions"] == 1
        assert usage_metrics["avg_session_minutes"] == 180
    
    def test_get_tool_usage_metrics_single_session(self, client, db_session, test_tools, test_user):
        """Test calcul de la moyenne avec une seule session."""
        from datetime import date, timedelta
        from app.models.usage_log import UsageLog
        
        # Créer un log pour un outil sans autres logs
        log = UsageLog(
            user_id=test_user.id,
            tool_id=test_tools[3].id,  # Figma
            session_date=date.today() - timedelta(days=5),
            usage_minutes=45,
            actions_count=15,
            created_at=datetime.now()
        )
        db_session.add(log)
        db_session.commit()
        
        response = client.get(f"/tools/{test_tools[3].id}")
        
        assert response.status_code == 200
        data = response.json()
        
        usage_metrics = data["usage_metrics"]["last_30_days"]
        assert usage_metrics["total_sessions"] == 1
        assert usage_metrics["avg_session_minutes"] == 45
    
    def test_get_tool_usage_metrics_zero_minutes(self, client, db_session, test_tools, test_user):
        """Test avec des sessions de 0 minutes (cas limite)."""
        from datetime import date, timedelta
        from app.models.usage_log import UsageLog
        
        # Créer des logs avec 0 minutes
        log1 = UsageLog(
            user_id=test_user.id,
            tool_id=test_tools[4].id,  # Deprecated Tool
            session_date=date.today() - timedelta(days=5),
            usage_minutes=0,
            actions_count=0,
            created_at=datetime.now()
        )
        log2 = UsageLog(
            user_id=test_user.id,
            tool_id=test_tools[4].id,
            session_date=date.today() - timedelta(days=10),
            usage_minutes=0,
            actions_count=0,
            created_at=datetime.now()
        )
        db_session.add(log1)
        db_session.add(log2)
        db_session.commit()
        
        response = client.get(f"/tools/{test_tools[4].id}")
        
        assert response.status_code == 200
        data = response.json()
        
        usage_metrics = data["usage_metrics"]["last_30_days"]
        assert usage_metrics["total_sessions"] == 2
        assert usage_metrics["avg_session_minutes"] == 0
    
    def test_get_tool_response_fields(self, client):
        """Test que tous les champs requis sont présents dans la réponse."""
        response = client.get("/tools/1")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "id", "name", "description", "vendor", "website_url",
            "category", "monthly_cost", "owner_department", "status",
            "active_users_count", "total_monthly_cost", "created_at",
            "updated_at", "usage_metrics"
        ]
        
        for field in required_fields:
            assert field in data, f"Le champ '{field}' est manquant dans la réponse"
    
    # 404 - Not Found (retourne NotFoundResponse)
    @pytest.mark.parametrize("invalid_id", [
        0,
        -1,
        999999,
    ])
    def test_get_tool_not_found_scenarios(self, client, invalid_id):
        """Test avec différents IDs inexistants."""
        response = client.get(f"/tools/{invalid_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"] == "Tool not found"
        assert "message" in data
        assert "does not exist" in data["message"].lower() or "not found" in data["message"].lower()
    
    # 422 - Validation errors
    @pytest.mark.parametrize("invalid_tool_id, expected_status", [
        ("not_a_number", 400),
        ("abc", 400),
        ("1.5", 400),
        ("", 307),  # FastAPI redirige vers /tools avec une chaîne vide
    ])
    def test_get_tool_invalid_id_type(self, client, invalid_tool_id, expected_status):
        """Test avec des IDs invalides (non numériques)."""
        response = client.get(f"/tools/{invalid_tool_id}", follow_redirects=False)
        
        assert response.status_code == expected_status
        
        if expected_status == 400:
            data = response.json()
            assert "error" in data
            assert data["error"] == "Validation failed"

