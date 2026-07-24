"""Configuração do Django Admin para autorizações."""

from __future__ import annotations

from django.contrib import admin

from autorizacoes.models import AutorizacaoPublicada


@admin.register(AutorizacaoPublicada)
class AutorizacaoPublicadaAdmin(admin.ModelAdmin):
    """Admin do modelo AutorizacaoPublicada."""

    list_display = [
        "cargo",
        "autorizacoes",
        "data_autorizacao",
        "observacao",
        "criado_em",
        "atualizado_em",
    ]
    list_filter = ["criado_em", "atualizado_em"]
    search_fields = ["cargo__nome", "observacao"]
    readonly_fields = ["uuid", "criado_em", "atualizado_em"]
    ordering = ["-criado_em"]

    fieldsets = (
        (
            "Informações Básicas",
            {
                "fields": (
                    "cargo",
                    "autorizacoes",
                    "data_autorizacao",
                    "observacao",
                )
            },
        ),
        (
            "Metadados",
            {
                "fields": ("uuid", "criado_em", "atualizado_em"),
                "classes": ("collapse",),
            },
        ),
    )
