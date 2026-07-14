"""Agregações para a extração de dados de autorizações publicadas."""

from typing import Any
from uuid import UUID

from autorizacoes.repository import AutorizacaoRepository


def montar_extracao_dados(
    concurso_uuid: UUID | str | None = None,
    anos: list[int] | None = None,
) -> dict[str, Any]:
    """Monta o dicionário de total de autorizações publicadas."""
    return AutorizacaoRepository.montar_extracao_dados(
        concurso_uuid=concurso_uuid,
        anos=anos,
    )
