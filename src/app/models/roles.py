"""Compatibility re-export — RBAC role lives in rbac_models."""

from src.app.models.rbac_models import Role, UserRoleLink

__all__ = ['Role', 'UserRoleLink']
