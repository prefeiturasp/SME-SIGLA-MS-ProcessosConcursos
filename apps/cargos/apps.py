"""Configuração do app Django ``cargos``."""

from django.apps import AppConfig


class CargosConfig(AppConfig):
    """App de cargos."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "cargos"
