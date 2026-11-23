from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    name: str
    email: str
    password: str
    role: str = "ROLE_USER"
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password=row["password"],
            role=row["role"],
            created_at=str(row["created_at"]) if "created_at" in row.keys() else None,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }
