"""Cliente HTTP para o MS-Escolhas."""

from __future__ import annotations

import requests
from django.conf import settings


class EscolhasAPIService:
    """Cliente para endpoints do microserviço de escolhas."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        """Inicializa cliente com URL base e timeout.

        Args:
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
        self._default_headers: dict[str, str] = {
            "Accept": "application/json",
        }

    def get_escolhas_por_cargo(
        self,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Agrupa escolhas por código de cargo no MS-Escolhas.

        Args:
            headers: cabeçalhos HTTP adicionais.

        Returns:
            Response HTTP com JSON ``{codigo_cargo: total, ...}``.

        Raises:
            requests.HTTPError: status HTTP de erro.
            requests.RequestException: falha de conexão.
        """
        url = f"{self.base_url}/api/v1/escolhas/agrupar-por-cargo/"
        merged_headers = {**self._default_headers, **(headers or {})}
        response = requests.get(
            url, headers=merged_headers, timeout=self.timeout_seconds
        )
        response.raise_for_status()
        return response
