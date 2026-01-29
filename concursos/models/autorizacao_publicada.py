from django.db import models
from auditlog.registry import auditlog
from .base import BaseModel
from .cargo import Cargo


class AutorizacaoPublicada(BaseModel):
    """
    Registra informações de autorizações publicadas.
    """
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, related_name='autorizacoes', null=True, blank=True, verbose_name="Cargo")
    vagas_sem_efeito = models.BooleanField(default=False, verbose_name="Vagas sem efeito")
    autorizacoes = models.IntegerField(default=0, verbose_name="Autorizações")
    autorizacoes_sem_efeito = models.IntegerField(default=0, verbose_name="Autorizações sem efeito")
    data_autorizacao = models.DateField(null=True, blank=True, verbose_name="Data da autorização")
    observacao = models.CharField(max_length=500, blank=True, default='', verbose_name="Observação")

    class Meta:
        db_table = 'autorizacoes_publicadas'
        verbose_name = "Autorização Publicada"
        verbose_name_plural = "Autorizações Publicadas"
        ordering = ['-data_autorizacao', '-criado_em']

    def __str__(self) -> str:
        return f"Autorização {self.uuid}"


auditlog.register(AutorizacaoPublicada)
