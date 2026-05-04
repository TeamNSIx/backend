"""Compatibility re-export — RBAC permission lives in rbac_models."""

from src.app.models.rbac_models import Permission, RolePermissionLink

__all__ = ['Permission', 'RolePermissionLink']
