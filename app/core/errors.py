"""Exceptions personnalisées pour l'application."""


class ResourceNotFoundError(Exception):
    """Exception de base pour les ressources non trouvées."""
    
    def __init__(self, resource_type: str, resource_id: int):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} with ID {resource_id} does not exist"
        super().__init__(message)
    
    @property
    def error_type(self) -> str:
        """Retourne le type d'erreur formaté pour la réponse JSON."""
        return f"{self.resource_type} not found"


class CategoryNotFoundError(ResourceNotFoundError):
    """Exception levée lorsqu'une catégorie n'est pas trouvée."""
    
    def __init__(self, category_id: int):
        super().__init__("Category", category_id)
        self.category_id = category_id


class ToolNotFoundError(ResourceNotFoundError):
    """Exception levée lorsqu'un outil n'est pas trouvée."""
    
    def __init__(self, tool_id: int):
        super().__init__("Tool", tool_id)
        self.tool_id = tool_id
