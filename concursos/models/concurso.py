from auditlog.registry import auditlog
from django.db import models

from .base import BaseModel
from .cargo import Cargo


class Concurso(BaseModel):
    """
    Model para concursos que podem ter múltiplos cargos.
    """

    nome = models.CharField(max_length=200, verbose_name="Nome do Concurso")
    cargos = models.ManyToManyField(
        Cargo, verbose_name="Cargos", related_name="concursos"
    )
    numero_processo = models.IntegerField(
        verbose_name="Número do Processo", blank=True, null=True, default=0
    )
    codigo = models.IntegerField(
        verbose_name="Código do Concurso", blank=True, null=True, default=0
    )

    class Meta:
        db_table = "concursos"
        verbose_name = "Concurso"
        verbose_name_plural = "Concursos"
        ordering = ["-criado_em"]

    def __str__(self):
        return self.nome


auditlog.register(Concurso)
