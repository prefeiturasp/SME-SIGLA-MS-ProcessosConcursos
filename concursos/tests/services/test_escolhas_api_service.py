"""Módulo tests/services/test_escolhas_api_service."""
from unittest.mock import Mock, patch

import pytest
import requests
from django.conf import settings

from concursos.services import EscolhasAPIService


def test_get_escolhas_por_cargo_success():
    """Verifica get escolhas por cargo success.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    service = EscolhasAPIService(
        base_url="http://example.com", timeout_seconds=5
    )
    fake_response = Mock()
    fake_response.json.return_value = {"1001": 5, "1002": 4}
    fake_response.raise_for_status.return_value = None
    with patch(
        "concursos.services.escolhas_api_service.requests.get",
        return_value=fake_response,
    ) as mocked_get:
        resp = service.get_escolhas_por_cargo(headers={"X-Test": "1"})
        assert resp is fake_response
        mocked_get.assert_called_once_with(
            "http://example.com/api/v1/escolhas/agrupar-por-cargo/",
            headers={"Accept": "application/json", "X-Test": "1"},
            timeout=5,
        )
        assert resp.json() == {"1001": 5, "1002": 4}


def test_get_escolhas_por_cargo_http_error_propagates():
    """Verifica get escolhas por cargo http error propagates.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    service = EscolhasAPIService(base_url="http://example.com")
    fake_response = Mock()
    fake_response.raise_for_status.side_effect = requests.HTTPError("boom")
    with (
        patch(
            "concursos.services.escolhas_api_service.requests.get",
            return_value=fake_response,
        ),
        pytest.raises(requests.HTTPError),
    ):
        service.get_escolhas_por_cargo()


def test_init_without_setting_and_without_base_url_raises(monkeypatch):
    # Garante que o setting está ausente/vazio
    """Verifica init without setting and without base url raises.
    
    Args:
        monkeypatch: Fixture do pytest para substituir objetos.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    monkeypatch.setattr(settings, "ESCOLHAS_API_URL", "", raising=False)
    with pytest.raises(ValueError):
        EscolhasAPIService()
