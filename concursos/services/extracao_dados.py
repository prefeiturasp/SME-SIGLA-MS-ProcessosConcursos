"""Agregações para a extração de dados de autorizações publicadas."""

from typing import Any
from uuid import UUID

from django.db.models import Sum
from django.db.models.functions import ExtractYear

from concursos.models import AutorizacaoPublicada, Concurso


def montar_extracao_dados(
    concurso_uuid: UUID | str | None = None,
    anos: list[int] | None = None,
) -> dict[str, Any]:
    """
    Monta o dicionário de total de autorizações publicadas (SUM).

    - ``concurso_uuid`` é opcional: ausente → agrega autorizações de todos
      os concursos; presente → filtra pelos cargos do concurso
      (``Concurso.cargos``).
    - Com ``anos``: agrupa por ano de ``data_autorizacao`` e restringe a
      esses anos.
    - Sem ``anos``: retorna a soma de todas as autorizações na raiz, em
      ``"autorizacoes-publicadas"`` (forma plana, sem quebra por ano).

    Registros com ``data_autorizacao`` nulo são ignorados.
    """
    qs = AutorizacaoPublicada.objects.filter(data_autorizacao__isnull=False)

    if concurso_uuid:
        cargos_ids = Concurso.objects.filter(uuid=concurso_uuid).values_list(
            "cargos__uuid", flat=True
        )
        qs = qs.filter(cargo__uuid__in=cargos_ids)

    if anos:
        totais = (
            qs.annotate(ano=ExtractYear("data_autorizacao"))
            .values("ano")
            .annotate(total=Sum("autorizacoes"))
            .filter(ano__in=anos)
        )
        return {
            str(item["ano"]): {"autorizacoes-publicadas": item["total"]}
            for item in totais
        }

    total = qs.aggregate(total=Sum("autorizacoes"))["total"] or 0
    return {"autorizacoes-publicadas": total}
