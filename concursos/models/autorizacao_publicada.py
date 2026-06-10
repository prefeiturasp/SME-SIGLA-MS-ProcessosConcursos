"""Módulo models/autorizacao_publicada."""

from auditlog.registry import auditlog
from django.db import models

from .base import BaseModel
from .cargo import Cargo


class AutorizacaoPublicada(BaseModel):
    """Registra informações de autorizações publicadas."""

    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.PROTECT,
        related_name="autorizacoes",
        null=True,
        blank=True,
        verbose_name="Cargo",
    )
    autorizacoes = models.IntegerField(default=0, verbose_name="Autorizações")
    data_autorizacao = models.DateField(
        null=True, blank=True, verbose_name="Data da autorização"
    )
    observacao = models.CharField(
        max_length=500, blank=True, default="", verbose_name="Observação"
    )

    class Meta:
        """Configuração do serializer."""

        db_table = "autorizacoes_publicadas"
        verbose_name = "Autorização Publicada"
        verbose_name_plural = "Autorizações Publicadas"
        ordering = ["-data_autorizacao", "-criado_em"]

    def __str__(self) -> str:
        """Retorna a string de representação do objeto."""
        return f"Autorização {self.uuid}"


auditlog.register(AutorizacaoPublicada)
