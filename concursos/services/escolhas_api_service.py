from typing import Optional, Dict, Any

import requests
from django.conf import settings


class EscolhasAPIService:
    """
    Cliente simples para o ms-escolhas, baseado em ESCOLHAS_API_URL.
    """
    def __init__(self, base_url: Optional[str] = None, timeout_seconds: int = 30):
        self.base_url = (base_url or getattr(settings, 'ESCOLHAS_API_URL', '') or '').rstrip('/')
        if not self.base_url:
            raise ValueError('ESCOLHAS_API_URL não configurada')
        self.timeout_seconds = timeout_seconds
        self._default_headers = {
            'Accept': 'application/json',
        }

    def get_escolhas_por_cargo(self,
            headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Executa um GET no ms-escolhas usando o cargo_codigo.
        """
        url = f'{self.base_url}/api/v1/escolhas/agrupar-por-cargo/'
        merged_headers = {**self._default_headers, **(headers or {})}
        response = requests.get(url, headers=merged_headers, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response

