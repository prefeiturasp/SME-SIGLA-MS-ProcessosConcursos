"""Cliente HTTP para o MS-Escolhas."""

from __future__ import annotations

import logging

import requests
from django.conf import settings
from sigla_sdk.context import get_correlation_id

logger = logging.getLogger(__name__)


class EscolhasAPIService:
    """Cliente para endpoints do microserviço de escolhas."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        """Inicializa cliente com URL base e timeout.

        Args:
            self: Instância do objeto.
            base_url: sobrescreve ``ESCOLHAS_API_URL`` das settings.
            timeout_seconds: timeout das requisições HTTP.

        Raises:
            ValueError: se ``ESCOLHAS_API_URL`` não estiver configurada.
        """
        self.base_url = (
            base_url or getattr(settings, "ESCOLHAS_API_URL", "") or ""
        ).rstrip("/")
        if not self.base_url:
            raise ValueError("ESCOLHAS_API_URL não configurada")
        self.timeout_seconds = timeout_seconds
        self.headers: dict[str, str] = {
            "Accept": "application/json",
            settings.API_KEY_HEADER: settings.ESCOLHAS_API_KEY,
        }

    def get_escolhas_por_cargo(
        self,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Agrupa escolhas por código de cargo no MS-Escolhas.

        Args:
            self: Instância do objeto.
            headers: cabeçalhos HTTP adicionais.

        Returns:
            Resposta HTTP com o resultado da operação.

        Raises:
            Nenhuma exceção específica documentada.
        """
        url = f"{self.base_url}/api/v1/escolhas/agrupar-por-cargo/"
        merged_headers = {**self.headers, **(headers or {})}
        logger.info(
            "Consultando escolhas por cargo no MS-Escolhas",
            extra={
                "correlation_id": get_correlation_id(),
                "method": "GET",
                "url": url,
                "headers": merged_headers.keys(),
            },
        )
        response = requests.get(
            url, headers=merged_headers, timeout=self.timeout_seconds
        )
        response.raise_for_status()
        return response
