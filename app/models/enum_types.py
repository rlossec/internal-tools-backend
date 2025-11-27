from enum import Enum

DEFAULT_COLOR_HEX = "#6366f1"

class DepartmentType(str, Enum):
    Engineering = "Engineering"
    Sales = "Sales"
    Marketing = "Marketing"
    HR = "HR"
    Finance = "Finance"
    Operations = "Operations"
    Design = "Design"


class ToolStatus(str, Enum):
    active = "active"
    deprecated = "deprecated"
    trial = "trial"


class UserRole(str, Enum):
    employee = "employee"
    manager = "manager"
    admin = "admin"


class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class AccessStatus(str, Enum):
    active = "active"
    revoked = "revoked"


class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
