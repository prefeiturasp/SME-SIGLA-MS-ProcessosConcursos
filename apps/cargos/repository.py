"""Repositório de acesso a dados de cargos.

As consultas de leitura retornam dados já serializados (dict / list[dict]),
não QuerySets do Django.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from django.db.models import Max, Sum

from cargos.models import Cargo


class CargoRepository:
    """Acesso aos dados de cargos (consultas e persistência)."""

    @staticmethod
    def montar_resposta(cargo: Cargo) -> dict[str, Any]:
        """Transforma um cargo em dicionário de resposta da API."""
        from cargos.serializers import CargoSerializer

        return CargoSerializer(cargo).data

    @classmethod
    def montar_lista_resposta(
        cls, cargos: list[Cargo]
    ) -> list[dict[str, Any]]:
        """Transforma uma lista de cargos em dicionários de resposta."""
        from cargos.serializers import CargoSerializer

        return CargoSerializer(cargos, many=True).data

    @classmethod
    def listar_todos(cls) -> list[dict[str, Any]]:
        """Lista todos os cargos (mais recentes primeiro)."""
        cargos = list(Cargo.objects.all().order_by("-criado_em"))
        return cls.montar_lista_resposta(cargos)

    @classmethod
    def obter_por_uuid(cls, cargo_uuid: str | UUID) -> dict[str, Any] | None:
        """Busca um cargo pelo UUID e devolve a resposta serializada."""
        cargo = Cargo.objects.filter(uuid=cargo_uuid).first()
        return cls.montar_resposta(cargo) if cargo else None

    @classmethod
    def listar_com_resumo_autorizacoes(cls) -> list[dict[str, Any]]:
        """Lista cargos com total de autorizações e data mais recente."""
        cargos = list(
            Cargo.objects.all()
            .annotate(
                total_autorizacoes=Sum("autorizacoes__autorizacoes"),
                ultima_autorizacao=Max("autorizacoes__data_autorizacao"),
            )
            .order_by("nome")
        )
        resultado: list[dict[str, Any]] = []
        for cargo in cargos:
            data_autorizacao = (
                cargo.ultima_autorizacao.isoformat()
                if cargo.ultima_autorizacao
                else None
            )
            resultado.append(
                {
                    "uuid": str(cargo.uuid),
                    "nome": cargo.nome,
                    "codigo": cargo.codigo,
                    "autorizacoes": int(cargo.total_autorizacoes or 0),
                    "data_autorizacao_mais_recente": data_autorizacao,
                }
            )
        return resultado
