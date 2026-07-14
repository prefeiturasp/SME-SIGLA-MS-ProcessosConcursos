"""Modelo Concurso."""

from auditlog.registry import auditlog
from core.models import BaseModel
from django.db import models
from django.db.models import Q

from concursos.constants import CONCURSO_STATUS_CHOICES


class Concurso(BaseModel):
    """Concurso com múltiplos cargos vinculados."""

    nome = models.CharField(max_length=200, verbose_name="Nome do Concurso")
    cargos = models.ManyToManyField(
        "concursos.Cargo",
        verbose_name="Cargos",
        related_name="concursos",
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
    status = models.CharField(
        max_length=10,
        choices=CONCURSO_STATUS_CHOICES,
        default="ATIVO",
        verbose_name="Status",
    )

    class Meta:
        """Meta do modelo Concurso."""

        db_table = "concursos"
        verbose_name = "Concurso"
        verbose_name_plural = "Concursos"
        ordering = ["-criado_em"]
        constraints = [
            models.UniqueConstraint(
                fields=["numero_processo"],
                condition=~Q(numero_processo=""),
                name="concurso_numero_processo_unico_nao_vazio",
            ),
        ]

    def __str__(self) -> str:
        """String de representação do objeto."""
        return self.nome


auditlog.register(Concurso)
