"""Serviços de cargos e agregações com MS-Escolhas."""

from __future__ import annotations

from typing import Any

from cargos.repository import CargoRepository
from cargos.services.escolhas_api_service import EscolhasAPIService


class CargosService:
    """Orquestra dados de cargos com integrações externas."""

    @staticmethod
    def listar_autorizacoes_publicadas_agregadas() -> list[dict[str, Any]]:
        """Lista cargos com totais de autorizações e escolhas."""
        escolhas_por_cargo: dict[str | int, Any] = {}
        resp = EscolhasAPIService().get_escolhas_por_cargo()
        escolhas_por_cargo = resp.json()

        cargos = CargoRepository.listar_com_resumo_autorizacoes()
        resultado: list[dict[str, Any]] = []
        for cargo in cargos:
            codigo = cargo["codigo"]
            total_escolhas = (
                escolhas_por_cargo.get(str(codigo))
                or escolhas_por_cargo.get(codigo)
                or 0
            )
            resultado.append(
                {
                    **cargo,
                    "total_escolhas": int(total_escolhas or 0),
                }
            )
        return resultado
