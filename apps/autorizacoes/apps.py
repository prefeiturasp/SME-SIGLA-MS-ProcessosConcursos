"""Configuração do app Django ``autorizacoes``."""

from django.apps import AppConfig


class AutorizacoesConfig(AppConfig):
    """App de autorizações publicadas."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "autorizacoes"
