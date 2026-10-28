"""Modelos compartilhados do projeto."""

import uuid

from auditlog.models import AuditlogHistoryField
from django.db import models


class BaseModel(models.Model):
    """Modelo base abstrato com ``id`` padrão, UUID público e histórico.

    Também traz ``criado_em`` e ``atualizado_em``.
    """

    history = AuditlogHistoryField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    criado_em = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização"
    )

    class Meta:
        abstract = True
