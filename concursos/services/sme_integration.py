from typing import List, Dict, Any, Tuple

import requests
from django.conf import settings


def _get_base_url_and_headers() -> Tuple[str, Dict[str, str]]:
    base_url = getattr(settings, 'SMEINTEGRACAO_API_URL', None)
    token = getattr(settings, 'SMEINTEGRACAO_API_TOKEN', None)

    if not base_url:
        raise ValueError('SMEINTEGRACAO_API_URL não configurada')
    if not token:
        raise ValueError('SMEINTEGRACAO_API_TOKEN não configurada')

    headers = {
        'x-api-eol-key': token,
        'Accept': 'application/json',
    }
    return base_url.rstrip('/'), headers


def buscar_cargos_de_smeintegracao() -> List[Dict[str, Any]]:
    base_url, headers = _get_base_url_and_headers()
    url = base_url + '/api/cargos'

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    payload = response.json()
    print(payload)
    if not isinstance(payload, list):
        raise ValueError('Formato de resposta inesperado ao buscar Cargos')

    list_cargos: List[Dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        codigo = item.get('codigoCargo')
        nome = item.get('nomeCargo')
        if not codigo or not nome:
            continue
        list_cargos.append({
            'codigo': str(codigo),
            'nome': str(nome),
        })

    return list_cargos


def buscar_concursos_de_smeintegracao() -> List[Dict[str, Any]]:
    base_url, headers = _get_base_url_and_headers()
    url = base_url + '/api/concurso/tipos'

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    payload = response.json()
    print(payload)
    if not isinstance(payload, list):
        raise ValueError('Formato de resposta inesperado ao buscar Concursos')

    list_concursos: List[Dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        codigo = item.get('codigo')
        nome = item.get('descricao')
        numero_processo = item.get('numeroProcesso')
        cargos = item.get('cargos')
        if not codigo or not nome or not numero_processo or not cargos:
            continue
        list_concursos.append({
            'codigo': int(codigo),
            'nome': nome,
            'numero_processo': int(numero_processo),
            'cargos': [int(cargo) for cargo in cargos],
        })

    return list_concursos