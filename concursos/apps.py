"""Configuração do app Django ``concursos``."""

from django.apps import AppConfig


class ConcursosConfig(AppConfig):
    """App de concursos, cargos e autorizações publicadas."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "concursos"
