"""Template Manager for seeding, retrieving, and saving extraction rules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.database.models import TemplateRepository
from src.templates.default_templates import DEFAULT_TEMPLATES


class TemplateManager:
    """Coordinates template persistence and active template retrieval."""

    def __init__(self, template_repo: Optional[TemplateRepository] = None, db_path: Optional[Path] = None):
        self.repo = template_repo or TemplateRepository(db_path)
        self._ensure_defaults_seeded()

    def _ensure_defaults_seeded(self) -> None:
        """Seed starter templates into SQLite if empty or missing."""
        existing = {t["name"] for t in self.repo.list_all()}
        for item in DEFAULT_TEMPLATES:
            if item["name"] not in existing:
                self.repo.insert(
                    name=item["name"],
                    description=item["description"],
                    category=item["category"],
                    rules=item["rules"],
                    is_builtin=True,
                )

    def list_templates(self) -> List[Dict[str, Any]]:
        """Return all available templates."""
        return self.repo.list_all()

    def get_template(self, name_or_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve template by name or UUID."""
        all_t = self.list_templates()
        for t in all_t:
            if t["name"].lower() == name_or_id.lower() or t["id"] == name_or_id:
                return t
        return None

    def save_custom_template(
        self,
        name: str,
        description: str,
        category: str,
        fields_config: Dict[str, Any],
    ) -> str:
        """Save a new user-defined template."""
        if not name.strip():
            raise ValueError("Template name cannot be empty.")

        rules = {"fields": fields_config}
        return self.repo.insert(
            name=name.strip(),
            description=description.strip(),
            category=category.strip() or "Custom",
            rules=rules,
            is_builtin=False,
        )

    def delete_template(self, template_id: str) -> bool:
        """Delete user-defined template (built-ins are protected)."""
        return self.repo.delete(template_id)
