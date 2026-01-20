import pytest
from unittest.mock import Mock, patch
import requests

from concursos.services import sme_integration as svc


def _set_settings(settings, url='http://api.local', token='secret'):
    settings.SMEINTEGRACAO_API_URL = url
    settings.SMEINTEGRACAO_API_TOKEN = token


def test_buscar_cargos_sucesso(settings):
    _set_settings(settings)

    payload = [
        {'codigoCargo': 101, 'nomeCargo': 'Professor A'},
        {'codigoCargo': 102, 'nomeCargo': 'Professor B'},
    ]
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None

    with patch('requests.get', return_value=mock_resp) as mock_get:
        result = svc.buscar_cargos_de_smeintegracao()

    # Verifica chamada
    mock_get.assert_called_once_with(
        'http://api.local/api/cargos',
        headers={'x-api-eol-key': 'secret', 'Accept': 'application/json'},
        timeout=30,
    )
    # Verifica transformação
    assert result == [
        {'codigo': '101', 'nome': 'Professor A'},
        {'codigo': '102', 'nome': 'Professor B'},
    ]


def test_buscar_cargos_payload_invalido(settings):
    _set_settings(settings)
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = {'unexpected': 'obj'}  # não é lista
    mock_resp.raise_for_status.return_value = None

    with patch('requests.get', return_value=mock_resp):
        with pytest.raises(ValueError):
            svc.buscar_cargos_de_smeintegracao()


def test_buscar_cargos_http_error(settings):
    _set_settings(settings)
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError('boom')

    with patch('requests.get', return_value=mock_resp):
        with pytest.raises(requests.HTTPError):
            svc.buscar_cargos_de_smeintegracao()


def test_buscar_concursos_sucesso(settings):
    _set_settings(settings)
    payload = [
        {
            'codigo': 1,
            'descricao': 'Concurso 2026',
            'numeroProcesso': 999,
            'cargos': [101, 102],
        }
    ]
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None

    with patch('requests.get', return_value=mock_resp) as mock_get:
        result = svc.buscar_concursos_de_smeintegracao()

    mock_get.assert_called_once_with(
        'http://api.local/api/concurso/tipos',
        headers={'x-api-eol-key': 'secret', 'Accept': 'application/json'},
        timeout=30,
    )
    assert result == [
        {
            'codigo': 1,
            'nome': 'Concurso 2026',
            'numero_processo': 999,
            'cargos': [101, 102],
        }
    ]


def test_buscar_concursos_payload_invalido(settings):
    _set_settings(settings)
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = {'unexpected': 'obj'}  # não é lista
    mock_resp.raise_for_status.return_value = None

    with patch('requests.get', return_value=mock_resp):
        with pytest.raises(ValueError):
            svc.buscar_concursos_de_smeintegracao()


def test_settings_faltando_url(settings):
    # Falta URL
    _set_settings(settings, url=None, token='x')
    with pytest.raises(ValueError):
        svc.buscar_cargos_de_smeintegracao()


def test_settings_faltando_token(settings):
    # Falta token
    _set_settings(settings, url='http://api', token=None)
    with pytest.raises(ValueError):
        svc.buscar_concursos_de_smeintegracao()


