"""Configuração do Django Admin para concursos."""

from __future__ import annotations

from django.contrib import admin

from .models import AutorizacaoPublicada, Cargo, Concurso


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

    def cargos_count(self, obj: Concurso) -> int:
        """Quantidade de cargos vinculados ao concurso.
        
        Args:
            self: Instância do objeto.
            obj: Instância do objeto processado.
        
        Returns:
            Valor inteiro calculado.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        return obj.cargos.count()

    cargos_count.short_description = "Número de Cargos"


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
