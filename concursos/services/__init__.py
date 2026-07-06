"""Módulo services/__init__."""

from .escolhas_api_service import EscolhasAPIService
from .extracao_dados import montar_extracao_dados
from concursos.models import Concurso


def numero_processo_esta_disponivel(
    numero_processo: str, excluir_uuid: str | None = None
) -> bool:
    """Verifica se um numero de processo esta disponivel.

    Valores vazios sao sempre considerados disponiveis (multiplos
    concursos podem ter numero_processo vazio).

    Args:
        numero_processo: Numero do processo a verificar.
        excluir_uuid: UUID de um concurso a ignorar na checagem
            (usado na edicao, para o concurso nao conflitar consigo
            mesmo).

    Returns:
        True se o numero estiver vazio ou se nenhum outro concurso o
        usar, False caso contrario.
    """
    if not numero_processo:
        return True

    queryset = Concurso.objects.filter(numero_processo=numero_processo)
    if excluir_uuid:
        queryset = queryset.exclude(uuid=excluir_uuid)
    return not queryset.exists()
