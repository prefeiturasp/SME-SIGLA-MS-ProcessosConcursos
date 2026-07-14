"""Repositório de acesso a dados de concursos.

As consultas de leitura retornam dados já serializados (dict / list[dict]),
não QuerySets do Django.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from concursos.models import Concurso


class ConcursosRepository:
    """Acesso aos dados de concursos (consultas e persistência)."""

    @staticmethod
    def montar_resposta(concurso: Concurso) -> dict[str, Any]:
        """Transforma um concurso em dicionário de resposta da API."""
        from concursos.serializers import ConcursoSerializer

        return ConcursoSerializer(concurso).data

    @classmethod
    def montar_lista_resposta(
        cls, concursos: list[Concurso]
    ) -> list[dict[str, Any]]:
        """Transforma uma lista de concursos em dicionários de listagem."""
        from concursos.serializers import ConcursoListSerializer

        return ConcursoListSerializer(concursos, many=True).data

    @classmethod
    def montar_opcoes_select(
        cls, concursos: list[Concurso]
    ) -> list[dict[str, Any]]:
        """Transforma concursos no formato value/label para selects."""
        from concursos.serializers import ConcursoSelectSerializer

        return ConcursoSelectSerializer(concursos, many=True).data

    @classmethod
    def listar_uuids_cargos_vinculados(
        cls, concurso_uuid: UUID | str
    ) -> list[UUID]:
        """Lista os UUIDs dos cargos vinculados a um concurso."""
        return list(
            Concurso.objects.filter(uuid=concurso_uuid).values_list(
                "cargos__uuid", flat=True
            )
        )

    @classmethod
    def obter_modelo_por_uuid(
        cls, concurso_uuid: str | UUID
    ) -> Concurso | None:
        """Busca o registro do concurso pelo UUID (para escrita/atualização)."""
        return Concurso.objects.filter(uuid=concurso_uuid).first()

    @classmethod
    def obter_por_uuid(
        cls, concurso_uuid: str | UUID
    ) -> dict[str, Any] | None:
        """Busca um concurso pelo UUID e devolve a resposta serializada."""
        concurso = cls.obter_modelo_por_uuid(concurso_uuid)
        if concurso is None:
            return None
        return cls.montar_resposta(concurso)
