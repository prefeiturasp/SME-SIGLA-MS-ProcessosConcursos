"""Repositório de acesso a dados de autorizações publicadas.

As consultas de leitura retornam dados já serializados (dict / list[dict]),
não QuerySets do Django.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any
from uuid import UUID

from django.db.models import Max, Sum
from django.db.models.functions import ExtractYear

from autorizacoes.models import AutorizacaoPublicada
from concursos.repository import ConcursosRepository


class AutorizacaoRepository:
    """Acesso aos dados de autorizações publicadas."""

    @staticmethod
    def montar_resposta(
        autorizacao: AutorizacaoPublicada,
    ) -> dict[str, Any]:
        """Transforma uma autorização em dicionário de resposta da API."""
        from autorizacoes.serializers import AutorizacaoPublicadaSerializer

        return AutorizacaoPublicadaSerializer(autorizacao).data

    @classmethod
    def montar_lista_resposta(
        cls, autorizacoes: list[AutorizacaoPublicada]
    ) -> list[dict[str, Any]]:
        """Transforma uma lista de autorizações em dicionários de resposta."""
        from autorizacoes.serializers import AutorizacaoPublicadaSerializer

        return AutorizacaoPublicadaSerializer(autorizacoes, many=True).data

    @staticmethod
    def _formatar_data(value: date | None) -> str | None:
        """Formata a data de autorização em ISO."""
        if value is None:
            return None
        return value.isoformat()

    @classmethod
    def _montar_resumo_cargo(
        cls,
        cargo_uuid: UUID,
        nome: str,
        codigo: int | None,
        autorizacoes: int | None,
        data_autorizacao: date | None,
    ) -> dict[str, Any]:
        """Monta o resumo de totais de um cargo."""
        return {
            "uuid": str(cargo_uuid),
            "nome": nome,
            "codigo": codigo,
            "autorizacoes": autorizacoes or 0,
            "data_autorizacao": cls._formatar_data(data_autorizacao),
        }

    @classmethod
    def montar_extracao_dados(
        cls,
        *,
        concurso_uuid: UUID | str | None = None,
        anos: list[int] | None = None,
    ) -> dict[str, Any]:
        """Monta a extração de dados com totais por cargo (e por ano, se pedido)."""
        qs = AutorizacaoPublicada.objects.filter(
            data_autorizacao__isnull=False
        )

        if concurso_uuid:
            cargos_ids = ConcursosRepository.listar_uuids_cargos_vinculados(
                concurso_uuid
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
            cargos_por_ano: dict[int, list[dict[str, Any]]] = defaultdict(
                list
            )
            for item in cargos_por_ano_raw:
                cargos_por_ano[item["ano"]].append(
                    cls._montar_resumo_cargo(
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
        itens = (
            qs.filter(cargo__isnull=False)
            .values("cargo__uuid", "cargo__nome", "cargo__codigo")
            .annotate(
                total=Sum("autorizacoes"),
                data_autorizacao=Max("data_autorizacao"),
            )
            .order_by("cargo__nome")
        )
        cargos = [
            cls._montar_resumo_cargo(
                item["cargo__uuid"],
                item["cargo__nome"],
                item["cargo__codigo"],
                item["total"],
                item["data_autorizacao"],
            )
            for item in itens
        ]
        return {"autorizacoes-publicadas": total, "cargos": cargos}
