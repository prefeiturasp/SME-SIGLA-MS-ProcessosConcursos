from auditlog.registry import auditlog
from django.db import models

from .base import BaseModel


class Cargo(BaseModel):
    """
    Model para cargos que podem ser associados a concursos.
    """

    nome = models.CharField(max_length=200, verbose_name="Nome do Cargo")
    codigo = models.IntegerField(
        verbose_name="Código do Cargo", blank=True, null=True, default=0
    )

    class Meta:
        db_table = "cargos"
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


auditlog.register(Cargo)
