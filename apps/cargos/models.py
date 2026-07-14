"""Modelo Cargo."""

from auditlog.registry import auditlog
from core.models import BaseModel
from django.db import models


class Cargo(BaseModel):
    """Cargo que pode ser associado a concursos."""

    nome = models.CharField(max_length=200, verbose_name="Nome do Cargo")
    codigo = models.IntegerField(
        verbose_name="Código do Cargo", blank=True, null=True, default=0
    )

    class Meta:
        """Meta do modelo Cargo."""

        # Mantém o label histórico das migrations em ``concursos``.
        app_label = "concursos"
        db_table = "cargos"
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ["nome"]

    def __str__(self) -> str:
        """String de representação do objeto."""
        return self.nome


auditlog.register(Cargo)
