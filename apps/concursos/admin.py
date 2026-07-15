"""Configuração do Django Admin para concursos."""

from __future__ import annotations

from django.contrib import admin

from concursos.models import Concurso


class CargoInline(admin.TabularInline):
    """Inline M2M de cargos em concurso."""

    model = Concurso.cargos.through
    extra = 1
    verbose_name = "Cargo"
    verbose_name_plural = "Cargos"


@admin.register(Concurso)
class ConcursoAdmin(admin.ModelAdmin):
    """Admin do modelo Concurso."""

    list_display = [
        "nome",
        "uuid",
        "cargos_count",
        "criado_em",
        "atualizado_em",
    ]
    list_filter = ["criado_em", "atualizado_em"]
    search_fields = ["nome"]
    readonly_fields = ["uuid", "criado_em", "atualizado_em"]
    ordering = ["-criado_em"]

    fieldsets = (
        ("Informações Básicas", {"fields": ("nome",)}),
        ("Cargos", {"fields": ("cargos",)}),
        (
            "Metadados",
            {
                "fields": ("uuid", "criado_em", "atualizado_em"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Número de Cargos")
    def cargos_count(self, obj: Concurso) -> int:
        """Quantidade de cargos vinculados ao concurso."""
        return obj.cargos.count()
