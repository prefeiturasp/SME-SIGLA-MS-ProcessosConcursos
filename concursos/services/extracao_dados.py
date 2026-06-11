"""Agregações para a extração de dados de autorizações publicadas."""

from typing import Any, Optional, Union
from uuid import UUID

from django.db.models import Sum
from django.db.models.functions import ExtractYear

from concursos.models import AutorizacaoPublicada, Concurso


def montar_extracao_dados(
    concurso_uuid: Optional[Union[UUID, str]] = None,
    anos: Optional[list[int]] = None,
) -> dict[str, Any]:
    """
    Monta o dicionário de total de autorizações publicadas (SUM) por ano.

    O resultado é sempre quebrado por ano de ``data_autorizacao``:

    - ``concurso_uuid`` + ``anos`` juntos: filtra pelos cargos do concurso
      (``Concurso.cargos``) e restringe aos anos informados.
    - Ambos ausentes: retorna todos os anos existentes, somando os cargos de
      todos os concursos.

    Registros com ``data_autorizacao`` nulo são ignorados.
    """
    qs = AutorizacaoPublicada.objects.filter(data_autorizacao__isnull=False)

    if concurso_uuid:
        cargos_ids = Concurso.objects.filter(
            uuid=concurso_uuid
        ).values_list("cargos__uuid", flat=True)
        qs = qs.filter(cargo__uuid__in=cargos_ids)

    totais = (
        qs.annotate(ano=ExtractYear("data_autorizacao"))
        .values("ano")
        .annotate(total=Sum("autorizacoes"))
        .order_by("ano")
    )
    if anos:
        totais = totais.filter(ano__in=anos)

    return {
        str(item["ano"]): {"autorizacoes-publicadas": item["total"]}
        for item in totais
    }
