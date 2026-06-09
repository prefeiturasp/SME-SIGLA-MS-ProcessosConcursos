"""Model base com UUID e timestamps para o app concursos."""

import uuid

from auditlog.models import AuditlogHistoryField
from django.db import models


class BaseModel(models.Model):
    """Modelo base abstrato com UUID, histórico e timestamps."""

    history = AuditlogHistoryField()
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    criado_em = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização"
    )

    class Meta:
        """Configuração do serializer."""

        abstract = True
