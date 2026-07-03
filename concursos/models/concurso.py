"""Model Concurso."""

from auditlog.registry import auditlog
from django.db import models

from .base import BaseModel
from .cargo import Cargo


class Concurso(BaseModel):
    """Concurso com múltiplos cargos vinculados."""

    nome = models.CharField(max_length=200, verbose_name="Nome do Concurso")
    cargos = models.ManyToManyField(
        Cargo, verbose_name="Cargos", related_name="concursos"
    )
    numero_processo = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Número do Processo",
    )
    codigo = models.IntegerField(
        verbose_name="Código do Concurso", blank=True, null=True
    )
    ano_edital = models.IntegerField(
        verbose_name="Ano do Edital", blank=True, null=True
    )
    banca_responsavel = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Banca Responsável",
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        """Configuração do serializer."""

        db_table = "concursos"
        verbose_name = "Concurso"
        verbose_name_plural = "Concursos"
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        """String de representação do objeto."""
        return self.nome


auditlog.register(Concurso)
