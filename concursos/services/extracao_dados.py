"""Agregações para a extração de dados de autorizações publicadas."""

from collections import defaultdict
from datetime import date
from typing import Any
from uuid import UUID

from django.db.models import Max, QuerySet, Sum
from django.db.models.functions import ExtractYear

from concursos.models import AutorizacaoPublicada, Concurso


def _formatar_data_autorizacao(value: date | None) -> str | None:
    """Formata a data de autorização em ISO.

    Args:
        value: Data a formatar; ausente → ``None``.

    Returns:
        Data em formato ISO ou ``None``.
    """
    if value is None:
        return None
    return value.isoformat()


def _montar_item_cargo(
    cargo_uuid: UUID,
    nome: str,
    codigo: int | None,
    autorizacoes: int | None,
    data_autorizacao: date | None,
) -> dict[str, Any]:
    """Monta o item de totais de um cargo.

    Args:
        cargo_uuid: UUID do cargo.
        nome: Nome do cargo.
        codigo: Código do cargo.
        autorizacoes: Total de autorizações do cargo.
        data_autorizacao: Data de autorização mais recente.

    Returns:
        Dicionário com os dados do cargo.
    """
    return {
        "uuid": str(cargo_uuid),
        "nome": nome,
        "codigo": codigo,
        "autorizacoes": autorizacoes or 0,
        "data_autorizacao": _formatar_data_autorizacao(
            data_autorizacao
        ),
    }


def _totais_por_cargo(qs: QuerySet) -> list[dict[str, Any]]:
    """Soma autorizações agrupadas por cargo.

    Args:
        qs: Queryset de autorizações a agregar.

    Returns:
        Lista de cargos com os totais de autorizações.
    """
    itens = (
        qs.filter(cargo__isnull=False)
        .values("cargo__uuid", "cargo__nome", "cargo__codigo")
        .annotate(
            total=Sum("autorizacoes"),
            data_autorizacao=Max("data_autorizacao"),
        )
        .order_by("cargo__nome")
    )
    return [
        _montar_item_cargo(
            item["cargo__uuid"],
            item["cargo__nome"],
            item["cargo__codigo"],
            item["total"],
            item["data_autorizacao"],
        )
        for item in itens
    ]


def montar_extracao_dados(
    concurso_uuid: UUID | str | None = None,
    anos: list[int] | None = None,
) -> dict[str, Any]:
    """Monta o dicionário de total de autorizações publicadas.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        anos: Anos de ``data_autorizacao`` a filtrar; ausente → soma total
            na raiz, sem quebra por ano.

    Returns:
        Dicionário com ``autorizacoes-publicadas`` (total) e ``cargos``
        (totais por cargo).
    """
    qs = AutorizacaoPublicada.objects.filter(data_autorizacao__isnull=False)

    if concurso_uuid:
        cargos_ids = Concurso.objects.filter(uuid=concurso_uuid).values_list(
            "cargos__uuid", flat=True
        )
        qs = qs.filter(cargo__uuid__in=cargos_ids)

    if anos:
        totais_ano = (
            qs.annotate(ano=ExtractYear("data_autorizacao"))
            .values("ano")
            .annotate(total=Sum("autorizacoes"))
            .filter(ano__in=anos)
        )
        cargos_por_ano_raw = (
            qs.annotate(ano=ExtractYear("data_autorizacao"))
            .filter(ano__in=anos, cargo__isnull=False)
            .values("ano", "cargo__uuid", "cargo__nome", "cargo__codigo")
            .annotate(
                total=Sum("autorizacoes"),
                data_autorizacao=Max("data_autorizacao"),
            )
            .order_by("ano", "cargo__nome")
        )
        cargos_por_ano: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for item in cargos_por_ano_raw:
            cargos_por_ano[item["ano"]].append(
                _montar_item_cargo(
                    item["cargo__uuid"],
                    item["cargo__nome"],
                    item["cargo__codigo"],
                    item["total"],
                    item["data_autorizacao"],
                )
            )

        totais_por_ano = {
            item["ano"]: item["total"] or 0 for item in totais_ano
        }

        return {
            str(ano): {
                "autorizacoes-publicadas": totais_por_ano.get(ano, 0),
                "cargos": cargos_por_ano.get(ano, []),
            }
            for ano in anos
        }

    total = qs.aggregate(total=Sum("autorizacoes"))["total"] or 0
    return {"autorizacoes-publicadas": total,"cargos": _totais_por_cargo(qs)}
