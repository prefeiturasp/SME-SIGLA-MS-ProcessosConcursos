"""Modelo Concurso."""

from auditlog.registry import auditlog
from django.db import models
from django.db.models import Q

from concursos.constants import (
    CONCURSO_SITUACAO_CHOICES,
    CONCURSO_SITUACAO_INCOMPLETO,
    CONCURSO_STATUS_CHOICES,
)
from core.models import BaseModel


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
    situacao = models.CharField(
        max_length=20,
        choices=CONCURSO_SITUACAO_CHOICES,
        default=CONCURSO_SITUACAO_INCOMPLETO,
        verbose_name="Situação do Concurso",
    )
    data_autorizacao = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Autorização do Concurso",
    )
    data_abertura = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Abertura do Concurso",
    )
    classificacao_final = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data da Classificação Final",
    )
    link_edital = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="Link do Edital",
    )
    habilitados_geral = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Habilitados (Geral)",
    )
    habilitados_nna = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Habilitados (NNA)",
    )
    habilitados_pcd = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Habilitados (PcD)",
    )
    retificacoes = models.TextField(
        blank=True,
        default="",
        verbose_name="Retificações",
    )
    data_homologacao = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data da Homologação",
    )
    data_prorrogacao = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data da Prorrogação",
    )
    vigencia_inicio = models.DateField(
        blank=True,
        null=True,
        verbose_name="Início da Vigência",
    )
    vigencia_fim = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fim da Vigência",
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
        """Representação textual do concurso."""
        return self.nome


auditlog.register(Concurso)
