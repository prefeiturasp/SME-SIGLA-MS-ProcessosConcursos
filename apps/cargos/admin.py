"""Configuração do Django Admin para cargos."""

from __future__ import annotations

from django.contrib import admin

from cargos.models import Cargo


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    """Admin do modelo Cargo."""

    list_display = ["nome", "uuid", "codigo", "criado_em", "atualizado_em"]
    list_filter = ["criado_em", "atualizado_em"]
    search_fields = ["nome"]
    readonly_fields = ["uuid", "criado_em", "atualizado_em"]
    ordering = ["nome"]

    fieldsets = (
        ("Informações Básicas", {"fields": ("nome",)}),
        (
            "Metadados",
            {
                "fields": ("uuid", "criado_em", "atualizado_em"),
                "classes": ("collapse",),
            },
        ),
    )
