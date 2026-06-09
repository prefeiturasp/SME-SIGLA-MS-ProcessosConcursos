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
    numero_processo = models.IntegerField(
        verbose_name="Número do Processo", blank=True, null=True, default=0
    )
    codigo = models.IntegerField(
        verbose_name="Código do Concurso", blank=True, null=True, default=0
    )

    class Meta:
        """Configuração do serializer."""

        db_table = "concursos"
        verbose_name = "Concurso"
        verbose_name_plural = "Concursos"
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        """Executa   str  .

        Args:
            self: Instância do objeto.

        Returns:
            Texto resultante da operação.

        Raises:
            Nenhuma exceção específica documentada.
        """
        return self.nome


auditlog.register(Concurso)
